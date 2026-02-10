-- Add status column to projects
ALTER TABLE projects ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active'
    CHECK (status IN ('pipeline', 'staffing', 'active', 'paused', 'completed', 'cancelled'));

-- Set completed for projects with end_date in the past
UPDATE projects SET status = 'completed' WHERE end_date IS NOT NULL AND end_date < CURRENT_DATE;

-- Add roles column to assignments
ALTER TABLE assignments ADD COLUMN roles TEXT[] NOT NULL DEFAULT '{tasker}'
    CHECK (roles <@ ARRAY['tasker', 'reviewer']::text[]);

-- Update some assignments to reviewer or dual roles for sample data
UPDATE assignments SET roles = '{reviewer}' WHERE id IN (8, 17);           -- Wei reviewing code (proj 3), Jonathan reviewing legal (proj 6)
UPDATE assignments SET roles = '{tasker,reviewer}' WHERE id IN (6, 14, 29, 38); -- Alex on safety (proj 2), Emily on med (proj 5), Henrik on sci (proj 9), Jonathan on safety (proj 2)

-- Add internal_roles column to taskers (nullable, freeform)
ALTER TABLE taskers ADD COLUMN internal_roles TEXT[];

-- Seed some sample internal_roles
UPDATE taskers SET internal_roles = '{tasker,reviewer}' WHERE id IN (1, 2, 6, 15);   -- Alex, Wei, Emily, Henrik
UPDATE taskers SET internal_roles = '{reviewer}' WHERE id = 9;                        -- Jonathan (primarily reviews)
UPDATE taskers SET internal_roles = '{tasker}' WHERE id = 13;               -- James Wilson (senior quant)
UPDATE taskers SET internal_roles = '{tasker,reviewer}' WHERE id = 18;      -- Eleanor (experienced professor)
UPDATE taskers SET internal_roles = '{tasker}' WHERE id IN (3, 4, 5, 7, 8, 10, 11, 12, 14, 16, 17, 19, 20);
