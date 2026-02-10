#!/usr/bin/env python3
"""Generate SQL migration to backfill education detail fields for all taskers.

Works backwards from each tasker's age, highest_education_level, domain, and
country to generate realistic undergrad/grad school, major, and graduation years.
"""

import random
import subprocess

random.seed(2025)

CONN_STR = "postgresql://neondb_owner:npg_H6ces9NyVEtw@ep-broad-haze-aifq29n7.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# ─── Job title → domain (same as demographics script) ────────────────────────

JOB_DOMAIN = {
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
    "Mechanical Engineer": "eng", "Electrical Engineer": "eng", "Civil Engineer": "eng",
    "Chemical Engineer": "eng", "Aerospace Engineer": "eng", "Biomedical Engineer": "eng",
    "Robotics Engineer": "eng", "Industrial Engineer": "eng", "Materials Engineer": "eng",
    "Environmental Engineer": "eng", "Design Engineer": "eng",
    "Cardiologist": "med", "Neurologist": "med", "Oncologist": "med",
    "Radiologist": "med", "Surgeon": "med", "Pediatrician": "med",
    "Psychiatrist": "med", "Anesthesiologist": "med", "Epidemiologist": "med",
    "Pharmacologist": "med", "OB/GYN Physician": "med",
    "Medical Imaging Specialist": "med", "General Practitioner": "med",
    "Attorney": "law", "Corporate Lawyer": "law", "Litigation Attorney": "law",
    "IP Attorney": "law", "International Law Attorney": "law",
    "Environmental Lawyer": "law", "Labor Attorney": "law", "Tax Attorney": "law",
    "Family Law Attorney": "law", "Immigration Attorney": "law",
    "Criminal Law Professor": "law", "Administrative Law Attorney": "law",
    "Tech Corporate Counsel": "law", "Human Rights & Immigration Lawyer": "law",
    "Data Scientist": "data", "Predictive Analytics Specialist": "data",
    "ML Researcher": "data", "Data Engineer": "data", "Data Analyst": "data",
    "Senior Data Engineer": "data", "Analytics Engineer": "data",
    "Financial Data Scientist": "data", "Financial Data Engineer": "data",
    "Computational Scientist": "data", "Computational Genomics Researcher": "data",
    "Applied Mathematician": "data", "Mathematical Physicist": "data",
    "Financial Analyst": "fin", "Investment Banker": "fin", "Risk Analyst": "fin",
    "Quantitative Analyst": "fin", "Accountant": "fin", "Portfolio Manager": "fin",
    "Tax Consultant": "fin", "Actuarial Analyst": "fin", "Asset Manager": "fin",
    "Investment Banking Analyst": "fin", "Portfolio Quant": "fin",
    "Quantitative Developer": "fin",
    "Operations Manager": "biz", "Supply Chain Analyst": "biz",
    "HR Specialist": "biz", "Customer Support Manager": "biz",
    "Business Strategy Consultant": "biz", "COO": "biz",
    "Molecular Biologist": "lifesci", "Geneticist": "lifesci",
    "Microbiologist": "lifesci", "Biochemist": "lifesci", "Immunologist": "lifesci",
    "Neuroscientist": "lifesci", "Ecologist": "lifesci",
    "Bioinformatics Scientist": "lifesci", "Biotechnologist": "lifesci",
    "Cell Biologist": "lifesci",
    "Physicist": "physci", "Astronomer": "physci", "Chemist": "physci",
    "Materials Chemist": "physci", "Geologist": "physci", "Meteorologist": "physci",
    "Oceanographer": "physci", "Acoustics Engineer": "physci",
    "Astrophysicist": "physci", "Theoretical Physicist": "physci",
    "Materials Scientist": "physci",
    "Economist": "socsci", "Sociologist": "socsci", "Psychologist": "socsci",
    "Anthropologist": "socsci", "Political Scientist": "socsci",
    "Public Policy Analyst": "socsci", "Criminologist": "socsci",
    "Geographer": "socsci",
    "Visual Artist": "arts", "UX/UI Designer": "arts", "Industrial Designer": "arts",
    "Architect": "arts", "Illustrator": "arts", "Photographer": "arts",
    "Game Designer": "arts", "Fashion Designer": "arts", "Creative Director": "arts",
    "Senior Product Designer": "arts", "Animation & Game Artist": "arts",
    "Mobile UX Designer": "arts", "Visual & Graphic Designer": "arts",
    "Industrial Design Architect": "arts", "Creative Photographer": "arts",
    "UX Designer": "arts",
    "Philosophy Professor": "hum", "Historian": "hum", "Literature Professor": "hum",
    "Religious Studies Scholar": "hum", "Classics Professor": "hum",
    "Cultural Studies Researcher": "hum", "Archaeologist": "hum",
    "Art Historian": "hum", "Area Studies Researcher": "hum",
    "Humanities Researcher": "hum", "Ethics Professor": "hum",
    "European History Scholar": "hum", "History Professor": "hum",
    "Educator": "misc", "Communications Specialist": "misc", "Librarian": "misc",
    "Artisan": "misc",
}

# ─── Undergrad major pools by domain ────────────────────────────────────────

