#!/usr/bin/env python3
"""Generate 10 intentional demographic clusters of taskers for demo queries.

Clusters:
1. Bay Area AI/ML Corridor (~120)
2. NYC Finance-Tech Crossover (~80)
3. Boston/Cambridge Life Sciences Belt (~70)
4. India Engineering Powerhouse (~150)
5. Seattle Security & Cloud Cluster (~80)
6. Multilingual Legal Hub — DC/NYC/London (~60)
7. China/Russia Non-English STEM (~80)
8. Latin America Spanish-Speaking Medical (~50)
9. European Humanities Cluster (~50)
10. Austin/Denver Creative-Tech Hybrid (~60)

Total: ~800 new taskers starting at ID 3533.
"""

import random
import json
import datetime

random.seed(2024)

# ─── Shared helpers ───────────────────────────────────────────────────────────

MIDDLE_NAMES_FULL = [
    "Alexander", "Andrew", "Anthony", "Benjamin", "Blake", "Bradley", "Brian",
    "Charles", "Christopher", "Daniel", "Edward", "Francis", "Grant", "Harrison",
    "Henry", "Howard", "Isaac", "Jackson", "James", "John", "Joseph", "Kenneth",
    "Lawrence", "Lee", "Louis", "Marcus", "Michael", "Nathan", "Oliver", "Patrick",
    "Paul", "Philip", "Raymond", "Robert", "Samuel", "Scott", "Thomas", "Vincent",
    "Walter", "Wayne", "Wesley",
    "Anne", "Beth", "Catherine", "Claire", "Dawn", "Diane", "Eleanor", "Faith",
    "Grace", "Hope", "Irene", "Jane", "Jean", "Joy", "June", "Kate", "Kay",
    "Lauren", "Louise", "Lynn", "Mae", "Marie", "Nicole", "Paige", "Quinn",
    "Renee", "Rose", "Ruth", "Sue", "Victoria",
]
MIDDLE_INITIALS = list("ABCDEFGHJKLMNPRSTW")

STREET_NAMES = [
    "Main St", "Oak Ave", "Park Blvd", "Elm St", "Cedar Ln", "Maple Dr",
    "Pine St", "Walnut Ave", "Market St", "Church St", "Broadway",
    "Washington Ave", "Lake Dr", "Highland Ave", "Sunset Blvd",
    "River Rd", "College Ave", "Mill St", "Spring St", "Union St",
    "1st Ave", "2nd Ave", "3rd St", "4th St", "5th Ave",
    "Ridge Rd", "Vine St", "Chestnut St", "Poplar Ave", "Birch Ln",
]

EMAIL_DOMAINS = ["gmail.com"] * 4 + ["outlook.com"] * 2 + ["yahoo.com", "protonmail.com", "icloud.com", "hotmail.com"]

INTERNAL_ROLES = ["{tasker}"] * 6 + ["{tasker,reviewer}"] * 2 + ["{reviewer}", "{tasker,team_lead}", None]

used_emails = set()
next_id = 3533


def sql_str(s):
    if s is None:
        return "NULL"
    return "'" + s.replace("'", "''") + "'"

def sql_arr(arr):
    if arr is None:
        return "NULL"
    return "'{" + ",".join(str(x) for x in arr) + "}'"

def sql_text_arr(arr):
    if arr is None:
        return "NULL"
    inner = ",".join(f'"{x}"' for x in arr)
    return "'{" + inner + "}'"

def make_email(first, last):
    global used_emails
    fc = first.lower().replace('-', '').replace("'", '')
    lc = last.lower().replace('-', '').replace(' ', '').replace("'", '')
    email = f"{fc}.{lc}@{random.choice(EMAIL_DOMAINS)}"
    suffix = 2
    while email in used_emails:
        email = f"{fc}.{lc}{suffix}@{random.choice(EMAIL_DOMAINS)}"
        suffix += 1
    used_emails.add(email)
    return email

def make_middle(prob=0.55):
    if random.random() < prob:
        return random.choice(MIDDLE_INITIALS) if random.random() < 0.4 else random.choice(MIDDLE_NAMES_FULL)
    return None

def make_hire():
    return (datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 1035))).isoformat()

def make_addr():
    a1 = f"{random.randint(1, 9999)} {random.choice(STREET_NAMES)}"
    a2 = f"Apt {random.randint(1, 200)}" if random.random() < 0.3 else None
    return a1, a2

def make_tasker(first, last, loc, job_title, subdomain_ids, languages, lang_prof, rate_range=(35, 85), hours_choices=None, status="active"):
    global next_id
    tid = next_id
    next_id += 1

    middle = make_middle()
    email = make_email(first, last)
    city, state, postal, country, tz = loc
    a1, a2 = make_addr()
    hire = make_hire()
    hours = random.choice(hours_choices or [15.0, 20.0, 25.0, 30.0, 35.0, 40.0]) if status == "active" else 0.0
    rate = round(random.uniform(*rate_range), 2)
    roles = random.choice(INTERNAL_ROLES)

    return (tid, first, middle, last, email, hire, a1, a2, city, state, postal,
            country, tz, status, job_title, subdomain_ids, hours, rate,
            languages, lang_prof, roles)

def format_row(t):
    (tid, first, middle, last, email, hire, a1, a2, city, state, postal,
     country, tz, status, job_title, subs, hours, rate, langs, prof, roles) = t
    parts = [
        str(tid), sql_str(first), sql_str(middle), sql_str(last), sql_str(email),
        sql_str(hire), sql_str(a1), sql_str(a2), sql_str(city), sql_str(state),
        sql_str(postal), sql_str(country), sql_str(tz), sql_str(status),
        sql_str(job_title), sql_arr(subs), str(hours), str(rate),
        sql_text_arr(langs), sql_str(json.dumps(prof)),
        sql_str(roles) if roles else "NULL",
    ]
    return "(" + ", ".join(parts) + ")"


