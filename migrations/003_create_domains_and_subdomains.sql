-- Domains
CREATE TABLE domains (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Subdomains
CREATE TABLE subdomains (
    id SERIAL PRIMARY KEY,
    domain_id INTEGER NOT NULL REFERENCES domains(id),
    name VARCHAR(255) NOT NULL
);

-- Seed domains (13 domains)
INSERT INTO domains (id, name) VALUES
(1, 'Software Engineering'),
(2, 'Other Engineering'),
(3, 'Medicine'),
(4, 'Law'),
(5, 'Data Analysis'),
(6, 'Finance'),
(7, 'Business Operations'),
(8, 'Life Sciences'),
(9, 'Physical Sciences'),
(10, 'Social Sciences'),
(11, 'Arts & Design'),
(12, 'Humanities'),
(13, 'Miscellaneous');

-- Seed subdomains
-- 1. Software Engineering (domain_id = 1)
INSERT INTO subdomains (id, domain_id, name) VALUES
(1, 1, 'Software Engineering - General'),
(2, 1, 'Software Engineering - AI/ML'),
(3, 1, 'Software Engineering - Full Stack'),
(4, 1, 'Software Engineering - Frontend'),
(5, 1, 'Software Engineering - Backend'),
(6, 1, 'Software Engineering - Security'),
(7, 1, 'Software Engineering - Platform'),
(8, 1, 'Software Engineering - Mobile'),
(9, 1, 'Software Engineering - Database'),
(10, 1, 'Software Engineering - Other');

-- 2. Other Engineering (domain_id = 2)
INSERT INTO subdomains (id, domain_id, name) VALUES
(11, 2, 'Mechanical Engineering'),
(12, 2, 'Electrical Engineering'),
(13, 2, 'Civil Engineering'),
(14, 2, 'Chemical Engineering'),
(15, 2, 'Materials Engineering'),
(16, 2, 'Industrial & Systems Engineering'),
(17, 2, 'Aerospace Engineering'),
(18, 2, 'Biomedical Engineering'),
(19, 2, 'Environmental Engineering'),
(20, 2, 'Robotics'),
(21, 2, 'Other Engineering - Other');

-- 3. Medicine (domain_id = 3)
INSERT INTO subdomains (id, domain_id, name) VALUES
(22, 3, 'Internal Medicine'),
(23, 3, 'Surgery'),
(24, 3, 'Pediatrics'),
(25, 3, 'Obstetrics & Gynecology'),
(26, 3, 'Psychiatry'),
(27, 3, 'Neurology'),
(28, 3, 'Cardiology'),
(29, 3, 'Oncology'),
(30, 3, 'Radiology'),
(31, 3, 'Anesthesiology'),
(32, 3, 'Epidemiology'),
(33, 3, 'Pharmacology'),
(34, 3, 'Medical Imaging'),
(35, 3, 'Medicine - Other');

-- 4. Law (domain_id = 4)
INSERT INTO subdomains (id, domain_id, name) VALUES
(36, 4, 'Constitutional Law'),
(37, 4, 'Criminal Law'),
(38, 4, 'Civil Law'),
(39, 4, 'Business Law'),
(40, 4, 'Contract Law'),
(41, 4, 'IP Law'),
(42, 4, 'International Law'),
(43, 4, 'Human Rights Law'),
(44, 4, 'Environmental Law'),
(45, 4, 'Labor Law'),
(46, 4, 'Tax Law'),
(47, 4, 'Family Law'),
(48, 4, 'Immigration Law'),
(49, 4, 'Administrative Law'),
(50, 4, 'Technology Law'),
(51, 4, 'Law - Other');

-- 5. Data Analysis (domain_id = 5)
INSERT INTO subdomains (id, domain_id, name) VALUES
(52, 5, 'Data Visualization'),
(53, 5, 'Predictive Analytics'),
(54, 5, 'Machine Learning'),
(55, 5, 'Statistical Modeling'),
(56, 5, 'Natural Language Processing'),
(57, 5, 'Data Engineering'),
(58, 5, 'Data Analysis - Other');

-- 6. Finance (domain_id = 6)
INSERT INTO subdomains (id, domain_id, name) VALUES
(59, 6, 'Corporate Finance'),
(60, 6, 'Investment Banking'),
(61, 6, 'Asset Management'),
(62, 6, 'Portfolio Management'),
(63, 6, 'Risk Management'),
(64, 6, 'Quantitative Finance'),
(65, 6, 'Financial Modeling'),
(66, 6, 'Accounting'),
(67, 6, 'Auditing'),
(68, 6, 'Taxation'),
(69, 6, 'Insurance'),
(70, 6, 'Actuarial'),
(71, 6, 'Finance - Other');

-- 7. Business Operations (domain_id = 7)
INSERT INTO subdomains (id, domain_id, name) VALUES
(72, 7, 'Operations'),
(73, 7, 'Supply Chain'),
(74, 7, 'Procurement & Sourcing'),
(75, 7, 'Project Management'),
(76, 7, 'Human Resources'),
(77, 7, 'Customer Support'),
(78, 7, 'Business Strategy'),
(79, 7, 'Business Operations - Other');

-- 8. Life Sciences (domain_id = 8)
INSERT INTO subdomains (id, domain_id, name) VALUES
(80, 8, 'Biology - General'),
(81, 8, 'Molecular Biology'),
(82, 8, 'Cell Biology'),
(83, 8, 'Evolutionary Biology'),
(84, 8, 'Microbiology'),
(85, 8, 'Genetics'),
(86, 8, 'Biochemistry'),
(87, 8, 'Immunology'),
(88, 8, 'Neuroscience'),
(89, 8, 'Ecology'),
(90, 8, 'Bioinformatics'),
(91, 8, 'Biotechnology'),
(92, 8, 'Physiology'),
(93, 8, 'Pharmacology'),
(94, 8, 'Life Sciences - Other');

-- 9. Physical Sciences (domain_id = 9)
INSERT INTO subdomains (id, domain_id, name) VALUES
(95, 9, 'Physics'),
(96, 9, 'Astrophysics'),
(97, 9, 'Astronomy'),
(98, 9, 'Chemistry'),
(99, 9, 'Earth Science'),
(100, 9, 'Geology'),
(101, 9, 'Meteorology'),
(102, 9, 'Oceanography'),
(103, 9, 'Materials Science'),
(104, 9, 'Acoustics'),
(105, 9, 'Physical Sciences - Other');

-- 10. Social Sciences (domain_id = 10)
INSERT INTO subdomains (id, domain_id, name) VALUES
(106, 10, 'Economics'),
(107, 10, 'Sociology'),
(108, 10, 'Psychology'),
(109, 10, 'Anthropology'),
(110, 10, 'Political Science'),
(111, 10, 'Human Geography'),
(112, 10, 'International Relations'),
(113, 10, 'Public Policy'),
(114, 10, 'Criminology'),
(115, 10, 'Social Sciences - Other');

-- 11. Arts & Design (domain_id = 11)
INSERT INTO subdomains (id, domain_id, name) VALUES
(116, 11, 'Visual Arts'),
(117, 11, 'Graphic Design'),
(118, 11, 'Industrial Design'),
(119, 11, 'UX/UI Design'),
(120, 11, 'Fashion Design'),
(121, 11, 'Interior Design'),
(122, 11, 'Architecture'),
(123, 11, 'Illustration'),
(124, 11, 'Animation'),
(125, 11, 'Film & Media Arts'),
(126, 11, 'Photography'),
(127, 11, 'Game Design'),
(128, 11, 'Arts & Design - Other');

-- 12. Humanities (domain_id = 12)
INSERT INTO subdomains (id, domain_id, name) VALUES
(129, 12, 'Philosophy'),
(130, 12, 'History'),
(131, 12, 'Literature'),
(132, 12, 'Religious Studies'),
(133, 12, 'Ethics'),
(134, 12, 'Classical Studies'),
(135, 12, 'Cultural Studies'),
(136, 12, 'Gender Studies'),
(137, 12, 'Area Studies'),
(138, 12, 'Archaeology'),
(139, 12, 'Art History'),
(140, 12, 'Humanities - Other');

-- 13. Miscellaneous (domain_id = 13)
INSERT INTO subdomains (id, domain_id, name) VALUES
(141, 13, 'Education'),
(142, 13, 'Communication Studies'),
(143, 13, 'Library Science'),
(144, 13, 'Basket Weaving'),
(145, 13, 'Miscellaneous - Other');

-- Reset sequences
SELECT setval('domains_id_seq', (SELECT MAX(id) FROM domains));
SELECT setval('subdomains_id_seq', (SELECT MAX(id) FROM subdomains));
