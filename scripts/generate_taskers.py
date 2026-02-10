#!/usr/bin/env python3
"""Generate SQL migration to insert taskers 21-1128 (1108 new taskers)."""

import random
import json

random.seed(42)

# ─── Name pools ───────────────────────────────────────────────────────────────

FIRST_NAMES_MALE = [
    "James", "John", "Robert", "Michael", "David", "William", "Richard", "Joseph",
    "Thomas", "Daniel", "Matthew", "Anthony", "Mark", "Steven", "Paul", "Andrew",
    "Joshua", "Kenneth", "Kevin", "Brian", "George", "Timothy", "Ronald", "Edward",
    "Jason", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas", "Eric", "Jonathan",
    "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin", "Samuel", "Raymond",
    # Hispanic
    "Carlos", "Miguel", "Luis", "Jorge", "Pedro", "Rafael", "Diego", "Alejandro",
    "Fernando", "Ricardo", "Sergio", "Javier", "Andres", "Pablo", "Mateo", "Santiago",
    "Emilio", "Rodrigo", "Hector", "Oscar",
    # East Asian
    "Wei", "Jun", "Hao", "Ming", "Tao", "Kai", "Chen", "Yong", "Jian", "Liang",
    "Hiroshi", "Takeshi", "Kenji", "Yuto", "Haruto", "Ren", "Sota", "Kaito",
    "Sang-Hoon", "Min-Jun", "Ji-Hoon", "Hyun-Woo", "Seo-Jun", "Do-Yun",
    # South Asian
    "Rajesh", "Vikram", "Amit", "Arun", "Sanjay", "Deepak", "Ravi", "Suresh",
    "Nikhil", "Arjun", "Rohan", "Karthik", "Pranav", "Varun", "Ashwin", "Rahul",
    "Gaurav", "Manish", "Sachin", "Vishal",
    # African
    "Kwame", "Chukwu", "Olumide", "Babajide", "Adewale", "Emeka", "Obinna",
    "Chinonso", "Tunde", "Segun", "Musa", "Ibrahim", "Youssef", "Omar", "Hassan",
    # European
    "Klaus", "Friedrich", "Hans", "Wolfgang", "Stefan", "Pierre", "Laurent",
    "Jacques", "Francois", "Antoine", "Luca", "Marco", "Alessandro", "Matteo",
    "Giovanni", "Piotr", "Andrzej", "Marek", "Krzysztof", "Jakub",
    "Dmitri", "Alexei", "Sergei", "Nikolai", "Ivan",
    "Lars", "Anders", "Erik", "Olaf", "Sven",
    # Middle Eastern
    "Ahmad", "Khalid", "Tariq", "Faisal", "Samir", "Nabil", "Rashid", "Zaid",
    "Ali", "Hamza",
    # Brazilian
    "Gustavo", "Henrique", "Felipe", "Thiago", "Caio", "Bruno", "Vinicius",
]

FIRST_NAMES_FEMALE = [
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
    "Ashley", "Emily", "Donna", "Michelle", "Dorothy", "Carol", "Amanda", "Melissa",
    "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia", "Kathleen",
    "Amy", "Angela", "Shirley", "Anna", "Brenda", "Pamela", "Emma", "Nicole",
    "Helen", "Samantha", "Katherine", "Christine", "Debra", "Rachel", "Carolyn",
    # Hispanic
    "Maria", "Carmen", "Ana", "Lucia", "Sofia", "Valentina", "Isabella", "Gabriela",
    "Camila", "Mariana", "Daniela", "Fernanda", "Alejandra", "Catalina", "Natalia",
    "Ximena", "Lorena", "Adriana", "Paola", "Elena",
    # East Asian
    "Mei", "Xiu", "Lan", "Hua", "Jing", "Yue", "Ling", "Na", "Fang", "Li",
    "Yuki", "Sakura", "Aiko", "Hana", "Mio", "Rin", "Saki",
    "Soo-Jin", "Min-Ji", "Hye-Jin", "Ji-Yeon", "Eun-Ji",
    # South Asian
    "Priya", "Ananya", "Kavita", "Sunita", "Deepa", "Neha", "Pooja", "Shreya",
    "Divya", "Meera", "Anjali", "Nandini", "Swati", "Aarti", "Rekha", "Sarita",
    # African
    "Amina", "Fatima", "Aisha", "Zainab", "Ngozi", "Chidinma", "Adaeze",
    "Folake", "Binta", "Mariama",
    # European
    "Ingrid", "Astrid", "Freya", "Elsa", "Greta", "Helga",
    "Francoise", "Colette", "Amelie", "Celine", "Margaux",
    "Katarina", "Petra", "Monika", "Ewa", "Agnieszka",
    "Olga", "Natasha", "Svetlana", "Tatiana", "Irina",
    "Giulia", "Chiara", "Francesca", "Alessia", "Martina",
    # Middle Eastern
    "Layla", "Nour", "Dalia", "Rania", "Huda", "Maryam", "Yasmin", "Salma",
    # Brazilian
    "Juliana", "Beatriz", "Larissa", "Leticia", "Rafaela", "Bianca",
]