# ─── Name pools per region ───────────────────────────────────────────────────

NAMES_AMERICAN_M = [
    "James", "John", "Robert", "Michael", "David", "William", "Richard", "Joseph",
    "Thomas", "Daniel", "Matthew", "Anthony", "Mark", "Steven", "Paul", "Andrew",
    "Joshua", "Kenneth", "Kevin", "Brian", "George", "Timothy", "Edward", "Jason",
    "Jeffrey", "Ryan", "Jacob", "Nicholas", "Eric", "Jonathan", "Stephen", "Justin",
    "Scott", "Brandon", "Benjamin", "Samuel", "Raymond", "Patrick", "Nathan", "Tyler",
    "Henry", "Alexander", "Ethan", "Noah", "Logan", "Mason", "Owen", "Luke", "Dylan",
    "Connor", "Levi", "Isaac", "Hunter", "Wyatt", "Nolan", "Cameron", "Marcus",
    "Trevor", "Grant", "Spencer", "Cole", "Austin", "Blake", "Chase", "Derek",
    "Aaron", "Peter", "Zachary", "Adam", "Caleb", "Gavin", "Jared", "Dustin",
]
NAMES_AMERICAN_F = [
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Susan", "Jessica",
    "Sarah", "Karen", "Lisa", "Nancy", "Margaret", "Sandra", "Ashley", "Emily",
    "Michelle", "Amanda", "Melissa", "Stephanie", "Rebecca", "Laura", "Kathleen",
    "Amy", "Angela", "Anna", "Pamela", "Emma", "Nicole", "Helen", "Samantha",
    "Katherine", "Christine", "Rachel", "Hannah", "Olivia", "Abigail", "Madison",
    "Megan", "Grace", "Victoria", "Natalie", "Lily", "Sophia", "Chloe", "Zoe",
    "Audrey", "Claire", "Haley", "Riley", "Savannah", "Allison", "Morgan",
    "Kimberly", "Brooke", "Taylor", "Paige", "Mackenzie", "Jordan", "Kelsey",
]
NAMES_CHINESE_M = ["Wei", "Jun", "Hao", "Ming", "Tao", "Kai", "Yong", "Jian", "Liang", "Feng",
                    "Zhi", "Bo", "Peng", "Chao", "Xiang", "Dong", "Guang", "Qiang", "Lei", "Bin"]
NAMES_CHINESE_F = ["Mei", "Xiu", "Lan", "Hua", "Jing", "Yue", "Ling", "Na", "Fang", "Li",
                    "Yan", "Xin", "Rui", "Wen", "Qian", "Ying", "Dan", "Shan", "Yun", "Hong"]
NAMES_CHINESE_L = ["Wang", "Li", "Zhang", "Liu", "Chen", "Yang", "Huang", "Zhao", "Wu", "Zhou",
                    "Xu", "Sun", "Ma", "Zhu", "Guo", "Lin", "He", "Luo", "Tang", "Xie"]

NAMES_INDIAN_M = ["Rajesh", "Vikram", "Amit", "Arun", "Sanjay", "Deepak", "Ravi", "Suresh",
                   "Nikhil", "Arjun", "Rohan", "Karthik", "Pranav", "Varun", "Ashwin", "Rahul",
                   "Gaurav", "Manish", "Sachin", "Vishal", "Anand", "Aditya", "Vivek", "Harsh",
                   "Siddharth", "Akash", "Dhruv", "Kunal", "Mohit", "Tarun"]
NAMES_INDIAN_F = ["Priya", "Ananya", "Kavita", "Sunita", "Deepa", "Neha", "Pooja", "Shreya",
                   "Divya", "Meera", "Anjali", "Nandini", "Swati", "Aarti", "Rekha", "Sarita",
                   "Ishita", "Aishwarya", "Tanvi", "Riya", "Nisha", "Aparna", "Pallavi", "Vidya"]
NAMES_INDIAN_L = ["Patel", "Sharma", "Singh", "Kumar", "Gupta", "Mehta", "Shah", "Joshi",
                   "Reddy", "Nair", "Rao", "Das", "Mishra", "Agarwal", "Bhat", "Pillai",
                   "Chandra", "Iyer", "Menon", "Verma", "Kapoor", "Malhotra", "Chopra",
                   "Banerjee", "Desai", "Thakur", "Pandey", "Srivastava", "Saxena", "Bose"]

NAMES_RUSSIAN_M = ["Dmitri", "Alexei", "Sergei", "Nikolai", "Ivan", "Andrei", "Mikhail",
                    "Vladimir", "Pavel", "Oleg", "Boris", "Yuri", "Viktor", "Konstantin",
                    "Aleksandr", "Igor", "Grigori", "Maxim", "Artem", "Fedor"]
NAMES_RUSSIAN_F = ["Olga", "Natasha", "Svetlana", "Tatiana", "Irina", "Elena", "Ekaterina",
                    "Anastasia", "Maria", "Anna", "Daria", "Yulia", "Ksenia", "Nadia",
                    "Vera", "Polina", "Alina", "Valentina", "Sofia", "Lydia"]
NAMES_RUSSIAN_L = ["Petrov", "Ivanov", "Volkov", "Sokolov", "Popov", "Kuznetsov", "Morozov",
                    "Novikov", "Kozlov", "Lebedev", "Smirnov", "Fedorov", "Orlov", "Egorov",
                    "Vasiliev", "Zaitsev", "Pavlov", "Nikitin", "Romanov", "Bogdanov"]

