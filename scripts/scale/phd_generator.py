"""
PHD Database generator: contracts, projects, assignments.
Keeps existing customers (1-5), billing_cycles (1-4), domains, subdomains, taskers, SPLs.
Replaces contracts, projects, assignments with scaled versions.
"""

import random
import hashlib
import math
from datetime import date, timedelta
from tqdm import tqdm

from config import (
    RANDOM_SEED, SCALE_FACTOR, BATCH_SIZE,
    CUSTOMERS, CONTRACT_TEMPLATES, PROJECT_EXTERNAL_TEMPLATES,
    PROJECT_INTERNAL_TEMPLATES, DOMAIN_SUBDOMAIN_MAP,
    SUBDOMAIN_TO_DOMAIN, REMOVAL_REASONS,
    get_monthly_multiplier, get_active_months, get_connection,
    PHD_DATABASE_URL, EXISTING_SPL_IDS,
)


def _deterministic_project_id(customer_id, project_id):
    """Generate a deterministic external project ID based on customer platform.

    Meta → proj_srt_<hash>
    OpenAI → proj_f_<hash>
    Google/xAI/Anthropic → base_<customer> (Fairtable has no per-project ID)
    """
    base_ids = {3: "base_google", 4: "base_xai", 5: "base_anthropic"}

    if customer_id in base_ids:
        # Fairtable doesn't have per-project IDs, just base_id
        return base_ids[customer_id]

    # SRT and Feather get deterministic hashed project IDs
    seed = f"project_{RANDOM_SEED}_{customer_id}_{project_id}"
    h = hashlib.sha256(seed.encode()).hexdigest()[:8]

    if customer_id == 1:  # Meta → SRT
        return f"proj_srt_{h}"
    elif customer_id == 2:  # OpenAI → Feather
        return f"proj_f_{h}"
    return f"proj_ext_{h}"


def _period_label(start_year, start_month, duration_months):
    """Generate a period label like 'Q3 2024' or 'H1 2025' or '2024-2025'."""
    if duration_months <= 4:
        q = (start_month - 1) // 3 + 1
        return f"Q{q} {start_year}"
    elif duration_months <= 7:
        h = 1 if start_month <= 6 else 2
        return f"H{h} {start_year}"
    else:
        end_year = start_year + (start_month + duration_months - 1) // 12
        if end_year > start_year:
            return f"{start_year}-{end_year}"
        return str(start_year)


