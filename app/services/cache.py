"""Simple TTL-based in-memory cache for analysis reports."""

import time, logging
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)
CACHE_TTL_SECONDS = 300

@dataclass
class CacheEntry:
    report: str
    created_at: float = 0.0

    def __post_init__(self):
        self.created_at = time.time()

    def is_valid(self):
        return (time.time() - self.created_at) < CACHE_TTL_SECONDS

class AnalysisCache:
    def __init__(self):
        self._store: Dict[str, CacheEntry] = {}

    def get(self, sector: str) -> Optional[str]:
        entry = self._store.get(sector)
        if entry and entry.is_valid():
            logger.info("Cache HIT: %s", sector)
            return entry.report
        if entry:
            del self._store[sector]
        return None

    def set(self, sector: str, report: str):
        self._store[sector] = CacheEntry(report=report)

    def clear(self):
        self._store.clear()

analysis_cache = AnalysisCache()
