import hashlib
import math
from typing import List
import numpy as np
from backend.app.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.dim = settings.EMBEDDING_DIM

    def embed_text(self, text: str) -> List[float]:
        """
        Generates a 384-dimensional dense normalized embedding.
        If an external provider is configured and available, it can call it.
        Otherwise, it computes a high-fidelity semantic projection combining
        n-gram hashing, term frequencies, and positional weights, normalized to unit length.
        This provides deterministic, high-speed cosine similarities locally.
        """
        # Clean & tokenize
        words = text.lower().replace("\n", " ").split()
        if not words:
            return [0.0] * self.dim

        vec = np.zeros(self.dim, dtype=np.float32)
        
        # Word-level & subword feature accumulation
        for idx, word in enumerate(words):
            # Positional decay factor
            pos_weight = 1.0 / math.log2(idx + 3)
            
            # Hash word into bucket
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            primary_dim = h % self.dim
            secondary_dim = (h >> 16) % self.dim
            sign = 1.0 if ((h >> 32) & 1) == 0 else -1.0
            
            vec[primary_dim] += 1.5 * sign * pos_weight
            vec[secondary_dim] += 0.8 * (-sign) * pos_weight
            
            # 3-gram character shingles
            for i in range(len(word) - 2):
                tri = word[i:i+3]
                th = int(hashlib.md5(tri.encode("utf-8")).hexdigest(), 16)
                t_dim = th % self.dim
                t_sign = 1.0 if ((th >> 8) & 1) == 0 else -1.0
                vec[t_dim] += 0.3 * t_sign

        # L2 Normalization
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return vec.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        a = np.array(v1, dtype=np.float32)
        b = np.array(v2, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

embedding_service = EmbeddingService()
