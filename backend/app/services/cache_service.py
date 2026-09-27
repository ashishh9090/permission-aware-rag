import hashlib
import time
from typing import Optional, Dict, Any, Tuple
from backend.app.core.config import settings
from backend.app.models.user import User

class TenantIsolatedCache:
    """
    Tenant-Isolated Semantic and Response Cache.
    Keys are strictly derived from:
    - tenant_id
    - user clearance level (ABAC)
    - user authorized roles & groups (RBAC)
    - authoritative access_policy_version
    - query text
    Prevents cross-tenant or cross-role cache bleeding.
    """
    def __init__(self):
        # In-memory dictionary: key -> (timestamp, data)
        self._cache: Dict[str, Tuple[float, Any]] = {}

    def _generate_key(self, user: User, query: str, policy_version: int) -> str:
        roles_str = ",".join(sorted(user.roles or []))
        groups_str = ",".join(sorted(user.groups or []))
        normalized_q = " ".join(query.strip().lower().split())
        
        raw_key = (
            f"tenant:{user.tenant_id}|"
            f"clearance:{user.clearance_level}|"
            f"roles:{roles_str}|"
            f"groups:{groups_str}|"
            f"pol_ver:{policy_version}|"
            f"q:{normalized_q}"
        )
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def get(self, user: User, query: str, policy_version: int) -> Optional[Any]:
        if not settings.CACHE_ENABLED:
            return None

        key = self._generate_key(user, query, policy_version)
        entry = self._cache.get(key)
        if not entry:
            return None

        cached_time, data = entry
        if time.time() - cached_time > settings.CACHE_TTL_SECONDS:
            del self._cache[key]
            return None

        return data

    def set(self, user: User, query: str, policy_version: int, data: Any):
        if not settings.CACHE_ENABLED:
            return

        key = self._generate_key(user, query, policy_version)
        self._cache[key] = (time.time(), data)

    def invalidate_tenant(self, tenant_id: str):
        """Invalidates all cache entries belonging to a given tenant."""
        to_del = []
        # Since we hash keys, we can also clear or maintain a secondary tenant index
        self._cache.clear()

cache_service = TenantIsolatedCache()
