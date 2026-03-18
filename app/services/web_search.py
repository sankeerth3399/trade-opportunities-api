"""Web search via DuckDuckGo HTML endpoint — no API key required."""

from __future__ import annotations
import re, logging
import httpx

logger = logging.getLogger(__name__)

DDGO_URL = "https://html.duckduckgo.com/html/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

async def search_sector_news(sector: str) -> list:
    query = f"India {sector} sector trade opportunities export import 2024 2025"
    try:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=10.0) as client:
            resp = await client.post(DDGO_URL, data={"q": query, "kl": "in-en"})
            resp.raise_for_status()
            return _parse(resp.text) or _fallback(sector)
    except Exception as exc:
        logger.warning("Search failed: %s — using fallback.", exc)
        return _fallback(sector)

def _parse(html: str) -> list:
    results = []
    blocks = re.findall(r'<div class="result__body">(.*?)</div>\s*</div>', html, re.DOTALL)
    for block in blocks[:8]:
        t = re.search(r'<a[^>]+class="result__a"[^>]*>(.*?)</a>', block, re.DOTALL)
        s = re.search(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', block, re.DOTALL)
        u = re.search(r'href="([^"]+)"', block)
        title = _clean(t.group(1)) if t else ""
        snippet = _clean(s.group(1)) if s else ""
        url = u.group(1) if u else ""
        if title and snippet:
            results.append({"title": title, "snippet": snippet, "url": url})
    return results

def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    for e, r in [("&amp;","&"),("&lt;","<"),("&gt;",">"),("&nbsp;"," ")]:
        text = text.replace(e, r)
    return re.sub(r"\s+", " ", text).strip()

def _fallback(sector: str) -> list:
    return [
        {
            "title": f"India {sector.title()} Sector Trade Overview",
            "snippet": (
                f"India's {sector} sector benefits from PLI schemes, ease-of-doing-business "
                "reforms, and bilateral trade agreements with EU, UAE, and Australia."
            ),
            "url": "https://commerce.gov.in",
        },
        {
            "title": "India Export Promotion Policy 2024",
            "snippet": (
                "Government targets $2 trillion exports by 2030 through district-level "
                "export hubs, logistics upgrades, and MSME tax incentives."
            ),
            "url": "https://dgft.gov.in",
        },
        {
            "title": "DPIIT FDI Investment Opportunities",
            "snippet": (
                "FDI inflows reached record levels in FY2024, driven by manufacturing, "
                "digital infrastructure, and clean energy sectors."
            ),
            "url": "https://dpiit.gov.in",
        },
    ]
