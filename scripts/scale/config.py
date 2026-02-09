"""
Shared configuration for PHD data scaling.
Growth curves, DB connections, customer configs, and constants.
"""

import os
import math
import random

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# Scale factor: 0.0–1.0  (1.0 = full $350M ARR, 0.1 = 10% for testing)
# Overridden by --scale CLI flag in run_all.py
# ---------------------------------------------------------------------------
SCALE_FACTOR = 1.0

# ---------------------------------------------------------------------------
# Batch size for bulk INSERTs
# ---------------------------------------------------------------------------
BATCH_SIZE = 5000

# ---------------------------------------------------------------------------
# Database connection strings
# ---------------------------------------------------------------------------
PHD_DATABASE_URL = os.environ.get(
    "PHD_DATABASE_URL",
    ""  # user must set this
)

SRT_DATABASE_URL = os.environ.get(
    "SRT_DATABASE_URL",
    "postgresql://neondb_owner:npg_SPD1CUfiV9Nz@ep-dawn-rice-aidjsb8a-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

FEATHER_DATABASE_URL = os.environ.get(
    "FEATHER_DATABASE_URL",
    "postgresql://neondb_owner:npg_WdYp2ucHzqI4@ep-green-grass-aiu49ik8-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

FAIRTABLE_DATABASE_URL = os.environ.get(
    "FAIRTABLE_DATABASE_URL",
    "postgresql://neondb_owner:npg_oRZ1er6qaHhc@ep-icy-snow-ai8wakfm-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

# ---------------------------------------------------------------------------
# Growth curve
# Maps (year, month) → multiplier 0.0–1.0 of peak capacity
# Peak = 1.0 corresponds to $350M net ARR run-rate
# ---------------------------------------------------------------------------
# Monthly milestones derived from the quarterly targets:
# Q3 2023: $3M, Q4 2023: $10M, Q1 2024: $25M, Q2 2024: $50M,
# Q3 2024: $90M, Q4 2024: $150M, Q1 2025: $230M, Q2 2025: $290M,
# Q3 2025: $330M, Q4 2025: $350M, Jan-Feb 2026: $350M

_MONTHLY_ARR = {
    (2023, 7): 1.0,   (2023, 8): 2.0,   (2023, 9): 3.0,
    (2023, 10): 5.0,  (2023, 11): 7.5,   (2023, 12): 10.0,
    (2024, 1): 15.0,  (2024, 2): 20.0,   (2024, 3): 25.0,
    (2024, 4): 32.0,  (2024, 5): 40.0,   (2024, 6): 50.0,
    (2024, 7): 60.0,  (2024, 8): 75.0,   (2024, 9): 90.0,
    (2024, 10): 110.0, (2024, 11): 130.0, (2024, 12): 150.0,
    (2025, 1): 175.0, (2025, 2): 200.0,  (2025, 3): 230.0,
    (2025, 4): 255.0, (2025, 5): 275.0,  (2025, 6): 290.0,
    (2025, 7): 305.0, (2025, 8): 318.0,  (2025, 9): 330.0,
    (2025, 10): 340.0, (2025, 11): 345.0, (2025, 12): 350.0,
    (2026, 1): 350.0, (2026, 2): 350.0,
}

PEAK_ARR = 350.0  # $350M


def get_monthly_multiplier(year: int, month: int) -> float:
    """Return 0.0–1.0 multiplier for the given month relative to peak."""
    arr = _MONTHLY_ARR.get((year, month), 0.0)
    return arr / PEAK_ARR


def get_active_months():
    """Return sorted list of (year, month) tuples where business is active."""
    return sorted(_MONTHLY_ARR.keys())


# ---------------------------------------------------------------------------
# Customer configuration
# ---------------------------------------------------------------------------
# customer_id → config
CUSTOMERS = {
    1: {
        "name": "Meta",
        "platform": "SRT Tool",
        "billing_cycle_id": 2,
        "primary_spl_id": 1,
        "start_quarter": (2023, 7),   # Q3 2023
        "base_billing_rate": (85, 130),
        "take_rate_range": (0.28, 0.32),
        "revenue_share": 0.30,  # fraction of total $350M
        "annotation_types": ["preference_ranking", "safety_labeling", "prompt_response"],
        "domain_focus": [1, 2, 3, 5, 6],  # SWE subdomains
    },
    2: {
        "name": "OpenAI",
        "platform": "Feather",
        "billing_cycle_id": 1,
        "primary_spl_id": 2,
        "start_quarter": (2023, 10),  # Q4 2023
        "base_billing_rate": (85, 140),
        "take_rate_range": (0.28, 0.32),
        "revenue_share": 0.25,
        "task_types": ["rlhf_ranking", "code_review", "text_generation"],
        "domain_focus": [1, 2, 3, 5, 9, 54, 56],
    },
    3: {
        "name": "Google",
        "platform": "Airtable",
        "billing_cycle_id": 1,
        "primary_spl_id": 3,
        "start_quarter": (2024, 1),   # Q1 2024
        "base_billing_rate": (100, 250),
        "take_rate_range": (0.25, 0.30),
        "revenue_share": 0.20,
        "task_types": ["medical_evaluation", "legal_evaluation", "domain_qa", "science_evaluation"],
        "base_id": "base_google",
        "domain_focus": [22, 27, 28, 29, 36, 37, 38, 40, 50, 80, 85, 95, 98],
    },
    4: {
        "name": "xAI",
        "platform": "Airtable",
        "billing_cycle_id": 3,
        "primary_spl_id": 4,
        "start_quarter": (2024, 4),   # Q2 2024
        "base_billing_rate": (80, 120),
        "take_rate_range": (0.30, 0.35),
        "revenue_share": 0.12,
        "task_types": ["code_generation", "code_review", "red_team", "adversarial_prompt"],
        "base_id": "base_xai",
        "domain_focus": [1, 2, 3, 5, 6, 50],
    },
    5: {
        "name": "Anthropic",
        "platform": "Airtable",
        "billing_cycle_id": 4,
        "primary_spl_id": 5,
        "start_quarter": (2024, 7),   # Q3 2024
        "base_billing_rate": (90, 180),
        "take_rate_range": (0.27, 0.30),
        "revenue_share": 0.13,
        "task_types": ["science_evaluation", "humanities_evaluation", "domain_qa", "red_team"],
        "base_id": "base_anthropic",
        "domain_focus": [80, 85, 88, 95, 98, 106, 108, 129, 130, 131],
    },
}

# Revenue share must sum to 1.0
assert abs(sum(c["revenue_share"] for c in CUSTOMERS.values()) - 1.0) < 0.01

# ---------------------------------------------------------------------------
# SPL data (existing 5 kept, plus 13 new → 18 total, but DB already has 21)
# We'll keep existing SPLs 1-21 and reference them.
# ---------------------------------------------------------------------------
EXISTING_SPL_IDS = list(range(1, 22))  # 1-21 already in DB

# ---------------------------------------------------------------------------
# Contract name templates per customer
# ---------------------------------------------------------------------------
CONTRACT_TEMPLATES = {
    1: [  # Meta
        "RLHF Preference Ranking {period}",
        "Safety Annotation Program {period}",
        "Multilingual Data Collection {period}",
        "Prompt-Response Evaluation {period}",
        "Red Team Safety Testing {period}",
        "Content Moderation Labeling {period}",
        "Llama Training Data {period}",
        "Video Understanding Annotation {period}",
    ],
    2: [  # OpenAI
        "Alignment Research Support {period}",
        "Code Quality Assessment {period}",
        "RLHF Data Pipeline {period}",
        "Instruction Following Eval {period}",
        "Reasoning Benchmark Data {period}",
        "Safety & Helpfulness Rating {period}",
        "GPT Training Data {period}",
    ],
    3: [  # Google
        "Multimodal Evaluation {period}",
        "Medical Domain Expert Review {period}",
        "Legal Analysis & Annotation {period}",
        "Gemini Science Evaluation {period}",
        "Search Quality Rating {period}",
        "Code Generation Review {period}",
        "Bard Training Data {period}",
    ],
    4: [  # xAI
        "Foundation Model Training {period}",
        "Adversarial Testing Program {period}",
        "Code Intelligence Data {period}",
        "Grok Training Pipeline {period}",
        "Red Team & Security Testing {period}",
        "Conversational AI Data {period}",
    ],
    5: [  # Anthropic
        "Domain Expert Evaluation {period}",
        "Constitutional AI Training {period}",
        "Science & Reasoning Eval {period}",
        "Humanities Expert Review {period}",
        "Safety Boundary Testing {period}",
        "Claude Training Data {period}",
        "Harmlessness Evaluation {period}",
    ],
}

# ---------------------------------------------------------------------------
# Project name templates
# ---------------------------------------------------------------------------
PROJECT_EXTERNAL_TEMPLATES = {
    1: [  # Meta
        "Llama-RLHF-v{v}", "Llama-Safety-v{v}", "Llama-MultiLang-v{v}",
        "Meta-PromptEval-v{v}", "Meta-RedTeam-v{v}", "Meta-ContentMod-v{v}",
        "Llama-VideoAnnot-v{v}", "Meta-CodeReview-v{v}",
    ],
    2: [  # OpenAI
        "Helios-RLHF-pass{v}", "Helios-CodeReview-pass{v}", "Helios-Instruct-v{v}",
        "GPT-Reasoning-v{v}", "GPT-Safety-v{v}", "Helios-TextGen-v{v}",
        "OpenAI-BenchmarkData-v{v}",
    ],
    3: [  # Google
        "Gemini-MedEval-{yr}", "Gemini-LegalEval-{yr}", "Gemini-SciEval-{yr}",
        "Gemini-CodeGen-{yr}", "Gemini-SearchQuality-{yr}", "Gemini-MultiModal-{yr}",
        "Bard-DomainReview-{yr}",
    ],
    4: [  # xAI
        "Grok-SWE-Training-v{v}", "Grok-RedTeam-{yr}", "Grok-CodeIntel-v{v}",
        "Grok-ConvAI-v{v}", "Grok-Security-v{v}", "xAI-DataPipeline-v{v}",
    ],
    5: [  # Anthropic
        "Claude-SciEval-{yr}", "Claude-HumanitiesEval-{yr}", "Claude-SafetyBound-v{v}",
        "Claude-ConstitAI-v{v}", "Claude-ReasoningEval-{yr}", "Claude-DomainExpert-{yr}",
        "Claude-HarmlessEval-v{v}",
    ],
}

PROJECT_INTERNAL_TEMPLATES = [
    "Text Preference Ranking ({domain})",
    "Safety Labeling & Red Team",
    "Code Quality Review ({domain})",
    "Domain Expert Evaluation ({domain})",
    "Multilingual Data Collection",
    "Prompt-Response Evaluation ({domain})",
    "Adversarial Prompt Testing",
    "Instruction Following Evaluation",
    "Reasoning & Logic Assessment",
    "Content Moderation Labeling",
    "Medical Domain Evaluation",
    "Legal Domain Evaluation",
    "Science Domain Evaluation",
    "Humanities & Social Science Evaluation",
    "Search Quality Rating",
    "Code Generation Review ({domain})",
    "Video Understanding Annotation",
    "Constitutional AI Training Data",
    "Harmlessness Boundary Testing",
    "Multi-Modal Evaluation ({domain})",
]

# ---------------------------------------------------------------------------
# Domain → subdomain ID mapping (from migration 003)
# ---------------------------------------------------------------------------
DOMAIN_SUBDOMAIN_MAP = {
    1: list(range(1, 11)),      # Software Engineering: 1-10
    2: list(range(11, 22)),     # Other Engineering: 11-21
    3: list(range(22, 36)),     # Medicine: 22-35
    4: list(range(36, 52)),     # Law: 36-51
    5: list(range(52, 59)),     # Data Analysis: 52-58
    6: list(range(59, 72)),     # Finance: 59-71
    7: list(range(72, 80)),     # Business Operations: 72-79
    8: list(range(80, 95)),     # Life Sciences: 80-94
    9: list(range(95, 106)),    # Physical Sciences: 95-105
    10: list(range(106, 116)),  # Social Sciences: 106-115
    11: list(range(116, 129)),  # Arts & Design: 116-128
    12: list(range(129, 141)),  # Humanities: 129-140
    13: list(range(141, 146)),  # Miscellaneous: 141-145
}

# Reverse map: subdomain_id → domain_id
SUBDOMAIN_TO_DOMAIN = {}
for domain_id, sub_ids in DOMAIN_SUBDOMAIN_MAP.items():
    for sid in sub_ids:
        SUBDOMAIN_TO_DOMAIN[sid] = domain_id

ALL_SUBDOMAIN_IDS = list(range(1, 146))

# ---------------------------------------------------------------------------
# Removal reason templates for assignments
# ---------------------------------------------------------------------------
REMOVAL_REASONS = [
    "Not completing tasks on time",
    "Quality scores consistently below threshold",
    "Reassigned to higher-priority project",
    "Contract hours reduced",
    "Tasker requested reassignment",
    "Project scope change — domain mismatch",
    "Workload conflict with other project",
    "Performance review — insufficient output",
    "Availability dropped below minimum threshold",
    "Client requested different expertise mix",
    "End of contract period",
    "Budget reallocation",
    "Moved to new customer project for domain expertise",
    "Tasker on extended leave",
    "Team restructuring",
]

# ---------------------------------------------------------------------------
# Task title templates
# ---------------------------------------------------------------------------
SRT_TASK_TITLES = {
    "preference_ranking": [
        "Rank response pair for helpfulness",
        "Compare model outputs — factuality",
        "Preference ranking: safety vs helpfulness tradeoff",
        "Rate response quality pair",
        "Rank completions by coherence",
        "Evaluate response pair for instruction following",
        "Compare outputs for reasoning quality",
        "Rank model responses — code correctness",
    ],
    "safety_labeling": [
        "Label prompt for safety category",
        "Flag potentially harmful content",
        "Classify response safety level",
        "Evaluate content moderation edge case",
        "Label adversarial prompt attempt",
        "Safety classification — violence category",
        "Review flagged content for policy violation",
        "Categorize harmful output type",
    ],
    "prompt_response": [
        "Evaluate prompt-response quality",
        "Rate response helpfulness and accuracy",
        "Assess factual correctness of response",
        "Review model response for completeness",
        "Evaluate multi-turn conversation quality",
        "Score response for instruction adherence",
        "Assess creative writing response",
        "Rate technical response accuracy",
    ],
}

FEATHER_TASK_TITLES = {
    "rlhf_ranking": [
        "Rank these two responses",
        "Compare model outputs for quality",
        "Rate response pair — helpfulness",
        "Evaluate output preference",
        "Rank completions by quality",
        "Choose better response — accuracy",
        "Preference comparison task",
        "Rate model output pair",
    ],
    "code_review": [
        "Review code snippet for correctness",
        "Evaluate code quality and style",
        "Check implementation for bugs",
        "Review pull request changes",
        "Assess code optimization opportunities",
        "Verify algorithm correctness",
        "Review security implications of code",
        "Evaluate test coverage adequacy",
    ],
    "text_generation": [
        "Generate response for given prompt",
        "Write evaluation for model output",
        "Create reference answer",
        "Draft instructional response",
        "Generate creative text sample",
        "Write technical documentation response",
        "Create conversation continuation",
        "Draft factual response to query",
    ],
}

FAIRTABLE_TASK_TITLES = {
    "medical_evaluation": [
        "Evaluate medical diagnosis accuracy",
        "Review clinical reasoning response",
        "Assess pharmacology recommendation",
        "Verify medical terminology usage",
        "Review patient case analysis",
        "Evaluate treatment plan response",
        "Assess medical imaging interpretation",
        "Review cardiology assessment quality",
    ],
    "legal_evaluation": [
        "Evaluate legal analysis accuracy",
        "Review contract interpretation",
        "Assess constitutional law reasoning",
        "Verify legal citation accuracy",
        "Review criminal law case analysis",
        "Evaluate IP law response quality",
        "Assess regulatory compliance answer",
        "Review civil procedure response",
    ],
    "domain_qa": [
        "Answer domain expert question",
        "Evaluate technical accuracy",
        "Review specialized knowledge response",
        "Assess expert-level reasoning",
        "Verify domain-specific claims",
        "Review professional knowledge answer",
        "Evaluate cross-domain reasoning",
        "Assess depth of expertise in response",
    ],
    "science_evaluation": [
        "Evaluate scientific reasoning",
        "Review physics problem solution",
        "Assess biology concept explanation",
        "Verify chemistry calculation",
        "Review neuroscience research summary",
        "Evaluate genetics analysis",
        "Assess environmental science response",
        "Review materials science explanation",
    ],
    "humanities_evaluation": [
        "Evaluate historical analysis accuracy",
        "Review philosophical argument quality",
        "Assess literary criticism response",
        "Verify cultural context interpretation",
        "Review economic analysis reasoning",
        "Evaluate psychology assessment",
        "Assess sociological analysis quality",
        "Review ethical reasoning response",
    ],
    "code_generation": [
        "Generate solution for coding problem",
        "Write implementation for algorithm",
        "Create test cases for function",
        "Generate API endpoint implementation",
        "Write data pipeline code",
        "Create utility function implementation",
        "Generate database query solution",
        "Write system design implementation",
    ],
    "code_review": [
        "Review code implementation quality",
        "Assess algorithm efficiency",
        "Evaluate code architecture",
        "Review error handling completeness",
        "Check code style and conventions",
        "Verify security best practices",
        "Review API design quality",
        "Assess test coverage",
    ],
    "red_team": [
        "Test adversarial prompt resistance",
        "Evaluate jailbreak attempt response",
        "Assess safety boundary handling",
        "Test harmful content detection",
        "Evaluate manipulation resistance",
        "Review policy violation edge case",
        "Test social engineering resistance",
        "Assess bias detection capability",
    ],
}

# ---------------------------------------------------------------------------
# Review feedback / notes templates
# ---------------------------------------------------------------------------
REVIEW_NOTES_POSITIVE = [
    "Accurate and thorough evaluation",
    "Well-reasoned assessment",
    "Clear and comprehensive analysis",
    "Excellent attention to detail",
    "Strong domain expertise demonstrated",
    "Consistent with evaluation guidelines",
    "High-quality work product",
    None,  # sometimes no notes
    None,
]

REVIEW_NOTES_NEGATIVE = [
    "Missed key evaluation criteria",
    "Incomplete analysis — needs more depth",
    "Factual errors in assessment",
    "Did not follow rubric guidelines",
    "Insufficient justification provided",
    "Response quality below minimum threshold",
    "Needs additional training on this task type",
]

REVIEW_NOTES_NEUTRAL = [
    "Adequate evaluation — meets minimum standards",
    "Some areas could use more detail",
    "Generally acceptable with minor issues",
    "Meets expectations — room for improvement",
    None,
    None,
]

# ---------------------------------------------------------------------------
# Helper: get a DB connection
# ---------------------------------------------------------------------------
def get_connection(db_url: str):
    """Create a psycopg2 connection from a URL string."""
    import psycopg2
    return psycopg2.connect(db_url)


def month_key_to_date(year: int, month: int, day: int = 1) -> str:
    """Return 'YYYY-MM-DD' string."""
    return f"{year:04d}-{month:02d}-{day:02d}"


def random_datetime_in_month(rng: random.Random, year: int, month: int):
    """Return a random datetime within the given month as ISO string.
    Caps to today's date so no future-dated records are generated."""
    import calendar
    from datetime import date as _date
    max_day = calendar.monthrange(year, month)[1]
    today = _date.today()
    if year == today.year and month == today.month:
        max_day = today.day
    elif _date(year, month, 1) > today:
        # Entire month is in the future — clamp to today
        year, month, max_day = today.year, today.month, today.day
    day = rng.randint(1, max_day)
    hour = rng.randint(6, 22)  # working hours-ish
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}"


def generate_hex_id(rng: random.Random, length: int = 12) -> str:
    """Generate a random hex string of given length."""
    return ''.join(rng.choices('0123456789abcdef', k=length))