UNDERGRAD_MAJORS = {
    "swe": [
        "Computer Science", "Computer Science", "Computer Science", "Computer Science",
        "Computer Engineering", "Computer Engineering",
        "Electrical Engineering & Computer Science",
        "Software Engineering", "Mathematics", "Mathematics",
        "Applied Mathematics", "Physics",
        "Information Systems", "Information Technology",
        "Data Science", "Statistics",
    ],
    "eng": [
        "Mechanical Engineering", "Mechanical Engineering",
        "Electrical Engineering", "Electrical Engineering",
        "Civil Engineering", "Chemical Engineering",
        "Aerospace Engineering", "Biomedical Engineering",
        "Materials Science & Engineering", "Industrial Engineering",
        "Environmental Engineering", "Engineering Physics",
    ],
    "med": [
        "Biology", "Biology", "Biology",
        "Biochemistry", "Biochemistry",
        "Chemistry", "Neuroscience",
        "Biomedical Sciences", "Pre-Medicine",
        "Molecular Biology", "Human Biology",
        "Physiology", "Health Sciences",
    ],
    "law": [
        "Political Science", "Political Science", "Political Science",
        "History", "History",
        "English", "Philosophy",
        "Economics", "Government",
        "International Relations", "Sociology",
        "Criminal Justice", "Pre-Law",
        "Public Policy",
    ],
    "data": [
        "Computer Science", "Computer Science",
        "Statistics", "Statistics",
        "Mathematics", "Mathematics",
        "Applied Mathematics", "Physics",
        "Data Science", "Economics",
        "Information Science", "Electrical Engineering",
    ],
    "fin": [
        "Finance", "Finance", "Finance",
        "Economics", "Economics", "Economics",
        "Accounting", "Accounting",
        "Business Administration", "Mathematics",
        "Applied Mathematics", "Statistics",
    ],
    "biz": [
        "Business Administration", "Business Administration",
        "Management", "Marketing",
        "Economics", "Supply Chain Management",
        "Human Resources Management", "Communications",
        "Industrial Engineering", "Psychology",
        "Organizational Behavior",
    ],
    "lifesci": [
        "Biology", "Biology", "Biology",
        "Biochemistry", "Biochemistry",
        "Molecular Biology", "Genetics",
        "Microbiology", "Neuroscience",
        "Chemistry", "Ecology",
        "Biotechnology", "Bioinformatics",
    ],
    "physci": [
        "Physics", "Physics", "Physics",
        "Chemistry", "Chemistry",
        "Mathematics", "Applied Physics",
        "Astrophysics", "Geoscience",
        "Earth Science", "Materials Science",
        "Atmospheric Science", "Oceanography",
    ],
    "socsci": [
        "Psychology", "Psychology",
        "Economics", "Economics",
        "Sociology", "Political Science",
        "Anthropology", "International Relations",
        "Geography", "Public Policy",
        "Criminal Justice",
    ],
    "arts": [
        "Fine Arts", "Graphic Design",
        "Industrial Design", "Architecture",
        "Visual Arts", "Illustration",
        "Animation", "Film Studies",
        "Photography", "Game Design",
        "Interaction Design", "Studio Art",
        "Art History", "Fashion Design",
    ],
    "hum": [
        "History", "History",
        "Philosophy", "Philosophy",
        "English Literature", "Classics",
        "Religious Studies", "Comparative Literature",
        "Art History", "Archaeology",
        "Cultural Studies", "Linguistics",
        "Anthropology",
    ],
    "misc": [
        "Education", "Communications",
        "Liberal Arts", "Library Science",
        "English", "Psychology",
        "Sociology", "Business Administration",
        "General Studies",
    ],
}

# ─── Grad field pools by domain ──────────────────────────────────────────────

