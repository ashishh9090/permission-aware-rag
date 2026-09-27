# AegisRAG: Architecture & Security Boundaries

## 1. Executive Architecture Summary

**AegisRAG** is an enterprise multi-tenant Retrieval-Augmented Generation (RAG) platform architected according to **Zero-Trust principles**. The platform guarantees that no document, chunk, metadata, or citation can ever be accessed across organizations or by unauthorized internal users—even in the presence of prompt injections, racing concurrent permission changes, or malicious client-supplied headers.

---

## 2. High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph ClientLayer["Untrusted Client Layer"]
        User["Authenticated User / Client"]
        Browser["React 18 + TS Enterprise Dashboard"]
    end

    subgraph GatewayBoundary["Security Boundary: Identity & Auth Gateway"]
        AuthService["Auth Service (JWT / OIDC)"]
        PolicyEngine["Server-Side Policy Engine\n(Default-Deny RBAC + ABAC)"]
    end

    subgraph DataStorage["Security Boundary: Multi-Tenant Data Store"]
        Postgres["PostgreSQL + pgvector (or SQLite Core)"]
        RLS["Row-Level Security (tenant_id enforcement)"]
        DocTable[("Documents Table")]
        ChunkTable[("Chunks Table + Vector Index")]
    end

    subgraph RetrievalPipeline["Zero-Trust Retrieval Pipeline"]
        TenantFilter["1. Database-Level Tenant Query"]
        HybridEngine["2. Hybrid Scoring\n(Dense Vector + Lexical BM25)"]
        Checkpoint1["3. Checkpoint 1: Real-Time Policy Revalidation"]
        Purge["4. Purge All Unauthorized Candidates"]
    end

    subgraph AssemblyAndLLM["Security Boundary: Context Assembly & LLM Gateway"]
        Checkpoint2["5. Checkpoint 2: Mid-Flight Revocation Check"]
        Sanitizer["6. Untrusted Data Sanitizer\n(Prompt Injection Defuser)"]
        LLM["7. Sandboxed LLM\n(Configurable OpenAI / Local Mock LLM)"]
    end

    subgraph AuditTrail["Security Boundary: Append-Only Audit Logging"]
        AuditService["Append-Only Audit Service"]
        AuditDB[("Audit Logs Store\n(Zero Unauthorized Text Leaked)")]
    end

    subgraph CacheLayer["Tenant-Isolated Semantic Cache"]
        Cache["Cache Key: tenant_id + clearance + roles + groups + policy_version + query"]
    end

    User --> Browser
    Browser -->|Bearer JWT| AuthService
    AuthService --> PolicyEngine
    PolicyEngine -->|Active Identity| RetrievalPipeline
    RetrievalPipeline --> RLS
    RLS --> DocTable
    RLS --> ChunkTable
    TenantFilter --> HybridEngine
    HybridEngine --> Checkpoint1
    Checkpoint1 --> Purge
    Purge --> Checkpoint2
    Checkpoint2 --> Sanitizer
    Sanitizer --> LLM
    RetrievalPipeline -.-> CacheLayer
    RetrievalPipeline --> AuditService
    AssemblyAndLLM --> AuditService
    AuditService --> AuditDB
```

---

## 3. The 7-Step Permission-Aware Retrieval Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as Authenticated User
    participant API as FastAPI Gateway
    participant Auth as Policy Engine
    participant DB as PostgreSQL (RLS)
    participant Reval as Security Checkpoint
    participant Sanitizer as Prompt Injection Guard
    participant LLM as Sandboxed LLM
    participant Audit as Append-Only Audit Log

    User->>API: POST /api/v1/rag/query (Bearer Token)
    API->>Auth: Validate JWT & Resolve Authoritative Identity (DB)
    Note over Auth: Ignores client-supplied tenant/roles.<br/>Resolves Tenant, Roles, Clearance, Groups.
    
    API->>DB: Execute Query: WHERE tenant_id = :tenant_id
    Note over DB: Database RLS guarantees ZERO cross-tenant<br/>candidates are retrieved into memory.
    DB-->>API: Candidate Chunks

    API->>Reval: Checkpoint 1: Real-Time Policy Revalidation
    Note over Reval: Re-evaluates ABAC clearance >= document classification.<br/>Checks allowed_roles & allowed_groups.<br/>Checks access_policy_version parity.
    Reval-->>API: Filtered Authorized Chunks (Drop Denied)

    API->>Reval: Checkpoint 2: Context-Assembly Boundary Check
    Note over Reval: Detects concurrent revocations occurring while<br/>query was running. If revoked, chunk dropped immediately!

    API->>Sanitizer: Scan Untrusted Chunk Text
    Note over Sanitizer: Detects & defuses indirect prompt injections<br/>(e.g., "SYSTEM PROMPT OVERRIDE").

    API->>LLM: Pass ONLY Authorized, Sanitized Context
    LLM-->>API: Grounded Answer with Valid Citations
    
    API->>Audit: Log Structured Event
    Note over Audit: Records candidate count, authorized count, denied count,<br/>policy version, and latency. ZERO document text logged.
    
    API-->>User: RAGResponse (Answer + Citations + Audit Trace)
```

