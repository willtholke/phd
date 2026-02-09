"""
SRT Tool API generator: annotations, completions, reviews for Meta projects.
Writes directly to the SRT Neon database.
"""

import random
import math
from datetime import date, timedelta
from tqdm import tqdm

from config import (
    RANDOM_SEED, SCALE_FACTOR, BATCH_SIZE,
    CUSTOMERS, SRT_TASK_TITLES,
    REVIEW_NOTES_POSITIVE, REVIEW_NOTES_NEGATIVE, REVIEW_NOTES_NEUTRAL,
    get_monthly_multiplier, get_active_months, get_connection,
    SRT_DATABASE_URL, generate_hex_id, random_datetime_in_month,
)


def _escape_sql(val):
    if val is None:
        return "NULL"
    s = str(val).replace("'", "''")
    return f"'{s}'"


def _get_meta_projects(projects):
    """Get all projects for Meta (customer_id=1)."""
    return [p for p in projects if p["customer_id"] == 1]


def _get_project_annotators(assignments, project_id, meta_mappings):
    """Get annotator IDs (srt_meta_xxx) for a project."""
    annotators = []
    for a in assignments:
        if a["project_id"] == project_id and a["tasker_id"] in meta_mappings:
            annotators.append({
                "tasker_id": a["tasker_id"],
                "external_id": meta_mappings[a["tasker_id"]],
                "assigned_date": a["assigned_date"],
                "removed_date": a["removed_date"],
                "status": a["status"],
                "roles": a.get("roles", ["tasker"]),
            })
    return annotators


def _is_annotator_active(annotator, year, month):
    """Check if an annotator was active during the given month."""
    assigned = date.fromisoformat(annotator["assigned_date"])
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(year, month + 1, 1) - timedelta(days=1)

    if assigned > month_end:
        return False
    if annotator["removed_date"]:
        removed = date.fromisoformat(annotator["removed_date"])
        if removed < month_start:
            return False
    return True