NAMES_HISPANIC_M = ["Carlos", "Miguel", "Luis", "Jorge", "Pedro", "Rafael", "Diego", "Alejandro",
                     "Fernando", "Ricardo", "Sergio", "Javier", "Andres", "Pablo", "Mateo",
                     "Santiago", "Emilio", "Rodrigo", "Hector", "Oscar", "Manuel", "Raul",
                     "Victor", "Alberto", "Enrique"]
NAMES_HISPANIC_F = ["Maria", "Carmen", "Ana", "Lucia", "Sofia", "Valentina", "Isabella",
                     "Gabriela", "Camila", "Mariana", "Daniela", "Fernanda", "Alejandra",
                     "Catalina", "Natalia", "Ximena", "Lorena", "Adriana", "Paola", "Elena",
                     "Rosa", "Claudia", "Monica", "Carolina", "Andrea"]
NAMES_HISPANIC_L = ["Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
                     "Sanchez", "Ramirez", "Torres", "Flores", "Rivera", "Gomez", "Diaz",
                     "Reyes", "Morales", "Ortiz", "Gutierrez", "Rojas", "Vargas", "Castillo",
                     "Jimenez", "Herrera", "Medina", "Aguilar", "Mendez"]

NAMES_EUROPEAN_M = ["Klaus", "Friedrich", "Hans", "Stefan", "Pierre", "Laurent", "Jacques",
                     "Francois", "Antoine", "Luca", "Marco", "Alessandro", "Matteo", "Giovanni",
                     "Piotr", "Lars", "Anders", "Erik", "Sven", "Nils"]
NAMES_EUROPEAN_F = ["Ingrid", "Astrid", "Freya", "Greta", "Francoise", "Amelie", "Celine",
                     "Margaux", "Colette", "Giulia", "Chiara", "Francesca", "Katarina",
                     "Petra", "Monika", "Ewa", "Elsa", "Helga", "Martina", "Alessia"]
NAMES_EUROPEAN_L = ["Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker",
                     "Schulz", "Hoffman", "Koch", "Dubois", "Laurent", "Moreau", "Bernard",
                     "Leroy", "Rossi", "Russo", "Ferrari", "Bianchi", "Kowalski", "Nowak",
                     "Johansson", "Lindberg", "Eriksson", "Nilsson", "Bergman"]

NAMES_US_MIXED_L = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson",
    "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson",
    "White", "Harris", "Clark", "Lewis", "Robinson", "Walker", "Young", "Allen",
    "King", "Wright", "Scott", "Hill", "Adams", "Green", "Baker", "Nelson", "Carter",
    "Mitchell", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans",
    "Collins", "Stewart", "Morris", "Murphy", "Cook", "Rogers", "Morgan", "Peterson",
    "Cooper", "Reed", "Bailey", "Bell", "Kelly", "Howard", "Ward", "Cox",
    "Richardson", "Wood", "Watson", "Brooks", "Bennett", "Gray", "Price", "Sanders",
    "Powell", "Russell", "Sullivan", "Fisher", "Hamilton", "Graham", "Wallace",
    "Cole", "Hart", "Fuller", "Wade", "Chambers", "Burns", "Dixon", "Hunt", "Palmer",
    "Warren", "Fox", "Rose", "Stone", "Burke", "Dunn", "Perkins", "Gordon", "Marsh",
    "Olson", "Harvey", "Simmons", "Grant", "Logan",
    # Asian-American last names (common in Bay Area)
    "Wang", "Li", "Zhang", "Liu", "Chen", "Yang", "Huang", "Wu", "Lin", "Kim",
    "Park", "Choi", "Patel", "Sharma", "Singh", "Kumar", "Gupta", "Shah",
    "Tanaka", "Suzuki", "Nakamura",
]

def pick_name(male_pool, female_pool, last_pool):
    is_f = random.random() < 0.45
    first = random.choice(female_pool if is_f else male_pool)
    last = random.choice(last_pool)
    return first, last


# ─── Location pools ──────────────────────────────────────────────────────────

LOC_SF = [
    ("San Francisco", "CA", "94105", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94107", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94103", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94102", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94110", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94114", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94158", "United States", "America/Los_Angeles"),
]
LOC_SOUTH_BAY = [
    ("Los Altos Hills", "CA", "94022", "United States", "America/Los_Angeles"),
    ("Los Altos", "CA", "94024", "United States", "America/Los_Angeles"),
    ("Palo Alto", "CA", "94301", "United States", "America/Los_Angeles"),
    ("Palo Alto", "CA", "94304", "United States", "America/Los_Angeles"),
    ("Mountain View", "CA", "94043", "United States", "America/Los_Angeles"),
    ("Mountain View", "CA", "94041", "United States", "America/Los_Angeles"),
    ("Sunnyvale", "CA", "94086", "United States", "America/Los_Angeles"),
    ("Cupertino", "CA", "95014", "United States", "America/Los_Angeles"),
    ("Saratoga", "CA", "95070", "United States", "America/Los_Angeles"),
    ("San Jose", "CA", "95113", "United States", "America/Los_Angeles"),
    ("Santa Clara", "CA", "95050", "United States", "America/Los_Angeles"),
    ("Menlo Park", "CA", "94025", "United States", "America/Los_Angeles"),
    ("Redwood City", "CA", "94063", "United States", "America/Los_Angeles"),
    ("Woodside", "CA", "94062", "United States", "America/Los_Angeles"),
    ("Campbell", "CA", "95008", "United States", "America/Los_Angeles"),
    ("Milpitas", "CA", "95035", "United States", "America/Los_Angeles"),
    ("Fremont", "CA", "94536", "United States", "America/Los_Angeles"),
]
LOC_BAY_AREA = LOC_SF + LOC_SOUTH_BAY + [
    ("Oakland", "CA", "94612", "United States", "America/Los_Angeles"),
    ("Berkeley", "CA", "94704", "United States", "America/Los_Angeles"),
]

