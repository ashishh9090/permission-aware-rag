from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class AuditLogResponse(BaseModel):
    event_id: str
    timestamp: datetime
    request_id: str
    tenant_id: str
    user_id: str
    action: str
    authorization_policy_version: int
    query_text: Optional[str] = None
    retrieved_chunk_ids: List[str]
    authorized_chunk_ids: List[str]
    denied_candidate_count: int
    document_ids_sent_to_llm: List[str]
    access_decision: str
    outcome: str
    latency_ms: float
    details_json: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

class AuditSummary(BaseModel):
    total_events: int
    permit_count: int
    deny_count: int
    tamper_attempts: int
    average_latency_ms: float
