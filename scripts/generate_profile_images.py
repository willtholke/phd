#!/usr/bin/env python3
"""
Generate AI profile images for taskers using FLUX 2 Dev on fal.ai.

Pulls all tasker data (name, country, city, job title, etc.) and builds
realistic prompts based on the full profile. ~30% of taskers get no image.

Usage:
    python scripts/generate_profile_images.py --dry-run          # preview
    python scripts/generate_profile_images.py --limit 15         # test batch
    python scripts/generate_profile_images.py                    # all taskers
    python scripts/generate_profile_images.py --resume-from 500  # resume

Required env vars:
    FAL_KEY     — fal.ai API key
"""

import os
import sys
import random
import asyncio
import argparse
import time
from typing import Optional, Dict

import psycopg2
import psycopg2.extras
import httpx
import boto3

# ─── Configuration ────────────────────────────────────────────────────────────

random.seed(42)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_H6ces9NyVEtw@ep-broad-haze-aifq29n7.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)
FAL_KEY = os.environ.get("FAL_KEY", "")
S3_BUCKET = os.environ.get("S3_BUCKET", "peregrine-human-data")
S3_PREFIX = "profile-images"
S3_REGION = "us-east-1"

MAX_CONCURRENCY = 3

# ─── Photo style distribution ────────────────────────────────────────────────

PHOTO_STYLES = {
    "no_image": 0.30,
    "iphone_selfie": 0.20,
    "friend_took_this": 0.15,
    "cozy_indoor": 0.10,
    "outside_casual": 0.08,
    "cropped_group_photo": 0.05,
    "with_friends": 0.04,
    "professional_headshot": 0.08,
}

# ─── Country → ethnicity/appearance mapping ──────────────────────────────────

COUNTRY_ETHNICITY = {
    "United States": "American",
    "India": "South Asian Indian",
    "China": "East Asian Chinese",
    "Russia": "Eastern European Russian",
    "United Kingdom": "British",
    "Germany": "German European",
    "Canada": "Canadian",
    "Mexico": "Mexican Latino",
    "France": "French European",
    "Poland": "Polish European",
    "Brazil": "Brazilian",
    "United Arab Emirates": "Middle Eastern Arab",
    "Spain": "Spanish European",
    "Pakistan": "South Asian Pakistani",
    "Japan": "East Asian Japanese",
    "Colombia": "Colombian Latino",
    "Italy": "Italian European",
    "South Africa": "South African",
    "Australia": "Australian",
    "Argentina": "Argentine",
    "South Korea": "East Asian Korean",
    "Nigeria": "West African Nigerian",
    "Philippines": "Southeast Asian Filipino",
    "Turkey": "Turkish",
    "Israel": "Israeli",
    "Egypt": "Egyptian North African",
    "Kenya": "East African Kenyan",
    "Netherlands": "Dutch European",
    "Sweden": "Swedish Scandinavian",
    "Switzerland": "Swiss European",
    "Indonesia": "Southeast Asian Indonesian",
    "Thailand": "Southeast Asian Thai",
    "Vietnam": "Southeast Asian Vietnamese",
    "Taiwan": "East Asian Taiwanese",
    "Singapore": "Singaporean",
    "Chile": "Chilean",
    "Peru": "Peruvian",
    "Austria": "Austrian European",
}


# ─── Name → ethnicity inference ───────────────────────────────────────────────
# Based on the name pools in generate_taskers.py

