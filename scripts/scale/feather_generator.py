"""
Feather API generator: tasks, submissions, quality_reviews for OpenAI projects.
Writes directly to the Feather Neon database.
"""

import random
from datetime import date, timedelta
from tqdm import tqdm

from config import (
    RANDOM_SEED, SCALE_FACTOR, BATCH_SIZE,
    CUSTOMERS, FEATHER_TASK_TITLES,
    REVIEW_NOTES_POSITIVE, REVIEW_NOTES_NEGATIVE, REVIEW_NOTES_NEUTRAL,
    get_monthly_multiplier, get_active_months, get_connection,
    FEATHER_DATABASE_URL, generate_hex_id, random_datetime_in_month,
)


def _escape_sql(val):
    if val is None:
        return "NULL"
    s = str(val).replace("'", "''")
    return f"'{s}'"


def _get_openai_projects(projects):
    return [p for p in projects if p["customer_id"] == 2]


def _get_project_workers(assignments, project_id, feather_mappings):
    workers = []
    for a in assignments:
        if a["project_id"] == project_id and a["tasker_id"] in feather_mappings:
            workers.append({
                "tasker_id": a["tasker_id"],
                "external_id": feather_mappings[a["tasker_id"]],
                "assigned_date": a["assigned_date"],
                "removed_date": a["removed_date"],
                "status": a["status"],
                "roles": a.get("roles", ["tasker"]),
            })
    return workers


def _is_worker_active(worker, year, month):
    assigned = date.fromisoformat(worker["assigned_date"])
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(year, month + 1, 1) - timedelta(days=1)

    if assigned > month_end:
        return False
    if worker["removed_date"]:
        removed = date.fromisoformat(worker["removed_date"])
        if removed < month_start:
            return False
    return True


def generate_feather_data(rng, projects, assignments, feather_mappings, scale_factor):
    """
    Generate tasks, submissions, quality_reviews for OpenAI Feather.

    Target at scale=1.0: ~1.5M tasks, ~1.8M submissions, ~1.2M reviews
    """
    all_tasks = []
    all_submissions = []
    all_reviews = []

    openai_projects = _get_openai_projects(projects)
    if not openai_projects:
        print("  No OpenAI projects found!")
        return [], [], []

    task_types = CUSTOMERS[2]["task_types"]
    active_months = get_active_months()
    openai_start = CUSTOMERS[2]["start_quarter"]
    active_months = [(y, m) for y, m in active_months if (y, m) >= openai_start]

    total_target = int(1_500_000 * scale_factor)

    month_weights = [get_monthly_multiplier(y, m) for y, m in active_months]
    total_weight = sum(month_weights) or 1.0

    month_counts = [max(1, int(total_target * w / total_weight)) for w in month_weights]
    diff = total_target - sum(month_counts)
    if diff > 0 and month_counts:
        month_counts[-1] += diff

    for month_idx, (y, m) in enumerate(tqdm(active_months, desc="Feather months")):
        target_this_month = month_counts[month_idx]

        active_projects = []
        for p in openai_projects:
            p_start = date.fromisoformat(p["start_date"])
            p_end = date.fromisoformat(p["end_date"]) if p["end_date"] else date(2026, 3, 1)
            month_start = date(y, m, 1)
            if p_start <= date(y, m, 28) and p_end >= month_start:
                workers = _get_project_workers(assignments, p["id"], feather_mappings)
                active_ws = [w for w in workers if _is_worker_active(w, y, m)]
                if active_ws:
                    active_projects.append((p, active_ws))

        if not active_projects:
            continue

        project_weights = [len(ws) for _, ws in active_projects]
        total_pw = sum(project_weights) or 1

        for proj_idx, (project, workers) in enumerate(active_projects):
            proj_count = max(1, int(target_this_month * project_weights[proj_idx] / total_pw))

            proj_type_idx = project["id"] % len(task_types)
            primary_type = task_types[proj_type_idx]

            # Use deterministic project_id from PHD projects table
            feather_project_id = project.get("external_project_id", f"proj_f_{generate_hex_id(rng, 8)}")

            for t_idx in range(proj_count):
                worker = rng.choice(workers)

                # Task type
                if rng.random() < 0.70:
                    task_type = primary_type
                else:
                    task_type = rng.choice(task_types)

                # Title
                titles = FEATHER_TASK_TITLES.get(task_type, FEATHER_TASK_TITLES["rlhf_ranking"])
                title = rng.choice(titles)

                # Status distribution
                s_roll = rng.random()
                if s_roll < 0.05:
                    status = "pending"
                elif s_roll < 0.13:
                    status = "in_progress"
                elif s_roll < 0.65:
                    status = "submitted"
                elif s_roll < 0.88:
                    status = "approved"
                else:
                    status = "rejected"

                created_at = random_datetime_in_month(rng, y, m)

                task_id = f"task_f_{generate_hex_id(rng, 12)}"

                all_tasks.append((
                    task_id, feather_project_id, title, task_type,
                    worker["external_id"], status, created_at
                ))

                # Submissions for non-pending/in-progress tasks
                if status in ("submitted", "approved", "rejected"):
                    # Multi-worker pattern
                    comp_roll = rng.random()
                    if comp_roll < 0.70:
                        num_submissions = 1
                    elif comp_roll < 0.90:
                        num_submissions = 1
                    else:
                        num_submissions = rng.randint(2, 3)

                    for s_idx in range(num_submissions):
                        if s_idx == 0:
                            submitter_id = worker["external_id"]
                        else:
                            other = rng.choice(workers)
                            submitter_id = other["external_id"]

                        # time_spent_seconds: 300-7200, normal around 1800
                        time_spent = max(300, min(7200, int(rng.gauss(1800, 600))))

                        # Submission status
                        ss_roll = rng.random()
                        if ss_roll < 0.10:
                            sub_status = "pending_review"
                        elif ss_roll < 0.75:
                            sub_status = "approved"
                        elif ss_roll < 0.90:
                            sub_status = "rejected"
                        else:
                            sub_status = "revision_requested"

                        submission_id = f"sub_f_{generate_hex_id(rng, 12)}"

                        all_submissions.append((
                            submission_id, task_id, submitter_id,
                            created_at, time_spent, sub_status
                        ))

                        # Reviews for this submission
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
                            reviewer_candidates = [w for w in workers if w["external_id"] != submitter_id]
                            if not reviewer_candidates:
                                reviewer_candidates = workers
                            reviewer = rng.choice(reviewer_candidates)

                            # Score: 0.0-1.0 float, normal around 0.72
                            score = max(0.0, min(1.0, round(rng.gauss(0.72, 0.15), 2)))

                            # Rating from score
                            if score >= 0.85:
                                rating = "excellent"
                            elif score >= 0.65:
                                rating = "acceptable"
                            elif score >= 0.4:
                                rating = "needs_improvement"
                            else:
                                rating = "unacceptable"

                            # Feedback
                            if score >= 0.7:
                                feedback = rng.choice(REVIEW_NOTES_POSITIVE)
                            elif score >= 0.5:
                                feedback = rng.choice(REVIEW_NOTES_NEUTRAL)
                            else:
                                feedback = rng.choice(REVIEW_NOTES_NEGATIVE)

                            review_id = f"rev_f_{generate_hex_id(rng, 12)}"

                            all_reviews.append((
                                review_id, submission_id, reviewer["external_id"],
                                score, rating, feedback, created_at
                            ))

    return all_tasks, all_submissions, all_reviews


