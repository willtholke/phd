"""
Generate external ID pairings for Meta (SRT) and OpenAI (Feather) taskers.
Outputs CSV files to output/ directory.
"""

import os
import hashlib
import csv
from config import RANDOM_SEED


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def _generate_hash(seed_str: str, length: int = 8) -> str:
    """Deterministic hash from a seed string."""
    h = hashlib.sha256(seed_str.encode()).hexdigest()
    # Use alphanumeric chars for readability
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = []
    for i in range(length):
        idx = int(h[i * 2:i * 2 + 2], 16) % len(chars)
        result.append(chars[idx])
    return "".join(result)


def generate_mappings(assignments, projects):
    """
    For every tasker assigned to a Meta project → srt_meta_<hash> ID
    For every tasker assigned to an OpenAI project → usr_<hash> ID

    Returns:
        meta_mappings: dict of tasker_id → meta_external_id
        feather_mappings: dict of tasker_id → feather_external_id
    """
    meta_mappings = {}     # tasker_id → srt_meta_<hash>
    feather_mappings = {}  # tasker_id → usr_<hash>

    # Build project_id → customer_id lookup
    project_customer = {p["id"]: p["customer_id"] for p in projects}

    for assignment in assignments:
        proj_id = assignment["project_id"]
        tasker_id = assignment["tasker_id"]
        customer_id = project_customer.get(proj_id)

        if customer_id == 1 and tasker_id not in meta_mappings:
            # Meta → SRT Tool
            seed = f"meta_{RANDOM_SEED}_{tasker_id}"
            meta_mappings[tasker_id] = f"srt_meta_{_generate_hash(seed)}"

        elif customer_id == 2 and tasker_id not in feather_mappings:
            # OpenAI → Feather
            seed = f"feather_{RANDOM_SEED}_{tasker_id}"
            feather_mappings[tasker_id] = f"usr_{_generate_hash(seed)}"

    return meta_mappings, feather_mappings


def write_csvs(meta_mappings, feather_mappings):
    """Write mapping CSVs to output directory."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    meta_path = os.path.join(OUTPUT_DIR, "meta_id_pairing.csv")
    with open(meta_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["peregrine_tasker_id", "meta_external_id"])
        for tasker_id in sorted(meta_mappings.keys()):
            writer.writerow([tasker_id, meta_mappings[tasker_id]])

    feather_path = os.path.join(OUTPUT_DIR, "feather_id_pairing.csv")
    with open(feather_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["peregrine_tasker_id", "feather_external_id"])
        for tasker_id in sorted(feather_mappings.keys()):
            writer.writerow([tasker_id, feather_mappings[tasker_id]])

    print(f"\n--- ID Mappings Summary ---")
    print(f"Meta (SRT) mappings:    {len(meta_mappings)} taskers → {meta_path}")
    print(f"Feather (OpenAI) mappings: {len(feather_mappings)} taskers → {feather_path}")

    return meta_path, feather_path


def run(assignments, projects):
    """Main entry point."""
    print("Generating ID mappings...")
    meta_mappings, feather_mappings = generate_mappings(assignments, projects)
    write_csvs(meta_mappings, feather_mappings)
    return meta_mappings, feather_mappings


if __name__ == "__main__":
    print("This module should be run via run_all.py")
