#!/usr/bin/env python3
"""Generate SQL migration to backfill demographic fields for all taskers.

Reads tasker data from Neon via psql, generates realistic demographics
correlated with job title/domain, writes migrations/014_backfill_demographics.sql.
"""

import random
import subprocess
import datetime
import math

random.seed(42)

CONN_STR = "postgresql://neondb_owner:npg_H6ces9NyVEtw@ep-broad-haze-aifq29n7.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
TODAY = datetime.date(2025, 12, 1)  # snapshot date for age calculation

# ─── Name → Gender mapping ──────────────────────────────────────────────────

FEMALE_NAMES = {
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
    "Ashley", "Emily", "Donna", "Michelle", "Dorothy", "Carol", "Amanda", "Melissa",
    "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia", "Kathleen",
    "Amy", "Angela", "Shirley", "Anna", "Brenda", "Pamela", "Emma", "Nicole",
    "Helen", "Samantha", "Katherine", "Christine", "Debra", "Rachel", "Carolyn",
    "Hannah", "Olivia", "Abigail", "Madison", "Megan", "Grace", "Victoria",
    "Natalie", "Lily", "Sophia", "Chloe", "Zoe", "Audrey", "Claire", "Haley",
    "Riley", "Savannah", "Allison", "Morgan", "Kimberly", "Brooke", "Taylor",
    "Paige", "Mackenzie", "Jordan", "Casey", "Kelsey", "Courtney", "Jenna",
    # Hispanic
    "Maria", "Carmen", "Ana", "Lucia", "Sofia", "Valentina", "Isabella", "Gabriela",
    "Camila", "Mariana", "Daniela", "Fernanda", "Alejandra", "Catalina", "Natalia",
    "Ximena", "Lorena", "Adriana", "Paola", "Elena", "Rosa", "Claudia", "Monica",
    "Carolina", "Andrea", "Gloria", "Silvia", "Teresa", "Pilar", "Beatriz",
    # East Asian
    "Mei", "Xiu", "Lan", "Hua", "Jing", "Yue", "Ling", "Na", "Fang",
    "Yan", "Xin", "Rui", "Wen", "Qian", "Ying", "Dan", "Shan", "Yun", "Hong",
    "Yuki", "Sakura", "Aiko", "Hana", "Mio", "Rin", "Saki", "Mai", "Ayumi",
    "Soo-Jin", "Min-Ji", "Hye-Jin", "Ji-Yeon", "Eun-Ji", "Su-Bin", "Ye-Rin",
    # South Asian
    "Priya", "Ananya", "Kavita", "Sunita", "Deepa", "Neha", "Pooja", "Shreya",
    "Divya", "Meera", "Anjali", "Nandini", "Swati", "Aarti", "Rekha", "Sarita",
    "Ishita", "Aishwarya", "Tanvi", "Riya", "Nisha", "Aparna", "Pallavi", "Vidya",
    # African
    "Amina", "Fatima", "Aisha", "Zainab", "Ngozi", "Chidinma", "Adaeze",
    "Folake", "Binta", "Mariama", "Nneka", "Chiamaka", "Ifeoma",
    # European
    "Ingrid", "Astrid", "Freya", "Elsa", "Greta", "Helga",
    "Francoise", "Colette", "Amelie", "Celine", "Margaux",
    "Katarina", "Petra", "Monika", "Ewa", "Agnieszka",
    "Olga", "Natasha", "Svetlana", "Tatiana", "Irina",
    "Giulia", "Chiara", "Francesca", "Alessia", "Martina",
    "Layla", "Nour", "Dalia", "Rania", "Huda", "Maryam", "Yasmin", "Salma",
    "Sara", "Lina", "Farah", "Rana", "Hala",
    "Juliana", "Larissa", "Leticia", "Rafaela", "Bianca",
    "Luisa", "Vitoria", "Manuela", "Clara",
    # Russian
    "Ekaterina", "Anastasia", "Daria", "Yulia", "Ksenia", "Nadia",
    "Vera", "Polina", "Alina", "Lydia",
    # Extra
    "Eleanor", "Sophie", "Anika",
}