def generate_srt_data(rng, projects, assignments, meta_mappings, scale_factor):
    """
    Generate annotations, completions, reviews for Meta SRT Tool.

    Target at scale=1.0: ~2M annotations, ~2.5M completions, ~1.6M reviews
    """
    all_annotations = []
    all_completions = []
    all_reviews = []

    meta_projects = _get_meta_projects(projects)
    if not meta_projects:
        print("  No Meta projects found!")
        return [], [], []

    # Annotation types per project (cycle through based on project index)
    ann_types = CUSTOMERS[1]["annotation_types"]

    active_months = get_active_months()
    # Filter to months where Meta is active (from Q3 2023)
    meta_start = CUSTOMERS[1]["start_quarter"]
    active_months = [(y, m) for y, m in active_months if (y, m) >= meta_start]

    # Total target annotations scaled
    total_target = int(2_000_000 * scale_factor)

    # Distribute annotations across months using growth curve
    month_weights = []
    for y, m in active_months:
        w = get_monthly_multiplier(y, m)
        month_weights.append(w)
    total_weight = sum(month_weights) or 1.0

    # Per-month annotation counts
    month_counts = []
    for w in month_weights:
        count = int(total_target * w / total_weight)
        month_counts.append(max(1, count))

    # Adjust to hit target
    diff = total_target - sum(month_counts)
    if diff > 0 and month_counts:
        month_counts[-1] += diff

    ann_counter = 0
    comp_counter = 0
    rev_counter = 0

    for month_idx, (y, m) in enumerate(tqdm(active_months, desc="SRT months")):
        target_this_month = month_counts[month_idx]

        # Distribute across active Meta projects this month
        active_projects = []
        for p in meta_projects:
            p_start = date.fromisoformat(p["start_date"])
            p_end = date.fromisoformat(p["end_date"]) if p["end_date"] else date(2026, 3, 1)
            month_start = date(y, m, 1)
            if p_start <= date(y, m, 28) and p_end >= month_start:
                annotators = _get_project_annotators(assignments, p["id"], meta_mappings)
                active_anns = [a for a in annotators if _is_annotator_active(a, y, m)]
                if active_anns:
                    active_projects.append((p, active_anns))

        if not active_projects:
            continue

        # Split annotations across projects (weighted by annotator count)
        project_weights = [len(anns) for _, anns in active_projects]
        total_pw = sum(project_weights) or 1

        for proj_idx, (project, annotators) in enumerate(active_projects):
            proj_count = max(1, int(target_this_month * project_weights[proj_idx] / total_pw))

            # Determine annotation type for this project
            proj_type_idx = project["id"] % len(ann_types)
            primary_type = ann_types[proj_type_idx]

            # Use deterministic project_id from PHD projects table
            srt_project_id = project.get("external_project_id", f"proj_srt_{generate_hex_id(rng, 8)}")

            # Distribute annotations across annotators (weighted)
            for ann_idx in range(proj_count):
                annotator = rng.choice(annotators)

                # Annotation type: 70% primary, 30% mixed
                if rng.random() < 0.70:
                    ann_type = primary_type
                else:
                    ann_type = rng.choice(ann_types)

                # Status distribution
                status_roll = rng.random()
                if status_roll < 0.05:
                    status = "assigned"
                elif status_roll < 0.13:
                    status = "in_progress"
                elif status_roll < 0.78:
                    status = "completed"
                elif status_roll < 0.93:
                    status = "under_review"
                else:
                    status = "rejected"

                created_at = random_datetime_in_month(rng, y, m)

                # Deadline: 2-14 days after creation, or None
                deadline = None
                if rng.random() < 0.6:
                    deadline_days = rng.randint(2, 14)
                    # Simple deadline calc
                    d = int(created_at[8:10]) + deadline_days
                    if d > 28:
                        d = 28
                    deadline = f"{created_at[:8]}{d:02d}{created_at[10:]}"

                annotation_id = f"ann_srt_{generate_hex_id(rng, 12)}"

                all_annotations.append((
                    annotation_id, srt_project_id, annotator["external_id"],
                    ann_type, status, created_at, deadline
                ))
                ann_counter += 1

                # Generate completions for non-assigned/in-progress annotations
                if status in ("completed", "under_review", "rejected"):
                    # 70%: 1 completion, 20%: 1 + flagged, 10%: 2-3 completions
                    comp_roll = rng.random()
                    if comp_roll < 0.70:
                        num_completions = 1
                    elif comp_roll < 0.90:
                        num_completions = 1
                    else:
                        num_completions = rng.randint(2, 3)

                    for c_idx in range(num_completions):
                        if c_idx == 0:
                            comp_annotator_id = annotator["external_id"]
                        else:
                            # Different annotator for multi-worker
                            other = rng.choice(annotators)
                            comp_annotator_id = other["external_id"]

                        # Duration: 5-60 min, normal around 20
                        duration = max(5.0, min(60.0, rng.gauss(20.0, 8.0)))
                        duration = round(duration, 1)

                        # Completed_at: same day or next day
                        comp_at = created_at  # simplify to same timestamp range

                        # Completion status
                        cs_roll = rng.random()
                        if cs_roll < 0.10:
                            comp_status = "submitted"
                        elif cs_roll < 0.80:
                            comp_status = "accepted"
                        elif cs_roll < 0.92:
                            comp_status = "rejected"
                        else:
                            comp_status = "needs_rework"

                        # Rework count
                        if comp_status == "needs_rework":
                            rework = rng.choices([1, 2, 3], weights=[70, 25, 5])[0]
                        elif rng.random() < 0.15:
                            rework = 1
                        else:
                            rework = 0

                        completion_id = f"comp_srt_{generate_hex_id(rng, 12)}"

                        all_completions.append((
                            completion_id, annotation_id, comp_annotator_id,
                            comp_at, duration, comp_status, rework
                        ))
                        comp_counter += 1

                        # Generate reviews for this completion
                        # 65% get 1, 15% get 2, 5% get 3, 15% get 0
                        rev_roll = rng.random()
                        if rev_roll < 0.15:
                            num_reviews = 0
                        elif rev_roll < 0.80:
                            num_reviews = 1
                        elif rev_roll < 0.95:
                            num_reviews = 2
                        else:
                            num_reviews = 3

                        for r_idx in range(num_reviews):
                            # Reviewer: different annotator (never self-review)
                            reviewer_candidates = [a for a in annotators if a["external_id"] != comp_annotator_id]
                            if not reviewer_candidates:
                                reviewer_candidates = annotators  # fallback
                            reviewer = rng.choice(reviewer_candidates)

                            # Quality score: 1-5, normal around 3.8
                            score = max(1, min(5, round(rng.gauss(3.8, 0.8))))

                            # Quality tier
                            if score == 5:
                                tier = "exceptional"
                            elif score == 4:
                                tier = "meets_expectations"
                            elif score == 3:
                                tier = "below_expectations"
                            else:
                                tier = "unacceptable"

                            # Notes
                            if score >= 4:
                                notes = rng.choice(REVIEW_NOTES_POSITIVE)
                            elif score == 3:
                                notes = rng.choice(REVIEW_NOTES_NEUTRAL)
                            else:
                                notes = rng.choice(REVIEW_NOTES_NEGATIVE)

                            review_id = f"rev_srt_{generate_hex_id(rng, 12)}"

                            all_reviews.append((
                                review_id, completion_id, reviewer["external_id"],
                                score, tier, notes, comp_at
                            ))
                            rev_counter += 1

    return all_annotations, all_completions, all_reviews