GRAD_FIELDS = {
    "swe": [
        "Computer Science", "Computer Science",
        "Machine Learning", "Artificial Intelligence",
        "Software Engineering", "Data Science",
        "Computer Engineering", "Cybersecurity",
        "Distributed Systems", "Human-Computer Interaction",
        "Natural Language Processing", "Computer Vision",
        "Robotics",
    ],
    "eng": [
        "Mechanical Engineering", "Electrical Engineering",
        "Civil Engineering", "Chemical Engineering",
        "Aerospace Engineering", "Biomedical Engineering",
        "Robotics", "Materials Science",
        "Environmental Engineering", "Systems Engineering",
    ],
    "med": [
        "Medicine", "Medicine",
        "Internal Medicine", "Surgery",
        "Pediatrics", "Neurology",
        "Cardiology", "Oncology",
        "Psychiatry", "Radiology",
        "Epidemiology", "Pharmacology",
    ],
    "law": [
        "Law", "Law",
        "Corporate Law", "Constitutional Law",
        "International Law", "Intellectual Property Law",
        "Criminal Law", "Environmental Law",
        "Tax Law", "Human Rights Law",
        "Immigration Law", "Labor Law",
    ],
    "data": [
        "Data Science", "Statistics",
        "Machine Learning", "Computer Science",
        "Applied Mathematics", "Computational Science",
        "Operations Research", "Biostatistics",
    ],
    "fin": [
        "Finance", "Business Administration",
        "Financial Engineering", "Economics",
        "Quantitative Finance", "Accounting",
        "Risk Management",
    ],
    "biz": [
        "Business Administration", "Management",
        "Operations Management", "Supply Chain Management",
        "Organizational Leadership", "Human Resources",
        "Public Administration",
    ],
    "lifesci": [
        "Biology", "Molecular Biology",
        "Biochemistry", "Genetics",
        "Neuroscience", "Immunology",
        "Microbiology", "Ecology",
        "Bioinformatics", "Biotechnology",
        "Cell Biology", "Pharmacology",
    ],
    "physci": [
        "Physics", "Chemistry",
        "Astrophysics", "Materials Science",
        "Geophysics", "Atmospheric Science",
        "Oceanography", "Applied Physics",
        "Theoretical Physics", "Nuclear Physics",
    ],
    "socsci": [
        "Psychology", "Economics",
        "Sociology", "Political Science",
        "Anthropology", "Public Policy",
        "International Relations", "Criminology",
        "Geography",
    ],
    "arts": [
        "Fine Arts", "Design",
        "Architecture", "Film",
        "Graphic Design", "Industrial Design",
        "Interactive Media", "Game Design",
        "Visual Arts",
    ],
    "hum": [
        "History", "Philosophy",
        "English Literature", "Comparative Literature",
        "Classics", "Religious Studies",
        "Archaeology", "Art History",
        "Cultural Studies", "Linguistics",
    ],
    "misc": [
        "Education", "Library Science",
        "Communications", "Curriculum & Instruction",
        "Educational Leadership", "Information Science",
    ],
}

# ─── University pools by country ─────────────────────────────────────────────

# US universities: tier 1 (elite), tier 2 (strong), tier 3 (state/regional)
US_TIER1 = [
    "MIT", "Stanford University", "Harvard University", "Caltech",
    "Princeton University", "Yale University", "Columbia University",
    "University of Chicago", "University of Pennsylvania", "Duke University",
    "Northwestern University", "Johns Hopkins University", "Cornell University",
    "Brown University", "Dartmouth College", "Rice University",
    "Vanderbilt University", "Washington University in St. Louis",
    "Carnegie Mellon University", "Georgetown University",
    "UC Berkeley", "UCLA", "University of Michigan",
    "Georgia Institute of Technology", "University of Virginia",
]

US_TIER2 = [
    "NYU", "Boston University", "University of Southern California",
    "University of Wisconsin-Madison", "University of Illinois Urbana-Champaign",
    "Purdue University", "University of Texas at Austin",
    "University of Washington", "University of Maryland",
    "University of Minnesota", "Penn State University",
    "Ohio State University", "University of Florida",
    "University of North Carolina at Chapel Hill",
    "University of Colorado Boulder", "University of Pittsburgh",
    "Northeastern University", "Tufts University",
    "Case Western Reserve University", "Emory University",
    "University of Rochester", "Tulane University",
    "Wake Forest University", "Lehigh University",
    "Rensselaer Polytechnic Institute", "Stevens Institute of Technology",
    "Santa Clara University", "San Jose State University",
    "Drexel University", "George Washington University",
    "University of Miami", "Syracuse University",
    "University of Notre Dame", "Villanova University",
    "Brandeis University", "College of William & Mary",
]

US_TIER3 = [
    "Arizona State University", "University of Arizona",
    "University of Oregon", "Oregon State University",
    "University of Utah", "University of Iowa",
    "University of Kansas", "University of Kentucky",
    "University of Tennessee", "University of Alabama",
    "Clemson University", "Virginia Tech",
    "Colorado State University", "University of Nebraska",
    "Iowa State University", "Kansas State University",
    "University of Connecticut", "University of New Hampshire",
    "University of Vermont", "University of Delaware",
    "University of Oklahoma", "University of Arkansas",
    "University of South Carolina", "Mississippi State University",
    "West Virginia University", "University of Nevada Las Vegas",
    "San Diego State University", "University of Houston",
    "Florida State University", "Texas A&M University",
    "NC State University", "Michigan State University",
    "Indiana University", "University of Cincinnati",
    "Temple University", "Rutgers University",
    "SUNY Stony Brook", "SUNY Buffalo",
    "Portland State University", "Boise State University",
]

# US med schools (for MD grad)
US_MED_SCHOOLS = [
    "Harvard Medical School", "Johns Hopkins School of Medicine",
    "Stanford School of Medicine", "UCSF School of Medicine",
    "University of Pennsylvania Perelman School of Medicine",
    "Columbia Vagelos College of Physicians and Surgeons",
    "Washington University School of Medicine",
    "Duke University School of Medicine",
    "Yale School of Medicine", "NYU Grossman School of Medicine",
    "University of Michigan Medical School",
    "UCLA David Geffen School of Medicine",
    "Mount Sinai Icahn School of Medicine",
    "University of Pittsburgh School of Medicine",
    "Northwestern Feinberg School of Medicine",
    "Cornell Weill Medical College", "Baylor College of Medicine",
    "Emory University School of Medicine",
    "University of Chicago Pritzker School of Medicine",
    "Case Western Reserve School of Medicine",
    "University of Virginia School of Medicine",
    "Vanderbilt University School of Medicine",
    "University of Wisconsin School of Medicine",
    "University of Colorado School of Medicine",
    "University of Rochester School of Medicine",
    "Georgetown University School of Medicine",
    "Tufts University School of Medicine",
    "Boston University Chobanian & Avedisian School of Medicine",
    "Oregon Health & Science University School of Medicine",
    "University of Minnesota Medical School",
    "University of Iowa Carver College of Medicine",
    "University of Alabama at Birmingham School of Medicine",
    "Medical College of Georgia at Augusta University",
    "University of South Florida Morsani College of Medicine",
]

