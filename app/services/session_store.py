"""In-memory session / token store."""

from __future__ import annotations
import time, uuid, hashlib, secrets
from dataclasses import dataclass, field
from typing import Dict, Optional

TOKEN_TTL_SECONDS = 3600

@dataclass
class Session:
    session_id: str
    username: str
    token_hash: str
    created_at: float = field(default_factory=time.time)
    request_count: int = 0
    last_request_at: Optional[float] = None

    def is_expired(self):
        return (time.time() - self.created_at) > TOKEN_TTL_SECONDS

    def record_request(self):
        self.request_count += 1
        self.last_request_at = time.time()

class SessionStore:
    _DEMO_USERS = {
        "admin":   "password123",
        "analyst": "trade2024!",
        "guest":   "guest123",
    }

    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self._token_index: Dict[str, str] = {}

    def authenticate(self, username: str, password: str):
        expected = self._DEMO_USERS.get(username)
        if not expected or expected != password:
            return None
        token = secrets.token_urlsafe(32)
        token_hash = self._hash(token)
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = Session(
            session_id=session_id, username=username, token_hash=token_hash
        )
        self._token_index[token_hash] = session_id
        self._purge_expired()
        return token, session_id

    def get_session_by_token(self, token: str):
        token_hash = self._hash(token)
        session_id = self._token_index.get(token_hash)
        if not session_id:
            return None
        session = self.sessions.get(session_id)
        if not session or session.is_expired():
            self.sessions.pop(session_id, None)
            self._token_index.pop(token_hash, None)
            return None
        return session

    def _purge_expired(self):
        expired = [sid for sid, s in self.sessions.items() if s.is_expired()]
        for sid in expired:
            s = self.sessions.pop(sid, None)
            if s:
                self._token_index.pop(s.token_hash, None)

    @staticmethod
    def _hash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

session_store = SessionStore()
