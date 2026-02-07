-- Strategic Project Leads (SPLs)
CREATE TABLE spls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    hire_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive'))
);

-- Seed SPLs (IDs 1-5 match customers.primary_spl_id references)
INSERT INTO spls (id, name, email, hire_date, status) VALUES
(1, 'Aakash Pattabi', 'aakash@peregrine.io', '2021-03-15', 'active'),
(2, 'Patrick Smith', 'patrick@peregrine.io', '2022-02-21', 'active'),
(3, 'Juan Bermudez', 'juan@peregrine.io', '2022-04-18', 'active'),
(4, 'Mike O''Donnell', 'mike.odonnell@peregrine.io', '2023-01-23', 'active'),
(5, 'Jag Madan', 'jag.madan@peregrine.io', '2025-06-23', 'active'),
(6, 'Aneesh Deshpande', 'aneesh.deshpande@peregrine.io', '2025-02-03', 'active'),
(7, 'Tejas Anturkar', 'tejas.anturkar@peregrine.io', '2024-02-12', 'active'),
(8, 'Robbie Aronoff', 'robbie.aronoff@peregrine.io', '2023-09-11', 'active'),
(9, 'Emily Dworkin', 'emily.dworkin@peregrine.io', '2024-06-24', 'active'),
(10, 'Jerod Nelsen', 'jerod.nelsen@peregrine.io', '2024-11-18', 'active'),
(11, 'James Wenzel', 'james.wenzel@peregrine.io', '2025-02-03', 'active'),
(12, 'Kelsey Thompson', 'kelsey.thompson@peregrine.io', '2025-02-03', 'active'),
(13, 'Stephen Hei', 'stephen.hei@peregrine.io', '2025-03-10', 'active'),
(14, 'Catherine Zhao', 'catherine.zhao@peregrine.io', '2025-05-19', 'active'),
(15, 'Tejas Ogale', 'tejas.ogale@peregrine.io', '2025-09-15', 'active'),
(16, 'Jessie Nguyen', 'jessie.nguyen@peregrine.io', '2025-01-13', 'active'),
(17, 'Ben Prudhomme', 'ben.prudhomme@peregrine.io', '2025-08-25', 'active'),
(18, 'Gaurav Mehta', 'gaurav.mehta@peregrine.io', '2024-02-12', 'active'),
(19, 'Rachel Lurie', 'rachel.lurie@peregrine.io', '2025-08-04', 'active'),
(20, 'Michael Gates', 'michael.gates@peregrine.io', '2025-10-06', 'inactive'),
(21, 'Tommy Rogers', 'thomas.rogers@peregrine.io', '2025-04-07', 'inactive');

-- Reset sequence
SELECT setval('spls_id_seq', (SELECT MAX(id) FROM spls));

-- Add FK constraint on customers now that spls table exists
ALTER TABLE customers ADD CONSTRAINT fk_customers_primary_spl FOREIGN KEY (primary_spl_id) REFERENCES spls(id);
