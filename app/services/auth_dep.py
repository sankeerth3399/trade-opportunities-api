"""Auth helper — extracts Bearer token from request headers."""

import logging
from fastapi import HTTPException, Request, status
from app.services.session_store import session_store, Session

logger = logging.getLogger(__name__)

def get_session_from_request(request: Request) -> Session:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token. Please authenticate via POST /auth/token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header[len("Bearer "):]
    session = session_store.get_session_by_token(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please re-authenticate via POST /auth/token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return session
