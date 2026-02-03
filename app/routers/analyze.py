from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import re

router = APIRouter()

# --- 1. Define the Input/Output Models ---


class AnalyzeRequest(BaseModel):
    message: str
    metadata: Optional[dict] = {}


class RiskReason(BaseModel):
    type: str
    description: str
    weight: int = 0  # Helper for backend calculation


class UrlIndicator(BaseModel):
    url: str        # <--- This exact name matches Frontend {url.url}
    risk_type: str


class AnalyzeResponse(BaseModel):
    scam_risk_score: int
    reasons: List[RiskReason]
    url_indicators: List[UrlIndicator]

# --- 2. The Risk Engine (The Brain) ---


def calculate_risk(text: str):
    score = 0
    reasons = []
    url_indicators = []

    text_lower = text.lower()

    # A. KEYWORD DETECTION (Weighted)
    keywords = {
        # High Risk (Urgency & Money)
        "urgent": 20, "immediately": 20, "suspended": 25, "blocked": 25,
        "kyc": 20, "pan card": 20, "update now": 15,

        # Financial / Lottery
        "winner": 25, "lottery": 25, "won": 20, "prize": 20,
        "credit": 15, "credited": 15, "bank": 10,

        # Job Scams (The Fix for your issue)
        "part-time": 25, "part time": 25, "job offer": 20, "wfh": 20,
        "working from home": 20, "earn": 15, "daily income": 20,
        "5000/day": 25, "salary": 10, "hiring": 10, "no experience": 15
    }

    for word, weight in keywords.items():
        if word in text_lower:
            score += weight
            reasons.append({
                "type": "keyword_match",
                "description": f"Contains high-risk phrase: '{word}'",
                "weight": weight
            })

    # B. PHONE NUMBER DETECTION (WhatsApp Scams)
    # Looks for patterns like +91, 10-digit numbers often found in job scams
    phone_pattern = r"(\+91[\-\s]?)?[6-9]\d{9}"
    if re.search(phone_pattern, text):
        score += 20
        reasons.append({
            "type": "suspicious_contact",
            "description": "Contains a phone number often associated with unsolicited contact.",
            "weight": 20
        })

    # C. URL FORENSICS (The Fix for the invisible link)
    # Regex to find urls
    url_pattern = r"(https?://\S+|www\.\S+|bit\.ly/\S+)"
    urls = re.findall(url_pattern, text)

    for url in urls:
        risk_type = "suspicious_link"
        link_score = 20

        # Check for URL shorteners (High Risk)
        if "bit.ly" in url or "tinyurl" in url:
            link_score = 35
            reasons.append({
                "type": "url_shortener",
                "description": f"Uses URL shortener '{url}' to hide destination.",
                "weight": 35
            })

        score += link_score
        # IMPORTANT: This matches the Frontend Interface perfectly
        url_indicators.append({"url": url, "risk_type": risk_type})

    # D. Final Score Clamping (Max 100)
    final_score = min(100, score)

    # Sort reasons by weight (most important first)
    reasons.sort(key=lambda x: x['weight'], reverse=True)

    return {
        "scam_risk_score": final_score,
        "reasons": reasons,
        "url_indicators": url_indicators
    }

# --- 3. The API Endpoint ---


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_message(request: AnalyzeRequest):
    result = calculate_risk(request.message)
    return result
