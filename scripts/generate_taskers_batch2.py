#!/usr/bin/env python3
"""Generate SQL migration to insert taskers 1129-3532 (2404 new taskers).

Requirements:
- Most taskers in the USA (~65%)
- ~55% have middle names
- Technical people (SWE, data, eng) concentrated in US tech hubs
"""

import random
import json
import datetime

random.seed(99)

# ─── Name pools ───────────────────────────────────────────────────────────────

FIRST_NAMES_MALE = [
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
    # Middle Eastern
    "Ahmad", "Khalid", "Tariq", "Faisal", "Samir", "Nabil", "Rashid", "Zaid",
    "Ali", "Hamza", "Karim", "Bilal", "Yousef", "Waleed", "Majid",
    # Brazilian
    "Gustavo", "Henrique", "Felipe", "Thiago", "Caio", "Bruno", "Vinicius",
    "Leonardo", "Rafael", "Bernardo", "Arthur", "Davi",
]

FIRST_NAMES_FEMALE = [
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
    "Mei", "Xiu", "Lan", "Hua", "Jing", "Yue", "Ling", "Na", "Fang", "Li",
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
    # Middle Eastern
    "Layla", "Nour", "Dalia", "Rania", "Huda", "Maryam", "Yasmin", "Salma",
    "Sara", "Lina", "Farah", "Rana", "Hala",
    # Brazilian
    "Juliana", "Larissa", "Leticia", "Rafaela", "Bianca",
    "Mariana", "Luisa", "Vitoria", "Manuela", "Clara",
]