MALE_NAMES = {
    "James", "John", "Robert", "Michael", "David", "William", "Richard", "Joseph",
    "Thomas", "Daniel", "Matthew", "Anthony", "Mark", "Steven", "Paul", "Andrew",
    "Joshua", "Kenneth", "Kevin", "Brian", "George", "Timothy", "Ronald", "Edward",
    "Jason", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas", "Eric", "Jonathan",
    "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin", "Samuel", "Raymond",
    "Patrick", "Frank", "Nathan", "Dennis", "Jerry", "Alexander", "Tyler", "Henry",
    "Douglas", "Aaron", "Peter", "Zachary", "Adam", "Caleb", "Ethan", "Noah",
    "Logan", "Mason", "Owen", "Luke", "Dylan", "Connor", "Levi", "Isaac",
    "Hunter", "Wyatt", "Nolan", "Cameron", "Jared", "Gavin", "Marcus", "Trevor",
    "Grant", "Spencer", "Cole", "Austin", "Blake", "Chase", "Derek", "Dustin",
    # Hispanic
    "Carlos", "Miguel", "Luis", "Jorge", "Pedro", "Rafael", "Diego", "Alejandro",
    "Fernando", "Ricardo", "Sergio", "Javier", "Andres", "Pablo", "Mateo", "Santiago",
    "Emilio", "Rodrigo", "Hector", "Oscar", "Manuel", "Raul", "Victor", "Alberto",
    "Enrique", "Ignacio", "Ernesto", "Arturo", "Ivan", "Cesar",
    # East Asian
    "Wei", "Jun", "Hao", "Ming", "Tao", "Kai", "Yong", "Jian", "Liang", "Feng",
    "Zhi", "Bo", "Peng", "Chao", "Xiang", "Dong", "Guang", "Qiang", "Lei", "Bin",
    "Hiroshi", "Takeshi", "Kenji", "Yuto", "Haruto", "Ren", "Sota", "Kaito",
    "Riku", "Hayato", "Daiki", "Shota", "Kenta", "Akira", "Taro",
    "Sang-Hoon", "Min-Jun", "Ji-Hoon", "Hyun-Woo", "Seo-Jun", "Do-Yun",
    "Jae-Won", "Sung-Min", "Tae-Hyun", "Young-Ho",
    # South Asian
    "Rajesh", "Vikram", "Amit", "Arun", "Sanjay", "Deepak", "Ravi", "Suresh",
    "Nikhil", "Arjun", "Rohan", "Karthik", "Pranav", "Varun", "Ashwin", "Rahul",
    "Gaurav", "Manish", "Sachin", "Vishal", "Anand", "Aditya", "Vivek", "Harsh",
    "Siddharth", "Akash", "Dhruv", "Kunal", "Mohit", "Tarun",
    # African
    "Kwame", "Chukwu", "Olumide", "Babajide", "Adewale", "Emeka", "Obinna",
    "Chinonso", "Tunde", "Segun", "Musa", "Youssef", "Hassan",
    "Kofi", "Olusegun", "Chinedu", "Ifeanyi", "Nnamdi",
    # European
    "Klaus", "Friedrich", "Hans", "Wolfgang", "Stefan", "Pierre", "Laurent",
    "Jacques", "Francois", "Antoine", "Luca", "Marco", "Alessandro", "Matteo",
    "Giovanni", "Piotr", "Andrzej", "Marek", "Krzysztof", "Jakub",
    "Dmitri", "Alexei", "Sergei", "Nikolai",
    "Lars", "Anders", "Erik", "Olaf", "Sven", "Nils",
    "Ahmad", "Khalid", "Tariq", "Faisal", "Samir", "Nabil", "Rashid", "Zaid",
    "Ali", "Hamza", "Karim", "Bilal", "Yousef", "Waleed", "Majid",
    "Gustavo", "Henrique", "Felipe", "Thiago", "Caio", "Bruno", "Vinicius",
    "Leonardo", "Bernardo", "Arthur", "Davi",
    # Russian
    "Andrei", "Mikhail", "Vladimir", "Pavel", "Oleg", "Boris", "Yuri",
    "Viktor", "Konstantin", "Aleksandr", "Igor", "Grigori", "Maxim", "Artem", "Fedor",
    # Extra
    "Alex", "Tomasz", "Henrik", "Lucas",
}

# Names that appear in both or are ambiguous — resolved to most common usage
AMBIGUOUS_FEMALE = {"Li", "Rui", "Chen"}  # treated as female when standalone first name


def detect_gender(first_name):
    if first_name in FEMALE_NAMES:
        return "Female"
    if first_name in MALE_NAMES:
        return "Male"
    if first_name in AMBIGUOUS_FEMALE:
        return "Female"
    # Fallback: assume male (matches the 55/45 split)
    return "Male"


