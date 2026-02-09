"""
Fairtable API generator: tasks, submissions, reviews for Google/xAI/Anthropic.
Uses PHD tasker IDs directly (no external ID mapping needed).
Writes directly to the Fairtable Neon database.
"""

import random
from datetime import date, timedelta
from tqdm import tqdm

from config import (
    RANDOM_SEED, SCALE_FACTOR, BATCH_SIZE,
    CUSTOMERS, FAIRTABLE_TASK_TITLES,
    REVIEW_NOTES_POSITIVE, REVIEW_NOTES_NEGATIVE, REVIEW_NOTES_NEUTRAL,
    get_monthly_multiplier, get_active_months, get_connection,
    FAIRTABLE_DATABASE_URL, generate_hex_id, random_datetime_in_month,
)


# Customer ID → base_id mapping
CUSTOMER_BASE = {
    3: "base_google",
    4: "base_xai",
    5: "base_anthropic",
}

# Customer ID → target task counts at scale=1.0
CUSTOMER_TARGETS = {
    3: 900_000,   # Google
    4: 450_000,   # xAI
    5: 450_000,   # Anthropic
}


def _escape_sql(val):
    if val is None:
        return "NULL"
    s = str(val).replace("'", "''")
    return f"'{s}'"


def _get_customer_projects(projects, customer_id):
    return [p for p in projects if p["customer_id"] == customer_id]


