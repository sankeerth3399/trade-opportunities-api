"""Core analysis router: GET /analyze/{sector}"""

import logging, re
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.schemas import ALLOWED_SECTORS
from app.services.auth_dep import get_session_from_request
from app.services.web_search import search_sector_news
from app.services.ai_analysis import generate_analysis
from app.services.cache import analysis_cache

logger = logging.getLogger(__name__)
router = APIRouter()
_SECTOR_RE = re.compile(r"^[a-z][a-z0-9_]{1,49}$")

def _validate(sector: str) -> str:
    sector = sector.strip().lower().replace(" ", "_").replace("-", "_")
    if not _SECTOR_RE.match(sector):
        raise HTTPException(status_code=422, detail="Invalid sector format.")
    if sector not in ALLOWED_SECTORS:
        raise HTTPException(status_code=400,
            detail=f"Unknown sector '{sector}'. Supported: {sorted(ALLOWED_SECTORS)}")
    return sector

@router.get("/analyze/{sector}",
    summary="Get trade opportunity analysis for an India sector",
    description=(
        "Returns a structured markdown report with current trade opportunities.\n\n"
        "**Requires Bearer token** from POST /auth/token.\n\n"
        "**Sectors**: pharmaceuticals, technology, agriculture, textiles, automotive, "
        "renewable_energy, chemicals, electronics, food_processing, gems_and_jewellery, "
        "steel, defence, aerospace, fintech, healthcare, education, logistics, "
        "real_estate, retail, telecommunications"
    ))
async def analyze_sector(sector: str, request: Request):
    session = get_session_from_request(request)
    sector = _validate(sector)
    request_id = getattr(request.state, "request_id", "unknown")
    refresh = request.query_params.get("refresh", "false").lower() == "true"

    logger.info("Analyze: sector=%s user=%s refresh=%s", sector, session.username, refresh)

    if not refresh:
        cached = analysis_cache.get(sector)
        if cached:
            return JSONResponse({"sector": sector,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "session_id": session.session_id, "request_id": request_id,
                "report": cached, "cached": True})

    search_results = await search_sector_news(sector)
    report = await generate_analysis(sector, search_results)
    analysis_cache.set(sector, report)
    session.record_request()

    return JSONResponse({"sector": sector,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "session_id": session.session_id, "request_id": request_id,
        "report": report, "cached": False})
