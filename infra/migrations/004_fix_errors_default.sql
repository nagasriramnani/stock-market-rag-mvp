-- Fix: Ensure errors column defaults to empty array, never NULL
-- This prevents Pydantic validation errors when PostgREST returns null for empty arrays

-- Set default for existing column
alter table runs
  alter column errors set default array[]::text[];

-- Update existing NULL values to empty arrays
update runs
  set errors = array[]::text[]
  where errors is null;

-- Prevent future NULLs (optional but recommended)
alter table runs
  alter column errors set not null;