LAST_NAME_ETHNICITY = {
    # East Asian — Chinese
    "Wang": "East Asian Chinese", "Li": "East Asian Chinese", "Zhang": "East Asian Chinese",
    "Liu": "East Asian Chinese", "Chen": "East Asian Chinese", "Yang": "East Asian Chinese",
    "Huang": "East Asian Chinese", "Zhao": "East Asian Chinese", "Wu": "East Asian Chinese",
    "Zhou": "East Asian Chinese", "Xu": "East Asian Chinese", "Sun": "East Asian Chinese",
    "Ma": "East Asian Chinese", "Zhu": "East Asian Chinese", "Guo": "East Asian Chinese",
    "Lin": "East Asian Chinese", "He": "East Asian Chinese", "Luo": "East Asian Chinese",
    "Tang": "East Asian Chinese", "Xie": "East Asian Chinese",
    # East Asian — Japanese
    "Tanaka": "East Asian Japanese", "Suzuki": "East Asian Japanese",
    "Watanabe": "East Asian Japanese", "Takahashi": "East Asian Japanese",
    "Ito": "East Asian Japanese", "Yamamoto": "East Asian Japanese",
    "Nakamura": "East Asian Japanese", "Kobayashi": "East Asian Japanese",
    "Saito": "East Asian Japanese", "Kato": "East Asian Japanese",
    "Yoshida": "East Asian Japanese", "Yamada": "East Asian Japanese",
    "Sasaki": "East Asian Japanese", "Kimura": "East Asian Japanese",
    # East Asian — Korean
    "Kim": "East Asian Korean", "Park": "East Asian Korean", "Choi": "East Asian Korean",
    "Jung": "East Asian Korean", "Kang": "East Asian Korean", "Yoon": "East Asian Korean",
    "Jang": "East Asian Korean", "Lim": "East Asian Korean", "Han": "East Asian Korean",
    "Shin": "East Asian Korean",
    # South Asian
    "Patel": "South Asian Indian", "Sharma": "South Asian Indian",
    "Singh": "South Asian Indian", "Kumar": "South Asian Indian",
    "Gupta": "South Asian Indian", "Mehta": "South Asian Indian",
    "Shah": "South Asian Indian", "Joshi": "South Asian Indian",
    "Reddy": "South Asian Indian", "Nair": "South Asian Indian",
    "Rao": "South Asian Indian", "Das": "South Asian Indian",
    "Mishra": "South Asian Indian", "Agarwal": "South Asian Indian",
    "Bhat": "South Asian Indian", "Pillai": "South Asian Indian",
    "Chandra": "South Asian Indian", "Iyer": "South Asian Indian",
    "Menon": "South Asian Indian", "Verma": "South Asian Indian",
    "Kapoor": "South Asian Indian", "Malhotra": "South Asian Indian",
    "Chopra": "South Asian Indian", "Banerjee": "South Asian Indian",
    # African
    "Okafor": "West African Nigerian", "Adeyemi": "West African Nigerian",
    "Ogundimu": "West African Nigerian", "Nwosu": "West African Nigerian",
    "Diallo": "West African", "Traore": "West African",
    "Mensah": "West African Ghanaian", "Asante": "West African Ghanaian",
    "Boateng": "West African Ghanaian", "Owusu": "West African Ghanaian",
    "Abubakar": "West African Nigerian", "Toure": "West African",
    "Bello": "West African Nigerian",
    # German
    "Schmidt": "German European", "Schneider": "German European",
    "Fischer": "German European", "Weber": "German European",
    "Meyer": "German European", "Wagner": "German European",
    "Becker": "German European", "Schulz": "German European",
    "Hoffman": "German European", "Koch": "German European",
    "Richter": "German European", "Wolf": "German European",
    "Braun": "German European", "Zimmermann": "German European",
    # French
    "Dubois": "French European", "Laurent": "French European",
    "Moreau": "French European", "Bernard": "French European",
    "Leroy": "French European", "Roux": "French European",
    "Girard": "French European",
    # Italian
    "Rossi": "Italian European", "Russo": "Italian European",
    "Ferrari": "Italian European", "Esposito": "Italian European",
    "Bianchi": "Italian European", "Romano": "Italian European",
    "Colombo": "Italian European",
    # Polish
    "Kowalski": "Polish European", "Nowak": "Polish European",
    "Wisniewski": "Polish European", "Wojciech": "Polish European",
    "Kaminski": "Polish European", "Lewandowski": "Polish European",
    # Russian
    "Petrov": "Eastern European Russian", "Ivanov": "Eastern European Russian",
    "Volkov": "Eastern European Russian", "Sokolov": "Eastern European Russian",
    "Popov": "Eastern European Russian",
    # Scandinavian
    "Johansson": "Swedish Scandinavian", "Lindberg": "Swedish Scandinavian",
    "Eriksson": "Swedish Scandinavian", "Nilsson": "Swedish Scandinavian",
    "Larsson": "Swedish Scandinavian", "Bergman": "Swedish Scandinavian",
    "Lindqvist": "Swedish Scandinavian",
    # Middle Eastern
    "Al-Rashid": "Middle Eastern Arab", "Al-Farsi": "Middle Eastern Arab",
    "Al-Sayed": "Middle Eastern Arab", "Khoury": "Middle Eastern Arab",
    "Haddad": "Middle Eastern Arab", "Mansour": "Middle Eastern Arab",
    "Nasser": "Middle Eastern Arab", "Ibrahim": "Middle Eastern Arab",
    # Latin American
    "Garcia": "Latino", "Fernandez": "Latino", "Mendez": "Latino",
    "Reyes": "Latino", "Flores": "Latino", "Morales": "Latino",
    "Ortiz": "Latino", "Gutierrez": "Latino", "Rojas": "Latino",
    "Vargas": "Latino", "Castillo": "Latino", "Jimenez": "Latino",
    "Herrera": "Latino", "Medina": "Latino", "Aguilar": "Latino",
    "Rodriguez": "Latino", "Martinez": "Latino", "Hernandez": "Latino",
    "Lopez": "Latino", "Gonzalez": "Latino", "Sanchez": "Latino",
    "Ramirez": "Latino", "Torres": "Latino", "Gomez": "Latino",
    "Diaz": "Latino", "Rivera": "Latino", "Perez": "Latino",
    # Brazilian
    "Silva": "Brazilian", "Santos": "Brazilian", "Oliveira": "Brazilian",
    "Souza": "Brazilian", "Costa": "Brazilian", "Ferreira": "Brazilian",
    "Almeida": "Brazilian", "Pereira": "Brazilian", "Carvalho": "Brazilian",
    "Ribeiro": "Brazilian", "Araujo": "Brazilian",
}

