-- Add detailed education fields to taskers
ALTER TABLE taskers ADD COLUMN undergrad_university VARCHAR(255);
ALTER TABLE taskers ADD COLUMN undergrad_major VARCHAR(255);
ALTER TABLE taskers ADD COLUMN undergrad_graduation_year INTEGER;
ALTER TABLE taskers ADD COLUMN grad_university VARCHAR(255);
ALTER TABLE taskers ADD COLUMN grad_degree VARCHAR(50);
ALTER TABLE taskers ADD COLUMN grad_field VARCHAR(255);
ALTER TABLE taskers ADD COLUMN grad_graduation_year INTEGER;
