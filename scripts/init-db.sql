-- ─── Project LIFELINK — Database Initialization ───
-- This runs automatically when PostgreSQL container starts for the first time.

-- Enable pgvector extension (for AI embeddings storage)
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Confirm extensions are loaded
SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp');
