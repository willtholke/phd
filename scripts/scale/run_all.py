#!/usr/bin/env python3
"""
Master orchestrator for PHD ecosystem data scaling.
Generates realistic $350M ARR data across 4 databases.

Usage:
    python3 run_all.py --scale 1.0    # Full scale (~15M records, 30-60 min)
    python3 run_all.py --scale 0.1    # 10% scale (~1.5M records, ~5 min)
    python3 run_all.py --scale 0.01   # 1% scale (~150K records, ~1 min)
"""

import sys
import os
import argparse
import time

# Add script directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config


def format_duration(seconds):
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f}m"
    hours = minutes / 60
    return f"{hours:.1f}h"


def main():
    parser = argparse.ArgumentParser(description="Generate scaled PHD ecosystem data")
    parser.add_argument("--scale", type=float, default=1.0,
                       help="Scale factor 0.0-1.0 (default: 1.0 = full $350M)")
    parser.add_argument("--skip-phd", action="store_true",
                       help="Skip PHD database generation")
    parser.add_argument("--skip-srt", action="store_true",
                       help="Skip SRT Tool generation")
    parser.add_argument("--skip-feather", action="store_true",
                       help="Skip Feather generation")
    parser.add_argument("--skip-fairtable", action="store_true",
                       help="Skip Fairtable generation")
    parser.add_argument("--phd-only", action="store_true",
                       help="Only run PHD database generation")
    args = parser.parse_args()

    scale = args.scale
    config.SCALE_FACTOR = scale

    print("=" * 60)
    print(f"PHD Ecosystem Data Generator")
    print(f"Scale: {scale:.0%} of $350M ARR target")
    print(f"Expected: ~{int(15_500_000 * scale):,} total records")
    print("=" * 60)

    # Validate PHD connection
    if not config.PHD_DATABASE_URL:
        print("\nERROR: PHD_DATABASE_URL environment variable not set!")
        print("Set it with: export PHD_DATABASE_URL='postgresql://...'")
        sys.exit(1)

    total_start = time.time()
    results = {}

    # ---------------------------------------------------------------
    # Step 1: PHD Database (contracts, projects, assignments)
    # ---------------------------------------------------------------
    if not args.skip_phd:
        print("\n" + "=" * 60)
        print("STEP 1: PHD Database (contracts, projects, assignments)")
        print("=" * 60)
        step_start = time.time()

        import phd_generator
        phd_data = phd_generator.run(scale_factor=scale)

        elapsed = time.time() - step_start
        results["phd"] = {
            "contracts": len(phd_data["contracts"]),
            "projects": len(phd_data["projects"]),
            "assignments": len(phd_data["assignments"]),
            "elapsed": elapsed,
        }
        print(f"\nStep 1 complete in {format_duration(elapsed)}")
    else:
        # Need to fetch existing data for downstream generators
        print("\nSkipping PHD generation, fetching existing data...")
        import phd_generator
        conn = config.get_connection(config.PHD_DATABASE_URL)

        # Fetch contracts
        cur = conn.cursor()
        cur.execute("SELECT id, customer_id, billing_cycle_id, contract_name, start_date, end_date, take_rate, contract_budget, status FROM contracts ORDER BY id")
        rows = cur.fetchall()
        phd_data = {"contracts": [], "projects": [], "assignments": [], "taskers": []}
        for r in rows:
            phd_data["contracts"].append({
                "id": r[0], "customer_id": r[1], "billing_cycle_id": r[2],
                "contract_name": r[3], "start_date": r[4].isoformat() if r[4] else None,
                "end_date": r[5].isoformat() if r[5] else None,
                "take_rate": r[6], "contract_budget": str(r[7]), "status": r[8],
            })

        # Fetch projects
        cur.execute("SELECT id, customer_id, contract_id, spl_id, external_name, internal_name, start_date, end_date, budget, billing_rate, subdomain_ids, status, external_project_id FROM projects ORDER BY id")
        rows = cur.fetchall()
        for r in rows:
            phd_data["projects"].append({
                "id": r[0], "customer_id": r[1], "contract_id": r[2], "spl_id": r[3],
                "external_name": r[4], "internal_name": r[5],
                "start_date": r[6].isoformat() if r[6] else None,
                "end_date": r[7].isoformat() if r[7] else None,
                "budget": str(r[8]), "billing_rate": str(r[9]),
                "subdomain_ids": r[10] if r[10] else [], "status": r[11],
                "external_project_id": r[12],
            })

        # Fetch assignments
        cur.execute("SELECT id, tasker_id, project_id, assigned_date, removed_date, status, removal_reason, roles FROM assignments ORDER BY id")
        rows = cur.fetchall()
        for r in rows:
            phd_data["assignments"].append({
                "id": r[0], "tasker_id": r[1], "project_id": r[2],
                "assigned_date": r[3].isoformat() if r[3] else None,
                "removed_date": r[4].isoformat() if r[4] else None,
                "status": r[5], "removal_reason": r[6],
                "roles": r[7] if r[7] else ["tasker"],
            })

        # Fetch taskers
        phd_data["taskers"] = phd_generator._fetch_taskers(conn)
        cur.close()
        conn.close()

    if args.phd_only:
        print("\n--phd-only flag set, skipping API generators.")
        _print_summary(results, total_start)
        return

    # ---------------------------------------------------------------
    # Step 2: ID Mappings
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("STEP 2: ID Mappings (Meta + OpenAI external IDs)")
    print("=" * 60)
    step_start = time.time()

    import id_mappings_generator
    meta_mappings, feather_mappings = id_mappings_generator.run(
        phd_data["assignments"], phd_data["projects"]
    )

    elapsed = time.time() - step_start
    results["mappings"] = {
        "meta": len(meta_mappings),
        "feather": len(feather_mappings),
        "elapsed": elapsed,
    }
    print(f"\nStep 2 complete in {format_duration(elapsed)}")

    # ---------------------------------------------------------------
    # Step 3: SRT Tool (Meta)
    # ---------------------------------------------------------------
    if not args.skip_srt:
        print("\n" + "=" * 60)
        print("STEP 3: SRT Tool API (Meta annotations/completions/reviews)")
        print("=" * 60)
        step_start = time.time()

        import srt_generator
        srt_counts = srt_generator.run(
            phd_data["projects"], phd_data["assignments"],
            meta_mappings, scale_factor=scale
        )

        elapsed = time.time() - step_start
        results["srt"] = {
            "annotations": srt_counts[0],
            "completions": srt_counts[1],
            "reviews": srt_counts[2],
            "elapsed": elapsed,
        }
        print(f"\nStep 3 complete in {format_duration(elapsed)}")

    # ---------------------------------------------------------------
    # Step 4: Feather (OpenAI)
    # ---------------------------------------------------------------
    if not args.skip_feather:
        print("\n" + "=" * 60)
        print("STEP 4: Feather API (OpenAI tasks/submissions/reviews)")
        print("=" * 60)
        step_start = time.time()

        import feather_generator
        feather_counts = feather_generator.run(
            phd_data["projects"], phd_data["assignments"],
            feather_mappings, scale_factor=scale
        )

        elapsed = time.time() - step_start
        results["feather"] = {
            "tasks": feather_counts[0],
            "submissions": feather_counts[1],
            "reviews": feather_counts[2],
            "elapsed": elapsed,
        }
        print(f"\nStep 4 complete in {format_duration(elapsed)}")

    # ---------------------------------------------------------------
    # Step 5: Fairtable (Google/xAI/Anthropic)
    # ---------------------------------------------------------------
    if not args.skip_fairtable:
        print("\n" + "=" * 60)
        print("STEP 5: Fairtable API (Google/xAI/Anthropic tasks/submissions/reviews)")
        print("=" * 60)
        step_start = time.time()

        import fairtable_generator
        fairtable_counts = fairtable_generator.run(
            phd_data["projects"], phd_data["assignments"],
            phd_data["taskers"], scale_factor=scale
        )

        elapsed = time.time() - step_start
        results["fairtable"] = {
            "tasks": fairtable_counts[0],
            "submissions": fairtable_counts[1],
            "reviews": fairtable_counts[2],
            "elapsed": elapsed,
        }
        print(f"\nStep 5 complete in {format_duration(elapsed)}")

    _print_summary(results, total_start)