FIRST_NAME_ETHNICITY = {
    # East Asian Chinese
    "Wei": "East Asian Chinese", "Jun": "East Asian Chinese", "Hao": "East Asian Chinese",
    "Ming": "East Asian Chinese", "Tao": "East Asian Chinese", "Kai": "East Asian Chinese",
    "Yong": "East Asian Chinese", "Jian": "East Asian Chinese", "Liang": "East Asian Chinese",
    "Mei": "East Asian Chinese", "Xiu": "East Asian Chinese", "Lan": "East Asian Chinese",
    "Hua": "East Asian Chinese", "Jing": "East Asian Chinese", "Yue": "East Asian Chinese",
    "Ling": "East Asian Chinese", "Na": "East Asian Chinese", "Fang": "East Asian Chinese",
    # Japanese
    "Hiroshi": "East Asian Japanese", "Takeshi": "East Asian Japanese",
    "Kenji": "East Asian Japanese", "Yuto": "East Asian Japanese",
    "Haruto": "East Asian Japanese", "Ren": "East Asian Japanese",
    "Sota": "East Asian Japanese", "Kaito": "East Asian Japanese",
    "Yuki": "East Asian Japanese", "Sakura": "East Asian Japanese",
    "Aiko": "East Asian Japanese", "Hana": "East Asian Japanese",
    "Mio": "East Asian Japanese", "Rin": "East Asian Japanese",
    "Saki": "East Asian Japanese", "Yumi": "East Asian Japanese",
    "Yoko": "East Asian Japanese", "Keiko": "East Asian Japanese",
    # Korean
    "Sang-Hoon": "East Asian Korean", "Min-Jun": "East Asian Korean",
    "Ji-Hoon": "East Asian Korean", "Hyun-Woo": "East Asian Korean",
    "Seo-Jun": "East Asian Korean", "Do-Yun": "East Asian Korean",
    "Soo-Jin": "East Asian Korean", "Min-Ji": "East Asian Korean",
    "Hye-Jin": "East Asian Korean", "Ji-Yeon": "East Asian Korean",
    "Eun-Ji": "East Asian Korean",
    # South Asian
    "Rajesh": "South Asian Indian", "Vikram": "South Asian Indian",
    "Amit": "South Asian Indian", "Arun": "South Asian Indian",
    "Sanjay": "South Asian Indian", "Deepak": "South Asian Indian",
    "Ravi": "South Asian Indian", "Suresh": "South Asian Indian",
    "Nikhil": "South Asian Indian", "Arjun": "South Asian Indian",
    "Rohan": "South Asian Indian", "Karthik": "South Asian Indian",
    "Pranav": "South Asian Indian", "Varun": "South Asian Indian",
    "Ashwin": "South Asian Indian", "Rahul": "South Asian Indian",
    "Sachin": "South Asian Indian", "Vishal": "South Asian Indian",
    "Priya": "South Asian Indian", "Ananya": "South Asian Indian",
    "Kavita": "South Asian Indian", "Sunita": "South Asian Indian",
    "Deepa": "South Asian Indian", "Neha": "South Asian Indian",
    "Pooja": "South Asian Indian", "Shreya": "South Asian Indian",
    "Divya": "South Asian Indian", "Meera": "South Asian Indian",
    "Anjali": "South Asian Indian", "Nandini": "South Asian Indian",
    "Swati": "South Asian Indian",
    # African
    "Kwame": "West African Ghanaian", "Chukwu": "West African Nigerian",
    "Olumide": "West African Nigerian", "Babajide": "West African Nigerian",
    "Adewale": "West African Nigerian", "Emeka": "West African Nigerian",
    "Obinna": "West African Nigerian", "Chinonso": "West African Nigerian",
    "Ngozi": "West African Nigerian", "Chidinma": "West African Nigerian",
    "Adaeze": "West African Nigerian", "Folake": "West African Nigerian",
    "Amina": "East African", "Fatima": "Middle Eastern Arab",
    "Aisha": "East African",
    # Middle Eastern
    "Ahmad": "Middle Eastern Arab", "Khalid": "Middle Eastern Arab",
    "Tariq": "Middle Eastern Arab", "Faisal": "Middle Eastern Arab",
    "Samir": "Middle Eastern Arab", "Nabil": "Middle Eastern Arab",
    "Rashid": "Middle Eastern Arab", "Zaid": "Middle Eastern Arab",
    "Layla": "Middle Eastern Arab", "Nour": "Middle Eastern Arab",
    "Dalia": "Middle Eastern Arab", "Rania": "Middle Eastern Arab",
    "Yasmin": "Middle Eastern Arab", "Salma": "Middle Eastern Arab",
    # Russian/Eastern European
    "Dmitri": "Eastern European Russian", "Alexei": "Eastern European Russian",
    "Sergei": "Eastern European Russian", "Nikolai": "Eastern European Russian",
    "Ivan": "Eastern European Russian",
    "Olga": "Eastern European Russian", "Natasha": "Eastern European Russian",
    "Svetlana": "Eastern European Russian", "Tatiana": "Eastern European Russian",
    "Irina": "Eastern European Russian",
    # Latino
    "Carlos": "Latino", "Miguel": "Latino", "Luis": "Latino",
    "Jorge": "Latino", "Pedro": "Latino", "Rafael": "Latino",
    "Diego": "Latino", "Alejandro": "Latino",
    "Maria": "Latino", "Carmen": "Latino", "Lucia": "Latino",
    "Sofia": "Latino", "Valentina": "Latino", "Isabella": "Latino",
    "Gabriela": "Latino", "Camila": "Latino",
}