LOC_NYC = [
    ("New York", "NY", "10001", "United States", "America/New_York"),
    ("New York", "NY", "10003", "United States", "America/New_York"),
    ("New York", "NY", "10011", "United States", "America/New_York"),
    ("New York", "NY", "10012", "United States", "America/New_York"),
    ("New York", "NY", "10013", "United States", "America/New_York"),
    ("New York", "NY", "10016", "United States", "America/New_York"),
    ("New York", "NY", "10022", "United States", "America/New_York"),
    ("New York", "NY", "10036", "United States", "America/New_York"),
    ("New York", "NY", "10038", "United States", "America/New_York"),
    ("Brooklyn", "NY", "11201", "United States", "America/New_York"),
    ("Brooklyn", "NY", "11215", "United States", "America/New_York"),
    ("Brooklyn", "NY", "11211", "United States", "America/New_York"),
    ("Jersey City", "NJ", "07302", "United States", "America/New_York"),
    ("Hoboken", "NJ", "07030", "United States", "America/New_York"),
]

LOC_BOSTON = [
    ("Boston", "MA", "02101", "United States", "America/New_York"),
    ("Boston", "MA", "02110", "United States", "America/New_York"),
    ("Boston", "MA", "02115", "United States", "America/New_York"),
    ("Cambridge", "MA", "02139", "United States", "America/New_York"),
    ("Cambridge", "MA", "02142", "United States", "America/New_York"),
    ("Somerville", "MA", "02143", "United States", "America/New_York"),
    ("Brookline", "MA", "02445", "United States", "America/New_York"),
]