LAST_NAMES = [
    # English / American (heavy)
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
    "Price", "Sanders", "Powell", "Russell", "Sullivan", "Fisher", "Hamilton",
    "Graham", "Wallace", "Henderson", "Cole", "Hart", "Fuller", "Wade",
    "Chambers", "Hicks", "Burns", "Dixon", "Hunt", "Palmer", "Boyd", "Mills",
    "Warren", "Fox", "Rose", "Stone", "Burke", "Dunn", "Perkins", "Gordon",
    "Marsh", "Olson", "Harvey", "Simmons", "Grant", "Logan", "Flores",
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
    "Desai", "Thakur", "Pandey", "Srivastava", "Saxena", "Bose",
    # African
    "Okafor", "Adeyemi", "Ogundimu", "Nwosu", "Ibrahim", "Diallo", "Traore",
    "Mensah", "Asante", "Boateng", "Owusu", "Abubakar", "Toure", "Bello",
    # European
    "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker",
    "Schulz", "Hoffman", "Koch", "Richter", "Wolf", "Braun", "Zimmermann",
    "Dubois", "Laurent", "Moreau", "Bernard", "Leroy", "Roux", "Girard",
    "Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo",
    "Kowalski", "Nowak", "Wisniewski", "Kaminski", "Lewandowski",
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

MIDDLE_NAMES = [
    # Full middle names (mix of common American middle names)
    "Alexander", "Andrew", "Anthony", "Benjamin", "Blake", "Bradley", "Brian",
    "Charles", "Christopher", "Daniel", "Edward", "Francis", "Grant", "Harrison",
    "Henry", "Howard", "Isaac", "Jackson", "James", "John", "Joseph", "Kenneth",
    "Lawrence", "Lee", "Louis", "Marcus", "Michael", "Nathan", "Oliver", "Patrick",
    "Paul", "Philip", "Raymond", "Robert", "Samuel", "Scott", "Thomas", "Vincent",
    "Walter", "Wayne", "Wesley",
    # Female middle names
    "Anne", "Beth", "Catherine", "Claire", "Dawn", "Diane", "Eleanor", "Faith",
    "Grace", "Hope", "Irene", "Jane", "Jean", "Joy", "June", "Kate", "Kay",
    "Lauren", "Louise", "Lynn", "Mae", "Marie", "Nicole", "Paige", "Quinn",
    "Renee", "Rose", "Ruth", "Sue", "Victoria",
]

MIDDLE_INITIALS = list("ABCDEFGHJKLMNPRSTW")

# ─── Location pools ──────────────────────────────────────────────────────────

# US Tech Hubs — used for technical profiles
US_TECH_HUBS = [
    # SF — heavy concentration (repeated for weighting)
    ("San Francisco", "CA", "94105", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94107", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94103", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94102", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94110", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94114", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94117", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94109", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94108", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94133", "United States", "America/Los_Angeles"),
    ("San Francisco", "CA", "94158", "United States", "America/Los_Angeles"),
    # South Bay — Los Altos Hills & neighbors (dense tech cluster)
    ("Los Altos Hills", "CA", "94022", "United States", "America/Los_Angeles"),
    ("Los Altos Hills", "CA", "94022", "United States", "America/Los_Angeles"),
    ("Los Altos Hills", "CA", "94022", "United States", "America/Los_Angeles"),
    ("Los Altos Hills", "CA", "94022", "United States", "America/Los_Angeles"),
    ("Los Altos", "CA", "94024", "United States", "America/Los_Angeles"),
    ("Los Altos", "CA", "94024", "United States", "America/Los_Angeles"),
    ("Los Altos", "CA", "94024", "United States", "America/Los_Angeles"),
    ("Palo Alto", "CA", "94301", "United States", "America/Los_Angeles"),
    ("Palo Alto", "CA", "94304", "United States", "America/Los_Angeles"),
    ("Palo Alto", "CA", "94306", "United States", "America/Los_Angeles"),
    ("Mountain View", "CA", "94043", "United States", "America/Los_Angeles"),
    ("Mountain View", "CA", "94041", "United States", "America/Los_Angeles"),
    ("Sunnyvale", "CA", "94086", "United States", "America/Los_Angeles"),
    ("Sunnyvale", "CA", "94087", "United States", "America/Los_Angeles"),
    ("Cupertino", "CA", "95014", "United States", "America/Los_Angeles"),
    ("Saratoga", "CA", "95070", "United States", "America/Los_Angeles"),
    ("San Jose", "CA", "95113", "United States", "America/Los_Angeles"),
    ("San Jose", "CA", "95110", "United States", "America/Los_Angeles"),
    ("San Jose", "CA", "95125", "United States", "America/Los_Angeles"),
    ("Santa Clara", "CA", "95050", "United States", "America/Los_Angeles"),
    ("Menlo Park", "CA", "94025", "United States", "America/Los_Angeles"),
    ("Redwood City", "CA", "94063", "United States", "America/Los_Angeles"),
    ("Woodside", "CA", "94062", "United States", "America/Los_Angeles"),
    ("Portola Valley", "CA", "94028", "United States", "America/Los_Angeles"),
    ("Campbell", "CA", "95008", "United States", "America/Los_Angeles"),
    ("Milpitas", "CA", "95035", "United States", "America/Los_Angeles"),
    ("Fremont", "CA", "94536", "United States", "America/Los_Angeles"),
    # East Bay
    ("Oakland", "CA", "94612", "United States", "America/Los_Angeles"),
    ("Berkeley", "CA", "94704", "United States", "America/Los_Angeles"),
    # NYC — heavy concentration
    ("New York", "NY", "10001", "United States", "America/New_York"),
    ("New York", "NY", "10003", "United States", "America/New_York"),
    ("New York", "NY", "10011", "United States", "America/New_York"),
    ("New York", "NY", "10012", "United States", "America/New_York"),
    ("New York", "NY", "10013", "United States", "America/New_York"),
    ("New York", "NY", "10014", "United States", "America/New_York"),
    ("New York", "NY", "10016", "United States", "America/New_York"),
    ("New York", "NY", "10018", "United States", "America/New_York"),
    ("New York", "NY", "10022", "United States", "America/New_York"),
    ("New York", "NY", "10036", "United States", "America/New_York"),
    ("New York", "NY", "10038", "United States", "America/New_York"),
    ("Brooklyn", "NY", "11201", "United States", "America/New_York"),
    ("Brooklyn", "NY", "11215", "United States", "America/New_York"),
    ("Brooklyn", "NY", "11211", "United States", "America/New_York"),
    ("Jersey City", "NJ", "07302", "United States", "America/New_York"),
    ("Hoboken", "NJ", "07030", "United States", "America/New_York"),
    # Seattle — heavy concentration
    ("Seattle", "WA", "98101", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98102", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98103", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98104", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98105", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98109", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98112", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98115", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98122", "United States", "America/Los_Angeles"),
    ("Bellevue", "WA", "98004", "United States", "America/Los_Angeles"),
    ("Bellevue", "WA", "98006", "United States", "America/Los_Angeles"),
    ("Redmond", "WA", "98052", "United States", "America/Los_Angeles"),
    ("Kirkland", "WA", "98033", "United States", "America/Los_Angeles"),
    # Austin
    ("Austin", "TX", "78701", "United States", "America/Chicago"),
    ("Austin", "TX", "78702", "United States", "America/Chicago"),
    ("Austin", "TX", "78704", "United States", "America/Chicago"),
    ("Austin", "TX", "78745", "United States", "America/Chicago"),
    # Boston
    ("Boston", "MA", "02101", "United States", "America/New_York"),
    ("Boston", "MA", "02110", "United States", "America/New_York"),
    ("Cambridge", "MA", "02139", "United States", "America/New_York"),
    ("Cambridge", "MA", "02142", "United States", "America/New_York"),
    ("Somerville", "MA", "02143", "United States", "America/New_York"),
    # Denver / Boulder
    ("Denver", "CO", "80202", "United States", "America/Denver"),
    ("Denver", "CO", "80203", "United States", "America/Denver"),
    ("Boulder", "CO", "80302", "United States", "America/Denver"),
    # LA
    ("Los Angeles", "CA", "90001", "United States", "America/Los_Angeles"),
    ("Los Angeles", "CA", "90024", "United States", "America/Los_Angeles"),
    ("Santa Monica", "CA", "90401", "United States", "America/Los_Angeles"),
    # Other tech-adjacent
    ("San Diego", "CA", "92101", "United States", "America/Los_Angeles"),
    ("Portland", "OR", "97201", "United States", "America/Los_Angeles"),
    ("Portland", "OR", "97209", "United States", "America/Los_Angeles"),
    ("Raleigh", "NC", "27601", "United States", "America/New_York"),
    ("Durham", "NC", "27701", "United States", "America/New_York"),
    ("Atlanta", "GA", "30308", "United States", "America/New_York"),
    ("Atlanta", "GA", "30309", "United States", "America/New_York"),
    ("Chicago", "IL", "60601", "United States", "America/Chicago"),
    ("Chicago", "IL", "60607", "United States", "America/Chicago"),
    ("Pittsburgh", "PA", "15213", "United States", "America/New_York"),
    ("Salt Lake City", "UT", "84101", "United States", "America/Denver"),
    ("Washington", "DC", "20001", "United States", "America/New_York"),
    ("Arlington", "VA", "22201", "United States", "America/New_York"),
]

# Other US locations — for non-technical profiles
US_OTHER = [
    ("New York", "NY", "10001", "United States", "America/New_York"),
    ("New York", "NY", "10021", "United States", "America/New_York"),
    ("Brooklyn", "NY", "11201", "United States", "America/New_York"),
    ("Boston", "MA", "02101", "United States", "America/New_York"),
    ("Philadelphia", "PA", "19103", "United States", "America/New_York"),
    ("Philadelphia", "PA", "19106", "United States", "America/New_York"),
    ("Washington", "DC", "20001", "United States", "America/New_York"),
    ("Washington", "DC", "20036", "United States", "America/New_York"),
    ("Baltimore", "MD", "21201", "United States", "America/New_York"),
    ("Atlanta", "GA", "30301", "United States", "America/New_York"),
    ("Atlanta", "GA", "30308", "United States", "America/New_York"),
    ("Miami", "FL", "33101", "United States", "America/New_York"),
    ("Miami", "FL", "33131", "United States", "America/New_York"),
    ("Orlando", "FL", "32801", "United States", "America/New_York"),
    ("Tampa", "FL", "33602", "United States", "America/New_York"),
    ("Charlotte", "NC", "28202", "United States", "America/New_York"),
    ("Raleigh", "NC", "27601", "United States", "America/New_York"),
    ("Nashville", "TN", "37201", "United States", "America/Chicago"),
    ("Chicago", "IL", "60601", "United States", "America/Chicago"),
    ("Chicago", "IL", "60614", "United States", "America/Chicago"),
    ("Minneapolis", "MN", "55401", "United States", "America/Chicago"),
    ("St Louis", "MO", "63101", "United States", "America/Chicago"),
    ("Kansas City", "MO", "64101", "United States", "America/Chicago"),
    ("Houston", "TX", "77001", "United States", "America/Chicago"),
    ("Houston", "TX", "77002", "United States", "America/Chicago"),
    ("Dallas", "TX", "75201", "United States", "America/Chicago"),
    ("Dallas", "TX", "75202", "United States", "America/Chicago"),
    ("San Antonio", "TX", "78205", "United States", "America/Chicago"),
    ("Austin", "TX", "78701", "United States", "America/Chicago"),
    ("Denver", "CO", "80202", "United States", "America/Denver"),
    ("Phoenix", "AZ", "85001", "United States", "America/Denver"),
    ("Tucson", "AZ", "85701", "United States", "America/Denver"),
    ("Salt Lake City", "UT", "84101", "United States", "America/Denver"),
    ("Albuquerque", "NM", "87101", "United States", "America/Denver"),
    ("San Francisco", "CA", "94105", "United States", "America/Los_Angeles"),
    ("Los Angeles", "CA", "90001", "United States", "America/Los_Angeles"),
    ("Los Angeles", "CA", "90015", "United States", "America/Los_Angeles"),
    ("San Diego", "CA", "92101", "United States", "America/Los_Angeles"),
    ("Sacramento", "CA", "95814", "United States", "America/Los_Angeles"),
    ("Seattle", "WA", "98101", "United States", "America/Los_Angeles"),
    ("Portland", "OR", "97201", "United States", "America/Los_Angeles"),
    ("Las Vegas", "NV", "89101", "United States", "America/Los_Angeles"),
    ("Honolulu", "HI", "96813", "United States", "Pacific/Honolulu"),
    ("Anchorage", "AK", "99501", "United States", "America/Anchorage"),
    ("Detroit", "MI", "48201", "United States", "America/New_York"),
    ("Columbus", "OH", "43215", "United States", "America/New_York"),
    ("Indianapolis", "IN", "46204", "United States", "America/New_York"),
    ("Milwaukee", "WI", "53202", "United States", "America/Chicago"),
    ("New Orleans", "LA", "70112", "United States", "America/Chicago"),
    ("Richmond", "VA", "23219", "United States", "America/New_York"),
    ("Hartford", "CT", "06103", "United States", "America/New_York"),
    ("Providence", "RI", "02903", "United States", "America/New_York"),
    ("Ann Arbor", "MI", "48104", "United States", "America/New_York"),
    ("Madison", "WI", "53703", "United States", "America/Chicago"),
]

# International locations
INTL_LOCATIONS = [
    # Canada
    ("Toronto", "ON", "M5V 3L9", "Canada", "America/Toronto"),
    ("Vancouver", "BC", "V6B 1A1", "Canada", "America/Vancouver"),
    ("Montreal", "QC", "H2X 1Y4", "Canada", "America/Toronto"),
    ("Ottawa", "ON", "K1P 1J1", "Canada", "America/Toronto"),
    ("Calgary", "AB", "T2P 1J9", "Canada", "America/Edmonton"),
    # UK
    ("London", "England", "EC1A 1BB", "United Kingdom", "Europe/London"),
    ("London", "England", "SW1A 1AA", "United Kingdom", "Europe/London"),
    ("Manchester", "England", "M1 1AE", "United Kingdom", "Europe/London"),
    ("Edinburgh", "Scotland", "EH1 1YZ", "United Kingdom", "Europe/London"),
    ("Cambridge", "England", "CB2 1TN", "United Kingdom", "Europe/London"),
    ("Oxford", "England", "OX1 1DP", "United Kingdom", "Europe/London"),
    ("Bristol", "England", "BS1 1AA", "United Kingdom", "Europe/London"),
    # Germany
    ("Berlin", "Berlin", "10115", "Germany", "Europe/Berlin"),
    ("Munich", "Bavaria", "80331", "Germany", "Europe/Berlin"),
    ("Hamburg", "Hamburg", "20095", "Germany", "Europe/Berlin"),
    ("Frankfurt", "Hesse", "60311", "Germany", "Europe/Berlin"),
    # France
    ("Paris", "Ile-de-France", "75001", "France", "Europe/Paris"),
    ("Lyon", "Auvergne-Rhone-Alpes", "69001", "France", "Europe/Paris"),
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
    # Sweden / Switzerland
    ("Stockholm", "Stockholm", "111 51", "Sweden", "Europe/Stockholm"),
    ("Zurich", "Zurich", "8001", "Switzerland", "Europe/Zurich"),
    # India (tech hub — heavy)
    ("Bangalore", "Karnataka", "560001", "India", "Asia/Kolkata"),
    ("Bangalore", "Karnataka", "560034", "India", "Asia/Kolkata"),
    ("Bangalore", "Karnataka", "560066", "India", "Asia/Kolkata"),
    ("Bangalore", "Karnataka", "560103", "India", "Asia/Kolkata"),
    ("Hyderabad", "Telangana", "500001", "India", "Asia/Kolkata"),
    ("Hyderabad", "Telangana", "500081", "India", "Asia/Kolkata"),
    ("Pune", "Maharashtra", "411001", "India", "Asia/Kolkata"),
    ("Pune", "Maharashtra", "411045", "India", "Asia/Kolkata"),
    ("Mumbai", "Maharashtra", "400001", "India", "Asia/Kolkata"),
    ("Mumbai", "Maharashtra", "400076", "India", "Asia/Kolkata"),
    ("Delhi", "Delhi", "110001", "India", "Asia/Kolkata"),
    ("Gurgaon", "Haryana", "122001", "India", "Asia/Kolkata"),
    ("Noida", "Uttar Pradesh", "201301", "India", "Asia/Kolkata"),
    ("Chennai", "Tamil Nadu", "600001", "India", "Asia/Kolkata"),
    ("Chennai", "Tamil Nadu", "600042", "India", "Asia/Kolkata"),
    ("Kolkata", "West Bengal", "700001", "India", "Asia/Kolkata"),
    # Japan
    ("Tokyo", "Tokyo", "100-0001", "Japan", "Asia/Tokyo"),
    ("Osaka", "Osaka", "530-0001", "Japan", "Asia/Tokyo"),
    # South Korea
    ("Seoul", "Seoul", "04524", "South Korea", "Asia/Seoul"),
    # China
    ("Beijing", "Beijing", "100000", "China", "Asia/Shanghai"),
    ("Shanghai", "Shanghai", "200000", "China", "Asia/Shanghai"),
    ("Shenzhen", "Guangdong", "518000", "China", "Asia/Shanghai"),
    # Singapore / Australia
    ("Singapore", "Singapore", "018956", "Singapore", "Asia/Singapore"),
    ("Sydney", "NSW", "2000", "Australia", "Australia/Sydney"),
    ("Melbourne", "VIC", "3000", "Australia", "Australia/Melbourne"),
    # Latin America
    ("Sao Paulo", "SP", "01310-100", "Brazil", "America/Sao_Paulo"),
    ("Rio de Janeiro", "RJ", "20040-020", "Brazil", "America/Sao_Paulo"),
    ("Mexico City", "CDMX", "06600", "Mexico", "America/Mexico_City"),
    ("Guadalajara", "Jalisco", "44100", "Mexico", "America/Mexico_City"),
    ("Bogota", "Cundinamarca", "110111", "Colombia", "America/Bogota"),
    ("Buenos Aires", "Buenos Aires", "C1002", "Argentina", "America/Argentina/Buenos_Aires"),
    ("Santiago", "Santiago", "8320000", "Chile", "America/Santiago"),
    # Africa
    ("Lagos", "Lagos", "101233", "Nigeria", "Africa/Lagos"),
    ("Nairobi", "Nairobi", "00100", "Kenya", "Africa/Nairobi"),
    ("Cape Town", "Western Cape", "8001", "South Africa", "Africa/Johannesburg"),
    ("Cairo", "Cairo", "11511", "Egypt", "Africa/Cairo"),
    # Middle East
    ("Dubai", "Dubai", "00000", "United Arab Emirates", "Asia/Dubai"),
    ("Tel Aviv", "Tel Aviv", "6100000", "Israel", "Asia/Jerusalem"),
    ("Istanbul", "Istanbul", "34000", "Turkey", "Europe/Istanbul"),
    # Southeast Asia
    ("Manila", "Metro Manila", "1000", "Philippines", "Asia/Manila"),
    ("Ho Chi Minh City", "Ho Chi Minh", "700000", "Vietnam", "Asia/Ho_Chi_Minh"),
    ("Taipei", "Taipei", "100", "Taiwan", "Asia/Taipei"),
    ("Bangkok", "Bangkok", "10100", "Thailand", "Asia/Bangkok"),
    ("Jakarta", "DKI Jakarta", "10110", "Indonesia", "Asia/Jakarta"),
    # Pakistan
    ("Karachi", "Sindh", "74200", "Pakistan", "Asia/Karachi"),
    ("Lahore", "Punjab", "54000", "Pakistan", "Asia/Karachi"),
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

# Non-English-speaking hubs — India, China, Russia (a few hundred will land here)
NON_ENGLISH_HUBS = [
    # India
    ("Bangalore", "Karnataka", "560001", "India", "Asia/Kolkata"),
    ("Bangalore", "Karnataka", "560034", "India", "Asia/Kolkata"),
    ("Bangalore", "Karnataka", "560066", "India", "Asia/Kolkata"),
    ("Hyderabad", "Telangana", "500001", "India", "Asia/Kolkata"),
    ("Hyderabad", "Telangana", "500081", "India", "Asia/Kolkata"),
    ("Pune", "Maharashtra", "411001", "India", "Asia/Kolkata"),
    ("Mumbai", "Maharashtra", "400001", "India", "Asia/Kolkata"),
    ("Delhi", "Delhi", "110001", "India", "Asia/Kolkata"),
    ("Gurgaon", "Haryana", "122001", "India", "Asia/Kolkata"),
    ("Noida", "Uttar Pradesh", "201301", "India", "Asia/Kolkata"),
    ("Chennai", "Tamil Nadu", "600001", "India", "Asia/Kolkata"),
    ("Kolkata", "West Bengal", "700001", "India", "Asia/Kolkata"),
    ("Ahmedabad", "Gujarat", "380001", "India", "Asia/Kolkata"),
    ("Jaipur", "Rajasthan", "302001", "India", "Asia/Kolkata"),
    ("Lucknow", "Uttar Pradesh", "226001", "India", "Asia/Kolkata"),
    ("Chandigarh", "Chandigarh", "160001", "India", "Asia/Kolkata"),
    # China
    ("Beijing", "Beijing", "100000", "China", "Asia/Shanghai"),
    ("Beijing", "Beijing", "100080", "China", "Asia/Shanghai"),
    ("Shanghai", "Shanghai", "200000", "China", "Asia/Shanghai"),
    ("Shanghai", "Shanghai", "200040", "China", "Asia/Shanghai"),
    ("Shenzhen", "Guangdong", "518000", "China", "Asia/Shanghai"),
    ("Shenzhen", "Guangdong", "518040", "China", "Asia/Shanghai"),
    ("Hangzhou", "Zhejiang", "310000", "China", "Asia/Shanghai"),
    ("Guangzhou", "Guangdong", "510000", "China", "Asia/Shanghai"),
    ("Chengdu", "Sichuan", "610000", "China", "Asia/Shanghai"),
    ("Wuhan", "Hubei", "430000", "China", "Asia/Shanghai"),
    ("Nanjing", "Jiangsu", "210000", "China", "Asia/Shanghai"),
    ("Xiamen", "Fujian", "361000", "China", "Asia/Shanghai"),
    # Russia
    ("Moscow", "Moscow", "101000", "Russia", "Europe/Moscow"),
    ("Moscow", "Moscow", "105064", "Russia", "Europe/Moscow"),
    ("Moscow", "Moscow", "119034", "Russia", "Europe/Moscow"),
    ("St Petersburg", "St Petersburg", "190000", "Russia", "Europe/Moscow"),
    ("St Petersburg", "St Petersburg", "191186", "Russia", "Europe/Moscow"),
    ("Novosibirsk", "Novosibirsk Oblast", "630099", "Russia", "Asia/Novosibirsk"),
    ("Yekaterinburg", "Sverdlovsk Oblast", "620000", "Russia", "Asia/Yekaterinburg"),
    ("Kazan", "Tatarstan", "420000", "Russia", "Europe/Moscow"),
    ("Nizhny Novgorod", "Nizhny Novgorod Oblast", "603000", "Russia", "Europe/Moscow"),
]

TECHNICAL_DOMAINS = {"swe", "data", "eng"}

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
    ([1, 10], "Software Engineer", "swe"),
    ([2, 3], "AI/ML Full Stack Engineer", "swe"),
    ([4, 8], "Frontend & Mobile Developer", "swe"),
    ([5, 7], "Infrastructure Engineer", "swe"),
    ([1, 2, 5], "Backend ML Engineer", "swe"),
    # Other Engineering (domain 2, subs 11-21)
    ([11], "Mechanical Engineer", "eng"),
    ([12], "Electrical Engineer", "eng"),
    ([13], "Civil Engineer", "eng"),
    ([14], "Chemical Engineer", "eng"),
    ([17], "Aerospace Engineer", "eng"),
    ([18], "Biomedical Engineer", "eng"),
    ([20], "Robotics Engineer", "eng"),
    ([16], "Industrial Engineer", "eng"),
    ([15], "Materials Engineer", "eng"),
    ([19], "Environmental Engineer", "eng"),
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
    ([22], "General Practitioner", "med"),
    ([27, 88], "Neurologist", "med"),
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
    ([49], "Administrative Law Attorney", "law"),
    ([40, 39, 50], "Tech Corporate Counsel", "law"),
    # Data Analysis (domain 5, subs 52-58)
    ([52, 54, 55], "Data Scientist", "data"),
    ([53, 55], "Predictive Analytics Specialist", "data"),
    ([54, 56], "ML Researcher", "data"),
    ([57], "Data Engineer", "data"),
    ([52, 58], "Data Analyst", "data"),
    ([54, 55, 57], "Senior Data Engineer", "data"),
    ([52, 53], "Analytics Engineer", "data"),
    # Finance (domain 6, subs 59-71)
    ([59, 65], "Financial Analyst", "fin"),
    ([60], "Investment Banker", "fin"),
    ([63, 64], "Risk Analyst", "fin"),
    ([64, 65], "Quantitative Analyst", "fin"),
    ([66, 67], "Accountant", "fin"),
    ([62], "Portfolio Manager", "fin"),
    ([68], "Tax Consultant", "fin"),
    ([69, 70], "Actuarial Analyst", "fin"),
    ([59, 61], "Asset Manager", "fin"),
    # Business Operations (domain 7, subs 72-79)
    ([72, 75], "Operations Manager", "biz"),
    ([73, 74], "Supply Chain Analyst", "biz"),
    ([76], "HR Specialist", "biz"),
    ([77], "Customer Support Manager", "biz"),
    ([78], "Business Strategy Consultant", "biz"),
    ([72, 78], "COO", "biz"),
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
    ([93], "Pharmacologist", "lifesci"),
    # Physical Sciences (domain 9, subs 95-105)
    ([95, 96], "Physicist", "physci"),
    ([97], "Astronomer", "physci"),
    ([98], "Chemist", "physci"),
    ([98, 103], "Materials Chemist", "physci"),
    ([99, 100], "Geologist", "physci"),
    ([101], "Meteorologist", "physci"),
    ([102], "Oceanographer", "physci"),
    ([104], "Acoustics Engineer", "physci"),
    # Social Sciences (domain 10, subs 106-115)
    ([106], "Economist", "socsci"),
    ([107], "Sociologist", "socsci"),
    ([108], "Psychologist", "socsci"),
    ([109], "Anthropologist", "socsci"),
    ([110, 112], "Political Scientist", "socsci"),
    ([113], "Public Policy Analyst", "socsci"),
    ([114], "Criminologist", "socsci"),
    ([111], "Geographer", "socsci"),
    # Arts & Design (domain 11, subs 116-128)
    ([116], "Visual Artist", "arts"),
    ([117, 119], "UX/UI Designer", "arts"),
    ([118], "Industrial Designer", "arts"),
    ([122], "Architect", "arts"),
    ([123, 124], "Illustrator", "arts"),
    ([125, 126], "Photographer", "arts"),
    ([127], "Game Designer", "arts"),
    ([120], "Fashion Designer", "arts"),
    ([128], "Creative Director", "arts"),
    # Humanities (domain 12, subs 129-140)
    ([129, 133], "Philosophy Professor", "hum"),
    ([130], "Historian", "hum"),
    ([131], "Literature Professor", "hum"),
    ([132], "Religious Studies Scholar", "hum"),
    ([134], "Classics Professor", "hum"),
    ([135, 136], "Cultural Studies Researcher", "hum"),
    ([138], "Archaeologist", "hum"),
    ([139], "Art Historian", "hum"),
    ([137], "Area Studies Researcher", "hum"),
    ([140], "Humanities Researcher", "hum"),
    # Miscellaneous (domain 13, subs 141-145)
    ([141], "Educator", "misc"),
    ([142], "Communications Specialist", "misc"),
    ([143], "Librarian", "misc"),
    ([144], "Artisan", "misc"),
]

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
    "1st Ave", "2nd Ave", "3rd St", "4th St", "5th Ave",
    "Ridge Rd", "Vine St", "Chestnut St", "Poplar Ave", "Birch Ln",
]

EMAIL_DOMAINS = [
    "gmail.com", "gmail.com", "gmail.com", "gmail.com",
    "outlook.com", "outlook.com",
    "yahoo.com",
    "protonmail.com",
    "icloud.com",
    "hotmail.com",
]


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


# Pre-build weighted profiles list once
_weighted_profiles = []
for p in PROFILES:
    w = DOMAIN_WEIGHTS.get(p[2], 1)
    _weighted_profiles.extend([p] * w)


def pick_location(domain_label):
    """Pick a location.

    Technical profiles → heavy US tech hubs + India tech cities.
    ~12% of ALL taskers land in non-English hubs (India/China/Russia).
    Overall USA target: ~65%.
    """
    is_tech = domain_label in TECHNICAL_DOMAINS
    r = random.random()

    if is_tech:
        # 65% US tech hub, 8% US other, 15% India/China/Russia, 12% other intl
        if r < 0.65:
            return random.choice(US_TECH_HUBS)
        elif r < 0.73:
            return random.choice(US_OTHER)
        elif r < 0.88:
            return random.choice(NON_ENGLISH_HUBS)
        else:
            return random.choice(INTL_LOCATIONS)
    else:
        # 50% US other, 8% US tech hub, 10% India/China/Russia, 32% other intl
        if r < 0.50:
            return random.choice(US_OTHER)
        elif r < 0.58:
            return random.choice(US_TECH_HUBS)
        elif r < 0.68:
            return random.choice(NON_ENGLISH_HUBS)
        else:
            return random.choice(INTL_LOCATIONS)


def generate_tasker(tid, used_emails):
    is_female = random.random() < 0.45
    first = random.choice(FIRST_NAMES_FEMALE if is_female else FIRST_NAMES_MALE)
    last = random.choice(LAST_NAMES)

    # ~55% get a middle name (mix of full names and initials)
    if random.random() < 0.55:
        if random.random() < 0.4:
            middle = random.choice(MIDDLE_INITIALS)
        else:
            middle = random.choice(MIDDLE_NAMES)
    else:
        middle = None

    # Unique email
    first_clean = first.lower().replace('-', '').replace("'", '')
    last_clean = last.lower().replace('-', '').replace(' ', '').replace("'", '')
    base = f"{first_clean}.{last_clean}"
    email_domain = random.choice(EMAIL_DOMAINS)
    email = f"{base}@{email_domain}"
    suffix = 2
    while email in used_emails:
        email = f"{base}{suffix}@{random.choice(EMAIL_DOMAINS)}"
        suffix += 1
    used_emails.add(email)

    # Profile (weighted by domain)
    profile = random.choice(_weighted_profiles)
    subdomain_ids, job_title, domain_label = profile

    # Location (tech people → US hubs)
    city, state, postal, country, tz = pick_location(domain_label)

    # Address
    addr1 = f"{random.randint(1, 9999)} {random.choice(STREET_NAMES)}"
    addr2 = f"Apt {random.randint(1, 200)}" if random.random() < 0.3 else None

    # Hire date: 2023-01-01 to 2025-11-01
    hire = datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 1035))

    # Status
    status = "inactive" if random.random() < 0.07 else "active"

    # Hours and rate
    hours = 0.0 if status == "inactive" else random.choice([10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0])
    rate = round(random.uniform(25, 95), 2)

    # Languages — non-English hub countries sometimes don't speak English
    base_langs = list(COUNTRY_LANGUAGES.get(country, [("English", "fluent")]))
    lang_names = {l[0] for l in base_langs}
    if "English" not in lang_names:
        # People in India/China/Russia: 70% speak English, 30% don't
        if country in ("India", "China", "Russia"):
            if random.random() < 0.70:
                prof = random.choice(["fluent", "intermediate"])
                base_langs.append(("English", prof))
        else:
            base_langs.append(("English", "fluent"))
    # ~25% chance of an extra language
    if random.random() < 0.25:
        extra = random.choice(EXTRA_LANGUAGES)
        if extra[0] not in {l[0] for l in base_langs}:
            base_langs.append(extra)

    languages = [l[0] for l in base_langs]
    proficiency = {l[0]: l[1] for l in base_langs}

    internal_roles = random.choice(INTERNAL_ROLES_OPTIONS)

    return (
        tid, first, middle, last, email, hire.isoformat(),
        addr1, addr2, city, state, postal, country, tz,
        status, job_title, subdomain_ids, hours, rate,
        languages, proficiency, internal_roles
    )