# ─── Job title → Domain mapping ─────────────────────────────────────────────

JOB_DOMAIN = {
    # SWE
    "Software Engineer": "swe", "Full Stack Engineer": "swe", "Frontend Developer": "swe",
    "Backend Engineer": "swe", "Security Engineer": "swe", "Platform Engineer": "swe",
    "Mobile Developer": "swe", "Database Engineer": "swe", "ML Engineer": "swe",
    "NLP Engineer": "swe", "Senior Software Engineer": "swe", "Senior Backend Engineer": "swe",
    "Full Stack Developer": "swe", "Staff Engineer": "swe", "DevSecOps Engineer": "swe",
    "AI/ML Full Stack Engineer": "swe", "Frontend & Mobile Developer": "swe",
    "Infrastructure Engineer": "swe", "Backend ML Engineer": "swe",
    "Application Security Engineer": "swe", "Staff Platform Engineer": "swe",
    "Cloud Data Engineer": "swe", "Senior Cloud Engineer": "swe",
    "Cloud Database Engineer": "swe", "Security & Compliance Engineer": "swe",
    "Financial Software Engineer": "swe", "ML Platform Engineer": "swe",
    "Fintech Data Engineer": "swe", "Frontend Design Engineer": "swe",
    "Game Developer": "swe", "AI Research Scientist": "swe",
    "Senior ML Engineer": "swe",
    # Engineering
    "Mechanical Engineer": "eng", "Electrical Engineer": "eng", "Civil Engineer": "eng",
    "Chemical Engineer": "eng", "Aerospace Engineer": "eng", "Biomedical Engineer": "eng",
    "Robotics Engineer": "eng", "Industrial Engineer": "eng", "Materials Engineer": "eng",
    "Environmental Engineer": "eng", "Design Engineer": "eng",
    # Medicine
    "Cardiologist": "med", "Neurologist": "med", "Oncologist": "med",
    "Radiologist": "med", "Surgeon": "med", "Pediatrician": "med",
    "Psychiatrist": "med", "Anesthesiologist": "med", "Epidemiologist": "med",
    "Pharmacologist": "med", "OB/GYN Physician": "med",
    "Medical Imaging Specialist": "med", "General Practitioner": "med",
    # Law
    "Attorney": "law", "Corporate Lawyer": "law", "Litigation Attorney": "law",
    "IP Attorney": "law", "International Law Attorney": "law",
    "Environmental Lawyer": "law", "Labor Attorney": "law", "Tax Attorney": "law",
    "Family Law Attorney": "law", "Immigration Attorney": "law",
    "Criminal Law Professor": "law", "Administrative Law Attorney": "law",
    "Tech Corporate Counsel": "law", "Human Rights & Immigration Lawyer": "law",
    # Data
    "Data Scientist": "data", "Predictive Analytics Specialist": "data",
    "ML Researcher": "data", "Data Engineer": "data", "Data Analyst": "data",
    "Senior Data Engineer": "data", "Analytics Engineer": "data",
    "Financial Data Scientist": "data", "Financial Data Engineer": "data",
    "Computational Scientist": "data", "Computational Genomics Researcher": "data",
    "Applied Mathematician": "data", "Mathematical Physicist": "data",
    # Finance
    "Financial Analyst": "fin", "Investment Banker": "fin", "Risk Analyst": "fin",
    "Quantitative Analyst": "fin", "Accountant": "fin", "Portfolio Manager": "fin",
    "Tax Consultant": "fin", "Actuarial Analyst": "fin", "Asset Manager": "fin",
    "Investment Banking Analyst": "fin", "Portfolio Quant": "fin",
    "Quantitative Developer": "fin",
    # Business Operations
    "Operations Manager": "biz", "Supply Chain Analyst": "biz",
    "HR Specialist": "biz", "Customer Support Manager": "biz",
    "Business Strategy Consultant": "biz", "COO": "biz",
    # Life Sciences
    "Molecular Biologist": "lifesci", "Geneticist": "lifesci",
    "Microbiologist": "lifesci", "Biochemist": "lifesci", "Immunologist": "lifesci",
    "Neuroscientist": "lifesci", "Ecologist": "lifesci",
    "Bioinformatics Scientist": "lifesci", "Biotechnologist": "lifesci",
    "Cell Biologist": "lifesci",
    # Physical Sciences
    "Physicist": "physci", "Astronomer": "physci", "Chemist": "physci",
    "Materials Chemist": "physci", "Geologist": "physci", "Meteorologist": "physci",
    "Oceanographer": "physci", "Acoustics Engineer": "physci",
    "Astrophysicist": "physci", "Theoretical Physicist": "physci",
    "Materials Scientist": "physci",
    # Social Sciences
    "Economist": "socsci", "Sociologist": "socsci", "Psychologist": "socsci",
    "Anthropologist": "socsci", "Political Scientist": "socsci",
    "Public Policy Analyst": "socsci", "Criminologist": "socsci",
    "Geographer": "socsci",
    # Arts & Design
    "Visual Artist": "arts", "UX/UI Designer": "arts", "Industrial Designer": "arts",
    "Architect": "arts", "Illustrator": "arts", "Photographer": "arts",
    "Game Designer": "arts", "Fashion Designer": "arts", "Creative Director": "arts",
    "Senior Product Designer": "arts", "Animation & Game Artist": "arts",
    "Mobile UX Designer": "arts", "Visual & Graphic Designer": "arts",
    "Industrial Design Architect": "arts", "Creative Photographer": "arts",
    "UX Designer": "arts",
    # Humanities
    "Philosophy Professor": "hum", "Historian": "hum", "Literature Professor": "hum",
    "Religious Studies Scholar": "hum", "Classics Professor": "hum",
    "Cultural Studies Researcher": "hum", "Archaeologist": "hum",
    "Art Historian": "hum", "Area Studies Researcher": "hum",
    "Humanities Researcher": "hum", "Ethics Professor": "hum",
    "European History Scholar": "hum", "History Professor": "hum",
    # Misc
    "Educator": "misc", "Communications Specialist": "misc", "Librarian": "misc",
    "Artisan": "misc",
}


