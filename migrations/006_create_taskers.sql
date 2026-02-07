-- Taskers
CREATE TABLE taskers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    hire_date DATE NOT NULL,
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    location_country VARCHAR(100) NOT NULL,
    location_timezone VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive')),
    external_job_title VARCHAR(255),
    subdomain_ids INTEGER[],
    hours_available DECIMAL(5, 2) NOT NULL,
    hourly_rate DECIMAL(8, 2) NOT NULL,
    languages TEXT[] NOT NULL,
    language_proficiency JSONB NOT NULL
);

-- Seed taskers (20 taskers with diverse domains, countries, languages)
INSERT INTO taskers (id, first_name, middle_name, last_name, email, hire_date, address_line1, address_line2, city, state_province, postal_code, location_country, location_timezone, status, external_job_title, subdomain_ids, hours_available, hourly_rate, languages, language_proficiency) VALUES

-- Software engineers
(1, 'Alex', NULL, 'Thompson', 'alex.thompson@gmail.com', '2023-11-15', '123 Main Street', 'APT 4B', 'New York', 'NY', '10001', 'United States', 'America/New_York', 'active', 'Software Engineer', '{1,2,3}', 30.0, 65.00, '{"English","Spanish"}', '{"English": "native", "Spanish": "fluent"}'),

(2, 'Wei', NULL, 'Zhang', 'wei.zhang@outlook.com', '2024-01-10', '456 Market St', NULL, 'San Francisco', 'CA', '94105', 'United States', 'America/Los_Angeles', 'active', 'Senior Backend Engineer', '{1,5,9}', 25.0, 75.00, '{"English","Mandarin"}', '{"English": "fluent", "Mandarin": "native"}'),

(3, 'Rajesh', 'K', 'Sharma', 'rajesh.sharma@gmail.com', '2024-02-20', '78 Nehru Place', NULL, 'Bangalore', 'Karnataka', '560001', 'India', 'Asia/Kolkata', 'active', 'Full Stack Developer', '{1,3,4}', 40.0, 35.00, '{"English","Hindi","Kannada"}', '{"English": "fluent", "Hindi": "native", "Kannada": "fluent"}'),

(4, 'Maria', 'L', 'Garcia', 'maria.garcia@yahoo.com', '2023-09-05', '234 Reforma Ave', 'Suite 12', 'Mexico City', 'CDMX', '06600', 'Mexico', 'America/Mexico_City', 'active', 'ML Engineer', '{2,54,56}', 35.0, 45.00, '{"English","Spanish"}', '{"English": "fluent", "Spanish": "native"}'),

(5, 'Tomasz', NULL, 'Kowalski', 'tomasz.kowalski@gmail.com', '2024-03-12', '15 Marszalkowska St', NULL, 'Warsaw', 'Masovia', '00-001', 'Poland', 'Europe/Warsaw', 'active', 'Security Engineer', '{1,6,7}', 20.0, 55.00, '{"English","Polish","German"}', '{"English": "fluent", "Polish": "native", "German": "intermediate"}'),

-- Medical professionals
(6, 'Emily', 'R', 'Chen', 'emily.chen@protonmail.com', '2024-04-01', '890 University Ave', NULL, 'Palo Alto', 'CA', '94301', 'United States', 'America/Los_Angeles', 'active', 'Cardiologist', '{22,28}', 15.0, 95.00, '{"English","Mandarin"}', '{"English": "native", "Mandarin": "fluent"}'),

(7, 'David', NULL, 'Okonkwo', 'david.okonkwo@gmail.com', '2024-05-15', '42 Victoria Island', NULL, 'Lagos', 'Lagos', '101233', 'Nigeria', 'Africa/Lagos', 'active', 'Neurologist', '{22,27,88}', 20.0, 70.00, '{"English","Yoruba","Igbo"}', '{"English": "native", "Yoruba": "fluent", "Igbo": "intermediate"}'),

(8, 'Sophie', NULL, 'Dubois', 'sophie.dubois@orange.fr', '2023-12-01', '27 Rue de Rivoli', 'Apt 5', 'Paris', 'Île-de-France', '75001', 'France', 'Europe/Paris', 'active', 'Oncologist', '{22,29,32}', 10.0, 90.00, '{"English","French"}', '{"English": "fluent", "French": "native"}'),

-- Legal professionals
(9, 'Jonathan', 'M', 'Blake', 'jonathan.blake@outlook.com', '2024-01-22', '55 Fleet Street', NULL, 'London', 'England', 'EC4Y 1AA', 'United Kingdom', 'Europe/London', 'active', 'Corporate Lawyer', '{39,40,41}', 15.0, 85.00, '{"English"}', '{"English": "native"}'),