# US law schools (for JD grad)
US_LAW_SCHOOLS = [
    "Yale Law School", "Harvard Law School", "Stanford Law School",
    "Columbia Law School", "University of Chicago Law School",
    "NYU School of Law", "University of Pennsylvania Carey Law School",
    "University of Virginia School of Law",
    "Duke University School of Law", "Northwestern Pritzker School of Law",
    "UC Berkeley School of Law", "University of Michigan Law School",
    "Cornell Law School", "Georgetown University Law Center",
    "UCLA School of Law", "Vanderbilt University Law School",
    "Washington University School of Law",
    "University of Texas School of Law",
    "University of Minnesota Law School",
    "Boston University School of Law",
    "George Washington University Law School",
    "University of Notre Dame Law School",
    "Emory University School of Law",
    "University of Florida Levin College of Law",
    "University of Wisconsin Law School",
    "University of North Carolina School of Law",
    "Fordham University School of Law",
    "University of Southern California Gould School of Law",
    "Arizona State University Sandra Day O'Connor College of Law",
    "University of Colorado Law School",
    "University of Iowa College of Law",
]

# International universities by country
INTL_UNIVERSITIES = {
    "India": {
        "elite": [
            "IIT Bombay", "IIT Delhi", "IIT Madras", "IIT Kanpur", "IIT Kharagpur",
            "IIT Roorkee", "IIT Guwahati", "IIT Hyderabad",
            "Indian Institute of Science", "BITS Pilani",
            "NIT Trichy", "NIT Warangal", "NIT Surathkal",
            "Delhi University", "Jawaharlal Nehru University",
        ],
        "standard": [
            "Anna University", "VIT Vellore", "Manipal Institute of Technology",
            "SRM Institute of Science and Technology", "Amity University",
            "Pune University", "Mumbai University", "Bangalore University",
            "Osmania University", "Jadavpur University",
            "University of Hyderabad", "University of Madras",
            "University of Calcutta", "University of Rajasthan",
            "Symbiosis International University", "Christ University",
            "Lovely Professional University", "Chandigarh University",
        ],
        "med": [
            "All India Institute of Medical Sciences (AIIMS) Delhi",
            "Christian Medical College Vellore",
            "Armed Forces Medical College Pune",
            "Maulana Azad Medical College Delhi",
            "Grant Medical College Mumbai",
            "King George's Medical University Lucknow",
            "Kasturba Medical College Manipal",
            "St. John's Medical College Bangalore",
        ],
        "law": [
            "National Law School of India University Bangalore",
            "National Law University Delhi",
            "NALSAR University of Law Hyderabad",
            "West Bengal National University of Juridical Sciences",
            "National Law Institute University Bhopal",
        ],
    },
    "China": {
        "elite": [
            "Tsinghua University", "Peking University", "Fudan University",
            "Shanghai Jiao Tong University", "Zhejiang University",
            "University of Science and Technology of China",
            "Nanjing University", "Wuhan University",
            "Harbin Institute of Technology", "Xi'an Jiaotong University",
            "Beihang University", "Tongji University",
        ],
        "standard": [
            "Sun Yat-sen University", "South China University of Technology",
            "Southeast University", "Tianjin University",
            "Dalian University of Technology", "Sichuan University",
            "Chongqing University", "Jilin University",
            "Huazhong University of Science and Technology",
            "Central South University", "Xiamen University",
            "Beijing Normal University", "East China Normal University",
        ],
    },
    "United Kingdom": {
        "elite": [
            "University of Oxford", "University of Cambridge",
            "Imperial College London", "University College London",
            "London School of Economics",
            "University of Edinburgh", "King's College London",
            "University of Manchester", "University of Bristol",
            "University of Warwick",
        ],
        "standard": [
            "University of Glasgow", "University of Birmingham",
            "University of Leeds", "University of Sheffield",
            "University of Nottingham", "University of Southampton",
            "University of Liverpool", "University of Exeter",
            "Queen Mary University of London", "Lancaster University",
            "University of Bath", "University of York",
            "University of St Andrews", "Durham University",
        ],
        "med": [
            "University of Oxford Medical School",
            "University of Cambridge School of Clinical Medicine",
            "Imperial College London School of Medicine",
            "UCL Medical School",
            "King's College London GKT School of Medical Education",
            "University of Edinburgh Medical School",
        ],
        "law": [
            "University of Oxford Faculty of Law",
            "University of Cambridge Faculty of Law",
            "LSE Law School",
            "UCL Faculty of Laws",
            "King's College London Dickson Poon School of Law",
        ],
    },
    "Germany": {
        "elite": [
            "Technical University of Munich", "Ludwig Maximilian University of Munich",
            "Heidelberg University", "Humboldt University of Berlin",
            "Free University of Berlin", "RWTH Aachen University",
            "University of Freiburg", "University of Gottingen",
            "Technical University of Berlin", "University of Tubingen",
        ],
        "standard": [
            "University of Hamburg", "University of Cologne",
            "University of Frankfurt", "University of Stuttgart",
            "University of Bonn", "University of Munster",
            "University of Erlangen-Nuremberg", "University of Dresden",
            "Karlsruhe Institute of Technology", "University of Mannheim",
        ],
    },
    "France": {
        "elite": [
            "Ecole Polytechnique", "Ecole Normale Superieure",
            "Sciences Po Paris", "Sorbonne University",
            "Universite Paris-Saclay", "Ecole des Mines de Paris",
            "HEC Paris", "INSEAD",
        ],
        "standard": [
            "University of Lyon", "University of Strasbourg",
            "University of Bordeaux", "University of Toulouse",
            "University of Montpellier", "University of Aix-Marseille",
            "University of Grenoble Alpes", "University of Lille",
        ],
    },
    "Canada": {
        "elite": [
            "University of Toronto", "McGill University",
            "University of British Columbia", "University of Waterloo",
            "University of Alberta", "University of Montreal",
        ],
        "standard": [
            "University of Ottawa", "University of Calgary",
            "Queen's University", "Western University",
            "McMaster University", "Simon Fraser University",
            "University of Victoria", "Dalhousie University",
            "Carleton University", "York University",
        ],
    },
    "Japan": {
        "elite": [
            "University of Tokyo", "Kyoto University",
            "Tokyo Institute of Technology", "Osaka University",
            "Tohoku University", "Nagoya University",
        ],
        "standard": [
            "Keio University", "Waseda University",
            "Hokkaido University", "Kyushu University",
            "Kobe University", "Hiroshima University",
            "Tsukuba University", "Yokohama National University",
        ],
    },
    "South Korea": {
        "elite": [
            "Seoul National University", "KAIST",
            "POSTECH", "Yonsei University", "Korea University",
        ],
        "standard": [
            "Sungkyunkwan University", "Hanyang University",
            "Kyung Hee University", "Sogang University",
            "Ewha Womans University", "Chung-Ang University",
        ],
    },
    "Brazil": {
        "elite": [
            "University of Sao Paulo (USP)", "University of Campinas (UNICAMP)",
            "Federal University of Rio de Janeiro (UFRJ)",
            "Federal University of Minas Gerais (UFMG)",
        ],
        "standard": [
            "Federal University of Rio Grande do Sul (UFRGS)",
            "University of Brasilia (UnB)",
            "Pontifical Catholic University of Rio de Janeiro (PUC-Rio)",
            "Federal University of Parana (UFPR)",
            "Sao Paulo State University (UNESP)",
        ],
    },
    "Australia": {
        "elite": [
            "University of Melbourne", "University of Sydney",
            "Australian National University", "University of Queensland",
            "University of New South Wales", "Monash University",
        ],
        "standard": [
            "University of Adelaide", "University of Western Australia",
            "Macquarie University", "University of Technology Sydney",
            "RMIT University", "Griffith University",
        ],
    },
    "Russia": {
        "elite": [
            "Moscow State University", "Moscow Institute of Physics and Technology",
            "Saint Petersburg State University", "Novosibirsk State University",
            "Bauman Moscow State Technical University",
            "National Research Nuclear University MEPhI",
        ],
        "standard": [
            "Ural Federal University", "Kazan Federal University",
            "Tomsk State University", "Samara University",
            "ITMO University", "Higher School of Economics",
            "Peter the Great St. Petersburg Polytechnic University",
        ],
    },
    "Mexico": {
        "elite": ["UNAM", "Tecnologico de Monterrey (ITESM)", "IPN"],
        "standard": [
            "Universidad de Guadalajara", "ITAM",
            "Universidad Iberoamericana", "Universidad Autonoma de Nuevo Leon",
            "Benemerita Universidad Autonoma de Puebla",
        ],
    },
    "Colombia": {
        "elite": ["Universidad de los Andes", "Universidad Nacional de Colombia"],
        "standard": [
            "Pontificia Universidad Javeriana", "Universidad del Rosario",
            "Universidad EAFIT", "Universidad del Valle",
        ],
    },
    "Argentina": {
        "elite": ["Universidad de Buenos Aires (UBA)", "Universidad Torcuato Di Tella"],
        "standard": [
            "Universidad Nacional de Cordoba", "Universidad Nacional de La Plata",
            "Universidad de San Andres", "Instituto Tecnologico de Buenos Aires (ITBA)",
        ],
    },
    "Chile": {
        "elite": ["Pontificia Universidad Catolica de Chile", "Universidad de Chile"],
        "standard": ["Universidad de Santiago de Chile", "Universidad de Concepcion"],
    },
    "Spain": {
        "elite": ["University of Barcelona", "Autonomous University of Madrid", "Complutense University of Madrid"],
        "standard": ["University of Valencia", "University of Seville", "University of Granada", "Pompeu Fabra University"],
    },
    "Italy": {
        "elite": ["University of Bologna", "Sapienza University of Rome", "Politecnico di Milano", "Bocconi University"],
        "standard": ["University of Padua", "University of Milan", "University of Turin", "University of Florence"],
    },
    "Netherlands": {
        "elite": ["Delft University of Technology", "University of Amsterdam", "Leiden University", "Utrecht University"],
        "standard": ["Eindhoven University of Technology", "University of Groningen", "Wageningen University", "Erasmus University Rotterdam"],
    },
    "Sweden": {
        "elite": ["KTH Royal Institute of Technology", "Lund University", "Uppsala University", "Stockholm University"],
        "standard": ["Chalmers University of Technology", "University of Gothenburg", "Linkoping University"],
    },
    "Switzerland": {
        "elite": ["ETH Zurich", "EPFL", "University of Zurich", "University of Geneva"],
        "standard": ["University of Bern", "University of Basel", "University of Lausanne"],
    },
    "Poland": {
        "elite": ["University of Warsaw", "Jagiellonian University", "Warsaw University of Technology"],
        "standard": ["AGH University of Science and Technology", "Wroclaw University of Technology", "Gdansk University of Technology", "Adam Mickiewicz University"],
    },
    "Singapore": {
        "elite": ["National University of Singapore", "Nanyang Technological University"],
        "standard": ["Singapore Management University", "Singapore University of Technology and Design"],
    },
    "Israel": {
        "elite": ["Technion - Israel Institute of Technology", "Hebrew University of Jerusalem", "Tel Aviv University", "Weizmann Institute of Science"],
        "standard": ["Ben-Gurion University of the Negev", "Bar-Ilan University", "University of Haifa"],
    },
    "Turkey": {
        "elite": ["Bogazici University", "Middle East Technical University", "Istanbul Technical University", "Koc University", "Sabanci University"],
        "standard": ["Bilkent University", "Hacettepe University", "Ankara University", "Istanbul University"],
    },
    "South Africa": {
        "elite": ["University of Cape Town", "University of the Witwatersrand", "Stellenbosch University"],
        "standard": ["University of Pretoria", "University of KwaZulu-Natal", "University of Johannesburg"],
    },
    "Nigeria": {
        "elite": ["University of Lagos", "University of Ibadan", "Obafemi Awolowo University"],
        "standard": ["University of Nigeria Nsukka", "Ahmadu Bello University", "Covenant University"],
    },
    "Kenya": {
        "elite": ["University of Nairobi", "Kenyatta University"],
        "standard": ["Strathmore University", "Jomo Kenyatta University of Agriculture and Technology"],
    },
    "Egypt": {
        "elite": ["Cairo University", "American University in Cairo", "Ain Shams University"],
        "standard": ["Alexandria University", "Mansoura University", "Helwan University"],
    },
    "United Arab Emirates": {
        "elite": ["Khalifa University", "American University of Sharjah", "New York University Abu Dhabi"],
        "standard": ["University of Sharjah", "American University in Dubai", "Zayed University"],
    },
    "Pakistan": {
        "elite": ["LUMS", "NUST", "Quaid-i-Azam University"],
        "standard": ["University of the Punjab", "University of Karachi", "COMSATS University Islamabad", "University of Engineering and Technology Lahore"],
    },
    "Philippines": {
        "elite": ["University of the Philippines Diliman", "Ateneo de Manila University", "De La Salle University"],
        "standard": ["University of Santo Tomas", "Mapua University"],
    },
    "Taiwan": {
        "elite": ["National Taiwan University", "National Tsing Hua University", "National Chiao Tung University"],
        "standard": ["National Cheng Kung University", "National Central University"],
    },
    "Thailand": {
        "elite": ["Chulalongkorn University", "Mahidol University"],
        "standard": ["Thammasat University", "Kasetsart University", "King Mongkut's University of Technology Thonburi"],
    },
    "Indonesia": {
        "elite": ["University of Indonesia", "Bandung Institute of Technology"],
        "standard": ["Gadjah Mada University", "Airlangga University", "Institut Teknologi Sepuluh Nopember"],
    },
    "Vietnam": {
        "elite": ["Vietnam National University Hanoi", "Vietnam National University Ho Chi Minh City"],
        "standard": ["Hanoi University of Science and Technology", "Ho Chi Minh City University of Technology"],
    },
    "Peru": {
        "elite": ["Pontificia Universidad Catolica del Peru"],
        "standard": ["Universidad Nacional Mayor de San Marcos", "Universidad de Lima"],
    },
    "Austria": {
        "elite": ["University of Vienna", "Vienna University of Technology"],
        "standard": ["University of Graz", "University of Innsbruck"],
    },
}


