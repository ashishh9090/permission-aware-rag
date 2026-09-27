export interface Persona {
  id: string;
  username: string;
  tenant_id: string;
  roles: string[];
  groups: string[];
  clearance_level: string;
  department: string;
}

export interface User {
  id: string;
  tenant_id: string;
  username: string;
  email: string;
  roles: string[];
  groups: string[];
  account_status: string;
  clearance_level: string;
  department: string;
  created_at: string;
}

export interface DocumentItem {
  document_id: string;
  tenant_id: string;
  owner_id: string;
  document_name: string;
  document_type: string;
  classification: string;
  allowed_roles: string[];
  allowed_users: string[];
  allowed_groups: string[];
  access_policy_version: number;
  ingestion_status: string;
  summary?: string;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  document_id: string;
  document_name: string;
  chunk_id: string;
  source_reference: string;
  classification: string;
  quote_snippet: string;
}

export interface RetrievalTrace {
  request_id: string;
  tenant_id: string;
  user_id: string;
  policy_version_applied: number;
  total_candidates_retrieved: number;
  authorized_chunks_count: number;
  denied_candidates_count: number;
  authorized_chunk_ids: string[];
  retrieval_latency_ms: number;
  revalidation_latency_ms: number;
  llm_generation_latency_ms: number;
  total_latency_ms: number;
  cache_hit: boolean;
}

export interface RAGResponse {
  query: string;
  answer: string;
  citations: Citation[];
  retrieval_trace: RetrievalTrace;
  insufficient_evidence: boolean;
  request_id: string;
}

export interface AuditLog {
  event_id: string;
  timestamp: string;
  request_id: string;
  tenant_id: string;
  user_id: string;
  action: string;
  authorization_policy_version: number;
  query_text?: string;
  retrieved_chunk_ids: string[];
  authorized_chunk_ids: string[];
  denied_candidate_count: number;
  document_ids_sent_to_llm: string[];
  access_decision: string;
  outcome: string;
  latency_ms: number;
  details_json: Record<string, any>;
}

export interface AuditSummary {
  total_events: number;
  permit_count: number;
  deny_count: number;
  tamper_attempts: number;
  average_latency_ms: number;
}