(10, 'Yuki', NULL, 'Tanaka', 'yuki.tanaka@gmail.com', '2024-06-10', '3-14 Roppongi', NULL, 'Tokyo', 'Tokyo', '106-0032', 'Japan', 'Asia/Tokyo', 'active', 'IP Attorney', '{41,50}', 20.0, 80.00, '{"English","Japanese"}', '{"English": "fluent", "Japanese": "native"}'),

(11, 'Carlos', NULL, 'Rodriguez', 'carlos.rodriguez@gmail.com', '2024-03-01', '100 Calle Serrano', NULL, 'Madrid', 'Madrid', '28006', 'Spain', 'Europe/Madrid', 'active', 'Criminal Law Professor', '{36,37,38}', 25.0, 60.00, '{"English","Spanish","Portuguese"}', '{"English": "fluent", "Spanish": "native", "Portuguese": "intermediate"}'),

-- Data / Finance
(12, 'Anika', NULL, 'Muller', 'anika.muller@web.de', '2024-02-15', '88 Friedrichstrasse', NULL, 'Berlin', 'Berlin', '10117', 'Germany', 'Europe/Berlin', 'active', 'Data Scientist', '{52,54,55}', 30.0, 60.00, '{"English","German"}', '{"English": "fluent", "German": "native"}'),

(13, 'James', 'P', 'Wilson', 'james.wilson@gmail.com', '2023-10-20', '200 Wall Street', 'Floor 14', 'New York', 'NY', '10005', 'United States', 'America/New_York', 'active', 'Quantitative Analyst', '{64,65,55}', 15.0, 85.00, '{"English"}', '{"English": "native"}'),

-- Life Sciences
(14, 'Fatima', NULL, 'Al-Rashid', 'fatima.alrashid@gmail.com', '2024-07-01', '45 Al Wasl Road', NULL, 'Dubai', 'Dubai', '00000', 'United Arab Emirates', 'Asia/Dubai', 'active', 'Molecular Biologist', '{80,81,85}', 25.0, 55.00, '{"English","Arabic"}', '{"English": "fluent", "Arabic": "native"}'),

(15, 'Henrik', NULL, 'Lindqvist', 'henrik.lindqvist@gmail.com', '2024-04-20', '12 Drottninggatan', NULL, 'Stockholm', 'Stockholm', '111 51', 'Sweden', 'Europe/Stockholm', 'active', 'Neuroscientist', '{88,92}', 20.0, 65.00, '{"English","Swedish","Norwegian"}', '{"English": "fluent", "Swedish": "native", "Norwegian": "fluent"}'),

-- Physical Sciences
(16, 'Priya', NULL, 'Nair', 'priya.nair@gmail.com', '2024-08-01', '99 MG Road', NULL, 'Mumbai', 'Maharashtra', '400001', 'India', 'Asia/Kolkata', 'active', 'Physicist', '{95,96}', 30.0, 40.00, '{"English","Hindi","Malayalam"}', '{"English": "fluent", "Hindi": "fluent", "Malayalam": "native"}'),

(17, 'Lucas', NULL, 'Ferreira', 'lucas.ferreira@gmail.com', '2024-05-01', '500 Av Paulista', NULL, 'São Paulo', 'SP', '01310-100', 'Brazil', 'America/Sao_Paulo', 'active', 'Chemist', '{98,103}', 25.0, 38.00, '{"English","Portuguese"}', '{"English": "fluent", "Portuguese": "native"}'),

-- Humanities / Social Sciences
(18, 'Eleanor', 'J', 'Wright', 'eleanor.wright@gmail.com', '2024-01-05', '34 Brattle Street', NULL, 'Cambridge', 'MA', '02138', 'United States', 'America/New_York', 'active', 'History Professor', '{129,130,133}', 20.0, 55.00, '{"English","French","Latin"}', '{"English": "native", "French": "fluent", "Latin": "intermediate"}'),

(19, 'Soo-Jin', NULL, 'Park', 'soojin.park@naver.com', '2024-06-20', '25 Gangnam-daero', NULL, 'Seoul', 'Seoul', '06236', 'South Korea', 'Asia/Seoul', 'active', 'Psychologist', '{108,107}', 20.0, 50.00, '{"English","Korean"}', '{"English": "fluent", "Korean": "native"}'),

-- Arts & Design
(20, 'Isabella', NULL, 'Rossi', 'isabella.rossi@gmail.com', '2024-09-01', '12 Via del Corso', NULL, 'Rome', 'Lazio', '00186', 'Italy', 'Europe/Rome', 'inactive', 'UX Designer', '{117,119,127}', 0.0, 50.00, '{"English","Italian"}', '{"English": "fluent", "Italian": "native"}');

-- Reset sequence
SELECT setval('taskers_id_seq', (SELECT MAX(id) FROM taskers));