def pick_undergrad_university(country, domain):
    """Pick a realistic undergrad university based on country."""
    if country == "United States":
        # Weight: 20% tier1, 40% tier2, 40% tier3
        r = random.random()
        if r < 0.20:
            return random.choice(US_TIER1)
        elif r < 0.60:
            return random.choice(US_TIER2)
        else:
            return random.choice(US_TIER3)

    if country in INTL_UNIVERSITIES:
        pools = INTL_UNIVERSITIES[country]
        elite = pools.get("elite", [])
        standard = pools.get("standard", [])
        combined = elite + standard
        if not combined:
            return random.choice(US_TIER2 + US_TIER3)
        # 35% elite, 65% standard
        if elite and standard:
            return random.choice(elite) if random.random() < 0.35 else random.choice(standard)
        return random.choice(combined)

    # Unknown country: pick from US schools (expat / studied abroad)
    return random.choice(US_TIER2 + US_TIER3)


def pick_grad_university(country, domain, education, undergrad_uni):
    """Pick a realistic grad school. Often different from undergrad."""
    # For MD/JD, use specialized school pools
    if education == "MD":
        if country == "United States":
            return random.choice(US_MED_SCHOOLS)
        if country in INTL_UNIVERSITIES and "med" in INTL_UNIVERSITIES[country]:
            return random.choice(INTL_UNIVERSITIES[country]["med"])
        # Some international students go to US med schools
        if random.random() < 0.3:
            return random.choice(US_MED_SCHOOLS)
        # Otherwise use elite schools from their country
        if country in INTL_UNIVERSITIES:
            elite = INTL_UNIVERSITIES[country].get("elite", [])
            if elite:
                return random.choice(elite) + " School of Medicine"
        return random.choice(US_MED_SCHOOLS)

    if education == "JD":
        if country == "United States":
            return random.choice(US_LAW_SCHOOLS)
        if country in INTL_UNIVERSITIES and "law" in INTL_UNIVERSITIES[country]:
            return random.choice(INTL_UNIVERSITIES[country]["law"])
        if country == "United Kingdom" and "law" in INTL_UNIVERSITIES.get("United Kingdom", {}):
            return random.choice(INTL_UNIVERSITIES["United Kingdom"]["law"])
        if random.random() < 0.3:
            return random.choice(US_LAW_SCHOOLS)
        if country in INTL_UNIVERSITIES:
            elite = INTL_UNIVERSITIES[country].get("elite", [])
            if elite:
                return random.choice(elite) + " Faculty of Law"
        return random.choice(US_LAW_SCHOOLS)

    # For Master's/PhD/MFA — pick from elite/standard pools, often different from undergrad
    if country == "United States":
        # Grad school tends to be higher tier
        r = random.random()
        if r < 0.35:
            pool = US_TIER1
        elif r < 0.80:
            pool = US_TIER2
        else:
            pool = US_TIER3
        # Try to pick a different school than undergrad
        attempts = 0
        while attempts < 5:
            choice = random.choice(pool)
            if choice != undergrad_uni:
                return choice
            attempts += 1
        return random.choice(pool)

    # International: ~30% go to US/UK for grad school
    if random.random() < 0.30:
        return random.choice(US_TIER1 + US_TIER2[:10])

    if country in INTL_UNIVERSITIES:
        elite = INTL_UNIVERSITIES[country].get("elite", [])
        standard = INTL_UNIVERSITIES[country].get("standard", [])
        combined = elite + standard
        if combined:
            return random.choice(combined)

    return random.choice(US_TIER1 + US_TIER2)


