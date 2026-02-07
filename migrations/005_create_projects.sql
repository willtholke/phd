-- Projects
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    contract_id INTEGER NOT NULL REFERENCES contracts(id),
    spl_id INTEGER NOT NULL REFERENCES spls(id),
    external_name VARCHAR(255) NOT NULL,
    internal_name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    budget DECIMAL(12, 2) NOT NULL,
    billing_rate DECIMAL(8, 2) NOT NULL,
    subdomain_ids INTEGER[]
);

-- Seed projects (~10 projects, 2 per customer)
-- subdomain_ids reference actual IDs from migration 003
INSERT INTO projects (id, customer_id, contract_id, spl_id, external_name, internal_name, start_date, end_date, budget, billing_rate, subdomain_ids) VALUES
-- Meta projects (customer 1, SPL 1 = Sarah Chen)
(1, 1, 2, 1, 'Llama-RLHF-v4', 'Text Preference Ranking (General)', '2025-01-15', NULL, 750000.00, 90.00, '{1,2,3}'),
(2, 1, 2, 1, 'Llama-Safety-Review', 'Safety Labeling & Red Team', '2025-02-01', NULL, 500000.00, 85.00, '{1,6,37}'),

-- OpenAI projects (customer 2, SPL 2 = Marcus Johnson)
(3, 2, 4, 2, 'Helios-CodeReview-pass2', 'Code Quality Review (Backend)', '2025-01-20', NULL, 300000.00, 95.00, '{1,5,9}'),
(4, 2, 4, 2, 'Helios-RLHF-pass3', 'Text Preference Comparison (General)', '2025-02-01', NULL, 280000.00, 85.00, '{1,2,56}'),

-- Google projects (customer 3, SPL 3 = Priya Patel)
(5, 3, 5, 3, 'Gemini-MedEval-2025', 'Medical Domain Evaluation', '2025-01-10', '2025-06-30', 500000.00, 110.00, '{22,27,28,29}'),
(6, 3, 5, 3, 'Gemini-LegalEval-2025', 'Legal Domain Evaluation', '2025-02-01', '2025-06-30', 400000.00, 105.00, '{36,37,38,40,50}'),

-- xAI projects (customer 4, SPL 4 = James O'Brien)
(7, 4, 6, 4, 'Grok-SWE-Training-v2', 'Software Engineering Training Data', '2024-09-15', '2025-03-01', 250000.00, 80.00, '{1,2,3,5}'),
(8, 4, 7, 4, 'Grok-RedTeam-2025', 'Adversarial Prompt Testing', '2025-02-01', NULL, 200000.00, 75.00, '{1,6,50}'),

-- Anthropic projects (customer 5, SPL 5 = Aisha Williams)
(9, 5, 8, 5, 'Claude-SciEval-2025', 'Science Domain Expert Evaluation', '2025-01-15', '2025-12-31', 550000.00, 100.00, '{80,85,88,95,98}'),
(10, 5, 8, 5, 'Claude-HumanitiesEval-2025', 'Humanities & Social Science Evaluation', '2025-02-01', '2025-12-31', 450000.00, 90.00, '{106,108,129,130,131}');

-- Reset sequence
SELECT setval('projects_id_seq', (SELECT MAX(id) FROM projects));
