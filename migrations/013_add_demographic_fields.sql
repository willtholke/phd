-- Add demographic fields to taskers
ALTER TABLE taskers ADD COLUMN date_of_birth DATE;
ALTER TABLE taskers ADD COLUMN age INTEGER;
ALTER TABLE taskers ADD COLUMN gender VARCHAR(20);
ALTER TABLE taskers ADD COLUMN highest_education_level VARCHAR(50);
ALTER TABLE taskers ADD COLUMN is_student BOOLEAN DEFAULT false;
ALTER TABLE taskers ADD COLUMN employment_status VARCHAR(50);
ALTER TABLE taskers ADD COLUMN company VARCHAR(255);
