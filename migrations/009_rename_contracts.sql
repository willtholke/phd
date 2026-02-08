-- Rename contracts to not include customer names
UPDATE contracts SET contract_name = 'RLHF Preference Ranking Q3-Q4 2024' WHERE id = 1;
UPDATE contracts SET contract_name = 'Safety Annotation Program 2025' WHERE id = 2;
UPDATE contracts SET contract_name = 'Alignment Research Support Q4 2024' WHERE id = 3;
UPDATE contracts SET contract_name = 'Code Quality Assessment 2025' WHERE id = 4;
UPDATE contracts SET contract_name = 'Multimodal Evaluation H1 2025' WHERE id = 5;
UPDATE contracts SET contract_name = 'Foundation Model Training 2024' WHERE id = 6;
UPDATE contracts SET contract_name = 'Adversarial Testing Program 2025' WHERE id = 7;
UPDATE contracts SET contract_name = 'Domain Expert Evaluation 2025' WHERE id = 8;
