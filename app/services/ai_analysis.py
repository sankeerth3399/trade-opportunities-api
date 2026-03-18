"""Gemini AI analysis service."""

from __future__ import annotations
import logging, os
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

def _build_prompt(sector: str, search_results: list) -> str:
    snippets = "\n".join(f"- **{r['title']}**: {r['snippet']}" for r in search_results)
    today = datetime.utcnow().strftime("%B %d, %Y")
    return f"""You are a senior trade analyst specializing in Indian markets.
Generate a comprehensive markdown report on trade opportunities for the
**{sector.replace('_', ' ').title()}** sector in India as of {today}.

Recent search intelligence:
{snippets}

Use this exact structure:

---
# 🇮🇳 India Trade Opportunities: {sector.replace('_', ' ').title()} Sector
**Generated:** {today} | **Powered by:** Gemini AI

---
## 📊 Executive Summary
[3-4 sentences on current state and top opportunity]

---
## 🌍 Global Market Context
[Global demand, India's positioning, key importing countries]

---
## 📈 Key Trade Opportunities
### 1. [Opportunity Name]
- **Market Size**: ...
- **Target Markets**: ...
- **Why Now**: ...
- **Entry Strategy**: ...
[Repeat for 4-5 opportunities]

---
## 🏭 Sector Insights
[PLI schemes, infrastructure, MSME ecosystem, regulations]

---
## ⚠️ Risks & Challenges
| Risk | Mitigation |
|------|-----------|
[3-4 rows]

---
## 🔗 Key Resources
[Ministries, export councils, trade bodies]

---
## 📌 Next Steps
[5 numbered actionable steps]

---
*Report by Trade Opportunities API v1.0*
"""

async def generate_analysis(sector: str, search_results: list) -> str:
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set — using fallback report.")
        return _fallback_report(sector, search_results)

    payload = {
        "contents": [{"parts": [{"text": _build_prompt(sector, search_results)}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 3000, "topP": 0.9},
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                GEMINI_URL, params={"key": GEMINI_API_KEY}, json=payload
            )
            resp.raise_for_status()
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as exc:
        logger.error("Gemini API error: %s", exc)
        return _fallback_report(sector, search_results)

def _fallback_report(sector: str, search_results: list) -> str:
    today = datetime.utcnow().strftime("%B %d, %Y")
    sd = sector.replace("_", " ").title()
    snippets_md = "\n".join(f"- **{r['title']}**: {r['snippet']}" for r in search_results) or "- No live data."
    return f"""# 🇮🇳 India Trade Opportunities: {sd} Sector
**Generated:** {today} | **Note:** Set GEMINI_API_KEY for AI-powered analysis.

---

## 📊 Executive Summary

India's **{sd}** sector is a significant trade opportunity. With PLI incentives,
export-first policy, and growing bilateral agreements, businesses are well-positioned
for both domestic growth and international expansion.

---

## 🌍 Global Market Context

India is asserting itself as a global supply-chain alternative with:
- **Cost advantages** of 20–40% vs Western peers
- **Large skilled workforce** and growing R&D ecosystem
- **Improving logistics** via PM GatiShakti National Master Plan

---

## 📈 Key Trade Opportunities

### 1. Export to High-Income Markets
- **Target Markets**: USA, EU, UAE, UK, Australia
- **Why Now**: India-UAE CEPA and India-Australia ECTA reduce tariffs
- **Entry Strategy**: Partner with Export Promotion Councils (EPC)

### 2. PLI Scheme Participation
- **Value**: ₹1.97 lakh crore allocated across PLI schemes
- **Why Now**: Scheme windows actively open; early movers get max incentives
- **Entry Strategy**: Apply through the nodal ministry portal

### 3. MSME Export Clusters
- **Target Markets**: South-East Asia, Africa, Middle East
- **Entry Strategy**: Join FIEO cluster programmes

### 4. Digital & E-Commerce Exports
- **Value**: Cross-border e-commerce projected at $350B by 2030
- **Entry Strategy**: List on Amazon Global, Alibaba, and ONDC export gateway

---

## 📰 Recent Intelligence
{snippets_md}

---

## 🏭 Sector Insights

- **PLI Schemes**: 4–6% incentive on incremental sales
- **Export Credit**: ECGC and EXIM Bank provide affordable insurance
- **SEZ Benefits**: Tax holidays and simplified compliance
- **Quality Certs**: BIS, FSSAI, BEE certifications for exports

---

## ⚠️ Risks & Challenges

| Risk | Mitigation |
|------|-----------|
| Global demand slowdown | Diversify across 5+ export markets |
| INR volatility | Use forward contracts and natural hedging |
| Regulatory compliance | Engage a compliance consultant early |
| Logistics bottlenecks | Use DPIIT logistics hub finder tool |

---

## 🔗 Key Resources

- **Ministry of Commerce** – Policy & trade agreements
- **DGFT** (dgft.gov.in) – Export licences, FTP 2023–28
- **FIEO** (fieo.org) – Federation of Indian Export Organisations
- **EXIM Bank** – Export financing and market intelligence
- **Invest India** (investindia.gov.in) – FDI facilitation

---

## 📌 Next Steps

1. Register on DGFT portal and obtain IEC (Import Export Code)
2. Identify target market using FIEO market intelligence reports
3. Apply for relevant PLI scheme through the nodal ministry
4. Connect with Export Promotion Council for your sub-sector
5. Arrange export credit insurance through ECGC

---
*Report by Trade Opportunities API v1.0 | Sources: DuckDuckGo + curated data*
"""