def insert_data(conn, annotations, completions, reviews):
    """Truncate and insert all SRT data."""
    cur = conn.cursor()

    print("  Truncating SRT tables...")
    cur.execute("TRUNCATE reviews, completions, annotations CASCADE;")
    conn.commit()

    # Insert annotations
    print(f"  Inserting {len(annotations)} annotations...")
    for i in tqdm(range(0, len(annotations), BATCH_SIZE), desc="  Annotations"):
        batch = annotations[i:i + BATCH_SIZE]
        values = []
        for a in batch:
            deadline = _escape_sql(a[6])
            values.append(
                f"({_escape_sql(a[0])}, {_escape_sql(a[1])}, {_escape_sql(a[2])}, "
                f"{_escape_sql(a[3])}, {_escape_sql(a[4])}, {_escape_sql(a[5])}, {deadline})"
            )
        sql = (
            "INSERT INTO annotations (annotation_id, project_id, annotator_id, "
            "annotation_type, status, created_at, deadline) VALUES\n"
            + ",\n".join(values) + ";"
        )
        cur.execute(sql)
        conn.commit()

    # Insert completions
    print(f"  Inserting {len(completions)} completions...")
    for i in tqdm(range(0, len(completions), BATCH_SIZE), desc="  Completions"):
        batch = completions[i:i + BATCH_SIZE]
        values = []
        for c in batch:
            values.append(
                f"({_escape_sql(c[0])}, {_escape_sql(c[1])}, {_escape_sql(c[2])}, "
                f"{_escape_sql(c[3])}, {c[4]}, {_escape_sql(c[5])}, {c[6]})"
            )
        sql = (
            "INSERT INTO completions (completion_id, annotation_id, annotator_id, "
            "completed_at, duration_minutes, status, rework_count) VALUES\n"
            + ",\n".join(values) + ";"
        )
        cur.execute(sql)
        conn.commit()

    # Insert reviews
    print(f"  Inserting {len(reviews)} reviews...")
    for i in tqdm(range(0, len(reviews), BATCH_SIZE), desc="  Reviews"):
        batch = reviews[i:i + BATCH_SIZE]
        values = []
        for r in batch:
            notes = _escape_sql(r[5])
            values.append(
                f"({_escape_sql(r[0])}, {_escape_sql(r[1])}, {_escape_sql(r[2])}, "
                f"{r[3]}, {_escape_sql(r[4])}, {notes}, {_escape_sql(r[6])})"
            )
        sql = (
            "INSERT INTO reviews (review_id, completion_id, reviewer_id, "
            "quality_score, quality_tier, notes, reviewed_at) VALUES\n"
            + ",\n".join(values) + ";"
        )
        cur.execute(sql)
        conn.commit()

    cur.close()


def run(projects, assignments, meta_mappings, scale_factor=None):
    """Main entry point."""
    sf = scale_factor if scale_factor is not None else SCALE_FACTOR
    rng = random.Random(RANDOM_SEED + 100)

    print("\nGenerating SRT Tool data...")
    annotations, completions, reviews = generate_srt_data(
        rng, projects, assignments, meta_mappings, sf
    )

    print(f"\n--- SRT Data Generated ---")
    print(f"Annotations: {len(annotations):,}")
    print(f"Completions: {len(completions):,}")
    print(f"Reviews:     {len(reviews):,}")

    print("\nConnecting to SRT database...")
    conn = get_connection(SRT_DATABASE_URL)

    insert_data(conn, annotations, completions, reviews)
    conn.close()

    print("SRT data insertion complete.")
    return len(annotations), len(completions), len(reviews)


if __name__ == "__main__":
    print("This module should be run via run_all.py")