# ─── Age distributions by domain ────────────────────────────────────────────
# (min_age, peak_age, max_age) — we'll use a skewed normal distribution

AGE_PARAMS = {
    "swe":     (22, 31, 52),
    "eng":     (24, 34, 58),
    "med":     (28, 42, 68),
    "law":     (26, 38, 65),
    "data":    (23, 30, 50),
    "fin":     (24, 34, 58),
    "biz":     (25, 38, 60),
    "lifesci": (24, 35, 62),
    "physci":  (24, 36, 65),
    "socsci":  (26, 38, 62),
    "arts":    (22, 32, 55),
    "hum":     (26, 42, 68),
    "misc":    (22, 35, 60),
}


def generate_age(domain):
    min_age, peak, max_age = AGE_PARAMS.get(domain, (22, 35, 60))
    # Use a beta distribution shaped around the peak
    # Map peak to alpha/beta params
    mean_norm = (peak - min_age) / (max_age - min_age)
    # Concentration parameter — higher = tighter distribution
    kappa = 8
    alpha = mean_norm * kappa
    beta_p = (1 - mean_norm) * kappa
    age = min_age + random.betavariate(max(alpha, 1.01), max(beta_p, 1.01)) * (max_age - min_age)
    return max(18, min(max_age, round(age)))


def generate_dob(age):
    """Generate a DOB that results in the given age as of TODAY."""
    birth_year = TODAY.year - age
    month = random.randint(1, 12)
    max_day = 28 if month == 2 else (30 if month in (4, 6, 9, 11) else 31)
    day = random.randint(1, max_day)
    return datetime.date(birth_year, month, day)


# ─── Education distributions by domain ──────────────────────────────────────
# (level, cumulative_probability)