# ─── Graduation year logic ──────────────────────────────────────────────────

def compute_grad_years(birth_year, education):
    """Compute undergrad and grad graduation years based on birth year and degree.

    Typical timelines:
    - Undergrad: birth + 22 (±1)
    - Master's: undergrad + 2 (±1)
    - PhD: undergrad + 5-7
    - MD: undergrad + 4
    - JD: undergrad + 3
    - MFA: undergrad + 2-3
    - MBA (CFA): undergrad + 3-5 (work experience first)
    """
    undergrad_year = birth_year + random.choice([21, 22, 22, 22, 23, 23, 24])

    if education in ("High School", "Associate"):
        return None, None
    if education == "Bachelor's":
        return undergrad_year, None
    if education == "Master's":
        gap = random.choice([2, 2, 2, 3, 3, 4])
        return undergrad_year, undergrad_year + gap
    if education == "PhD":
        gap = random.choice([5, 5, 6, 6, 6, 7, 7, 8])
        return undergrad_year, undergrad_year + gap
    if education == "MD":
        return undergrad_year, undergrad_year + 4
    if education == "JD":
        gap = random.choice([3, 3, 3, 4, 5])  # some work before law school
        return undergrad_year, undergrad_year + gap
    if education == "MFA":
        gap = random.choice([2, 2, 3, 3, 4])
        return undergrad_year, undergrad_year + gap
    if education == "CFA":
        # CFA is a certification, person likely has a Bachelor's, maybe MBA
        if random.random() < 0.4:
            gap = random.choice([3, 4, 5])
            return undergrad_year, undergrad_year + gap  # MBA
        return undergrad_year, None
    return undergrad_year, None