def generate_contracts(rng):
    """Generate ~35 contracts across all customers following growth curve."""
    contracts = []
    contract_id = 1

    for customer_id, cfg in CUSTOMERS.items():
        templates = CONTRACT_TEMPLATES[customer_id]
        start_year, start_month = cfg["start_quarter"]
        take_lo, take_hi = cfg["take_rate_range"]

        # Number of contracts per customer
        num_contracts = {1: 8, 2: 7, 3: 7, 4: 6, 5: 7}[customer_id]

        template_idx = 0
        # Spread contracts over time
        months_available = []
        for y, m in get_active_months():
            if (y, m) >= (start_year, start_month):
                months_available.append((y, m))

        # Distribute contract starts across available months
        spacing = max(1, len(months_available) // num_contracts)

        for i in range(num_contracts):
            month_idx = min(i * spacing, len(months_available) - 1)
            sy, sm = months_available[month_idx]

            # Contract duration: 4-14 months
            duration = rng.randint(4, 14)
            end_year = sy + (sm + duration - 1) // 12
            end_month = ((sm + duration - 1) % 12) + 1

            # Determine if contract should have ended
            contract_end = date(end_year, end_month, 28)
            today = date(2026, 2, 1)

            take_rate = round(rng.uniform(take_lo, take_hi), 2)

            # Budget grows with growth curve — early contracts smaller, later ones bigger
            multiplier = get_monthly_multiplier(sy, sm)

            # Status logic — determine first so we can size budgets appropriately
            if contract_end < today and i < num_contracts - 3:
                if rng.random() < 0.08:
                    status = "canceled"
                else:
                    status = "completed"
                end_date = contract_end.isoformat()
            elif i >= num_contracts - 3:
                status = "active"
                end_date = None
            else:
                if rng.random() < 0.1:
                    status = "inactive"
                    end_date = contract_end.isoformat()
                else:
                    status = "completed"
                    end_date = contract_end.isoformat()

            # Budget calculation
            # Target: active contracts' annualized budgets × take_rates ≈ $350M net
            # $350M net / avg_take_rate(0.30) = ~$1.17B gross annual billing
            # With ~15 active contracts, ~$78M each avg annual gross
            # contract_budget = gross billing for the contract's full duration
            if status == "active":
                # Active contracts: sized so their collective annualized throughput
                # × take_rate ≈ customer's revenue_share × $350M
                # Each customer has ~3 active contracts
                customer_net_target = cfg["revenue_share"] * 350_000_000  # annual net target
                per_contract_annual_net = customer_net_target / 3
                per_contract_annual_gross = per_contract_annual_net / take_rate
                # Contracts are ongoing, budget = ~12 months of gross billing
                budget = int(per_contract_annual_gross * rng.uniform(0.85, 1.15))
                budget = round(budget, -3)
            else:
                # Historical contracts: scale with the growth curve at their start time
                peak_gross = cfg["revenue_share"] * 350_000_000 / 0.30
                monthly_gross = peak_gross / 12 * max(0.03, multiplier)
                budget = int(monthly_gross * duration * rng.uniform(0.5, 1.2))
                budget = max(200_000, round(budget, -3))

            period = _period_label(sy, sm, duration)
            template = templates[template_idx % len(templates)]
            contract_name = template.format(period=period)
            template_idx += 1

            contracts.append({
                "id": contract_id,
                "customer_id": customer_id,
                "billing_cycle_id": cfg["billing_cycle_id"],
                "contract_name": contract_name,
                "start_date": date(sy, sm, 1).isoformat(),
                "end_date": end_date,
                "take_rate": take_rate,
                "contract_budget": f"{budget:.2f}",
                "status": status,
            })
            contract_id += 1

    return contracts


def generate_projects(rng, contracts):
    """Generate ~70 projects, 2-4 per contract."""
    projects = []
    project_id = 1

    for contract in contracts:
        customer_id = contract["customer_id"]
        cfg = CUSTOMERS[customer_id]
        ext_templates = PROJECT_EXTERNAL_TEMPLATES[customer_id]

        num_projects = rng.randint(2, 3)
        # Bigger contracts get more projects
        budget = float(contract["contract_budget"])
        if budget > 20_000_000:
            num_projects = rng.randint(3, 4)

        contract_start = date.fromisoformat(contract["start_date"])

        # Pick subdomain_ids based on customer domain focus
        domain_focus = cfg["domain_focus"]

        for j in range(num_projects):
            # Project starts within first month of contract
            proj_start = contract_start + timedelta(days=rng.randint(0, 21))

            # Project end follows contract end
            proj_end = None
            if contract["end_date"]:
                ce = date.fromisoformat(contract["end_date"])
                proj_end = ce - timedelta(days=rng.randint(0, 14))

            # Budget is fraction of contract budget
            proj_budget = budget / num_projects * rng.uniform(0.7, 1.3)
            proj_budget = round(proj_budget, -2)

            # Billing rate
            rate_lo, rate_hi = cfg["base_billing_rate"]
            billing_rate = round(rng.uniform(rate_lo, rate_hi), 2)

            # Pick subdomains for this project (2-5 from domain focus)
            num_subs = min(len(domain_focus), rng.randint(2, 5))
            subdomain_ids = sorted(rng.sample(domain_focus, num_subs))

            # External name
            ext_template = ext_templates[j % len(ext_templates)]
            version = rng.randint(1, 12)
            yr = proj_start.year
            external_name = ext_template.format(v=version, yr=yr)

            # Internal name
            # Pick a domain name for the template
            domain_names = ["General", "SWE", "Medical", "Legal", "Science",
                           "Code", "Safety", "Multilingual", "Humanities"]
            domain_label = rng.choice(domain_names)
            int_template = rng.choice(PROJECT_INTERNAL_TEMPLATES)
            internal_name = int_template.format(domain=domain_label)

            # Status
            today = date(2026, 2, 1)
            if contract["status"] == "active":
                status = rng.choice(["active"] * 8 + ["staffing", "paused"])
            elif contract["status"] == "completed":
                status = "completed"
            elif contract["status"] == "canceled":
                status = "cancelled"
            else:
                status = rng.choice(["completed", "paused"])

            # Assign an SPL
            spl_id = rng.choice(EXISTING_SPL_IDS[:15])  # active SPLs

            # Deterministic external project ID for platform linkage
            ext_proj_id = _deterministic_project_id(customer_id, project_id)

            projects.append({
                "id": project_id,
                "customer_id": customer_id,
                "contract_id": contract["id"],
                "spl_id": spl_id,
                "external_name": external_name,
                "internal_name": internal_name,
                "start_date": proj_start.isoformat(),
                "end_date": proj_end.isoformat() if proj_end else None,
                "budget": f"{proj_budget:.2f}",
                "billing_rate": f"{billing_rate:.2f}",
                "subdomain_ids": subdomain_ids,
                "status": status,
                "external_project_id": ext_proj_id,
            })
            project_id += 1

    return projects


def _fetch_taskers(conn):
    """Fetch all taskers with their subdomain_ids from the DB."""
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, last_name, subdomain_ids, hours_available, hourly_rate, status FROM taskers ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    taskers = []
    for row in rows:
        taskers.append({
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "subdomain_ids": row[3] if row[3] else [],
            "hours_available": float(row[4]) if row[4] else 0,
            "hourly_rate": float(row[5]) if row[5] else 0,
            "status": row[6],
        })
    return taskers


def generate_assignments(rng, projects, taskers, scale_factor):
    """
    Generate assignments matching taskers to projects by subdomain overlap.
    Target: ~18,000-22,000 at full scale.
    """
    assignments = []
    assignment_id = 1

    # Build subdomain → tasker index
    subdomain_to_taskers = {}
    for t in taskers:
        if t["status"] != "active":
            continue
        for sid in t["subdomain_ids"]:
            subdomain_to_taskers.setdefault(sid, []).append(t)

    # Growth curve affects how many taskers get assigned per project
    active_months = get_active_months()

    for project in tqdm(projects, desc="Generating assignments"):
        proj_start = date.fromisoformat(project["start_date"])
        proj_end = date.fromisoformat(project["end_date"]) if project["end_date"] else date(2026, 2, 1)

        # Find eligible taskers (subdomain overlap)
        eligible = set()
        for sid in project["subdomain_ids"]:
            for t in subdomain_to_taskers.get(sid, []):
                eligible.add(t["id"])
        eligible = list(eligible)

        if not eligible:
            continue

        # How many taskers? Scale with project budget and growth curve
        budget = float(project["budget"])
        billing_rate = float(project["billing_rate"])

        # Hours this project represents
        total_hours = budget / billing_rate
        # At ~30 hrs/week per tasker, how many taskers for this project?
        project_months = max(1, (proj_end - proj_start).days / 30)
        monthly_hours = total_hours / project_months
        ideal_taskers = max(3, int(monthly_hours / 120))  # ~120 hrs/month per tasker

        # Scale and cap
        num_taskers = max(3, int(ideal_taskers * scale_factor))
        num_taskers = min(num_taskers, len(eligible))

        # Select taskers
        selected = rng.sample(eligible, num_taskers)

        for tasker_id in selected:
            # Assignment date within first 30 days of project
            days_offset = rng.randint(0, min(30, max(0, (proj_end - proj_start).days - 1)))
            assigned_date = proj_start + timedelta(days=days_offset)

            # ~12% get removed
            removed = rng.random() < 0.12
            removed_date = None
            removal_reason = None
            status = "active"

            if removed:
                # Removed sometime during project
                remaining_days = max(1, (proj_end - assigned_date).days)
                remove_offset = rng.randint(14, max(14, remaining_days))
                removed_date = assigned_date + timedelta(days=remove_offset)
                if removed_date > proj_end:
                    removed_date = proj_end
                removal_reason = rng.choice(REMOVAL_REASONS)
                status = "removed"

            # Roles distribution: 70% tasker, 20% tasker+reviewer, 8% reviewer, 2% tasker+team_lead
            role_roll = rng.random()
            if role_roll < 0.70:
                roles = ["tasker"]
            elif role_roll < 0.90:
                roles = ["tasker", "reviewer"]
            elif role_roll < 0.98:
                roles = ["reviewer"]
            else:
                roles = ["tasker", "reviewer"]  # team_lead stored in taskers.internal_roles

            assignments.append({
                "id": assignment_id,
                "tasker_id": tasker_id,
                "project_id": project["id"],
                "assigned_date": assigned_date.isoformat(),
                "removed_date": removed_date.isoformat() if removed_date else None,
                "status": status,
                "removal_reason": removal_reason,
                "roles": roles,
            })
            assignment_id += 1

    return assignments


def _escape_sql(val):
    """Escape a string for SQL insertion."""
    if val is None:
        return "NULL"
    s = str(val).replace("'", "''")
    return f"'{s}'"


def _sql_array(arr):
    """Format a Python list as a PostgreSQL array literal."""
    if not arr:
        return "NULL"
    items = ",".join(str(x) for x in arr)
    return f"'{{{items}}}'"


def _sql_text_array(arr):
    """Format a Python list of strings as a PostgreSQL text array literal."""
    if not arr:
        return "'{tasker}'"
    items = ",".join(str(x) for x in arr)
    return f"'{{{items}}}'"


def insert_contracts(conn, contracts):
    """Insert contracts into the database."""
    cur = conn.cursor()
    for i in range(0, len(contracts), BATCH_SIZE):
        batch = contracts[i:i + BATCH_SIZE]
        values = []
        for c in batch:
            end_date = _escape_sql(c["end_date"])
            values.append(
                f"({c['id']}, {c['customer_id']}, {c['billing_cycle_id']}, "
                f"{_escape_sql(c['contract_name'])}, '{c['start_date']}', {end_date}, "
                f"{c['take_rate']}, {c['contract_budget']}, {_escape_sql(c['status'])})"
            )
        sql = (
            "INSERT INTO contracts (id, customer_id, billing_cycle_id, contract_name, "
            "start_date, end_date, take_rate, contract_budget, status) VALUES\n"
            + ",\n".join(values) + ";"
        )
        cur.execute(sql)
    cur.execute(f"SELECT setval('contracts_id_seq', {contracts[-1]['id']});")
    conn.commit()
    cur.close()


def insert_projects(conn, projects):
    """Insert projects into the database."""
    cur = conn.cursor()
    # Ensure external_project_id column exists
    cur.execute("""
        DO $$ BEGIN
            ALTER TABLE projects ADD COLUMN external_project_id VARCHAR(255);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)
    conn.commit()
    for i in range(0, len(projects), BATCH_SIZE):
        batch = projects[i:i + BATCH_SIZE]
        values = []
        for p in batch:
            end_date = _escape_sql(p["end_date"])
            values.append(
                f"({p['id']}, {p['customer_id']}, {p['contract_id']}, {p['spl_id']}, "
                f"{_escape_sql(p['external_name'])}, {_escape_sql(p['internal_name'])}, "
                f"'{p['start_date']}', {end_date}, {p['budget']}, {p['billing_rate']}, "
                f"{_sql_array(p['subdomain_ids'])}, {_escape_sql(p['status'])}, "
                f"{_escape_sql(p['external_project_id'])})"
            )
        sql = (
            "INSERT INTO projects (id, customer_id, contract_id, spl_id, external_name, "
            "internal_name, start_date, end_date, budget, billing_rate, subdomain_ids, status, "
            "external_project_id) VALUES\n"
            + ",\n".join(values) + ";"
        )
        cur.execute(sql)
    cur.execute(f"SELECT setval('projects_id_seq', {projects[-1]['id']});")
    conn.commit()
    cur.close()


def insert_assignments(conn, assignments):
    """Insert assignments into the database in batches."""
    cur = conn.cursor()
    for i in tqdm(range(0, len(assignments), BATCH_SIZE), desc="Inserting assignments"):
        batch = assignments[i:i + BATCH_SIZE]
        values = []
        for a in batch:
            removed_date = _escape_sql(a["removed_date"])
            values.append(
                f"({a['id']}, {a['tasker_id']}, {a['project_id']}, "
                f"'{a['assigned_date']}', {removed_date}, "
                f"{_escape_sql(a['status'])}, {_escape_sql(a['removal_reason'])}, "
                f"{_sql_text_array(a['roles'])})"
            )
        sql = (
            "INSERT INTO assignments (id, tasker_id, project_id, assigned_date, "
            "removed_date, status, removal_reason, roles) VALUES\n"
            + ",\n".join(values) + ";"
        )
        cur.execute(sql)
    cur.execute(f"SELECT setval('assignments_id_seq', {assignments[-1]['id']});")
    conn.commit()
    cur.close()


def run(scale_factor=None):
    """Main entry point for PHD data generation."""
    sf = scale_factor if scale_factor is not None else SCALE_FACTOR
    rng = random.Random(RANDOM_SEED)

    print("Connecting to PHD database...")
    conn = get_connection(PHD_DATABASE_URL)

    print("Fetching existing taskers...")
    taskers = _fetch_taskers(conn)
    print(f"  Found {len(taskers)} taskers")

    # Delete existing data in safe order
    print("Clearing existing assignments, projects, contracts...")
    cur = conn.cursor()
    cur.execute("DELETE FROM assignments;")
    cur.execute("DELETE FROM projects;")
    cur.execute("DELETE FROM contracts;")
    conn.commit()
    cur.close()

    print("Generating contracts...")
    contracts = generate_contracts(rng)
    print(f"  Generated {len(contracts)} contracts")

    print("Generating projects...")
    projects = generate_projects(rng, contracts)
    print(f"  Generated {len(projects)} projects")

    print("Generating assignments...")
    assignments = generate_assignments(rng, projects, taskers, sf)
    print(f"  Generated {len(assignments)} assignments")

    print("Inserting contracts...")
    insert_contracts(conn, contracts)

    print("Inserting projects...")
    insert_projects(conn, projects)

    print("Inserting assignments...")
    insert_assignments(conn, assignments)

    conn.close()

    # Print summary
    active_contracts = sum(1 for c in contracts if c["status"] == "active")
    active_projects = sum(1 for p in projects if p["status"] == "active")
    active_assignments = sum(1 for a in assignments if a["status"] == "active")

    # Revenue verification
    total_active_budget = sum(float(c["contract_budget"]) for c in contracts if c["status"] == "active")
    avg_take_rate = sum(c["take_rate"] for c in contracts if c["status"] == "active") / max(1, active_contracts)

    print(f"\n--- PHD Summary ---")
    print(f"Contracts: {len(contracts)} ({active_contracts} active)")
    print(f"Projects:  {len(projects)} ({active_projects} active)")
    print(f"Assignments: {len(assignments)} ({active_assignments} active)")
    print(f"Active contract budgets: ${total_active_budget:,.0f}")
    print(f"Average take rate: {avg_take_rate:.1%}")
    print(f"Estimated net ARR: ${total_active_budget * avg_take_rate:,.0f}")

    return {
        "contracts": contracts,
        "projects": projects,
        "assignments": assignments,
        "taskers": taskers,
    }


if __name__ == "__main__":
    run()