LAST_NAMES = [
    # English
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Hill",
    "Adams", "Green", "Baker", "Nelson", "Carter", "Mitchell", "Roberts", "Turner",
    "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart",
    "Morris", "Murphy", "Rivera", "Cook", "Rogers", "Morgan", "Peterson",
    "Cooper", "Reed", "Bailey", "Bell", "Gomez", "Kelly", "Howard", "Ward",
    "Cox", "Diaz", "Richardson", "Wood", "Watson", "Brooks", "Bennett", "Gray",
    # East Asian
    "Wang", "Li", "Zhang", "Liu", "Chen", "Yang", "Huang", "Zhao", "Wu", "Zhou",
    "Xu", "Sun", "Ma", "Zhu", "Guo", "Lin", "He", "Luo", "Tang", "Xie",
    "Tanaka", "Suzuki", "Watanabe", "Takahashi", "Ito", "Yamamoto", "Nakamura",
    "Kobayashi", "Saito", "Kato", "Yoshida", "Yamada", "Sasaki", "Kimura",
    "Kim", "Park", "Choi", "Jung", "Kang", "Yoon", "Jang", "Lim", "Han", "Shin",
    # South Asian
    "Patel", "Sharma", "Singh", "Kumar", "Gupta", "Mehta", "Shah", "Joshi",
    "Reddy", "Nair", "Rao", "Das", "Mishra", "Agarwal", "Bhat", "Pillai",
    "Chandra", "Iyer", "Menon", "Verma", "Kapoor", "Malhotra", "Chopra", "Banerjee",
    # African
    "Okafor", "Adeyemi", "Ogundimu", "Nwosu", "Ibrahim", "Diallo", "Traore",
    "Mensah", "Asante", "Boateng", "Owusu", "Abubakar", "Toure", "Bello",
    # European
    "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker",
    "Schulz", "Hoffman", "Koch", "Richter", "Wolf", "Braun", "Zimmermann",
    "Dubois", "Laurent", "Moreau", "Bernard", "Leroy", "Roux", "Girard",
    "Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo",
    "Kowalski", "Nowak", "Wisniewski", "Wojciech", "Kaminski", "Lewandowski",
    "Petrov", "Ivanov", "Volkov", "Sokolov", "Popov",
    "Johansson", "Lindberg", "Eriksson", "Nilsson", "Larsson", "Bergman",
    # Middle Eastern
    "Al-Rashid", "Al-Farsi", "Al-Sayed", "Khoury", "Haddad", "Mansour", "Nasser",
    # Latin American
    "Fernandez", "Mendez", "Reyes", "Flores", "Morales", "Ortiz", "Gutierrez",
    "Rojas", "Vargas", "Castillo", "Jimenez", "Herrera", "Medina", "Aguilar",
    "Silva", "Santos", "Oliveira", "Souza", "Costa", "Ferreira", "Almeida",
    "Pereira", "Carvalho", "Ribeiro", "Araujo",
]

MIDDLE_INITIALS = list("ABCDEFGHJKLMNPRSTW")

# ─── Location pools ──────────────────────────────────────────────────────────

