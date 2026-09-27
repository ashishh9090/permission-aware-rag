import time
import uuid
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from rank_bm25 import BM25Okapi

from backend.app.core.config import settings
from backend.app.core.security import AuthorizationEngine
from backend.app.models.user import User
from backend.app.models.chunk import Chunk
from backend.app.models.document import Document
from backend.app.services.embedding_service import embedding_service
from backend.app.services.audit_service import audit_service
from backend.app.schemas.retrieval import ChunkResult

class PermissionAwareRetrievalService:
    @staticmethod
    def _execute_hybrid_scoring(
        query: str,
        query_vec: List[float],
        candidate_chunks: List[Chunk],
        alpha: float = 0.6
    ) -> List[Tuple[Chunk, float]]:
        """
        Combines Dense Vector Cosine Similarity and Lexical BM25 ranking.
        score = alpha * vector_sim + (1 - alpha) * bm25_normalized_score
        """
        if not candidate_chunks:
            return []

        # 1. Vector cosine similarities
        vec_scores = []
        for chk in candidate_chunks:
            if not chk.embedding or not isinstance(chk.embedding, list):
                vec_scores.append(0.0)
            else:
                sim = max(0.0, embedding_service.cosine_similarity(query_vec, chk.embedding))
                vec_scores.append(sim)

        # 2. BM25 keyword scores
        corpus = [c.chunk_text.lower().split() for c in candidate_chunks]
        tokenized_query = query.lower().split()
        bm25 = BM25Okapi(corpus)
        raw_bm25_scores = [max(0.0, float(s)) for s in bm25.get_scores(tokenized_query)]
        max_bm25 = max(raw_bm25_scores) if len(raw_bm25_scores) > 0 and max(raw_bm25_scores) > 0 else 1.0
        norm_bm25_scores = [s / max_bm25 for s in raw_bm25_scores]

        stopwords = {"what", "is", "the", "for", "in", "of", "and", "to", "a", "an", "does", "have", "do", "how", "why", "are", "with", "regarding", "about"}
        query_keywords = {w.strip("?,.:;!") for w in tokenized_query} - stopwords

        # 3. Hybrid fusion with relevance filtering
        combined = []
        for i, chk in enumerate(candidate_chunks):
            v_score = vec_scores[i]
            k_score = norm_bm25_scores[i]
            chunk_words = {w.strip("?,.:;!") for w in corpus[i]}
            has_keyword = bool(query_keywords.intersection(chunk_words))

            if not has_keyword and v_score < 0.20:
                final_score = 0.0
            else:
                final_score = (alpha * v_score) + ((1.0 - alpha) * k_score)
            combined.append((chk, final_score))

        combined.sort(key=lambda x: x[1], reverse=True)
        return combined

    @classmethod
    def retrieve(
        cls,
        db: Session,
        user: User,
        query: str,
        top_k: int = 5,
        request_id: Optional[str] = None,
        simulation_delay_ms: int = 0
    ) -> Tuple[List[ChunkResult], Dict[str, Any]]:
        """
        7-Step Zero-Trust Permission-Aware Retrieval Pipeline:
        Step 1: Authenticate requesting user (Provided by FastAPI dependency).
        Step 2: Resolve tenant, roles, groups, clearance attributes.
        Step 3: Construct server-side authorization policy.
        Step 4: Execute database-enforced tenant-filtered query (Zero cross-tenant retrieval).
        Step 5: Real-time revalidation security checkpoint against authoritative live policy.
        Step 6: Purge every unauthorized result.
        Step 7: Return only authorized chunks to reranker/LLM.
        """
        start_time = time.time()
        req_id = request_id or f"ret_{uuid.uuid4().hex[:10]}"
        query_vec = embedding_service.embed_text(query)

        # Step 4: Mandatory database-enforced tenant isolation query.
        # NEVER retrieve across tenants. Database query forces Chunk.tenant_id == user.tenant_id
        candidate_chunks: List[Chunk] = (
            db.query(Chunk)
            .filter(Chunk.tenant_id == user.tenant_id)
            .all()
        )

        total_candidates = len(candidate_chunks)
        candidate_ids = [c.chunk_id for c in candidate_chunks]

        # Simulate delay if requested (to test concurrent revocation race conditions)
        if simulation_delay_ms > 0:
            time.sleep(simulation_delay_ms / 1000.0)

        # Step 4b: Rank candidates using hybrid vector + lexical search
        scored_candidates = cls._execute_hybrid_scoring(
            query=query,
            query_vec=query_vec,
            candidate_chunks=candidate_chunks,
            alpha=settings.HYBRID_ALPHA
        )

        revalidation_start = time.time()

        # Step 5 & 6: Security Checkpoint - Real-time revalidation
        # Fetch current parent documents to verify access_policy_version consistency
        authorized_results: List[ChunkResult] = []
        denied_chunk_ids: List[str] = []
        authorized_chunk_ids: List[str] = []
        doc_cache: Dict[str, Document] = {}

        for chk, score in scored_candidates:
            if score <= 0.05:
                continue

            # 5a. Look up fresh parent document record
            if chk.document_id not in doc_cache:
                doc = (
                    db.query(Document)
                    .filter(
                        Document.document_id == chk.document_id,
                        Document.tenant_id == user.tenant_id
                    )
                    .first()
                )
                doc_cache[chk.document_id] = doc
            else:
                doc = doc_cache[chk.document_id]

            # If parent document was deleted or tenant mismatch
            if not doc:
                denied_chunk_ids.append(chk.chunk_id)
                continue

            # 5b. Stale Metadata Check: Chunk policy version must match parent document policy version
            if chk.access_policy_version != doc.access_policy_version:
                # Stale index detected! Deny retrieval unconditionally (default-deny)
                denied_chunk_ids.append(chk.chunk_id)
                continue

            # 5c. Effective permissions must never exceed parent document permissions!
            # Evaluate document-level authorization
            doc_authorized = AuthorizationEngine.is_authorized(
                user=user,
                resource_classification=doc.classification,
                allowed_roles=doc.allowed_roles,
                allowed_users=doc.allowed_users,
                allowed_groups=doc.allowed_groups,
                resource_tenant_id=doc.tenant_id
            )

            # Evaluate chunk-level authorization
            chunk_authorized = AuthorizationEngine.is_authorized(
                user=user,
                resource_classification=chk.classification,
                allowed_roles=chk.allowed_roles,
                allowed_users=chk.allowed_users,
                allowed_groups=chk.allowed_groups,
                resource_tenant_id=chk.tenant_id
            )

            # Both parent and chunk MUST pass authorization
            if doc_authorized and chunk_authorized:
                authorized_chunk_ids.append(chk.chunk_id)
                authorized_results.append(
                    ChunkResult(
                        chunk_id=chk.chunk_id,
                        document_id=doc.document_id,
                        document_name=doc.document_name,
                        chunk_text=chk.chunk_text,
                        score=round(score, 4),
                        classification=chk.classification,
                        source_reference=chk.source_reference,
                        access_policy_version=chk.access_policy_version
                    )
                )
            else:
                denied_chunk_ids.append(chk.chunk_id)

        revalidation_latency = (time.time() - revalidation_start) * 1000.0

        # Step 7: Top-k slice of authorized chunks only
        final_authorized = authorized_results[:top_k]
        final_authorized_ids = [r.chunk_id for r in final_authorized]
        doc_ids_sent = list({r.document_id for r in final_authorized})

        total_latency = (time.time() - start_time) * 1000.0

        decision = "PERMIT" if len(final_authorized) > 0 else ("DENY" if len(denied_chunk_ids) > 0 else "NO_MATCH")
        outcome = "SUCCESS" if decision == "PERMIT" else ("FORBIDDEN_ALL" if len(denied_chunk_ids) > 0 else "ZERO_RESULTS")

        # Authoritative Audit Trail
        audit_service.log_event(
            db=db,
            request_id=req_id,
            tenant_id=user.tenant_id,
            user_id=user.id,
            action="retrieval",
            policy_version=final_authorized[0].access_policy_version if final_authorized else 1,
            query_text=query,
            retrieved_chunk_ids=candidate_ids,
            authorized_chunk_ids=final_authorized_ids,
            denied_count=len(denied_chunk_ids),
            doc_ids_sent=doc_ids_sent,
            decision=decision,
            outcome=outcome,
            latency_ms=total_latency,
            details={
                "top_k_requested": top_k,
                "revalidation_latency_ms": round(revalidation_latency, 2),
                "denied_count": len(denied_chunk_ids)
            }
        )

        trace_meta = {
            "request_id": req_id,
            "tenant_id": user.tenant_id,
            "user_id": user.id,
            "total_candidates": total_candidates,
            "authorized_count": len(authorized_results),
            "denied_count": len(denied_chunk_ids),
            "authorized_chunk_ids": final_authorized_ids,
            "policy_version": final_authorized[0].access_policy_version if final_authorized else 1,
            "retrieval_latency_ms": round(total_latency - revalidation_latency, 2),
            "revalidation_latency_ms": round(revalidation_latency, 2),
            "total_latency_ms": round(total_latency, 2)
        }

        return final_authorized, trace_meta

retrieval_service = PermissionAwareRetrievalService()