def _get_project_workers(assignments, project_id, taskers_by_id):
    """Get workers for a project. Returns list of dicts with tasker info."""
    workers = []
    for a in assignments:
        if a["project_id"] == project_id:
            tasker = taskers_by_id.get(a["tasker_id"])
            if tasker:
                workers.append({
                    "tasker_id": a["tasker_id"],
                    "name": f"{tasker['first_name']} {tasker['last_name']}",
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


def generate_fairtable_data(rng, projects, assignments, taskers, scale_factor):
    """
    Generate tasks, submissions, reviews for Google/xAI/Anthropic via Fairtable.

    Target at scale=1.0:
    - base_google: ~900K tasks, ~1.1M submissions, ~700K reviews
    - base_xai: ~450K tasks, ~540K submissions, ~350K reviews
    - base_anthropic: ~450K tasks, ~540K submissions, ~350K reviews
    """
    all_tasks = []
    all_submissions = []
    all_reviews = []

    # Build tasker lookup
    taskers_by_id = {t["id"]: t for t in taskers}

    for customer_id in [3, 4, 5]:
        cfg = CUSTOMERS[customer_id]
        base_id = CUSTOMER_BASE[customer_id]
        customer_projects = _get_customer_projects(projects, customer_id)

        if not customer_projects:
            print(f"  No {cfg['name']} projects found!")
            continue

        task_types = cfg["task_types"]
        customer_start = cfg["start_quarter"]

        active_months = get_active_months()
        active_months = [(y, m) for y, m in active_months if (y, m) >= customer_start]

        total_target = int(CUSTOMER_TARGETS[customer_id] * scale_factor)

        month_weights = [get_monthly_multiplier(y, m) for y, m in active_months]
        total_weight = sum(month_weights) or 1.0

        month_counts = [max(1, int(total_target * w / total_weight)) for w in month_weights]
        diff = total_target - sum(month_counts)
        if diff > 0 and month_counts:
            month_counts[-1] += diff

        desc = f"Fairtable {cfg['name']}"
        for month_idx, (y, m) in enumerate(tqdm(active_months, desc=desc)):
            target_this_month = month_counts[month_idx]

            active_projects = []
            for p in customer_projects:
                p_start = date.fromisoformat(p["start_date"])
                p_end = date.fromisoformat(p["end_date"]) if p["end_date"] else date(2026, 3, 1)
                month_start = date(y, m, 1)
                if p_start <= date(y, m, 28) and p_end >= month_start:
                    workers = _get_project_workers(assignments, p["id"], taskers_by_id)
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

                for t_idx in range(proj_count):
                    worker = rng.choice(workers)

                    # Task type
                    if rng.random() < 0.70:
                        task_type = primary_type
                    else:
                        task_type = rng.choice(task_types)

                    # Task name
                    titles = FAIRTABLE_TASK_TITLES.get(task_type, FAIRTABLE_TASK_TITLES["domain_qa"])
                    task_name = rng.choice(titles)

                    # Status distribution
                    s_roll = rng.random()
                    if s_roll < 0.05:
                        status = "todo"
                    elif s_roll < 0.13:
                        status = "in_progress"
                    elif s_roll < 0.78:
                        status = "done"
                    else:
                        status = "reviewed"

                    created_at = random_datetime_in_month(rng, y, m)

                    # Due date: 3-21 days after creation, or None
                    due_date = None
                    if rng.random() < 0.5:
                        d_day = int(created_at[8:10]) + rng.randint(3, 21)
                        if d_day > 28:
                            d_day = 28
                        due_date = f"{created_at[:8]}{d_day:02d}"

                    record_id = f"rec_{generate_hex_id(rng, 12)}"

                    all_tasks.append((
                        record_id, base_id, task_name, task_type,
                        worker["tasker_id"], status, created_at, due_date
                    ))

                    # Submissions for done/reviewed tasks
                    if status in ("done", "reviewed"):
                        comp_roll = rng.random()
                        if comp_roll < 0.70:
                            num_submissions = 1
                        elif comp_roll < 0.90:
                            num_submissions = 1
                        else:
                            num_submissions = rng.randint(2, 3)

                        for s_idx in range(num_submissions):
                            if s_idx == 0:
                                submitter_id = worker["tasker_id"]
                            else:
                                other = rng.choice(workers)
                                submitter_id = other["tasker_id"]

                            # hours_logged: 0.25-6.0, normal around 1.5
                            hours = max(0.25, min(6.0, round(rng.gauss(1.5, 0.6), 2)))

                            # Submission status
                            ss_roll = rng.random()
                            if ss_roll < 0.10:
                                sub_status = "pending"
                            elif ss_roll < 0.82:
                                sub_status = "approved"
                            else:
                                sub_status = "rejected"

                            sub_record_id = f"rec_{generate_hex_id(rng, 12)}"

                            all_submissions.append((
                                sub_record_id, base_id, record_id,
                                submitter_id, created_at, hours, sub_status
                            ))

                            # Reviews
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
                                reviewer_candidates = [w for w in workers if w["tasker_id"] != submitter_id]
                                if not reviewer_candidates:
                                    reviewer_candidates = workers
                                reviewer = rng.choice(reviewer_candidates)

                                # Score: 0-100, normal around 75
                                score = max(0.0, min(100.0, round(rng.gauss(75.0, 12.0), 1)))

                                # Status from score (uses pass/fail/conditional_pass per actual SQL schema)
                                if score >= 70:
                                    rev_status = "pass"
                                elif score >= 50:
                                    rev_status = "conditional_pass"
                                else:
                                    rev_status = "fail"

                                # Comments
                                if score >= 70:
                                    comments = rng.choice(REVIEW_NOTES_POSITIVE)
                                elif score >= 50:
                                    comments = rng.choice(REVIEW_NOTES_NEUTRAL)
                                else:
                                    comments = rng.choice(REVIEW_NOTES_NEGATIVE)

                                rev_record_id = f"rec_{generate_hex_id(rng, 12)}"

                                all_reviews.append((
                                    rev_record_id, base_id, sub_record_id,
                                    reviewer["name"], score, rev_status,
                                    comments, created_at
                                ))

    return all_tasks, all_submissions, all_reviews


def insert_data(conn, tasks, submissions, reviews):
    """Truncate and insert all Fairtable data."""
    cur = conn.cursor()

    print("  Truncating Fairtable tables...")
    cur.execute("TRUNCATE reviews, submissions, tasks CASCADE;")
    conn.commit()

    print(f"  Inserting {len(tasks)} tasks...")
    for i in tqdm(range(0, len(tasks), BATCH_SIZE), desc="  Tasks"):
        batch = tasks[i:i + BATCH_SIZE]
        values = []
        for t in batch:
            due = _escape_sql(t[7])
            values.append(
                f"({_escape_sql(t[0])}, {_escape_sql(t[1])}, {_escape_sql(t[2])}, "
                f"{_escape_sql(t[3])}, {t[4]}, {_escape_sql(t[5])}, "
                f"{_escape_sql(t[6])}, {due})"
            )
        sql = (
            "INSERT INTO tasks (record_id, base_id, task_name, task_type, "
            "assigned_to, status, created_at, due_date) VALUES\n"
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
                f"{s[3]}, {_escape_sql(s[4])}, {s[5]}, {_escape_sql(s[6])})"
            )
        sql = (
            "INSERT INTO submissions (record_id, base_id, task_record_id, "
            "submitted_by, submitted_at, hours_logged, status) VALUES\n"
            + ",\n".join(values) + ";"
        )
        cur.execute(sql)
        conn.commit()

    print(f"  Inserting {len(reviews)} reviews...")
    for i in tqdm(range(0, len(reviews), BATCH_SIZE), desc="  Reviews"):
        batch = reviews[i:i + BATCH_SIZE]
        values = []
        for r in batch:
            comments = _escape_sql(r[6])
            values.append(
                f"({_escape_sql(r[0])}, {_escape_sql(r[1])}, {_escape_sql(r[2])}, "
                f"{_escape_sql(r[3])}, {r[4]}, {_escape_sql(r[5])}, "
                f"{comments}, {_escape_sql(r[7])})"
            )
        sql = (
            "INSERT INTO reviews (record_id, base_id, submission_record_id, "
            "reviewed_by, score, status, comments, reviewed_at) VALUES\n"
            + ",\n".join(values) + ";"
        )
        cur.execute(sql)
        conn.commit()

    cur.close()


def run(projects, assignments, taskers, scale_factor=None):
    """Main entry point."""
    sf = scale_factor if scale_factor is not None else SCALE_FACTOR
    rng = random.Random(RANDOM_SEED + 300)

    print("\nGenerating Fairtable data...")
    tasks, submissions, reviews = generate_fairtable_data(
        rng, projects, assignments, taskers, sf
    )

    print(f"\n--- Fairtable Data Generated ---")
    print(f"Tasks:       {len(tasks):,}")
    print(f"Submissions: {len(submissions):,}")
    print(f"Reviews:     {len(reviews):,}")

    print("\nConnecting to Fairtable database...")
    conn = get_connection(FAIRTABLE_DATABASE_URL)

    insert_data(conn, tasks, submissions, reviews)
    conn.close()

    print("Fairtable data insertion complete.")
    return len(tasks), len(submissions), len(reviews)


if __name__ == "__main__":
    print("This module should be run via run_all.py")