EDUCATION_DIST = {
    "swe":     [("High School", 0.03), ("Associate", 0.05), ("Bachelor's", 0.62), ("Master's", 0.90), ("PhD", 1.0)],
    "eng":     [("Associate", 0.02), ("Bachelor's", 0.52), ("Master's", 0.90), ("PhD", 1.0)],
    "med":     [("MD", 1.0)],
    "law":     [("JD", 1.0)],
    "data":    [("Bachelor's", 0.35), ("Master's", 0.75), ("PhD", 1.0)],
    "fin":     [("Bachelor's", 0.45), ("Master's", 0.88), ("PhD", 0.95), ("CFA", 1.0)],
    "biz":     [("High School", 0.05), ("Associate", 0.10), ("Bachelor's", 0.55), ("Master's", 0.92), ("PhD", 1.0)],
    "lifesci": [("Bachelor's", 0.18), ("Master's", 0.48), ("PhD", 1.0)],
    "physci":  [("Bachelor's", 0.15), ("Master's", 0.42), ("PhD", 1.0)],
    "socsci":  [("Bachelor's", 0.22), ("Master's", 0.55), ("PhD", 1.0)],
    "arts":    [("High School", 0.10), ("Associate", 0.15), ("Bachelor's", 0.60), ("Master's", 0.90), ("MFA", 0.95), ("PhD", 1.0)],
    "hum":     [("Bachelor's", 0.18), ("Master's", 0.45), ("PhD", 1.0)],
    "misc":    [("High School", 0.25), ("Associate", 0.35), ("Bachelor's", 0.72), ("Master's", 0.92), ("PhD", 1.0)],
}


def generate_education(domain):
    dist = EDUCATION_DIST.get(domain, EDUCATION_DIST["misc"])
    r = random.random()
    for level, cum_prob in dist:
        if r <= cum_prob:
            return level
    return dist[-1][0]


# ─── Student probability by age ──────────────────────────────────────────────

def generate_is_student(age, education):
    # PhD/MD/JD students tend to be a bit older
    if education in ("PhD", "MD", "JD", "MFA"):
        if age <= 32:
            return random.random() < 0.12
        elif age <= 38:
            return random.random() < 0.04
        else:
            return random.random() < 0.01
    # Everyone else
    if age <= 22:
        return random.random() < 0.45
    elif age <= 25:
        return random.random() < 0.20
    elif age <= 30:
        return random.random() < 0.08
    elif age <= 40:
        return random.random() < 0.03
    else:
        return random.random() < 0.01


# ─── Employment status ──────────────────────────────────────────────────────

def generate_employment_status(is_student, age, domain):
    if is_student:
        r = random.random()
        if r < 0.45:
            return "Student"
        elif r < 0.75:
            return "Part-time"
        else:
            return "Employed"

    r = random.random()
    if domain in ("swe", "data", "eng"):
        # Tech workers — high employment, some freelance
        if r < 0.60:
            return "Employed"
        elif r < 0.75:
            return "Self-employed"
        elif r < 0.90:
            return "Freelance"
        elif r < 0.95:
            return "Part-time"
        else:
            return "Unemployed"
    elif domain in ("med", "law"):
        # Professionals — very high employment
        if r < 0.72:
            return "Employed"
        elif r < 0.88:
            return "Self-employed"
        elif r < 0.95:
            return "Part-time"
        else:
            return "Freelance"
    elif domain in ("arts", "hum", "misc"):
        # Creative/humanities — more freelance
        if r < 0.40:
            return "Employed"
        elif r < 0.55:
            return "Self-employed"
        elif r < 0.75:
            return "Freelance"
        elif r < 0.88:
            return "Part-time"
        else:
            return "Unemployed"
    else:
        # Default
        if r < 0.55:
            return "Employed"
        elif r < 0.70:
            return "Self-employed"
        elif r < 0.82:
            return "Freelance"
        elif r < 0.92:
            return "Part-time"
        else:
            return "Unemployed"


# ─── Company pools by domain ────────────────────────────────────────────────