def insert_data(conn, tasks, submissions, reviews):
    """Truncate and insert all Feather data."""
    cur = conn.cursor()

    print("  Truncating Feather tables...")
    cur.execute("TRUNCATE quality_reviews, submissions, tasks CASCADE;")
    conn.commit()

    print(f"  Inserting {len(tasks)} tasks...")
    for i in tqdm(range(0, len(tasks), BATCH_SIZE), desc="  Tasks"):
        batch = tasks[i:i + BATCH_SIZE]
        values = []
        for t in batch:
            values.append(
                f"({_escape_sql(t[0])}, {_escape_sql(t[1])}, {_escape_sql(t[2])}, "
                f"{_escape_sql(t[3])}, {_escape_sql(t[4])}, {_escape_sql(t[5])}, "
                f"{_escape_sql(t[6])})"
            )
        sql = (
            "INSERT INTO tasks (task_id, project_id, title, type, "
            "assigned_to, status, created_at) VALUES\n"
            + ",\n".join(values) + ";"
        )
        cur.execute(sql)
        conn.commit()

    print(f"  Inserting {len(submissions)} submissions...")
    for i in tqdm(range(0, len(submissions), BATCH_SIZE), desc="  Submissions"):
        batch = submissions[i:i + BATCH_SIZE]
        values = []
        for s in batch:
            values.append(
                f"({_escape_sql(s[0])}, {_escape_sql(s[1])}, {_escape_sql(s[2])}, "
                f"{_escape_sql(s[3])}, {s[4]}, {_escape_sql(s[5])})"
            )
        sql = (
            "INSERT INTO submissions (submission_id, task_id, submitted_by, "
            "submitted_at, time_spent_seconds, status) VALUES\n"
            + ",\n".join(values) + ";"
        )
        cur.execute(sql)
        conn.commit()

    print(f"  Inserting {len(reviews)} reviews...")
    for i in tqdm(range(0, len(reviews), BATCH_SIZE), desc="  Reviews"):
        batch = reviews[i:i + BATCH_SIZE]
        values = []
        for r in batch:
            feedback = _escape_sql(r[5])
            values.append(
                f"({_escape_sql(r[0])}, {_escape_sql(r[1])}, {_escape_sql(r[2])}, "
                f"{r[3]}, {_escape_sql(r[4])}, {feedback}, {_escape_sql(r[6])})"
            )
        sql = (
            "INSERT INTO quality_reviews (review_id, submission_id, reviewer_id, "
            "score, rating, feedback, reviewed_at) VALUES\n"
            + ",\n".join(values) + ";"
        )
        cur.execute(sql)
        conn.commit()

    cur.close()


def run(projects, assignments, feather_mappings, scale_factor=None):
    """Main entry point."""
    sf = scale_factor if scale_factor is not None else SCALE_FACTOR
    rng = random.Random(RANDOM_SEED + 200)

    print("\nGenerating Feather data...")
    tasks, submissions, reviews = generate_feather_data(
        rng, projects, assignments, feather_mappings, sf
    )

    print(f"\n--- Feather Data Generated ---")
    print(f"Tasks:       {len(tasks):,}")
    print(f"Submissions: {len(submissions):,}")
    print(f"Reviews:     {len(reviews):,}")

    print("\nConnecting to Feather database...")
    conn = get_connection(FEATHER_DATABASE_URL)

    insert_data(conn, tasks, submissions, reviews)
    conn.close()

    print("Feather data insertion complete.")
    return len(tasks), len(submissions), len(reviews)


if __name__ == "__main__":
    print("This module should be run via run_all.py")
