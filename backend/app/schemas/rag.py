from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Citation(BaseModel):
    document_id: str
    document_name: str
    chunk_id: str
    source_reference: str
    classification: str
    quote_snippet: str

class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    conversation_history: Optional[List[Dict[str, str]]] = None
    simulate_mid_flight_revocation_doc_id: Optional[str] = None  # To demonstrate/test mid-flight permission revocation

class RetrievalTrace(BaseModel):
    request_id: str
    tenant_id: str
    user_id: str
    policy_version_applied: int
    total_candidates_retrieved: int
    authorized_chunks_count: int
    denied_candidates_count: int
    authorized_chunk_ids: List[str]
    retrieval_latency_ms: float
    revalidation_latency_ms: float
    llm_generation_latency_ms: float
    total_latency_ms: float
    cache_hit: bool

class RAGResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
    retrieval_trace: RetrievalTrace
    insufficient_evidence: bool
    request_id: str
