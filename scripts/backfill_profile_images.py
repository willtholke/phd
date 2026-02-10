#!/usr/bin/env python3
"""
Backfill missing profile images using FLUX 2 Klein.

Reads the list of tasker IDs that are missing images, excludes the last 25
taskers and a random 5% sample, then generates images for the rest.

Usage:
    python scripts/backfill_profile_images.py --dry-run
    python scripts/backfill_profile_images.py
"""

import os
import sys
import random
import asyncio
import argparse
import time
from typing import Optional, Dict, List, Set

import psycopg2
import psycopg2.extras
import httpx
import boto3

# ─── Configuration ────────────────────────────────────────────────────────────

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_H6ces9NyVEtw@ep-broad-haze-aifq29n7.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)
FAL_KEY = os.environ.get("FAL_KEY", "")
S3_BUCKET = os.environ.get("S3_BUCKET", "peregrine-human-data")
S3_PREFIX = "profile-images"
S3_REGION = "us-east-1"

MAX_CONCURRENCY = 3
MISSING_IDS_FILE = "/tmp/missing_ids.txt"

# Last 25 tasker IDs should have no image
LAST_25_START = 4308  # IDs 4308-4332 inclusive
TOTAL_TASKERS = 4332
TARGET_NO_IMAGE_PCT = 0.05  # 5%

# ─── Import prompt logic from main script ─────────────────────────────────────

# We import the shared logic inline to keep this self-contained
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)
from generate_profile_images import (
    PHOTO_STYLES,
    infer_ethnicity,
    build_prompt,
)

# Style choices for backfill — no "no_image" since we already filtered
BACKFILL_STYLES = {k: v for k, v in PHOTO_STYLES.items() if k != "no_image"}
# Normalize weights
_total_w = sum(BACKFILL_STYLES.values())
BACKFILL_STYLES = {k: v / _total_w for k, v in BACKFILL_STYLES.items()}


def assign_backfill_style(tasker_id):
    """Assign a photo style for backfill (never no_image)."""
    rng = random.Random(99 + tasker_id)  # Different seed from original
    styles = list(BACKFILL_STYLES.keys())
    weights = list(BACKFILL_STYLES.values())
    return rng.choices(styles, weights=weights, k=1)[0]


# ─── fal.ai client ───────────────────────────────────────────────────────────


async def generate_image(client, prompt, tasker_id):
    # type: (httpx.AsyncClient, str, int) -> Optional[bytes]
    """Call fal.ai FLUX 2 Klein 4B. Returns image bytes."""
    url = "https://fal.run/fal-ai/flux-2/klein/4b"

    headers = {
        "Authorization": "Key %s" % FAL_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "prompt": prompt,
        "image_size": "square",
        "num_images": 1,
        "output_format": "jpeg",
        "enable_safety_checker": False,
    }

    try:
        resp = await client.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        result = resp.json()
        image_url = result["images"][0]["url"]

        img_resp = await client.get(image_url, timeout=30)
        img_resp.raise_for_status()
        return img_resp.content

    except Exception as e:
        print("  [ERROR] Tasker %d: %s" % (tasker_id, e))
        return None


# ─── S3 upload ────────────────────────────────────────────────────────────────


def upload_to_s3(s3_client, image_bytes, tasker_id):
    key = "%s/%d_profile_image.jpg" % (S3_PREFIX, tasker_id)
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=image_bytes,
        ContentType="image/jpeg",
    )
    return "s3://%s/%s" % (S3_BUCKET, key)


# ─── Main pipeline ───────────────────────────────────────────────────────────


def compute_backfill_ids(missing_ids):
    # type: (List[int]) -> tuple
    """Figure out which missing IDs should get images."""
    last_25 = set(range(LAST_25_START, TOTAL_TASKERS + 1))

    # Split: last-25 stay no-image, rest are candidates
    in_last_25 = [i for i in missing_ids if i in last_25]
    candidates = [i for i in missing_ids if i not in last_25]

    # Target: 5% of all taskers have no image = ~217
    target_no_image = round(TOTAL_TASKERS * TARGET_NO_IMAGE_PCT)
    # 25 are the last-25 (forced no-image)
    # Additional random no-image from candidates
    additional_no_image = max(0, target_no_image - 25)

    # Randomly select which candidates stay without images
    rng = random.Random(12345)
    rng.shuffle(candidates)
    stay_no_image = set(candidates[:additional_no_image])
    to_generate = [i for i in candidates if i not in stay_no_image]
    to_generate.sort(reverse=True)  # Highest IDs first

    return to_generate, in_last_25, list(stay_no_image)


