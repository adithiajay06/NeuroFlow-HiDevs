
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Documents table
CREATE TABLE documents (...);

-- Chunks table
CREATE TABLE chunks (...);

-- Add indexes here
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
CREATE INDEX ON chunks USING gin (to_tsvector('english', content));