---

## 4. Multi-Tenant Data Model & Relationship Diagram

```mermaid
erDiagram
    TENANTS ||--o{ USERS : "has members"
    TENANTS ||--o{ DOCUMENTS : "owns"
    TENANTS ||--o{ CHUNKS : "isolates"
    TENANTS ||--o{ AUDIT_LOGS : "records"
    DOCUMENTS ||--o{ CHUNKS : "chunks into"
    USERS ||--o{ DOCUMENTS : "uploads"

    TENANTS {
        string id PK
        string name
        string slug UK
        datetime created_at
        json settings_json
    }

    USERS {
        string id PK
        string tenant_id FK
        string username
        string email
        string hashed_password
        json roles "RBAC Roles"
        json groups "ABAC Groups"
        string account_status "active | suspended"
        string clearance_level "Public | Internal | Confidential | Restricted"
        string department
        datetime created_at
    }

    DOCUMENTS {
        string document_id PK
        string tenant_id FK
        string owner_id FK
        string document_name
        string document_type
        string classification "Public | Internal | Confidential | Restricted"
        json allowed_roles
        json allowed_users
        json allowed_groups
        int access_policy_version
        string ingestion_status
        string content_hash
        text summary
        datetime created_at
        datetime updated_at
    }

    CHUNKS {
        string chunk_id PK
        string document_id FK
        string tenant_id FK
        text chunk_text
        vector embedding "384-dimensional dense vector"
        string classification
        json allowed_roles
        json allowed_users
        json allowed_groups
        int access_policy_version
        string source_reference
        int chunk_index
        json metadata_json
    }

    AUDIT_LOGS {
        string event_id PK
        datetime timestamp
        string request_id
        string tenant_id
        string user_id
        string action
        int authorization_policy_version
        string query_text
        json retrieved_chunk_ids
        json authorized_chunk_ids
        int denied_candidate_count
        json document_ids_sent_to_llm
        string access_decision "PERMIT | DENY | PARTIAL_PERMIT"
        string outcome "SUCCESS | FORBIDDEN | PROMPT_INJECTION_DEFUSED"
        float latency_ms
        json details_json "Sanitized metadata (no raw text)"
    }
```

---

## 5. Security Boundary Guarantees

| Security Layer | Threat Addressed | Defense Mechanism |
| :--- | :--- | :--- |
| **Identity Gateway** | Forged Tenant ID / Header Spoofing | Client-supplied tenant IDs and roles are rejected. Authoritative state is derived from signed JWT + DB lookup. |
| **Storage Layer** | Cross-Tenant Data Leakage | Database Row-Level Security (RLS) and query predicates enforce `tenant_id` at the SQL level. |
| **Retrieval Layer** | Privilege Escalation (RBAC/ABAC) | Chunks must satisfy both parent document policy and chunk-level policy across roles, groups, and clearance. |
| **Mid-Flight Boundary** | Race Conditions / Dynamic Revocation | Secondary revalidation occurs immediately before context assembly; revoked documents are purged in-flight. |
| **Context Assembly** | Indirect Prompt Injection | Chunk text is treated as untrusted data; malicious system prompt override patterns are neutralized. |
| **Audit Layer** | Log File Confidentiality Leakage | Append-only logs record metadata, latency, and counts without storing raw document text. |
