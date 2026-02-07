-- Billing Cycles
CREATE TABLE billing_cycles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    frequency_type VARCHAR(50) NOT NULL CHECK (frequency_type IN ('monthly', 'biweekly', 'weekly', 'custom')),
    billing_days INTEGER[],
    day_of_week VARCHAR(10) CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'))
);

-- Customers
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('Feather', 'SRT Tool', 'Airtable')),
    primary_spl_id INTEGER NOT NULL,
    billing_cycle_id INTEGER NOT NULL REFERENCES billing_cycles(id)
);

-- Seed billing_cycles
INSERT INTO billing_cycles (id, name, description, frequency_type, billing_days, day_of_week) VALUES
(1, 'Standard Monthly', 'Bills on the 1st of each month', 'monthly', '{1}', NULL),
(2, 'Meta Custom Cycle', 'Bills on the 7th, 19th, and 20th of each month', 'custom', '{7,19,20}', NULL),
(3, 'Biweekly Friday', 'Bills every other Friday', 'biweekly', NULL, 'Friday'),
(4, 'Monthly Mid-Month', 'Bills on the 15th of each month', 'monthly', '{15}', NULL);

-- Seed customers
INSERT INTO customers (id, name, platform, primary_spl_id, billing_cycle_id) VALUES
(1, 'Meta', 'SRT Tool', 1, 2),
(2, 'OpenAI', 'Feather', 2, 1),
(3, 'Google', 'Airtable', 3, 1),
(4, 'xAI', 'Airtable', 4, 3),
(5, 'Anthropic', 'Airtable', 5, 4);

-- Reset sequences so next inserts get the right IDs
SELECT setval('billing_cycles_id_seq', (SELECT MAX(id) FROM billing_cycles));
SELECT setval('customers_id_seq', (SELECT MAX(id) FROM customers));