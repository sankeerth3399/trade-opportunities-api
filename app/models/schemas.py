"""Data models using plain dataclasses — no pydantic, Python 3.14 compatible."""

from dataclasses import dataclass
from datetime import datetime

ALLOWED_SECTORS = {
    "pharmaceuticals", "technology", "agriculture", "textiles",
    "automotive", "renewable_energy", "chemicals", "electronics",
    "food_processing", "gems_and_jewellery", "steel", "defence",
    "aerospace", "fintech", "healthcare", "education", "logistics",
    "real_estate", "retail", "telecommunications",
}

@dataclass
class TokenResponse:
    access_token: str
    session_id: str
    token_type: str = "bearer"
    expires_in: int = 3600

    def to_dict(self):
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "session_id": self.session_id,
        }

@dataclass
class AnalysisResponse:
    sector: str
    generated_at: datetime
    session_id: str
    request_id: str
    report: str
    cached: bool = False

    def to_dict(self):
        return {
            "sector": self.sector,
            "generated_at": self.generated_at.isoformat(),
            "session_id": self.session_id,
            "request_id": self.request_id,
            "report": self.report,
            "cached": self.cached,
        }