COMPANIES = {
    "swe": [
        # FAANG+
        "Google", "Google", "Meta", "Meta", "Amazon", "Amazon", "Microsoft", "Microsoft",
        "Apple", "Apple", "Netflix",
        # AI
        "OpenAI", "Anthropic", "DeepMind", "Cohere", "Mistral AI", "Databricks",
        "Scale AI", "Hugging Face", "Stability AI",
        # Cloud/Infra
        "Snowflake", "Cloudflare", "HashiCorp", "Vercel", "Confluent", "Elastic",
        "MongoDB", "CrowdStrike", "Palo Alto Networks", "Datadog",
        # Fintech
        "Stripe", "Square", "Plaid", "Robinhood", "Coinbase", "Brex",
        # Consumer
        "Uber", "Airbnb", "DoorDash", "Instacart", "Spotify", "Pinterest",
        "Snap", "Reddit", "Discord", "Figma",
        # Enterprise
        "Salesforce", "ServiceNow", "Workday", "Palantir", "Atlassian",
        "Twilio", "Okta", "HubSpot", "Splunk",
        # Startups / other
        "Notion", "Linear", "Retool", "Supabase", "Rippling", "Ramp",
        "Anduril", "SpaceX", "Tesla", "Rivian",
        # India tech
        "Infosys", "TCS", "Wipro", "HCL Technologies", "Tech Mahindra",
        "Flipkart", "Razorpay", "Freshworks", "Zoho", "Ola",
        # China tech
        "Alibaba", "Tencent", "ByteDance", "Baidu", "Huawei",
        "Xiaomi", "JD.com", "Meituan", "Didi", "SenseTime",
    ],
    "eng": [
        "Boeing", "Lockheed Martin", "Northrop Grumman", "Raytheon Technologies",
        "SpaceX", "Blue Origin", "Airbus", "BAE Systems",
        "Tesla", "Ford", "General Motors", "Toyota", "BMW", "Rivian", "Lucid Motors",
        "Siemens", "GE Aerospace", "Honeywell", "3M", "Caterpillar", "John Deere",
        "ExxonMobil", "Chevron", "Shell", "BP", "NextEra Energy",
        "AECOM", "Jacobs Engineering", "Bechtel", "Fluor Corporation",
        "Medtronic", "Boston Scientific", "Stryker", "Abbott Laboratories",
        "Intel", "AMD", "NVIDIA", "Qualcomm", "Texas Instruments",
        "Bosch", "ABB", "Schneider Electric", "Emerson Electric",
    ],
    "med": [
        "Johns Hopkins Hospital", "Mayo Clinic", "Cleveland Clinic",
        "Massachusetts General Hospital", "Stanford Health Care",
        "UCLA Health", "Mount Sinai Health System", "NYU Langone Health",
        "Northwestern Memorial Hospital", "Cedars-Sinai Medical Center",
        "Kaiser Permanente", "HCA Healthcare", "CommonSpirit Health",
        "Ascension Health", "Providence Health",
        "Pfizer", "Johnson & Johnson", "Merck", "AbbVie", "Eli Lilly",
        "Bristol-Myers Squibb", "Amgen", "Gilead Sciences", "Regeneron",
        "Novartis", "Roche", "AstraZeneca", "Sanofi", "GSK",
        "UnitedHealth Group", "Cigna", "Anthem", "Humana",
        "NHS", "Charite Berlin", "University Hospital Zurich",
        "Apollo Hospitals", "Fortis Healthcare", "Max Healthcare",
        "Hospital Israelita Albert Einstein", "Hospital Sirio-Libanes",
    ],
    "law": [
        "Kirkland & Ellis", "Latham & Watkins", "DLA Piper",
        "Baker McKenzie", "Skadden Arps", "Sullivan & Cromwell",
        "White & Case", "Jones Day", "Hogan Lovells",
        "Clifford Chance", "Allen & Overy", "Freshfields",
        "Linklaters", "Norton Rose Fulbright", "Dentons",
        "Gibson Dunn", "Weil Gotshal", "Sidley Austin",
        "Cleary Gottlieb", "Davis Polk", "Simpson Thacher",
        "Cravath Swaine & Moore", "Covington & Burling",
        "WilmerHale", "Morrison & Foerster",
        "Department of Justice", "Federal Trade Commission",
        "American Civil Liberties Union",
    ],
    "data": [
        "Google", "Meta", "Amazon", "Microsoft", "Apple", "Netflix",
        "Databricks", "Snowflake", "Palantir", "Datadog", "Splunk",
        "Uber", "Airbnb", "Stripe", "DoorDash", "Instacart",
        "McKinsey", "BCG", "Bain & Company", "Deloitte",
        "Two Sigma", "Citadel", "D.E. Shaw", "Renaissance Technologies",
        "OpenAI", "Anthropic", "DeepMind",
        "IBM Research", "Microsoft Research", "Google DeepMind",
        "MIT", "Stanford University", "Carnegie Mellon University",
        "UC Berkeley", "Harvard University",
    ],
    "fin": [
        "Goldman Sachs", "JPMorgan Chase", "Morgan Stanley",
        "Bank of America", "Citigroup", "Wells Fargo",
        "Barclays", "Deutsche Bank", "UBS", "Credit Suisse", "HSBC",
        "BlackRock", "Vanguard", "Fidelity Investments", "State Street",
        "PIMCO", "T. Rowe Price", "Charles Schwab",
        "Citadel", "Two Sigma", "Bridgewater Associates",
        "Renaissance Technologies", "D.E. Shaw", "Point72",
        "KKR", "Blackstone", "Carlyle Group", "Apollo Global",
        "Sequoia Capital", "Andreessen Horowitz",
        "AIG", "MetLife", "Prudential", "Allstate",
        "Deloitte", "PwC", "EY", "KPMG",
    ],
    "biz": [
        "McKinsey & Company", "BCG", "Bain & Company",
        "Deloitte", "Accenture", "PwC", "EY", "KPMG",
        "Amazon", "Walmart", "Target", "Costco",
        "Procter & Gamble", "Unilever", "Johnson & Johnson",
        "FedEx", "UPS", "DHL",
        "Salesforce", "HubSpot", "ServiceNow",
        "General Electric", "Siemens", "Honeywell",
        "IBM", "Oracle", "SAP",
    ],
    "lifesci": [
        "Genentech", "Amgen", "Gilead Sciences", "Biogen", "Moderna",
        "Regeneron", "Vertex Pharmaceuticals", "Illumina",
        "Novartis", "Roche", "AstraZeneca", "Sanofi", "GSK",
        "Pfizer", "Merck", "Bristol-Myers Squibb",
        "23andMe", "Grail", "Tempus", "Recursion Pharmaceuticals",
        "MIT", "Harvard University", "Stanford University",
        "UC San Francisco", "Caltech", "Johns Hopkins University",
        "NIH", "CDC", "Broad Institute", "Salk Institute",
        "Max Planck Institute", "Pasteur Institute",
    ],
    "physci": [
        "NASA", "NOAA", "Los Alamos National Laboratory",
        "Sandia National Laboratories", "Oak Ridge National Laboratory",
        "Brookhaven National Laboratory", "Fermilab", "CERN",
        "MIT", "Stanford University", "Caltech",
        "Princeton University", "Harvard University", "UC Berkeley",
        "University of Cambridge", "University of Oxford",
        "Max Planck Institute", "ETH Zurich",
        "BASF", "Dow Chemical", "DuPont", "3M",
        "Shell", "ExxonMobil", "Chevron",
        "USGS", "EPA",
        "Chinese Academy of Sciences", "Russian Academy of Sciences",
    ],
    "socsci": [
        "Harvard University", "Stanford University", "MIT",
        "Yale University", "Princeton University", "Columbia University",
        "University of Chicago", "UC Berkeley", "University of Michigan",
        "London School of Economics", "University of Oxford",
        "World Bank", "International Monetary Fund", "United Nations",
        "RAND Corporation", "Brookings Institution",
        "McKinsey Global Institute", "Gallup",
        "Federal Reserve", "Bureau of Labor Statistics",
    ],
    "arts": [
        "Google", "Apple", "Meta", "Microsoft", "Airbnb",
        "IDEO", "Frog Design", "Pentagram", "R/GA",
        "Nike", "Adidas", "LVMH", "Gucci", "Prada",
        "Pixar", "DreamWorks", "Walt Disney Animation",
        "EA", "Activision Blizzard", "Riot Games", "Epic Games",
        "Nintendo", "Ubisoft", "Valve",
        "Getty Images", "Shutterstock", "Adobe",
        "Gensler", "Foster + Partners", "Zaha Hadid Architects",
        "Spotify", "Netflix",
    ],
    "hum": [
        "Harvard University", "Yale University", "Princeton University",
        "Stanford University", "Columbia University", "MIT",
        "University of Oxford", "University of Cambridge",
        "Sorbonne University", "Humboldt University of Berlin",
        "University of Tokyo", "Peking University",
        "Smithsonian Institution", "The Metropolitan Museum of Art",
        "British Museum", "Louvre Museum", "MoMA",
        "New York Times", "Washington Post", "The Guardian",
        "Penguin Random House", "HarperCollins",
        "National Geographic", "BBC",
    ],
    "misc": [
        "Google", "Amazon", "Microsoft",
        "New York Public Library", "Library of Congress",
        "Teach for America", "Khan Academy", "Coursera",
        "Pearson", "McGraw-Hill", "Scholastic",
        "YMCA", "Red Cross", "Habitat for Humanity",
        "Walmart", "Target", "Starbucks",
        "Local School District", "Community College",
        "State University", "Public Library System",
    ],
}