def format_insert(t):
    (tid, first, middle, last, email, hire_str,
     addr1, addr2, city, state, postal, country, tz,
     status, job_title, subdomain_ids, hours, rate,
     languages, proficiency, internal_roles) = t

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
        sql_str(json.dumps(proficiency)),
        sql_str(internal_roles) if internal_roles else "NULL",
    ]
    return "(" + ", ".join(parts) + ")"


def main():
    used_emails = set()
    taskers = []
    for tid in range(1129, 3533):
        taskers.append(generate_tasker(tid, used_emails))

    cols = "id, first_name, middle_name, last_name, email, hire_date, address_line1, address_line2, city, state_province, postal_code, location_country, location_timezone, status, external_job_title, subdomain_ids, hours_available, hourly_rate, languages, language_proficiency, internal_roles"
    header = f"INSERT INTO taskers ({cols}) VALUES"

    lines = [f"-- Auto-generated: 2404 additional taskers (IDs 1129-3532)"]
    batch_size = 200
    for i in range(0, len(taskers), batch_size):
        batch = taskers[i : i + batch_size]
        lines.append("")
        lines.append(header)
        for j, t in enumerate(batch):
            comma = "," if j < len(batch) - 1 else ";"
            lines.append(format_insert(t) + comma)

    lines.append("")
    lines.append("-- Reset sequence")
    lines.append("SELECT setval('taskers_id_seq', (SELECT MAX(id) FROM taskers));")

    outfile = "migrations/011_add_taskers_1129_to_3532.sql"
    with open(outfile, "w") as f:
        f.write("\n".join(lines) + "\n")

    # Print stats
    countries = {}
    middle_count = 0
    for t in taskers:
        c = t[11]  # country
        countries[c] = countries.get(c, 0) + 1
        if t[2] is not None:
            middle_count += 1

    us_count = countries.get("United States", 0)
    print(f"Generated {len(taskers)} taskers → {outfile}")
    print(f"USA: {us_count} ({100*us_count/len(taskers):.1f}%)")
    print(f"Middle names: {middle_count} ({100*middle_count/len(taskers):.1f}%)")
    print(f"Countries: {len(countries)}")
    for c, n in sorted(countries.items(), key=lambda x: -x[1])[:10]:
        print(f"  {c}: {n}")


if __name__ == "__main__":
    main()