def infer_ethnicity(first_name, last_name, country):
    """Infer ethnicity from name first, then fall back to country."""
    # Last name is most reliable
    if last_name in LAST_NAME_ETHNICITY:
        return LAST_NAME_ETHNICITY[last_name]
    # First name as backup
    if first_name in FIRST_NAME_ETHNICITY:
        return FIRST_NAME_ETHNICITY[first_name]
    # Fall back to country — but make ambiguous countries more specific
    return COUNTRY_ETHNICITY.get(country, "")


def assign_style(tasker_id, force=False):
    rng = random.Random(42 + tasker_id)
    styles = list(PHOTO_STYLES.keys())
    weights = list(PHOTO_STYLES.values())
    style = rng.choices(styles, weights=weights, k=1)[0]
    if force and style == "no_image":
        real_styles = {k: v for k, v in PHOTO_STYLES.items() if k != "no_image"}
        total = sum(real_styles.values())
        real_styles = {k: v / total for k, v in real_styles.items()}
        style = rng.choices(list(real_styles.keys()), weights=list(real_styles.values()), k=1)[0]
    return style


def build_prompt(tasker, style):
    # type: (Dict, str) -> str
    """Build a FLUX prompt using the full tasker row. Casual iPhone-era vibes."""
    country = tasker["location_country"]
    city = tasker["city"] or ""
    age = tasker["age"] or 30
    gender = "woman" if tasker["gender"] == "Female" else "man"
    is_student = tasker["is_student"]
    ethnicity = infer_ethnicity(tasker["first_name"], tasker["last_name"], country)

    person = "%d-year-old %s %s" % (age, ethnicity, gender)
    rng = random.Random(hash(tasker["first_name"] + country))

    # Student-age taskers get campus/dorm vibes mixed in
    student_settings = [
        "in a college dorm room",
        "at a university library",
        "on a campus quad",
        "at a college house party",
    ]

    if style == "iphone_selfie":
        settings = [
            "in their bathroom mirror",
            "in their car",
            "on their couch at home",
            "in their kitchen",
            "at a coffee shop",
            "at a restaurant",
            "in an elevator",
        ]
        if is_student:
            settings.extend(student_settings)
        setting = rng.choice(settings)
        prompt = (
            "Casual iPhone selfie of a %s, %s, "
            "slightly messy hair, natural expression, no makeup or minimal makeup, "
            "iPhone front camera quality, slightly warm lighting, "
            "not perfectly framed, real authentic social media selfie, photorealistic"
        ) % (person, setting)

    elif style == "friend_took_this":
        settings = [
            "at a bar with warm ambient lighting",
            "at a restaurant table",
            "at a backyard barbecue",
            "at a rooftop party",
            "at a park picnic",
            "sitting on a bench outside",
            "leaning against a wall on a city street",
            "at a birthday party",
        ]
        if is_student:
            settings.extend(["at a college house party", "at a tailgate", "in a dorm common room"])
        setting = rng.choice(settings)
        prompt = (
            "Candid photo of a %s taken by a friend, %s, "
            "natural relaxed smile, casual clothing, "
            "iPhone camera quality, slightly off-center composition, "
            "real life candid moment, not posed, photorealistic"
        ) % (person, setting)

    elif style == "cozy_indoor":
        settings = [
            "on their couch wrapped in a blanket",
            "in their living room with warm lamp light",
            "at their kitchen table with a cup of coffee",
            "sitting in bed with pillows behind them",
            "in a cozy armchair reading",
            "at their desk at home",
        ]
        setting = rng.choice(settings)
        prompt = (
            "Cozy indoor photo of a %s, %s, "
            "wearing comfortable casual clothes like a hoodie or sweater, "
            "warm soft indoor lighting, relaxed vibes, "
            "iPhone photo quality, photorealistic"
        ) % (person, setting)

    elif style == "outside_casual":
        settings = [
            "walking down a sidewalk",
            "at a beach",
            "at a park",
            "on a hiking trail in nature",
            "outside a cafe with a drink in hand",
            "on a city street with buildings behind them",
            "at a farmers market",
        ]
        setting = rng.choice(settings)
        prompt = (
            "Casual outdoor photo of a %s, %s, "
            "wearing everyday casual clothes, natural sunlight, "
            "relaxed genuine smile, slightly squinting from sun, "
            "iPhone photo taken by a friend, photorealistic"
        ) % (person, setting)

    elif style == "cropped_group_photo":
        prompt = (
            "Cropped profile photo of a %s, clearly cropped from a larger group photo, "
            "someone else's arm or shoulder barely visible at the edge, "
            "slightly blurry background of a social gathering, "
            "natural smile, casual clothes, flash photography or indoor lighting, "
            "iPhone quality, photorealistic"
        ) % person

    elif style == "with_friends":
        prompt = (
            "Casual group photo focused on a %s with one or two friends, "
            "arms around each other, at a social outing, "
            "everyone smiling and having fun, casual clothes, "
            "iPhone photo quality, slightly imperfect framing, "
            "real authentic friend group photo, photorealistic"
        ) % person

    elif style == "professional_headshot":
        prompt = (
            "Professional headshot portrait of a %s, "
            "clean neutral background, studio lighting, "
            "sharp focus on face, shallow depth of field, "
            "corporate photography, photorealistic"
        ) % person

    else:
        prompt = (
            "Casual photo of a %s, looking at camera, "
            "iPhone quality, photorealistic"
        ) % person

    return prompt



