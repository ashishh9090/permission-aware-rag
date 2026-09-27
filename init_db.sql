-- ==============================================================================
-- Permission-Aware Multi-Tenant RAG Schema & Row-Level Security (PostgreSQL + pgvector)
-- ==============================================================================

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Tenants Table
CREATE TABLE IF NOT EXISTS tenants (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    slug VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    settings_json JSONB DEFAULT '{}'::jsonb
);

-- 3. Users Table (RBAC + ABAC Attributes)
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    username VARCHAR(64) NOT NULL,
    email VARCHAR(128) NOT NULL,
    hashed_password VARCHAR(256) NOT NULL,
    roles JSONB NOT NULL DEFAULT '["Employee"]'::jsonb,
    groups JSONB NOT NULL DEFAULT '[]'::jsonb,
    account_status VARCHAR(32) NOT NULL DEFAULT 'active',
    clearance_level VARCHAR(32) NOT NULL DEFAULT 'Internal',
    department VARCHAR(64) NOT NULL DEFAULT 'General',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);

-- 4. Documents Table
CREATE TABLE IF NOT EXISTS documents (
    document_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    owner_id VARCHAR(64) NOT NULL REFERENCES users(id),
    document_name VARCHAR(256) NOT NULL,
    document_type VARCHAR(32) NOT NULL,
    classification VARCHAR(32) DEFAULT 'Internal',
    allowed_roles JSONB DEFAULT '["Employee"]'::jsonb,
    allowed_users JSONB DEFAULT '[]'::jsonb,
    allowed_groups JSONB DEFAULT '[]'::jsonb,
    access_policy_version INTEGER NOT NULL DEFAULT 1,
    ingestion_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    content_hash VARCHAR(64),
    summary TEXT,
    metadata_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_documents_tenant_id ON documents(tenant_id);
CREATE INDEX IF NOT EXISTS idx_documents_owner_id ON documents(owner_id);

-- 5. Chunks Table (Vector Storage + Access Metadata)
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id VARCHAR(64) PRIMARY KEY,
    document_id VARCHAR(64) NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    classification VARCHAR(32) DEFAULT 'Internal',
    allowed_roles JSONB DEFAULT '["Employee"]'::jsonb,
    allowed_users JSONB DEFAULT '[]'::jsonb,
    allowed_groups JSONB DEFAULT '[]'::jsonb,
    access_policy_version INTEGER NOT NULL DEFAULT 1,
    source_reference VARCHAR(256) NOT NULL,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    metadata_json JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_chunks_tenant_id ON chunks(tenant_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
-- HNSW Cosine Similarity Index on pgvector embeddings
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING hnsw (embedding vector_cosine_ops);

-- 6. Append-Only Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    event_id VARCHAR(64) PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    request_id VARCHAR(64) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    action VARCHAR(64) NOT NULL,
    authorization_policy_version INTEGER NOT NULL DEFAULT 1,
    query_text VARCHAR(512),
    retrieved_chunk_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    authorized_chunk_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    denied_candidate_count INTEGER NOT NULL DEFAULT 0,
    document_ids_sent_to_llm JSONB NOT NULL DEFAULT '[]'::jsonb,
    access_decision VARCHAR(32) NOT NULL,
    outcome VARCHAR(64) NOT NULL,
    latency_ms DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant ON audit_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- ==============================================================================
-- Database-Enforced Row-Level Security (RLS) Policies
-- ==============================================================================

-- Enable RLS on multi-tenant tables
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Tenants can only see their own documents
CREATE POLICY tenant_isolation_documents ON documents
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), ''));

-- Tenants can only see their own chunks (Database-enforced isolation)
CREATE POLICY tenant_isolation_chunks ON chunks
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), ''));

-- Tenant audit isolation
CREATE POLICY tenant_isolation_audit ON audit_logs
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), ''));
