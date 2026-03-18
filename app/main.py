"""Trade Opportunities API — Python 3.14 compatible, no pydantic."""

import time, uuid, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from app.routers import analyze, auth
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.services.session_store import session_store

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Trade Opportunities API starting up ...")
    yield
    logger.info("Trade Opportunities API shutting down ...")

app = FastAPI(
    title="Trade Opportunities API",
    description="Analyzes market data and provides trade opportunity insights for sectors in India. Powered by Gemini AI.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(RateLimiterMiddleware)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    start = time.time()
    response = await call_next(request)
    elapsed = round((time.time() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{elapsed}ms"
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(analyze.router, prefix="", tags=["Analysis"])

@app.get("/app", tags=["Frontend"], include_in_schema=False)
async def serve_app():
    return FileResponse("app.html")

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0",
            "active_sessions": len(session_store.sessions)}

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Trade Opportunities API",
        "ui": "https://trade-opportunities-api.onrender.com/app",
        "docs": "https://trade-opportunities-api.onrender.com/docs",
        "health": "https://trade-opportunities-api.onrender.com/health",
        "usage": {
            "step_1": "POST /auth/token  ->  get Bearer token",
            "step_2": "GET  /analyze/{sector}  ->  get markdown report",
            "sectors": ["pharmaceuticals","technology","agriculture","textiles",
                        "automotive","renewable_energy","fintech","healthcare"]
        }
    }
