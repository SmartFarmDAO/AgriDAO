-- Production database initialization
-- This file is automatically executed when PostgreSQL container starts

-- Create database if not exists (PostgreSQL will create it automatically from environment variables)
-- Additional initialization can be added here if needed

-- Example: Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set default permissions and configurations
-- (Add any additional setup needed for production)