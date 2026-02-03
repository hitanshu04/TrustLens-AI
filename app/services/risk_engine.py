from __future__ import annotations

"""
Risk engine: combines multiple signals into one final scam risk score.

High-level flow for a single request:
1. Each component (keywords, URLs, behavior, ML, ...) looks at the message
   and returns a risk score between 0 and 1 **for its own signal only**.
2. The `RiskEngine` multiplies each component score by a configurable
   weight (for example: keywords = 0.5, urls = 0.3, ...).
3. The weighted scores are added together to produce a final risk score
   in the range [0, 1], which is then converted to [0, 100] for the API.
4. Each component also returns one or more `Reason` objects explaining
   *why* it contributed risk. These are aggregated and re-normalized so
   their `weight` fields sum to ~1.0 (making them easy to interpret).

This design is:
- **Explainable**: every contribution is labeled (keyword/url/behavior/ml)
  and accompanied by a human-readable description.
- **Extensible**: new components (especially ML models) can be added by
  implementing `RiskComponent` and assigning a weight in `RiskEngine`.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol, Tuple

from app.models.schemas import Reason
from app.services.url_reputation import check_url_reputation


class RiskComponent(Protocol):
    """
    Pluggable risk component interface.

    Both rule-based detectors and ML models should implement this
    interface so they can be combined into the overall risk score.
    """

    def analyze(self, message: str, metadata: Dict[str, Any] | None) -> Tuple[float, List[Reason]]:
        """
        Analyze the message and optional metadata.

        Returns:
        - score:  floating value in [0.0, 1.0] where 0.0 means "no risk"
                  from this specific component and 1.0 means "very high
                  risk according to this component alone".
        - reasons: list of `Reason` objects explaining the score.
        """


class KeywordRuleComponent:
    """
    Simple keyword-based rules using heuristics commonly seen in scam messages.

    Think of this as a "bag of phrases" detector: if the message contains
    one of the phrases below, it adds to the risk score.
    """

    # Each keyword (lowercased) maps to an approximate risk weight.
    KEYWORD_WEIGHTS: Dict[str, float] = {
        "wire transfer": 0.25,
        "gift card": 0.3,
        "bitcoin": 0.2,
        "crypto": 0.2,
        "western union": 0.25,
        "moneygram": 0.25,
        "urgent": 0.15,
        "immediately": 0.1,
        "limited time": 0.15,
        "act now": 0.15,
        "verification code": 0.2,
        "otp": 0.2,
        "one-time password": 0.2,
        "bank account": 0.2,
        "routing number": 0.25,
        "ssn": 0.25,
        "social security": 0.25,
        "congratulations": 0.15,
        "you have won": 0.3,
        "prize": 0.2,
        "lottery": 0.25,
    }

    def analyze(self, message: str, metadata: Dict[str, Any] | None) -> Tuple[float, List[Reason]]:
        # Normalize to lower-case so we can do simple substring checks.
        text = (message or "").lower()
        if not text.strip():
            # Empty or whitespace-only message: no keyword risk.
            return 0.0, []

        matched_terms: List[str] = []
        aggregate_score = 0.0

        # Add up contributions for every matched keyword.
        for term, weight in self.KEYWORD_WEIGHTS.items():
            if term in text:
                matched_terms.append(term)
                aggregate_score += weight

        if not matched_terms:
            return 0.0, []

        # Cap at 1.0 so this component can never exceed full risk.
        aggregate_score = min(1.0, aggregate_score)

        description = (
            "Detected high-risk phrases associated with common scam patterns: "
            + ", ".join(sorted(set(matched_terms)))
        )

        reasons = [
            Reason(
                type="keyword",
                description=description,
                # For now we store the raw component score; the engine will
                # re-normalize all reason weights at the end.
                weight=aggregate_score,
            )
        ]

        return aggregate_score, reasons


class UrlReputationComponent:
    """
    URL reputation component built on top of simple rule-based checks.

    Currently it focuses on:
    - Detecting shortened links (e.g. bit.ly), which are often used to
      hide the real destination of a phishing/scam website.
    - Flagging the presence of URLs in general as mildly risky.
    """

    def analyze(self, message: str, metadata: Dict[str, Any] | None) -> Tuple[float, List[Reason]]:
        # Delegate the low-level work (URL extraction + basic heuristics)
        # to the `check_url_reputation` helper.
        score, suspicious_urls, reasons_text = check_url_reputation(message)
        if score <= 0.0:
            return 0.0, []

        reasons: List[Reason] = []
        for desc in reasons_text:
            reasons.append(
                Reason(
                    type="url_reputation",
                    description=desc,
                    # Split the component score equally across all URL reasons.
                    weight=score / max(1, len(reasons_text)),
                )
            )

        return score, reasons


class BehavioralSignalComponent:
    """
    Placeholder component for behavioral signals.

    Examples of future behavioral features:
    - high sending frequency
    - new sender contacting many recipients
    - unusual time-of-day or geo-location

    Right now this component does not increase the risk score, but it
    shows where you would implement these checks.
    """

    def analyze(self, message: str, metadata: Dict[str, Any] | None) -> Tuple[float, List[Reason]]:
        # Placeholder: no behavioral signals implemented yet.
        if not metadata:
            return 0.0, []

        description = (
            "Behavioral signals were provided but advanced behavioral risk modeling "
            "is not yet implemented. Future ML models can plug into this component."
        )

        reasons = [
            Reason(
                type="behavioral",
                description=description,
                weight=0.0,
            )
        ]
        # Score remains neutral for now.
        return 0.0, reasons


class MlModelComponent:
    """
    Extension point for ML-based risk scoring.

    This component is a stub showing how a production ML model can be
    integrated without changing the rest of the API or router logic.

    To plug in a real model later, you might:
    - Load the model in `__init__` (e.g. from disk or a remote service).
    - Use `message` and `metadata` as features.
    - Return `score` as the model's predicted scam probability
      (already in [0, 1]).
    """

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled
        # self.model = load_your_model_here()  # Example for later.

    def analyze(self, message: str, metadata: Dict[str, Any] | None) -> Tuple[float, List[Reason]]:
        if not self.enabled:
            # ML is disabled in this deployment, so it does not affect the score.
            return 0.0, []

        # Example (pseudo-implementation):
        # score = float(self.model.predict_proba(message, metadata))
        # description = f"ML model estimated scam probability at {score:.2f}."
        # For now, we leave it as neutral and just explain the hook.
        description = (
            "ML model scoring would be applied here. Currently disabled in this deployment."
        )
        reasons = [
            Reason(
                type="ml_model",
                description=description,
                weight=0.0,
            )
        ]
        return 0.0, reasons


@dataclass
class ComponentConfig:
    """
    Configuration for a single risk component.

    - name:   human-friendly label (for debugging/monitoring)
    - weight: how important this component is when combining scores.
              All weights are relative; they do **not** need to sum to 1,
              but it is usually convenient if they do.
    - component: instance implementing `RiskComponent`.
    """

    name: str
    weight: float
    component: RiskComponent


class RiskEngine:
    """
    Composable risk engine that aggregates multiple components.

    This class is responsible for:
    - Calling every component.
    - Applying a weight to each component's score.
    - Producing a single final score in [0, 100].
    - Merging and normalizing all `Reason` objects for explainability.
    """

    def __init__(self, components: List[ComponentConfig] | None = None) -> None:
        # Default set of components and their relative importance.
        #
        # You can safely change these weights later (for example after
        # you add a real ML model) without touching the API layer.
        if components is None:
            components = [
                ComponentConfig(
                    name="keywords",
                    weight=0.5,
                    component=KeywordRuleComponent(),
                ),
                ComponentConfig(
                    name="urls",
                    weight=0.3,
                    component=UrlReputationComponent(),
                ),
                ComponentConfig(
                    name="behavior",
                    weight=0.1,
                    component=BehavioralSignalComponent(),
                ),
                ComponentConfig(
                    name="ml_model",
                    weight=0.1,
                    component=MlModelComponent(enabled=False),
                ),
            ]
        self.components = components

    def analyze(self, message: str, metadata: Dict[str, Any] | None = None) -> Tuple[int, List[Reason]]:
        """
        Run all components and aggregate their scores into a 0-100 integer.

        Steps:
        1. Ask each component for its own risk score in [0, 1].
        2. Multiply that score by the component's weight.
        3. Add all weighted scores together.
        4. Convert the final score to [0, 100].
        """

        weighted_score_sum = 0.0
        total_weight = 0.0
        all_reasons: List[Reason] = []

        for config in self.components:
            score, reasons = config.component.analyze(message, metadata)

            # Safety: clamp each score to [0, 1].
            score = max(0.0, min(1.0, score))

            # Combine scores using the configured weight.
            weighted_score_sum += score * config.weight
            total_weight += config.weight

            all_reasons.extend(reasons)

        # If total_weight is 0 (e.g. misconfiguration), avoid division by zero
        # and treat the final score as 0.
        if total_weight <= 0.0:
            normalized_score = 0.0
        else:
            # Final normalized score in [0, 1].
            normalized_score = max(
                0.0, min(1.0, weighted_score_sum / total_weight))

        int_score = int(round(normalized_score * 100))

        # Re-normalize weights in reasons so they sum to ~1.0
        raw_weight_sum = sum(r.weight for r in all_reasons) or 1.0
        normalized_reasons: List[Reason] = []
        for r in all_reasons:
            normalized_reasons.append(
                Reason(
                    type=r.type,
                    description=r.description,
                    weight=r.weight / raw_weight_sum,
                )
            )

        return int_score, normalized_reasons


default_risk_engine = RiskEngine()
