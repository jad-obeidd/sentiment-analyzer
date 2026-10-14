"""Sentiment model wrapper.

Uses a DistilBERT model distilled for three-way sentiment (positive / neutral /
negative). The predicted label is the class with the highest probability,
except that low-confidence predictions are reported as NEUTRAL: short factual
sentences ("The package arrived today.") often get a weak positive lean that
isn't real sentiment.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass

MODEL_NAME = os.getenv("SENTIMENT_MODEL", "lxyuan/distilbert-base-multilingual-cased-sentiments-student")
NEUTRAL_THRESHOLD = float(os.getenv("NEUTRAL_THRESHOLD", "0.55"))
MAX_CHARS = 2000


@dataclass
class SentimentResult:
    label: str  # POSITIVE | NEUTRAL | NEGATIVE
    confidence: float  # probability of the top model class (0-1)
    positive: float
    neutral: float
    negative: float

    def to_dict(self) -> dict:
        return asdict(self)


def classify(positive: float, neutral: float, negative: float, threshold: float = NEUTRAL_THRESHOLD) -> SentimentResult:
    """Turn class probabilities into a label, falling back to NEUTRAL when unsure."""
    scores = {"POSITIVE": positive, "NEUTRAL": neutral, "NEGATIVE": negative}
    top_label = max(scores, key=scores.get)
    top = scores[top_label]
    label = top_label if top >= threshold else "NEUTRAL"
    return SentimentResult(
        label=label,
        confidence=round(top, 4),
        positive=round(positive, 4),
        neutral=round(neutral, 4),
        negative=round(negative, 4),
    )


class DistilBertAnalyzer:
    """Lazily loads the Hugging Face pipeline on first use (the download is ~540 MB)."""

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self._pipeline = None

    def _load(self):
        if self._pipeline is None:
            from transformers import pipeline  # imported lazily so tests don't need torch

            self._pipeline = pipeline("sentiment-analysis", model=self.model_name, top_k=None)
        return self._pipeline

    def analyze(self, text: str) -> SentimentResult:
        scores = self._load()(text[:MAX_CHARS], truncation=True)
        # With top_k=None the pipeline returns every label's score.
        if scores and isinstance(scores[0], list):
            scores = scores[0]
        by_label = {s["label"].upper(): float(s["score"]) for s in scores}
        return classify(by_label.get("POSITIVE", 0.0), by_label.get("NEUTRAL", 0.0), by_label.get("NEGATIVE", 0.0))
