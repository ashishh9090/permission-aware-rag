from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RetrievalQuery(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    simulation_delay_ms: int = Field(default=0, ge=0, le=10000)

class ChunkResult(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    chunk_text: str
    score: float
    classification: str
    source_reference: str
    access_policy_version: int

class RetrievalResponse(BaseModel):
    query: str
    results: List[ChunkResult]
    total_candidates: int
    authorized_count: int
    denied_count: int
    latency_ms: float
    request_id: str
    policy_version_applied: int