def s3_image_exists(s3_client, tasker_id):
    """Check if a profile image already exists in S3."""
    key = "%s/%d_profile_image.jpg" % (S3_PREFIX, tasker_id)
    try:
        s3_client.head_object(Bucket=S3_BUCKET, Key=key)
        return True
    except Exception:
        return False


async def process_batch(batch, client, s3_client, semaphore):
    async def process_one(tasker):
        async with semaphore:
            tid = tasker["id"]

            if s3_image_exists(s3_client, tid):
                print("  [%d] SKIP (already exists)" % tid)
                return

            style = assign_backfill_style(tid)
            prompt = build_prompt(tasker, style)

            print("  [%d] %s %s (%s, %s) — %s..." % (
                tid, tasker["first_name"], tasker["last_name"],
                tasker["external_job_title"] or "?",
                tasker["location_country"], style))
            image_bytes = await generate_image(client, prompt, tid)

            if image_bytes is None:
                print("  [%d] FAILED" % tid)
                return

            s3_path = upload_to_s3(s3_client, image_bytes, tid)
            print("  [%d] OK → %s" % (tid, s3_path))

    await asyncio.gather(*[process_one(t) for t in batch])


async def main():
    parser = argparse.ArgumentParser(description="Backfill missing profile images")
    parser.add_argument("--dry-run", action="store_true", help="Preview without generating")
    args = parser.parse_args()

    if not args.dry_run and not FAL_KEY:
        print("ERROR: Set FAL_KEY environment variable")
        sys.exit(1)

    # Read missing IDs
    print("Reading missing IDs from %s..." % MISSING_IDS_FILE)
    missing_ids = [int(line.strip()) for line in open(MISSING_IDS_FILE) if line.strip()]
    print("Found %d missing IDs" % len(missing_ids))

    # Compute which ones to generate
    to_generate, skipped_last25, skipped_random = compute_backfill_ids(missing_ids)

    print("\n=== Backfill Plan ===")
    print("Total missing:           %d" % len(missing_ids))
    print("Skipping (last 25):      %d %s" % (len(skipped_last25), skipped_last25))
    print("Skipping (random 5%%):    %d" % len(skipped_random))
    print("Will generate:           %d images" % len(to_generate))
    print("Est. cost (FLUX 2 Klein $0.015): $%.2f" % (len(to_generate) * 0.015))
    print()

    # Style distribution for backfill
    style_counts = {}  # type: Dict[str, int]
    for tid in to_generate:
        s = assign_backfill_style(tid)
        style_counts[s] = style_counts.get(s, 0) + 1

    print("Style distribution:")
    for style, count in sorted(style_counts.items(), key=lambda x: -x[1]):
        pct = count / len(to_generate) * 100
        print("  %-25s %5d (%.1f%%)" % (style, count, pct))
    print()

    if args.dry_run:
        print("--- DRY RUN --- (first 20 IDs to generate: %s)" % to_generate[:20])
        return

    # Fetch tasker data for the IDs we need
    print("Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    id_list = ",".join(str(i) for i in to_generate)
    query = """SELECT id, first_name, last_name, location_country, city,
                      external_job_title, status, gender, age,
                      date_of_birth, is_student, employment_status,
                      highest_education_level, company
               FROM taskers WHERE id IN (%s) ORDER BY id DESC""" % id_list
    cur.execute(query)
    taskers = cur.fetchall()
    cur.close()
    conn.close()

    print("Fetched %d taskers from DB\n" % len(taskers))

    s3_client = boto3.client("s3", region_name=S3_REGION)
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async with httpx.AsyncClient() as client:
        batch_size = 20
        total = len(taskers)
        start_time = time.time()
        generated = 0

        for i in range(0, total, batch_size):
            batch = taskers[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size
            elapsed = time.time() - start_time

            print("=== Batch %d/%d (IDs %d-%d) [%ds elapsed, %d generated] ===" % (
                batch_num, total_batches,
                batch[0]["id"], batch[-1]["id"],
                int(elapsed), generated))

            await process_batch(batch, client, s3_client, semaphore)
            generated += len(batch)
            print()

    elapsed = time.time() - start_time
    print("=" * 50)
    print("Backfill done in %ds — %d images generated" % (int(elapsed), generated))
    print("Images at: s3://%s/%s/" % (S3_BUCKET, S3_PREFIX))
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
