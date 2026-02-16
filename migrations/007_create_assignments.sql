-- Assignments
CREATE TABLE assignments (
    id SERIAL PRIMARY KEY,
    tasker_id INTEGER NOT NULL REFERENCES taskers(id),
    project_id INTEGER NOT NULL REFERENCES projects(id),
    assigned_date DATE NOT NULL,
    removed_date DATE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'removed')),
    removal_reason TEXT
);

INSERT INTO assignments (id, tasker_id, project_id, assigned_date, removed_date, status, removal_reason) VALUES
-- Project 1: Llama-RLHF-v4 (SWE taskers: 1,2,3,4)
(1, 1, 1, '2025-01-15', NULL, 'active', NULL),
(2, 2, 1, '2025-01-15', NULL, 'active', NULL),
(3, 3, 1, '2025-01-20', NULL, 'active', NULL),
(4, 4, 1, '2025-01-20', '2025-02-10', 'removed', 'Reassigned to OpenAI project due to NLP expertise'),

-- Project 2: Llama-Safety-Review (Security/Law: 5,11; SWE: 1)
(5, 5, 2, '2025-02-01', NULL, 'active', NULL),
(6, 1, 2, '2025-02-01', NULL, 'active', NULL),
(7, 11, 2, '2025-02-05', NULL, 'active', NULL),

-- Project 3: Helios-CodeReview-pass2 (Backend/DB SWE: 2,3)
(8, 2, 3, '2025-01-20', NULL, 'active', NULL),
(9, 3, 3, '2025-01-25', NULL, 'active', NULL),
(10, 5, 3, '2025-01-25', '2025-02-15', 'removed', 'Moved to Meta Safety project for security expertise'),

-- Project 4: Helios-RLHF-pass3 (AI/ML + NLP: 4,1,12)
(11, 4, 4, '2025-02-01', NULL, 'active', NULL),
(12, 1, 4, '2025-02-05', NULL, 'active', NULL),
(13, 12, 4, '2025-02-05', NULL, 'active', NULL),

-- Project 5: Gemini-MedEval-2025 (Medical: 6,7,8)
(14, 6, 5, '2025-01-10', NULL, 'active', NULL),
(15, 7, 5, '2025-01-10', NULL, 'active', NULL),
(16, 8, 5, '2025-01-15', NULL, 'active', NULL),

-- Project 6: Gemini-LegalEval-2025 (Legal: 9,10,11)
(17, 9, 6, '2025-02-01', NULL, 'active', NULL),
(18, 10, 6, '2025-02-01', NULL, 'active', NULL),
(19, 11, 6, '2025-02-05', NULL, 'active', NULL),

-- Project 7: Grok-SWE-Training-v2 (SWE: 1,2,3,4,5)
(20, 1, 7, '2024-09-15', NULL, 'active', NULL),
(21, 2, 7, '2024-09-15', '2024-12-01', 'removed', 'Contract hours reduced'),
(22, 3, 7, '2024-09-20', NULL, 'active', NULL),
(23, 4, 7, '2024-10-01', '2024-11-15', 'removed', 'Not completing tasks on time'),
(24, 5, 7, '2024-10-15', NULL, 'active', NULL),

-- Project 8: Grok-RedTeam-2025 (Security + Tech Law: 5,10)
(25, 5, 8, '2025-02-01', NULL, 'active', NULL),
(26, 10, 8, '2025-02-05', NULL, 'active', NULL),
(27, 1, 8, '2025-02-05', NULL, 'active', NULL),

-- Project 9: Claude-SciEval-2025 (Science: 14,15,16,17)
(28, 14, 9, '2025-01-15', NULL, 'active', NULL),
(29, 15, 9, '2025-01-15', NULL, 'active', NULL),
(30, 16, 9, '2025-01-20', NULL, 'active', NULL),
(31, 17, 9, '2025-01-20', NULL, 'active', NULL),
(32, 6, 9, '2025-01-25', '2025-02-10', 'removed', 'Workload conflict with Google MedEval project'),

-- Project 10: Claude-HumanitiesEval-2025 (Humanities/Social: 18,19)
(33, 18, 10, '2025-02-01', NULL, 'active', NULL),
(34, 19, 10, '2025-02-01', NULL, 'active', NULL),
(35, 13, 10, '2025-02-05', NULL, 'active', NULL),

-- Additional cross-project assignments for realism
(36, 3, 4, '2025-02-10', NULL, 'active', NULL),
(37, 7, 9, '2025-02-01', NULL, 'active', NULL),
(38, 9, 2, '2025-02-10', NULL, 'active', NULL),
(39, 12, 1, '2025-02-01', NULL, 'active', NULL),
(40, 18, 6, '2025-02-10', NULL, 'active', NULL);

SELECT setval('assignments_id_seq', (SELECT MAX(id) FROM assignments));