def generate_company(employment_status, domain):
    if employment_status in ("Self-employed", "Freelance", "Unemployed", "Student"):
        return None
    pool = COMPANIES.get(domain, COMPANIES["misc"])
    return random.choice(pool)


# ─── SQL helpers ─────────────────────────────────────────────────────────────

def sql_str(s):
    if s is None:
        return "NULL"
    return "'" + s.replace("'", "''") + "'"


def sql_bool(b):
    return "true" if b else "false"


# ─── Main ────────────────────────────────────────────────────────────────────

def fetch_taskers():
    """Fetch all tasker IDs, first names, and job titles from Neon."""
    result = subprocess.run(
        ["psql", CONN_STR, "-t", "-A", "-F", "|",
         "-c", "SELECT id, first_name, external_job_title FROM taskers ORDER BY id"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"psql failed: {result.stderr}")

    rows = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) >= 3:
            tid = int(parts[0])
            first_name = parts[1]
            job_title = parts[2] if parts[2] else None
            rows.append((tid, first_name, job_title))
    return rows


def main():
    print("Fetching taskers from Neon...")
    taskers = fetch_taskers()
    print(f"  Found {len(taskers)} taskers")

    print("Generating demographics...")
    updates = []
    stats = {"gender": {}, "education": {}, "employment": {}, "student": 0, "age_sum": 0}

    for tid, first_name, job_title in taskers:
        domain = JOB_DOMAIN.get(job_title, "misc")
        gender = detect_gender(first_name)
        age = generate_age(domain)
        dob = generate_dob(age)
        education = generate_education(domain)
        is_student = generate_is_student(age, education)
        employment = generate_employment_status(is_student, age, domain)
        company = generate_company(employment, domain)

        updates.append((tid, dob, age, gender, education, is_student, employment, company))

        # Stats
        stats["gender"][gender] = stats["gender"].get(gender, 0) + 1
        stats["education"][education] = stats["education"].get(education, 0) + 1
        stats["employment"][employment] = stats["employment"].get(employment, 0) + 1
        if is_student:
            stats["student"] += 1
        stats["age_sum"] += age

    print("Writing migration...")

    lines = [
        "-- Auto-generated: backfill demographic fields for all taskers",
        f"-- Generated for {len(updates)} taskers",
        "",
    ]

    # Write in batches using UPDATE ... FROM VALUES
    batch_size = 500
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i + batch_size]
        lines.append(f"-- Batch {i // batch_size + 1}")
        lines.append("UPDATE taskers AS t SET")
        lines.append("  date_of_birth = v.dob::date,")
        lines.append("  age = v.age,")
        lines.append("  gender = v.gender,")
        lines.append("  highest_education_level = v.education,")
        lines.append("  is_student = v.is_student,")
        lines.append("  employment_status = v.employment,")
        lines.append("  company = v.company")
        lines.append("FROM (VALUES")

        for j, (tid, dob, age, gender, education, is_student, employment, company) in enumerate(batch):
            comma = "," if j < len(batch) - 1 else ""
            row = f"  ({tid}, {sql_str(dob.isoformat())}, {age}, {sql_str(gender)}, {sql_str(education)}, {sql_bool(is_student)}, {sql_str(employment)}, {sql_str(company)}){comma}"
            lines.append(row)

        lines.append(") AS v(id, dob, age, gender, education, is_student, employment, company)")
        lines.append("WHERE t.id = v.id;")
        lines.append("")

    outfile = "migrations/014_backfill_demographics.sql"
    with open(outfile, "w") as f:
        f.write("\n".join(lines) + "\n")

    # Print stats
    n = len(updates)
    avg_age = stats["age_sum"] / n
    print(f"\nGenerated {n} updates → {outfile}")
    print(f"\nAge: avg={avg_age:.1f}")
    print(f"Students: {stats['student']} ({100 * stats['student'] / n:.1f}%)")
    print(f"\nGender:")
    for g, count in sorted(stats["gender"].items()):
        print(f"  {g}: {count} ({100 * count / n:.1f}%)")
    print(f"\nEducation:")
    for e, count in sorted(stats["education"].items(), key=lambda x: -x[1]):
        print(f"  {e}: {count} ({100 * count / n:.1f}%)")
    print(f"\nEmployment:")
    for e, count in sorted(stats["employment"].items(), key=lambda x: -x[1]):
        print(f"  {e}: {count} ({100 * count / n:.1f}%)")


if __name__ == "__main__":
    main()