LOCATIONS = [
    # (city, state_province, postal_code, country, timezone)
    ("New York", "NY", "10001", "United States", "America/New_York"),
    ("Brooklyn", "NY", "11201", "United States", "America/New_York"),
    ("Boston", "MA", "02101", "United States", "America/New_York"),
    ("Philadelphia", "PA", "19101", "United States", "America/New_York"),
    ("Washington", "DC", "20001", "United States", "America/New_York"),
    ("Atlanta", "GA", "30301", "United States", "America/New_York"),
    ("Miami", "FL", "33101", "United States", "America/New_York"),
    ("Chicago", "IL", "60601", "United States", "America/Chicago"),
    ("Houston", "TX", "77001", "United States", "America/Chicago"),
    ("Dallas", "TX", "75201", "United States", "America/Chicago"),
    ("Austin", "TX", "73301", "United States", "America/Chicago"),
    ("Minneapolis", "MN", "55401", "United States", "America/Chicago"),
    ("Denver", "CO", "80201", "United States", "America/Denver"),
    ("Phoenix", "AZ", "85001", "United States", "America/Denver"),
    ("Salt Lake City", "UT", "84101", "United States", "America/Denver"),
    ("San Francisco", "CA", "94105", "United States", "America/Los_Angeles"),
    ("Los Angeles", "CA", "90001", "United States", "America/Los_Angeles"),
    ("San Diego", "CA", "92101", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98101", "United States", "America/Los_Angeles"),
    ("Portland", "OR", "97201", "United States", "America/Los_Angeles"),
    ("Palo Alto", "CA", "94301", "United States", "America/Los_Angeles"),
    # Canada
    ("Toronto", "ON", "M5V 3L9", "Canada", "America/Toronto"),
    ("Vancouver", "BC", "V6B 1A1", "Canada", "America/Vancouver"),
    ("Montreal", "QC", "H2X 1Y4", "Canada", "America/Toronto"),
    # UK
    ("London", "England", "EC1A 1BB", "United Kingdom", "Europe/London"),
    ("Manchester", "England", "M1 1AE", "United Kingdom", "Europe/London"),
    ("Edinburgh", "Scotland", "EH1 1YZ", "United Kingdom", "Europe/London"),
    ("Cambridge", "England", "CB2 1TN", "United Kingdom", "Europe/London"),
    ("Oxford", "England", "OX1 1DP", "United Kingdom", "Europe/London"),
    # Germany
    ("Berlin", "Berlin", "10115", "Germany", "Europe/Berlin"),
    ("Munich", "Bavaria", "80331", "Germany", "Europe/Berlin"),
    ("Hamburg", "Hamburg", "20095", "Germany", "Europe/Berlin"),
    ("Frankfurt", "Hesse", "60311", "Germany", "Europe/Berlin"),
    # France
    ("Paris", "Ile-de-France", "75001", "France", "Europe/Paris"),
    ("Lyon", "Auvergne-Rhone-Alpes", "69001", "France", "Europe/Paris"),
    ("Marseille", "Provence-Alpes-Cote d Azur", "13001", "France", "Europe/Paris"),
    # Netherlands
    ("Amsterdam", "North Holland", "1012", "Netherlands", "Europe/Amsterdam"),
    # Spain
    ("Madrid", "Madrid", "28001", "Spain", "Europe/Madrid"),
    ("Barcelona", "Catalonia", "08001", "Spain", "Europe/Madrid"),
    # Italy
    ("Rome", "Lazio", "00100", "Italy", "Europe/Rome"),
    ("Milan", "Lombardy", "20121", "Italy", "Europe/Rome"),
    # Poland
    ("Warsaw", "Masovia", "00-001", "Poland", "Europe/Warsaw"),
    ("Krakow", "Lesser Poland", "30-001", "Poland", "Europe/Warsaw"),
    # Sweden
    ("Stockholm", "Stockholm", "111 51", "Sweden", "Europe/Stockholm"),
    # Switzerland
    ("Zurich", "Zurich", "8001", "Switzerland", "Europe/Zurich"),
    # India
    ("Bangalore", "Karnataka", "560001", "India", "Asia/Kolkata"),
    ("Mumbai", "Maharashtra", "400001", "India", "Asia/Kolkata"),
    ("Delhi", "Delhi", "110001", "India", "Asia/Kolkata"),
    ("Hyderabad", "Telangana", "500001", "India", "Asia/Kolkata"),
    ("Chennai", "Tamil Nadu", "600001", "India", "Asia/Kolkata"),
    ("Pune", "Maharashtra", "411001", "India", "Asia/Kolkata"),
    # Japan
    ("Tokyo", "Tokyo", "100-0001", "Japan", "Asia/Tokyo"),
    ("Osaka", "Osaka", "530-0001", "Japan", "Asia/Tokyo"),
    # South Korea
    ("Seoul", "Seoul", "04524", "South Korea", "Asia/Seoul"),
    ("Busan", "Busan", "48058", "South Korea", "Asia/Seoul"),
    # China
    ("Beijing", "Beijing", "100000", "China", "Asia/Shanghai"),
    ("Shanghai", "Shanghai", "200000", "China", "Asia/Shanghai"),
    ("Shenzhen", "Guangdong", "518000", "China", "Asia/Shanghai"),
    # Singapore
    ("Singapore", "Singapore", "018956", "Singapore", "Asia/Singapore"),
    # Australia
    ("Sydney", "NSW", "2000", "Australia", "Australia/Sydney"),
    ("Melbourne", "VIC", "3000", "Australia", "Australia/Melbourne"),
    # Brazil
    ("Sao Paulo", "SP", "01310-100", "Brazil", "America/Sao_Paulo"),
    ("Rio de Janeiro", "RJ", "20040-020", "Brazil", "America/Sao_Paulo"),
    # Mexico
    ("Mexico City", "CDMX", "06600", "Mexico", "America/Mexico_City"),
    ("Guadalajara", "Jalisco", "44100", "Mexico", "America/Mexico_City"),
    # Colombia
    ("Bogota", "Cundinamarca", "110111", "Colombia", "America/Bogota"),
    ("Medellin", "Antioquia", "050001", "Colombia", "America/Bogota"),
    # Argentina
    ("Buenos Aires", "Buenos Aires", "C1002", "Argentina", "America/Argentina/Buenos_Aires"),
    # Chile
    ("Santiago", "Santiago", "8320000", "Chile", "America/Santiago"),
    # Nigeria
    ("Lagos", "Lagos", "101233", "Nigeria", "Africa/Lagos"),
    ("Abuja", "FCT", "900001", "Nigeria", "Africa/Lagos"),
    # Kenya
    ("Nairobi", "Nairobi", "00100", "Kenya", "Africa/Nairobi"),
    # South Africa
    ("Cape Town", "Western Cape", "8001", "South Africa", "Africa/Johannesburg"),
    ("Johannesburg", "Gauteng", "2000", "South Africa", "Africa/Johannesburg"),
    # Egypt
    ("Cairo", "Cairo", "11511", "Egypt", "Africa/Cairo"),
    # UAE
    ("Dubai", "Dubai", "00000", "United Arab Emirates", "Asia/Dubai"),
    ("Abu Dhabi", "Abu Dhabi", "00000", "United Arab Emirates", "Asia/Dubai"),
    # Israel
    ("Tel Aviv", "Tel Aviv", "6100000", "Israel", "Asia/Jerusalem"),
    # Turkey
    ("Istanbul", "Istanbul", "34000", "Turkey", "Europe/Istanbul"),
    # Philippines
    ("Manila", "Metro Manila", "1000", "Philippines", "Asia/Manila"),
    # Vietnam
    ("Ho Chi Minh City", "Ho Chi Minh", "700000", "Vietnam", "Asia/Ho_Chi_Minh"),
    # Taiwan
    ("Taipei", "Taipei", "100", "Taiwan", "Asia/Taipei"),
    # Thailand
    ("Bangkok", "Bangkok", "10100", "Thailand", "Asia/Bangkok"),
    # Indonesia
    ("Jakarta", "DKI Jakarta", "10110", "Indonesia", "Asia/Jakarta"),
    # Pakistan
    ("Karachi", "Sindh", "74200", "Pakistan", "Asia/Karachi"),
    ("Lahore", "Punjab", "54000", "Pakistan", "Asia/Karachi"),
    # Russia
    ("Moscow", "Moscow", "101000", "Russia", "Europe/Moscow"),
    ("St Petersburg", "St Petersburg", "190000", "Russia", "Europe/Moscow"),
]

# Map country to likely languages
COUNTRY_LANGUAGES = {
    "United States": [("English", "native")],
    "Canada": [("English", "native")],
    "United Kingdom": [("English", "native")],
    "Germany": [("German", "native"), ("English", "fluent")],
    "France": [("French", "native"), ("English", "fluent")],
    "Netherlands": [("Dutch", "native"), ("English", "fluent")],
    "Spain": [("Spanish", "native"), ("English", "fluent")],
    "Italy": [("Italian", "native"), ("English", "fluent")],
    "Poland": [("Polish", "native"), ("English", "fluent")],
    "Sweden": [("Swedish", "native"), ("English", "fluent")],
    "Switzerland": [("German", "native"), ("English", "fluent")],
    "India": [("Hindi", "native"), ("English", "fluent")],
    "Japan": [("Japanese", "native"), ("English", "fluent")],
    "South Korea": [("Korean", "native"), ("English", "fluent")],
    "China": [("Mandarin", "native"), ("English", "fluent")],
    "Singapore": [("English", "native"), ("Mandarin", "fluent")],
    "Australia": [("English", "native")],
    "Brazil": [("Portuguese", "native"), ("English", "fluent")],
    "Mexico": [("Spanish", "native"), ("English", "fluent")],
    "Colombia": [("Spanish", "native"), ("English", "fluent")],
    "Argentina": [("Spanish", "native"), ("English", "fluent")],
    "Chile": [("Spanish", "native"), ("English", "fluent")],
    "Nigeria": [("English", "native"), ("Yoruba", "fluent")],
    "Kenya": [("English", "native"), ("Swahili", "fluent")],
    "South Africa": [("English", "native"), ("Afrikaans", "fluent")],
    "Egypt": [("Arabic", "native"), ("English", "fluent")],
    "United Arab Emirates": [("Arabic", "native"), ("English", "fluent")],
    "Israel": [("Hebrew", "native"), ("English", "fluent")],
    "Turkey": [("Turkish", "native"), ("English", "fluent")],
    "Philippines": [("Filipino", "native"), ("English", "fluent")],
    "Vietnam": [("Vietnamese", "native"), ("English", "fluent")],
    "Taiwan": [("Mandarin", "native"), ("English", "fluent")],
    "Thailand": [("Thai", "native"), ("English", "fluent")],
    "Indonesia": [("Indonesian", "native"), ("English", "fluent")],
    "Pakistan": [("Urdu", "native"), ("English", "fluent")],
    "Russia": [("Russian", "native"), ("English", "fluent")],
}

EXTRA_LANGUAGES = [
    ("Spanish", "intermediate"), ("French", "intermediate"), ("German", "intermediate"),
    ("Mandarin", "intermediate"), ("Japanese", "intermediate"), ("Korean", "intermediate"),
    ("Portuguese", "intermediate"), ("Arabic", "intermediate"), ("Hindi", "intermediate"),
    ("Italian", "intermediate"), ("Russian", "intermediate"), ("Dutch", "intermediate"),
    ("Swedish", "intermediate"), ("Polish", "intermediate"), ("Turkish", "intermediate"),
    ("Spanish", "fluent"), ("French", "fluent"), ("German", "fluent"),
    ("Mandarin", "fluent"), ("Portuguese", "fluent"),
]

# ─── Domain/subdomain pools ──────────────────────────────────────────────────

# (subdomain_ids list, external_job_title, domain_label)
PROFILES = [
    # Software Engineering (domain 1, subs 1-10)
    ([1, 2], "Software Engineer", "swe"),
    ([1, 3], "Full Stack Engineer", "swe"),
    ([1, 4], "Frontend Developer", "swe"),
    ([1, 5], "Backend Engineer", "swe"),
    ([1, 6], "Security Engineer", "swe"),
    ([1, 7], "Platform Engineer", "swe"),
    ([1, 8], "Mobile Developer", "swe"),
    ([1, 9], "Database Engineer", "swe"),
    ([2, 54], "ML Engineer", "swe"),
    ([2, 56], "NLP Engineer", "swe"),
    ([1, 2, 3], "Senior Software Engineer", "swe"),
    ([1, 5, 9], "Senior Backend Engineer", "swe"),
    ([1, 3, 4], "Full Stack Developer", "swe"),
    ([1, 2, 7], "Staff Engineer", "swe"),
    ([1, 6, 7], "DevSecOps Engineer", "swe"),
    # Other Engineering (domain 2, subs 11-21)
    ([11], "Mechanical Engineer", "eng"),
    ([12], "Electrical Engineer", "eng"),
    ([13], "Civil Engineer", "eng"),
    ([14], "Chemical Engineer", "eng"),
    ([17], "Aerospace Engineer", "eng"),
    ([18], "Biomedical Engineer", "eng"),
    ([20], "Robotics Engineer", "eng"),
    ([16], "Industrial Engineer", "eng"),
    # Medicine (domain 3, subs 22-35)
    ([22, 28], "Cardiologist", "med"),
    ([22, 27], "Neurologist", "med"),
    ([22, 29], "Oncologist", "med"),
    ([22, 30], "Radiologist", "med"),
    ([22, 23], "Surgeon", "med"),
    ([22, 24], "Pediatrician", "med"),
    ([22, 26], "Psychiatrist", "med"),
    ([22, 31], "Anesthesiologist", "med"),
    ([22, 32], "Epidemiologist", "med"),
    ([22, 33], "Pharmacologist", "med"),
    ([25], "OB/GYN Physician", "med"),
    ([34], "Medical Imaging Specialist", "med"),
    # Law (domain 4, subs 36-51)
    ([36, 37], "Attorney", "law"),
    ([39, 40], "Corporate Lawyer", "law"),
    ([37, 38], "Litigation Attorney", "law"),
    ([41, 50], "IP Attorney", "law"),
    ([42, 43], "International Law Attorney", "law"),
    ([44], "Environmental Lawyer", "law"),
    ([45], "Labor Attorney", "law"),
    ([46], "Tax Attorney", "law"),
    ([47], "Family Law Attorney", "law"),
    ([48], "Immigration Attorney", "law"),
    ([36, 37, 38], "Criminal Law Professor", "law"),
    # Data Analysis (domain 5, subs 52-58)
    ([52, 54, 55], "Data Scientist", "data"),
    ([53, 55], "Predictive Analytics Specialist", "data"),
    ([54, 56], "ML Researcher", "data"),
    ([57], "Data Engineer", "data"),
    ([52, 58], "Data Analyst", "data"),
    # Finance (domain 6, subs 59-71)
    ([59, 65], "Financial Analyst", "fin"),
    ([60], "Investment Banker", "fin"),
    ([63, 64], "Risk Analyst", "fin"),
    ([64, 65], "Quantitative Analyst", "fin"),
    ([66, 67], "Accountant", "fin"),
    ([62], "Portfolio Manager", "fin"),
    ([68], "Tax Consultant", "fin"),
    ([69, 70], "Actuarial Analyst", "fin"),
    # Business Operations (domain 7, subs 72-79)
    ([72, 75], "Operations Manager", "biz"),
    ([73, 74], "Supply Chain Analyst", "biz"),
    ([76], "HR Specialist", "biz"),
    ([77], "Customer Support Manager", "biz"),
    ([78], "Business Strategy Consultant", "biz"),
    # Life Sciences (domain 8, subs 80-94)
    ([80, 81], "Molecular Biologist", "lifesci"),
    ([80, 85], "Geneticist", "lifesci"),
    ([80, 84], "Microbiologist", "lifesci"),
    ([86], "Biochemist", "lifesci"),
    ([87], "Immunologist", "lifesci"),
    ([88, 92], "Neuroscientist", "lifesci"),
    ([89], "Ecologist", "lifesci"),
    ([90], "Bioinformatics Scientist", "lifesci"),
    ([91], "Biotechnologist", "lifesci"),
    # Physical Sciences (domain 9, subs 95-105)
    ([95, 96], "Physicist", "physci"),
    ([97], "Astronomer", "physci"),
    ([98], "Chemist", "physci"),
    ([98, 103], "Materials Chemist", "physci"),
    ([99, 100], "Geologist", "physci"),
    ([101], "Meteorologist", "physci"),
    ([102], "Oceanographer", "physci"),
    # Social Sciences (domain 10, subs 106-115)
    ([106], "Economist", "socsci"),
    ([107], "Sociologist", "socsci"),
    ([108], "Psychologist", "socsci"),
    ([109], "Anthropologist", "socsci"),
    ([110, 112], "Political Scientist", "socsci"),
    ([113], "Public Policy Analyst", "socsci"),
    ([114], "Criminologist", "socsci"),
    # Arts & Design (domain 11, subs 116-128)
    ([116], "Visual Artist", "arts"),
    ([117, 119], "UX/UI Designer", "arts"),
    ([118], "Industrial Designer", "arts"),
    ([122], "Architect", "arts"),
    ([123, 124], "Illustrator", "arts"),
    ([125, 126], "Photographer", "arts"),
    ([127], "Game Designer", "arts"),
    # Humanities (domain 12, subs 129-140)
    ([129, 133], "Philosophy Professor", "hum"),
    ([130], "Historian", "hum"),
    ([131], "Literature Professor", "hum"),
    ([132], "Religious Studies Scholar", "hum"),
    ([134], "Classics Professor", "hum"),
    ([135, 136], "Cultural Studies Researcher", "hum"),
    ([138], "Archaeologist", "hum"),
    ([139], "Art Historian", "hum"),
    # Miscellaneous (domain 13, subs 141-145)
    ([141], "Educator", "misc"),
    ([142], "Communications Specialist", "misc"),
    ([143], "Librarian", "misc"),
]

# Distribution weights — more SWE and med, fewer misc
DOMAIN_WEIGHTS = {
    "swe": 30,
    "eng": 8,
    "med": 12,
    "law": 10,
    "data": 8,
    "fin": 6,
    "biz": 4,
    "lifesci": 6,
    "physci": 4,
    "socsci": 4,
    "arts": 3,
    "hum": 3,
    "misc": 2,
}

INTERNAL_ROLES_OPTIONS = [
    "{tasker}",
    "{tasker}",
    "{tasker}",
    "{tasker}",
    "{tasker}",
    "{tasker}",
    "{tasker,reviewer}",
    "{tasker,reviewer}",
    "{reviewer}",
    "{tasker}",
    None,
]

STREET_NAMES = [
    "Main St", "Oak Ave", "Park Blvd", "Elm St", "Cedar Ln", "Maple Dr",
    "Pine St", "Walnut Ave", "Market St", "Church St", "Broadway",
    "Washington Ave", "Lake Dr", "Highland Ave", "Sunset Blvd",
    "River Rd", "College Ave", "Mill St", "Spring St", "Union St",
]

EMAIL_DOMAINS = [
    "gmail.com", "gmail.com", "gmail.com", "gmail.com",  # weighted
    "outlook.com", "outlook.com",
    "yahoo.com",
    "protonmail.com",
    "icloud.com",
    "hotmail.com",
]

def sql_str(s):
    """Escape a string for SQL."""
    if s is None:
        return "NULL"
    return "'" + s.replace("'", "''") + "'"

def sql_arr(arr):
    """Format a Python list as a SQL array literal."""
    if arr is None:
        return "NULL"
    return "'{" + ",".join(str(x) for x in arr) + "}'"

def sql_text_arr(arr):
    """Format a Python list of strings as a SQL TEXT[] literal."""
    if arr is None:
        return "NULL"
    inner = ",".join(f'"{x}"' for x in arr)
    return "'{" + inner + "}'"

def generate_tasker(tid, used_emails):
    is_female = random.random() < 0.45
    first = random.choice(FIRST_NAMES_FEMALE if is_female else FIRST_NAMES_MALE)
    last = random.choice(LAST_NAMES)
    middle = random.choice(MIDDLE_INITIALS) if random.random() < 0.3 else None

    # Build unique email
    base_email = f"{first.lower().replace('-', '')}.{last.lower().replace('-', '').replace(' ', '')}@{random.choice(EMAIL_DOMAINS)}"
    email = base_email
    suffix = 2
    while email in used_emails:
        email = f"{first.lower().replace('-', '')}.{last.lower().replace('-', '').replace(' ', '')}{suffix}@{random.choice(EMAIL_DOMAINS)}"
        suffix += 1
    used_emails.add(email)

    # Location
    loc = random.choice(LOCATIONS)
    city, state, postal, country, tz = loc

    # Address
    addr1 = f"{random.randint(1, 999)} {random.choice(STREET_NAMES)}"
    addr2 = f"Apt {random.randint(1, 50)}" if random.random() < 0.25 else None

    # Hire date: 2023-01-01 to 2025-10-01
    days_offset = random.randint(0, 1000)
    base_date = 1672531200  # 2023-01-01
    import datetime
    hire = datetime.date(2023, 1, 1) + datetime.timedelta(days=days_offset)
    hire_str = hire.isoformat()

    # Status
    status = "inactive" if random.random() < 0.08 else "active"

    # Profile (weighted)
    weighted_profiles = []
    for p in PROFILES:
        w = DOMAIN_WEIGHTS.get(p[2], 1)
        weighted_profiles.extend([p] * w)
    profile = random.choice(weighted_profiles)
    subdomain_ids, job_title, _ = profile

    # Hours and rate
    if status == "inactive":
        hours = 0.0
    else:
        hours = random.choice([10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0])
    rate = round(random.uniform(25, 95), 2)

    # Languages
    base_langs = COUNTRY_LANGUAGES.get(country, [("English", "fluent")])
    langs = list(base_langs)
    # Ensure English is present
    lang_names = [l[0] for l in langs]
    if "English" not in lang_names:
        langs.append(("English", "fluent"))
    # Maybe add an extra language
    if random.random() < 0.2:
        extra = random.choice(EXTRA_LANGUAGES)
        if extra[0] not in [l[0] for l in langs]:
            langs.append(extra)

    languages = [l[0] for l in langs]
    proficiency = {l[0]: l[1] for l in langs}

    # Internal roles
    internal_roles = random.choice(INTERNAL_ROLES_OPTIONS)

    return (
        tid, first, middle, last, email, hire_str,
        addr1, addr2, city, state, postal, country, tz,
        status, job_title, subdomain_ids, hours, rate,
        languages, proficiency, internal_roles
    )

def format_insert(t):
    (tid, first, middle, last, email, hire_str,
     addr1, addr2, city, state, postal, country, tz,
     status, job_title, subdomain_ids, hours, rate,
     languages, proficiency, internal_roles) = t

    prof_json = json.dumps(proficiency)

    parts = [
        str(tid),
        sql_str(first),
        sql_str(middle),
        sql_str(last),
        sql_str(email),
        sql_str(hire_str),
        sql_str(addr1),
        sql_str(addr2),
        sql_str(city),
        sql_str(state),
        sql_str(postal),
        sql_str(country),
        sql_str(tz),
        sql_str(status),
        sql_str(job_title),
        sql_arr(subdomain_ids),
        str(hours),
        str(rate),
        sql_text_arr(languages),
        sql_str(prof_json),
        sql_str(internal_roles) if internal_roles else "NULL"
    ]
    return "(" + ", ".join(parts) + ")"

def main():
    used_emails = set()
    taskers = []
    for tid in range(21, 1129):
        taskers.append(generate_tasker(tid, used_emails))

    lines = []
    lines.append("-- Auto-generated: 1108 additional taskers (IDs 21-1128)")
    lines.append("INSERT INTO taskers (id, first_name, middle_name, last_name, email, hire_date, address_line1, address_line2, city, state_province, postal_code, location_country, location_timezone, status, external_job_title, subdomain_ids, hours_available, hourly_rate, languages, language_proficiency, internal_roles) VALUES")

    # Write in batches of 100 for readability
    batch_size = 100
    for i in range(0, len(taskers), batch_size):
        batch = taskers[i:i+batch_size]
        for j, t in enumerate(batch):
            is_last = (i + j == len(taskers) - 1)
            suffix = ";" if is_last else ","
            # Start a new INSERT every batch (except first)
            if j == 0 and i > 0:
                lines.append("")
                lines.append("INSERT INTO taskers (id, first_name, middle_name, last_name, email, hire_date, address_line1, address_line2, city, state_province, postal_code, location_country, location_timezone, status, external_job_title, subdomain_ids, hours_available, hourly_rate, languages, language_proficiency, internal_roles) VALUES")
            line = format_insert(t)
            # Last in batch but not last overall → close with semicolon and start new INSERT
            if j == len(batch) - 1 and not is_last:
                lines.append(line + ";")
            else:
                lines.append(line + suffix)

    lines.append("")
    lines.append("-- Reset sequence")
    lines.append("SELECT setval('taskers_id_seq', (SELECT MAX(id) FROM taskers));")

    with open("migrations/010_add_taskers_21_to_1128.sql", "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Generated {len(taskers)} tasker inserts")

if __name__ == "__main__":
    main()