# ─── fal.ai client (synchronous endpoint) ────────────────────────────────────


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

        # Download the image
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


async def process_batch(batch, client, s3_client, semaphore, dry_run=False, force=False):
    async def process_one(tasker):
        async with semaphore:
            tid = tasker["id"]
            style = assign_style(tid, force=force)

            if style == "no_image":
                print("  [%d] %s %s (%s) — NO IMAGE" % (
                    tid, tasker["first_name"], tasker["last_name"],
                    tasker["external_job_title"] or "?"))
                return

            prompt = build_prompt(tasker, style)

            if dry_run:
                print("  [%d] %s %s | %s | %s, %s | %s" % (
                    tid, tasker["first_name"], tasker["last_name"],
                    tasker["external_job_title"] or "?",
                    tasker["city"] or "?", tasker["location_country"],
                    style))
                print("        %s" % prompt[:140])
                return

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
    parser = argparse.ArgumentParser(description="Generate AI profile images for taskers")
    parser.add_argument("--dry-run", action="store_true", help="Preview without generating")
    parser.add_argument("--resume-from", type=int, default=0, help="Resume from tasker ID")
    parser.add_argument("--limit", type=int, default=0, help="Process N taskers only")
    parser.add_argument("--force-ids", type=str, default="", help="Comma-separated IDs to force-generate (overrides no_image)")
    args = parser.parse_args()

    force_ids = [int(x.strip()) for x in args.force_ids.split(",") if x.strip()] if args.force_ids else []

    if not args.dry_run and not FAL_KEY:
        print("ERROR: Set FAL_KEY environment variable")
        sys.exit(1)

    print("Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = """SELECT id, first_name, last_name, location_country, city,
                      external_job_title, status, gender, age,
                      date_of_birth, is_student, employment_status,
                      highest_education_level, company
               FROM taskers"""
    if force_ids:
        query += " WHERE id IN (%s)" % ",".join(str(i) for i in force_ids)
    elif args.resume_from > 0:
        query += " WHERE id >= %d" % args.resume_from
    query += " ORDER BY id"
    if not force_ids and args.limit > 0:
        query += " LIMIT %d" % args.limit

    cur.execute(query)
    taskers = cur.fetchall()
    cur.close()
    conn.close()

    print("Fetched %d taskers\n" % len(taskers))

    # Style distribution
    forcing = bool(force_ids)
    style_counts = {}
    for t in taskers:
        s = assign_style(t["id"], force=forcing)
        style_counts[s] = style_counts.get(s, 0) + 1

    print("Style distribution:")
    for style, count in sorted(style_counts.items(), key=lambda x: -x[1]):
        pct = count / len(taskers) * 100
        print("  %-25s %5d (%.1f%%)" % (style, count, pct))

    to_generate = len(taskers) - style_counts.get("no_image", 0)
    print("\nWill generate: %d images" % to_generate)
    print("Will skip:     %d (no_image)" % style_counts.get("no_image", 0))
    print("Est. cost:     $%.2f\n" % (to_generate * 0.008))

    if args.dry_run:
        print("--- DRY RUN ---\n")
        for t in taskers[:30]:
            style = assign_style(t["id"], force=forcing)
            prompt = build_prompt(t, style) if style != "no_image" else ""
            if style == "no_image":
                print("  [%d] %s %s | %s — NO IMAGE" % (
                    t["id"], t["first_name"], t["last_name"],
                    t["external_job_title"] or "?"))
            else:
                print("  [%d] %s %s | %s | %s, %s | %s" % (
                    t["id"], t["first_name"], t["last_name"],
                    t["external_job_title"] or "?",
                    t["city"] or "?", t["location_country"], style))
                print("        %s" % prompt[:150])
        print("\nRun without --dry-run to generate images.")
        return

    s3_client = boto3.client("s3", region_name=S3_REGION)
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async with httpx.AsyncClient() as client:
        batch_size = 20
        total = len(taskers)
        start_time = time.time()

        for i in range(0, total, batch_size):
            batch = taskers[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size
            elapsed = time.time() - start_time

            print("=== Batch %d/%d (IDs %d-%d) [%ds elapsed] ===" % (
                batch_num, total_batches,
                batch[0]["id"], batch[-1]["id"],
                int(elapsed)))

            await process_batch(batch, client, s3_client, semaphore, force=forcing)
            print()

    elapsed = time.time() - start_time
    print("=" * 50)
    print("Done in %ds" % int(elapsed))
    print("Images at: s3://%s/%s/" % (S3_BUCKET, S3_PREFIX))
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