# ─── SQL helpers ─────────────────────────────────────────────────────────────

def sql_str(s):
    if s is None:
        return "NULL"
    return "'" + s.replace("'", "''") + "'"

def sql_int(n):
    if n is None:
        return "NULL"
    return str(n)


# ─── Main ────────────────────────────────────────────────────────────────────

def fetch_taskers():
    result = subprocess.run(
        ["psql", CONN_STR, "-t", "-A", "-F", "|",
         "-c", "SELECT id, first_name, date_of_birth, age, highest_education_level, external_job_title, location_country FROM taskers ORDER BY id"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"psql failed: {result.stderr}")

    rows = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) >= 7:
            rows.append({
                "id": int(parts[0]),
                "first_name": parts[1],
                "dob": parts[2],
                "age": int(parts[3]),
                "education": parts[4],
                "job_title": parts[5] or "",
                "country": parts[6],
            })
    return rows


def main():
    print("Fetching taskers from Neon...")
    taskers = fetch_taskers()
    print(f"  Found {len(taskers)} taskers")

    print("Generating education details...")
    updates = []
    stats = {"has_undergrad": 0, "has_grad": 0, "total": len(taskers)}

    for t in taskers:
        domain = JOB_DOMAIN.get(t["job_title"], "misc")
        education = t["education"]
        birth_year = int(t["dob"].split("-")[0])

        undergrad_year, grad_year = compute_grad_years(birth_year, education)

        if undergrad_year is None:
            # No college education
            updates.append((t["id"], None, None, None, None, None, None, None))
            continue

        stats["has_undergrad"] += 1

        undergrad_uni = pick_undergrad_university(t["country"], domain)
        undergrad_major = random.choice(UNDERGRAD_MAJORS.get(domain, UNDERGRAD_MAJORS["misc"]))

        if grad_year is not None:
            stats["has_grad"] += 1
            grad_uni = pick_grad_university(t["country"], domain, education, undergrad_uni)

            # Grad degree type
            if education == "MD":
                grad_degree = "MD"
            elif education == "JD":
                grad_degree = "JD"
            elif education == "PhD":
                grad_degree = "PhD"
            elif education == "MFA":
                grad_degree = "MFA"
            elif education == "CFA":
                grad_degree = "MBA" if grad_year else None
            else:
                # Master's — pick specific type
                if domain == "biz":
                    grad_degree = random.choice(["MBA", "MBA", "MS", "MA"])
                elif domain == "fin":
                    grad_degree = random.choice(["MBA", "MS", "MS", "MFE"])
                elif domain in ("swe", "eng", "data", "physci"):
                    grad_degree = random.choice(["MS", "MS", "MS", "MEng", "MEng"])
                elif domain in ("arts",):
                    grad_degree = random.choice(["MA", "MFA", "MFA", "MS"])
                elif domain in ("hum", "socsci"):
                    grad_degree = random.choice(["MA", "MA", "MA", "MS"])
                else:
                    grad_degree = random.choice(["MS", "MA"])

            grad_field = random.choice(GRAD_FIELDS.get(domain, GRAD_FIELDS["misc"]))
        else:
            grad_uni = None
            grad_degree = None
            grad_field = None

        updates.append((
            t["id"],
            undergrad_uni, undergrad_major, undergrad_year,
            grad_uni, grad_degree, grad_field, grad_year
        ))

    print("Writing migration...")
    lines = [
        "-- Auto-generated: backfill education detail fields for all taskers",
        f"-- Generated for {len(updates)} taskers",
        "",
    ]

    batch_size = 500
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i + batch_size]
        lines.append(f"-- Batch {i // batch_size + 1}")
        lines.append("UPDATE taskers AS t SET")
        lines.append("  undergrad_university = v.ug_uni,")
        lines.append("  undergrad_major = v.ug_major,")
        lines.append("  undergrad_graduation_year = v.ug_year::integer,")
        lines.append("  grad_university = v.g_uni,")
        lines.append("  grad_degree = v.g_degree,")
        lines.append("  grad_field = v.g_field,")
        lines.append("  grad_graduation_year = v.g_year::integer")
        lines.append("FROM (VALUES")

        for j, (tid, ug_uni, ug_major, ug_year, g_uni, g_degree, g_field, g_year) in enumerate(batch):
            comma = "," if j < len(batch) - 1 else ""
            row = f"  ({tid}, {sql_str(ug_uni)}, {sql_str(ug_major)}, {sql_int(ug_year)}, {sql_str(g_uni)}, {sql_str(g_degree)}, {sql_str(g_field)}, {sql_int(g_year)}){comma}"
            lines.append(row)

        lines.append(") AS v(id, ug_uni, ug_major, ug_year, g_uni, g_degree, g_field, g_year)")
        lines.append("WHERE t.id = v.id;")
        lines.append("")

    outfile = "migrations/016_backfill_education_details.sql"
    with open(outfile, "w") as f:
        f.write("\n".join(lines) + "\n")

    n = stats["total"]
    print(f"\nGenerated {n} updates → {outfile}")
    print(f"Has undergrad: {stats['has_undergrad']} ({100 * stats['has_undergrad'] / n:.1f}%)")
    print(f"Has grad: {stats['has_grad']} ({100 * stats['has_grad'] / n:.1f}%)")


if __name__ == "__main__":
    main()
