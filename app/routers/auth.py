"""Authentication router."""

import logging
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.services.session_store import session_store, TOKEN_TTL_SECONDS

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/token", summary="Obtain a Bearer token",
    description="**Demo credentials:**\n- `admin` / `password123`\n- `analyst` / `trade2024!`\n- `guest` / `guest123`")
async def get_token(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    username = body.get("username", "").strip()
    password = body.get("password", "").strip()

    if not username or len(username) < 3:
        raise HTTPException(status_code=422, detail="username must be at least 3 characters.")
    if not password or len(password) < 6:
        raise HTTPException(status_code=422, detail="password must be at least 6 characters.")

    result = session_store.authenticate(username, password)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    token, session_id = result
    logger.info("Token issued: user=%s session=%s", username, session_id)
    return JSONResponse({"access_token": token, "token_type": "bearer",
                         "expires_in": TOKEN_TTL_SECONDS, "session_id": session_id})
