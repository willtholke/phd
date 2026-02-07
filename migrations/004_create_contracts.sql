-- Contracts
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    billing_cycle_id INTEGER NOT NULL REFERENCES billing_cycles(id),
    contract_name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    take_rate REAL NOT NULL,
    contract_budget DECIMAL(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive', 'completed', 'canceled'))
);

INSERT INTO contracts (id, customer_id, billing_cycle_id, contract_name, start_date, end_date, take_rate, contract_budget, status) VALUES
-- Meta
(1, 1, 2, 'Meta RLHF Q3-Q4 2024', '2024-07-01', '2024-12-31', 0.30, 1200000.00, 'completed'),
(2, 1, 2, 'Meta Safety Labeling 2025', '2025-01-01', NULL, 0.28, 1500000.00, 'active'),

-- OpenAI
(3, 2, 1, 'OpenAI RLHF Q4 2024', '2024-08-01', '2025-02-01', 0.30, 850000.00, 'completed'),
(4, 2, 1, 'OpenAI Code Review 2025', '2025-01-15', NULL, 0.32, 600000.00, 'active'),

-- Google
(5, 3, 1, 'Google Gemini Eval H1 2025', '2025-01-01', '2025-06-30', 0.25, 950000.00, 'active'),

-- xAI
(6, 4, 3, 'xAI Grok Training 2024', '2024-09-01', '2025-03-01', 0.35, 400000.00, 'active'),
(7, 4, 3, 'xAI Red Team 2025', '2025-02-01', NULL, 0.33, 250000.00, 'active'),

-- Anthropic
(8, 5, 4, 'Anthropic Claude Eval 2025', '2025-01-01', '2025-12-31', 0.27, 1100000.00, 'active');

-- Reset sequence
SELECT setval('contracts_id_seq', (SELECT MAX(id) FROM contracts));