LOC_SEATTLE = [
    ("Seattle", "WA", "98101", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98102", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98103", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98104", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98109", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98112", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98115", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98122", "United States", "America/Los_Angeles"),
    ("Bellevue", "WA", "98004", "United States", "America/Los_Angeles"),
    ("Bellevue", "WA", "98006", "United States", "America/Los_Angeles"),
    ("Redmond", "WA", "98052", "United States", "America/Los_Angeles"),
    ("Kirkland", "WA", "98033", "United States", "America/Los_Angeles"),
]

LOC_DC = [
    ("Washington", "DC", "20001", "United States", "America/New_York"),
    ("Washington", "DC", "20036", "United States", "America/New_York"),
    ("Washington", "DC", "20005", "United States", "America/New_York"),
    ("Arlington", "VA", "22201", "United States", "America/New_York"),
    ("Bethesda", "MD", "20814", "United States", "America/New_York"),
]

LOC_AUSTIN_DENVER = [
    ("Austin", "TX", "78701", "United States", "America/Chicago"),
    ("Austin", "TX", "78702", "United States", "America/Chicago"),
    ("Austin", "TX", "78704", "United States", "America/Chicago"),
    ("Austin", "TX", "78745", "United States", "America/Chicago"),
    ("Denver", "CO", "80202", "United States", "America/Denver"),
    ("Denver", "CO", "80203", "United States", "America/Denver"),
    ("Boulder", "CO", "80302", "United States", "America/Denver"),
]

LOC_INDIA = [
    ("Bangalore", "Karnataka", "560001", "India", "Asia/Kolkata"),
    ("Bangalore", "Karnataka", "560034", "India", "Asia/Kolkata"),
    ("Bangalore", "Karnataka", "560066", "India", "Asia/Kolkata"),
    ("Bangalore", "Karnataka", "560103", "India", "Asia/Kolkata"),
    ("Hyderabad", "Telangana", "500001", "India", "Asia/Kolkata"),
    ("Hyderabad", "Telangana", "500081", "India", "Asia/Kolkata"),
    ("Pune", "Maharashtra", "411001", "India", "Asia/Kolkata"),
    ("Pune", "Maharashtra", "411045", "India", "Asia/Kolkata"),
    ("Mumbai", "Maharashtra", "400001", "India", "Asia/Kolkata"),
    ("Delhi", "Delhi", "110001", "India", "Asia/Kolkata"),
    ("Gurgaon", "Haryana", "122001", "India", "Asia/Kolkata"),
    ("Noida", "Uttar Pradesh", "201301", "India", "Asia/Kolkata"),
    ("Chennai", "Tamil Nadu", "600001", "India", "Asia/Kolkata"),
]

LOC_CHINA = [
    ("Beijing", "Beijing", "100000", "China", "Asia/Shanghai"),
    ("Beijing", "Beijing", "100080", "China", "Asia/Shanghai"),
    ("Shanghai", "Shanghai", "200000", "China", "Asia/Shanghai"),
    ("Shanghai", "Shanghai", "200040", "China", "Asia/Shanghai"),
    ("Shenzhen", "Guangdong", "518000", "China", "Asia/Shanghai"),
    ("Hangzhou", "Zhejiang", "310000", "China", "Asia/Shanghai"),
    ("Guangzhou", "Guangdong", "510000", "China", "Asia/Shanghai"),
    ("Chengdu", "Sichuan", "610000", "China", "Asia/Shanghai"),
    ("Nanjing", "Jiangsu", "210000", "China", "Asia/Shanghai"),
    ("Wuhan", "Hubei", "430000", "China", "Asia/Shanghai"),
]

LOC_RUSSIA = [
    ("Moscow", "Moscow", "101000", "Russia", "Europe/Moscow"),
    ("Moscow", "Moscow", "105064", "Russia", "Europe/Moscow"),
    ("Moscow", "Moscow", "119034", "Russia", "Europe/Moscow"),
    ("St Petersburg", "St Petersburg", "190000", "Russia", "Europe/Moscow"),
    ("St Petersburg", "St Petersburg", "191186", "Russia", "Europe/Moscow"),
    ("Novosibirsk", "Novosibirsk Oblast", "630099", "Russia", "Asia/Novosibirsk"),
    ("Yekaterinburg", "Sverdlovsk Oblast", "620000", "Russia", "Asia/Yekaterinburg"),
    ("Kazan", "Tatarstan", "420000", "Russia", "Europe/Moscow"),
]

LOC_LATAM = [
    ("Mexico City", "CDMX", "06600", "Mexico", "America/Mexico_City"),
    ("Mexico City", "CDMX", "06700", "Mexico", "America/Mexico_City"),
    ("Guadalajara", "Jalisco", "44100", "Mexico", "America/Mexico_City"),
    ("Monterrey", "Nuevo Leon", "64000", "Mexico", "America/Mexico_City"),
    ("Bogota", "Cundinamarca", "110111", "Colombia", "America/Bogota"),
    ("Medellin", "Antioquia", "050001", "Colombia", "America/Bogota"),
    ("Buenos Aires", "Buenos Aires", "C1002", "Argentina", "America/Argentina/Buenos_Aires"),
    ("Buenos Aires", "Buenos Aires", "C1006", "Argentina", "America/Argentina/Buenos_Aires"),
    ("Santiago", "Santiago", "8320000", "Chile", "America/Santiago"),
    ("Lima", "Lima", "15001", "Peru", "America/Lima"),
    ("Sao Paulo", "SP", "01310-100", "Brazil", "America/Sao_Paulo"),
]

LOC_LONDON = [
    ("London", "England", "EC1A 1BB", "United Kingdom", "Europe/London"),
    ("London", "England", "SW1A 1AA", "United Kingdom", "Europe/London"),
    ("London", "England", "WC2N 5DU", "United Kingdom", "Europe/London"),
    ("London", "England", "E1 6AN", "United Kingdom", "Europe/London"),
    ("Cambridge", "England", "CB2 1TN", "United Kingdom", "Europe/London"),
    ("Oxford", "England", "OX1 1DP", "United Kingdom", "Europe/London"),
]

LOC_EUROPE_HUMANITIES = [
    ("London", "England", "EC1A 1BB", "United Kingdom", "Europe/London"),
    ("London", "England", "WC1B 3DG", "United Kingdom", "Europe/London"),
    ("Oxford", "England", "OX1 1DP", "United Kingdom", "Europe/London"),
    ("Cambridge", "England", "CB2 1TN", "United Kingdom", "Europe/London"),
    ("Edinburgh", "Scotland", "EH1 1YZ", "United Kingdom", "Europe/London"),
    ("Paris", "Ile-de-France", "75005", "France", "Europe/Paris"),
    ("Paris", "Ile-de-France", "75006", "France", "Europe/Paris"),
    ("Lyon", "Auvergne-Rhone-Alpes", "69001", "France", "Europe/Paris"),
    ("Berlin", "Berlin", "10115", "Germany", "Europe/Berlin"),
    ("Berlin", "Berlin", "10117", "Germany", "Europe/Berlin"),
    ("Munich", "Bavaria", "80331", "Germany", "Europe/Berlin"),
    ("Amsterdam", "North Holland", "1012", "Netherlands", "Europe/Amsterdam"),
    ("Rome", "Lazio", "00100", "Italy", "Europe/Rome"),
    ("Florence", "Tuscany", "50122", "Italy", "Europe/Rome"),
    ("Vienna", "Vienna", "1010", "Austria", "Europe/Vienna"),
]


# ─── Cluster generators ──────────────────────────────────────────────────────

all_taskers = []

def cluster_1_bay_area_ai_ml(n=120):
    """Bay Area AI/ML Corridor — ML, NLP, Data Science. Many English/Mandarin bilingual."""
    profiles = [
        ([2, 54], "ML Engineer"),
        ([2, 56], "NLP Engineer"),
        ([2, 54, 56], "Senior ML Engineer"),
        ([52, 54, 55], "Data Scientist"),
        ([54, 56], "ML Researcher"),
        ([54, 55, 57], "Senior Data Engineer"),
        ([2, 3], "AI/ML Full Stack Engineer"),
        ([1, 2, 5], "Backend ML Engineer"),
        ([1, 2, 7], "ML Platform Engineer"),
        ([90, 2], "AI Research Scientist"),
    ]
    for _ in range(n):
        first, last = pick_name(NAMES_AMERICAN_M + NAMES_CHINESE_M + NAMES_INDIAN_M,
                                NAMES_AMERICAN_F + NAMES_CHINESE_F + NAMES_INDIAN_F,
                                NAMES_US_MIXED_L)
        loc = random.choice(LOC_BAY_AREA)
        subs, title = random.choice(profiles)

        # ~40% speak Mandarin
        if random.random() < 0.40:
            langs = ["English", "Mandarin"]
            prof = {"English": "native", "Mandarin": random.choice(["native", "fluent"])}
        elif random.random() < 0.15:
            langs = ["English", "Hindi"]
            prof = {"English": "native", "Hindi": "fluent"}
        else:
            langs = ["English"]
            prof = {"English": "native"}

        all_taskers.append(make_tasker(first, last, loc, title, subs, langs, prof,
                                       rate_range=(55, 95)))


def cluster_2_nyc_finance_tech(n=80):
    """NYC Finance-Tech Crossover — quants, financial modelers, data engineers with finance."""
    profiles = [
        ([64, 65], "Quantitative Analyst"),
        ([64, 65, 55], "Quantitative Developer"),
        ([59, 65], "Financial Analyst"),
        ([63, 64], "Risk Analyst"),
        ([65, 1, 5], "Financial Software Engineer"),
        ([57, 59], "Financial Data Engineer"),
        ([52, 59, 65], "Financial Data Scientist"),
        ([60, 65], "Investment Banking Analyst"),
        ([62, 64], "Portfolio Quant"),
        ([66, 67, 57], "Fintech Data Engineer"),
    ]
    for _ in range(n):
        first, last = pick_name(NAMES_AMERICAN_M, NAMES_AMERICAN_F, NAMES_US_MIXED_L)
        loc = random.choice(LOC_NYC)
        subs, title = random.choice(profiles)
        langs = ["English"]
        prof = {"English": "native"}
        if random.random() < 0.15:
            langs.append("Mandarin")
            prof["Mandarin"] = "fluent"
        all_taskers.append(make_tasker(first, last, loc, title, subs, langs, prof,
                                       rate_range=(65, 95)))


def cluster_3_boston_life_sciences(n=70):
    """Boston/Cambridge Life Sciences Belt — bio, neuro, genetics around Harvard/MIT."""
    profiles = [
        ([80, 81], "Molecular Biologist"),
        ([80, 85], "Geneticist"),
        ([80, 82], "Cell Biologist"),
        ([86], "Biochemist"),
        ([87], "Immunologist"),
        ([88, 92], "Neuroscientist"),
        ([90], "Bioinformatics Scientist"),
        ([91], "Biotechnologist"),
        ([80, 84], "Microbiologist"),
        ([93], "Pharmacologist"),
        ([85, 90], "Computational Genomics Researcher"),
    ]
    for _ in range(n):
        first, last = pick_name(NAMES_AMERICAN_M, NAMES_AMERICAN_F, NAMES_US_MIXED_L)
        loc = random.choice(LOC_BOSTON)
        subs, title = random.choice(profiles)
        langs = ["English"]
        prof = {"English": "native"}
        all_taskers.append(make_tasker(first, last, loc, title, subs, langs, prof,
                                       rate_range=(50, 90)))


def cluster_4_india_engineering(n=150):
    """India Engineering Powerhouse — backend, full stack, platform. Trilingual."""
    profiles = [
        ([1, 5], "Backend Engineer"),
        ([1, 5, 9], "Senior Backend Engineer"),
        ([1, 3], "Full Stack Engineer"),
        ([1, 3, 4], "Full Stack Developer"),
        ([1, 7], "Platform Engineer"),
        ([1, 2], "Software Engineer"),
        ([1, 2, 3], "Senior Software Engineer"),
        ([2, 54], "ML Engineer"),
        ([1, 9], "Database Engineer"),
        ([1, 8], "Mobile Developer"),
        ([57], "Data Engineer"),
        ([5, 7], "Infrastructure Engineer"),
    ]
    regional_langs = [
        ("Tamil", "fluent"), ("Telugu", "fluent"), ("Kannada", "fluent"),
        ("Malayalam", "fluent"), ("Marathi", "fluent"), ("Bengali", "fluent"),
        ("Gujarati", "fluent"), ("Punjabi", "fluent"),
    ]
    for _ in range(n):
        first, last = pick_name(NAMES_INDIAN_M, NAMES_INDIAN_F, NAMES_INDIAN_L)
        loc = random.choice(LOC_INDIA)
        subs, title = random.choice(profiles)
        # Trilingual: Hindi + English + regional
        regional = random.choice(regional_langs)
        langs = ["English", "Hindi", regional[0]]
        prof = {"English": "fluent", "Hindi": "native", regional[0]: regional[1]}
        all_taskers.append(make_tasker(first, last, loc, title, subs, langs, prof,
                                       rate_range=(25, 55),
                                       hours_choices=[20.0, 25.0, 30.0, 35.0, 40.0]))


def cluster_5_seattle_security_cloud(n=80):
    """Seattle Security & Cloud — security, platform, DevSecOps (MSFT/AMZN vibes)."""
    profiles = [
        ([1, 6], "Security Engineer"),
        ([1, 6, 7], "DevSecOps Engineer"),
        ([1, 7], "Platform Engineer"),
        ([5, 7], "Infrastructure Engineer"),
        ([1, 7, 9], "Cloud Database Engineer"),
        ([1, 6], "Application Security Engineer"),
        ([1, 2, 7], "Staff Platform Engineer"),
        ([7, 57], "Cloud Data Engineer"),
        ([1, 5, 7], "Senior Cloud Engineer"),
        ([6, 50], "Security & Compliance Engineer"),
    ]
    for _ in range(n):
        first, last = pick_name(NAMES_AMERICAN_M, NAMES_AMERICAN_F, NAMES_US_MIXED_L)
        loc = random.choice(LOC_SEATTLE)
        subs, title = random.choice(profiles)
        langs = ["English"]
        prof = {"English": "native"}
        all_taskers.append(make_tasker(first, last, loc, title, subs, langs, prof,
                                       rate_range=(60, 95)))


def cluster_6_legal_hub(n=60):
    """Multilingual Legal Hub — DC/NYC/London. Many bilingual (esp Spanish)."""
    profiles = [
        ([42, 43], "International Law Attorney"),
        ([48], "Immigration Attorney"),
        ([41, 50], "IP Attorney"),
        ([39, 40], "Corporate Lawyer"),
        ([36, 37], "Attorney"),
        ([37, 38], "Litigation Attorney"),
        ([45], "Labor Attorney"),
        ([44], "Environmental Lawyer"),
        ([43, 48], "Human Rights & Immigration Lawyer"),
        ([40, 39, 50], "Tech Corporate Counsel"),
    ]
    locs = LOC_DC + LOC_NYC + LOC_LONDON
    for _ in range(n):
        # Mix of American, Hispanic, European names
        pool_r = random.random()
        if pool_r < 0.5:
            first, last = pick_name(NAMES_AMERICAN_M, NAMES_AMERICAN_F, NAMES_US_MIXED_L)
        elif pool_r < 0.8:
            first, last = pick_name(NAMES_HISPANIC_M, NAMES_HISPANIC_F, NAMES_HISPANIC_L)
        else:
            first, last = pick_name(NAMES_EUROPEAN_M, NAMES_EUROPEAN_F, NAMES_EUROPEAN_L)

        loc = random.choice(locs)
        subs, title = random.choice(profiles)

        # ~45% speak Spanish, ~15% French
        langs = ["English"]
        prof = {"English": "native"}
        if random.random() < 0.45:
            langs.append("Spanish")
            prof["Spanish"] = random.choice(["native", "fluent"])
        elif random.random() < 0.25:
            langs.append("French")
            prof["French"] = random.choice(["native", "fluent"])

        all_taskers.append(make_tasker(first, last, loc, title, subs, langs, prof,
                                       rate_range=(60, 95)))


def cluster_7_china_russia_stem(n=80):
    """China/Russia Non-English STEM — physicists, chemists, mathematicians. Many monolingual."""
    profiles_phys = [
        ([95, 96], "Physicist"),
        ([95], "Theoretical Physicist"),
        ([96], "Astrophysicist"),
        ([98], "Chemist"),
        ([98, 103], "Materials Scientist"),
        ([97], "Astronomer"),
        ([55, 95], "Mathematical Physicist"),
    ]
    profiles_cs = [
        ([2, 54], "ML Researcher"),
        ([54, 55], "Applied Mathematician"),
        ([52, 55], "Computational Scientist"),
    ]
    profiles = profiles_phys + profiles_cs

    n_china = n // 2
    n_russia = n - n_china

    # China
    for _ in range(n_china):
        first, last = pick_name(NAMES_CHINESE_M, NAMES_CHINESE_F, NAMES_CHINESE_L)
        loc = random.choice(LOC_CHINA)
        subs, title = random.choice(profiles)
        # 60% Mandarin-only, 40% Mandarin + basic English
        if random.random() < 0.60:
            langs = ["Mandarin"]
            prof = {"Mandarin": "native"}
        else:
            langs = ["Mandarin", "English"]
            prof = {"Mandarin": "native", "English": "intermediate"}
        all_taskers.append(make_tasker(first, last, loc, title, subs, langs, prof,
                                       rate_range=(30, 65)))

    # Russia
    for _ in range(n_russia):
        first, last = pick_name(NAMES_RUSSIAN_M, NAMES_RUSSIAN_F, NAMES_RUSSIAN_L)
        loc = random.choice(LOC_RUSSIA)
        subs, title = random.choice(profiles)
        # 55% Russian-only, 45% Russian + basic English
        if random.random() < 0.55:
            langs = ["Russian"]
            prof = {"Russian": "native"}
        else:
            langs = ["Russian", "English"]
            prof = {"Russian": "native", "English": "intermediate"}
        all_taskers.append(make_tasker(first, last, loc, title, subs, langs, prof,
                                       rate_range=(25, 55)))


def cluster_8_latam_medical(n=50):
    """Latin America Spanish-Speaking Medical professionals."""
    profiles = [
        ([22, 28], "Cardiologist"),
        ([22, 27], "Neurologist"),
        ([22, 29], "Oncologist"),
        ([22, 23], "Surgeon"),
        ([22, 24], "Pediatrician"),
        ([22, 26], "Psychiatrist"),
        ([22, 32], "Epidemiologist"),
        ([22, 33], "Pharmacologist"),
        ([22], "General Practitioner"),
        ([25], "OB/GYN Physician"),
        ([22, 30], "Radiologist"),
    ]
    for _ in range(n):
        first, last = pick_name(NAMES_HISPANIC_M, NAMES_HISPANIC_F, NAMES_HISPANIC_L)
        loc = random.choice(LOC_LATAM)
        subs, title = random.choice(profiles)
        country = loc[3]
        # All speak Spanish; Brazilians speak Portuguese instead
        if country == "Brazil":
            langs = ["Portuguese", "English"]
            prof = {"Portuguese": "native", "English": "fluent"}
            if random.random() < 0.4:
                langs.append("Spanish")
                prof["Spanish"] = "fluent"
        elif country == "Peru":
            langs = ["Spanish", "English"]
            prof = {"Spanish": "native", "English": "fluent"}
        else:
            langs = ["Spanish", "English"]
            prof = {"Spanish": "native", "English": random.choice(["fluent", "intermediate"])}
        all_taskers.append(make_tasker(first, last, loc, title, subs, langs, prof,
                                       rate_range=(30, 70)))


def cluster_9_europe_humanities(n=50):
    """European Humanities Cluster — historians, philosophers, lit profs in London/Paris/Berlin."""
    profiles = [
        ([129, 133], "Philosophy Professor"),
        ([130], "Historian"),
        ([131], "Literature Professor"),
        ([132], "Religious Studies Scholar"),
        ([134], "Classics Professor"),
        ([135, 136], "Cultural Studies Researcher"),
        ([138], "Archaeologist"),
        ([139], "Art Historian"),
        ([133, 129], "Ethics Professor"),
        ([130, 137], "European History Scholar"),
    ]
    for _ in range(n):
        first, last = pick_name(NAMES_EUROPEAN_M + NAMES_AMERICAN_M[:20],
                                NAMES_EUROPEAN_F + NAMES_AMERICAN_F[:20],
                                NAMES_EUROPEAN_L + NAMES_US_MIXED_L[:20])
        loc = random.choice(LOC_EUROPE_HUMANITIES)
        subs, title = random.choice(profiles)
        country = loc[3]

        # Language based on country
        if country == "France":
            langs = ["French", "English"]
            prof = {"French": "native", "English": "fluent"}
            if random.random() < 0.3:
                langs.append("German")
                prof["German"] = "intermediate"
        elif country == "Germany" or country == "Austria":
            langs = ["German", "English"]
            prof = {"German": "native", "English": "fluent"}
            if random.random() < 0.3:
                langs.append("French")
                prof["French"] = "intermediate"
        elif country == "Italy":
            langs = ["Italian", "English"]
            prof = {"Italian": "native", "English": "fluent"}
            if random.random() < 0.25:
                langs.append("Latin")
                prof["Latin"] = "intermediate"
        elif country == "Netherlands":
            langs = ["Dutch", "English"]
            prof = {"Dutch": "native", "English": "fluent"}
        else:  # UK
            langs = ["English"]
            prof = {"English": "native"}
            if random.random() < 0.4:
                extra = random.choice([("French", "fluent"), ("German", "intermediate"), ("Latin", "intermediate"), ("Italian", "intermediate")])
                langs.append(extra[0])
                prof[extra[0]] = extra[1]

        all_taskers.append(make_tasker(first, last, loc, title, subs, langs, prof,
                                       rate_range=(45, 80)))


def cluster_10_austin_denver_creative_tech(n=60):
    """Austin/Denver Creative-Tech Hybrid — UX/UI + Game Design + SWE crossovers."""
    profiles = [
        ([117, 119], "UX/UI Designer"),
        ([119, 4], "Design Engineer"),
        ([127], "Game Designer"),
        ([127, 1], "Game Developer"),
        ([117, 119, 4], "Senior Product Designer"),
        ([124, 127], "Animation & Game Artist"),
        ([1, 4, 119], "Frontend Design Engineer"),
        ([119, 8], "Mobile UX Designer"),
        ([116, 117], "Visual & Graphic Designer"),
        ([118, 122], "Industrial Design Architect"),
        ([125, 126], "Creative Photographer"),
        ([128, 117], "Creative Director"),
    ]
    for _ in range(n):
        first, last = pick_name(NAMES_AMERICAN_M, NAMES_AMERICAN_F, NAMES_US_MIXED_L)
        loc = random.choice(LOC_AUSTIN_DENVER)
        subs, title = random.choice(profiles)
        langs = ["English"]
        prof = {"English": "native"}
        if random.random() < 0.2:
            langs.append("Spanish")
            prof["Spanish"] = random.choice(["fluent", "intermediate"])
        all_taskers.append(make_tasker(first, last, loc, title, subs, langs, prof,
                                       rate_range=(40, 80)))


# ─── Generate all clusters ───────────────────────────────────────────────────

cluster_1_bay_area_ai_ml(120)
cluster_2_nyc_finance_tech(80)
cluster_3_boston_life_sciences(70)
cluster_4_india_engineering(150)
cluster_5_seattle_security_cloud(80)
cluster_6_legal_hub(60)
cluster_7_china_russia_stem(80)
cluster_8_latam_medical(50)
cluster_9_europe_humanities(50)
cluster_10_austin_denver_creative_tech(60)


# ─── Write SQL ────────────────────────────────────────────────────────────────

cols = "id, first_name, middle_name, last_name, email, hire_date, address_line1, address_line2, city, state_province, postal_code, location_country, location_timezone, status, external_job_title, subdomain_ids, hours_available, hourly_rate, languages, language_proficiency, internal_roles"
header = f"INSERT INTO taskers ({cols}) VALUES"

lines = [f"-- Auto-generated: {len(all_taskers)} cluster taskers (IDs {all_taskers[0][0]}-{all_taskers[-1][0]})"]
lines.append(f"-- Cluster 1: Bay Area AI/ML (120)")
lines.append(f"-- Cluster 2: NYC Finance-Tech (80)")
lines.append(f"-- Cluster 3: Boston Life Sciences (70)")
lines.append(f"-- Cluster 4: India Engineering (150)")
lines.append(f"-- Cluster 5: Seattle Security & Cloud (80)")
lines.append(f"-- Cluster 6: Multilingual Legal Hub (60)")
lines.append(f"-- Cluster 7: China/Russia Non-English STEM (80)")
lines.append(f"-- Cluster 8: LATAM Spanish-Speaking Medical (50)")
lines.append(f"-- Cluster 9: European Humanities (50)")
lines.append(f"-- Cluster 10: Austin/Denver Creative-Tech (60)")

batch_size = 200
for i in range(0, len(all_taskers), batch_size):
    batch = all_taskers[i : i + batch_size]
    lines.append("")
    lines.append(header)
    for j, t in enumerate(batch):
        comma = "," if j < len(batch) - 1 else ";"
        lines.append(format_row(t) + comma)

lines.append("")
lines.append("-- Reset sequence")
lines.append("SELECT setval('taskers_id_seq', (SELECT MAX(id) FROM taskers));")

outfile = "migrations/012_add_tasker_clusters.sql"
with open(outfile, "w") as f:
    f.write("\n".join(lines) + "\n")

# Stats
print(f"Generated {len(all_taskers)} cluster taskers (IDs {all_taskers[0][0]}-{all_taskers[-1][0]}) → {outfile}")
print()
clusters = [
    ("Bay Area AI/ML", 120), ("NYC Finance-Tech", 80), ("Boston Life Sci", 70),
    ("India Engineering", 150), ("Seattle Sec/Cloud", 80), ("Legal Hub", 60),
    ("China/Russia STEM", 80), ("LATAM Medical", 50), ("Euro Humanities", 50),
    ("Austin/Denver Creative", 60),
]
offset = 0
for name, size in clusters:
    chunk = all_taskers[offset:offset+size]
    countries = {}
    for t in chunk:
        c = t[11]
        countries[c] = countries.get(c, 0) + 1
    top = sorted(countries.items(), key=lambda x: -x[1])[:3]
    top_str = ", ".join(f"{c}:{n}" for c, n in top)
    print(f"  {name}: {size} — {top_str}")
    offset += size
