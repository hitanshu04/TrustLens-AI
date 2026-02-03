from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """
    Input payload for /analyze.

    `metadata` provides a placeholder for behavioral / contextual signals
    (e.g. channel, previous interactions, sending frequency) that a future
    ML model can leverage.
    """

    message: str = Field(..., description="Raw message text to analyze.")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional behavioral/contextual signals for ML models.",
    )


class Reason(BaseModel):
    """
    Explainable reason contributing to the final scam risk score.
    """

    type: Literal["keyword", "url_reputation", "behavioral", "ml_model"] = Field(
        ...,
        description="Source of the signal (rules, URL reputation, behavioral, ML).",
    )
    description: str = Field(
        ..., description="Human-readable explanation of this contribution."
    )
    weight: float = Field(
        ...,
        description=(
            "Relative contribution (0-1) of this reason to the final score. "
            "The sum of weights across reasons is approximately 1.0."
        ),
    )


class AnalyzeResponse(BaseModel):
    """
    Scam risk analysis output.
    """

    scam_risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Scam risk score from 0 (safe) to 100 (highly likely scam).",
    )
    reasons: List[Reason] = Field(
        ..., description="Explainable reasons contributing to the risk score."
    )
    url_indicators: List[str] = Field(
        default_factory=list,
        description="List of URLs or URL patterns that looked suspicious.",
    )