def _print_summary(results, total_start):
    total_elapsed = time.time() - total_start

    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    total_records = 0

    if "phd" in results:
        r = results["phd"]
        count = r["contracts"] + r["projects"] + r["assignments"]
        total_records += count
        print(f"\nPHD Database ({format_duration(r['elapsed'])}):")
        print(f"  Contracts:   {r['contracts']:>10,}")
        print(f"  Projects:    {r['projects']:>10,}")
        print(f"  Assignments: {r['assignments']:>10,}")
        print(f"  Subtotal:    {count:>10,}")

    if "mappings" in results:
        r = results["mappings"]
        print(f"\nID Mappings ({format_duration(r['elapsed'])}):")
        print(f"  Meta (SRT):    {r['meta']:>10,}")
        print(f"  Feather (OAI): {r['feather']:>10,}")

    if "srt" in results:
        r = results["srt"]
        count = r["annotations"] + r["completions"] + r["reviews"]
        total_records += count
        print(f"\nSRT Tool - Meta ({format_duration(r['elapsed'])}):")
        print(f"  Annotations: {r['annotations']:>10,}")
        print(f"  Completions: {r['completions']:>10,}")
        print(f"  Reviews:     {r['reviews']:>10,}")
        print(f"  Subtotal:    {count:>10,}")

    if "feather" in results:
        r = results["feather"]
        count = r["tasks"] + r["submissions"] + r["reviews"]
        total_records += count
        print(f"\nFeather - OpenAI ({format_duration(r['elapsed'])}):")
        print(f"  Tasks:       {r['tasks']:>10,}")
        print(f"  Submissions: {r['submissions']:>10,}")
        print(f"  Reviews:     {r['reviews']:>10,}")
        print(f"  Subtotal:    {count:>10,}")

    if "fairtable" in results:
        r = results["fairtable"]
        count = r["tasks"] + r["submissions"] + r["reviews"]
        total_records += count
        print(f"\nFairtable - Google/xAI/Anthropic ({format_duration(r['elapsed'])}):")
        print(f"  Tasks:       {r['tasks']:>10,}")
        print(f"  Submissions: {r['submissions']:>10,}")
        print(f"  Reviews:     {r['reviews']:>10,}")
        print(f"  Subtotal:    {count:>10,}")

    print(f"\n{'─' * 40}")
    print(f"Total records: {total_records:>10,}")
    print(f"Total time:    {format_duration(total_elapsed)}")
    print(f"{'─' * 40}")


if __name__ == "__main__":
    main()
