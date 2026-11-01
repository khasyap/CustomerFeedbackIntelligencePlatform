import os
import joblib
import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from backend.app.config import settings
from backend.app.ml.preprocessor import TextPreprocessor

# High-impact linguistic sentiment anchors
POSITIVE_WORDS = {
    "love", "excellent", "great", "fantastic", "amazing", "smooth", "helpful", "polite",
    "lightning", "fast", "pristine", "superior", "flawlessly", "affordable", "transparent",
    "intuitive", "elegant", "frictionless", "generous", "brilliant", "pleased", "satisfied",
    "accha", "shandar", "dhanyawad", "sehr gut", "excelente"
}
NEGATIVE_WORDS = {
    "poor", "cheap", "broke", "defective", "scratches", "substandard", "overpriced", "rip-off",
    "hidden", "aggressive", "rude", "unhelpful", "delayed", "crushed", "damaged", "freezes",
    "lag", "crash", "crashed", "crashing", "terrible", "latency", "confusing", "cluttered",
    "nightmare", "failed", "stuck", "deducted", "rejected", "locked", "suspended", "broken",
    "outages", "unreliable", "downtime", "lacks", "bekar", "kharab", "frustrante"
}
MIXED_INDICATORS = {
    "but", "however", "although", "though", "yet", "except", "disappointing", "on the other hand",
    "lekin", "pero", "aber", "mais"
}

class SentimentClassifier:
    """Production NLP Sentiment Classifier with explanations and decision rules."""

    MODEL_VERSION = "v1.2.0-tfidf-logreg"

    def __init__(self):
        self.pipeline: Pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=10000, sublinear_tf=True)),
            ("clf", LogisticRegression(class_weight="balanced", max_iter=500, random_state=settings.RANDOM_SEED))
        ])
        self.classes_ = ["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"]
        self.is_trained = False

        # Attempt loading pre-trained artifact if available
        model_path = os.path.join(os.path.dirname(__file__), "sentiment_model.joblib")
        if os.path.exists(model_path):
            try:
                self.load(model_path)
            except Exception:
                pass

    def train(self, texts: List[str], labels: List[str]):
        """Trains model strictly on training split."""
        cleaned_texts = [TextPreprocessor.clean_for_ml(t) for t in texts]
        self.pipeline.fit(cleaned_texts, labels)
        self.is_trained = True

    def predict_one(self, text: str) -> Dict[str, Any]:
        """Classifies a single text record and produces full confidence and explanation."""
        if not text or not text.strip():
            return {
                "predicted_sentiment": "NEUTRAL",
                "confidence_score": 0.50,
                "model_version": self.MODEL_VERSION,
                "review_status": "FLAGGED_FOR_REVIEW",
                "explanation": "Empty or whitespace-only feedback text"
            }

        cleaned = TextPreprocessor.clean_for_ml(text)
        
        # If model is not yet trained, fall back to robust rule-based lexicon
        if not self.is_trained:
            return self._heuristic_classify(text, cleaned)

        # Trained pipeline prediction
        probs = self.pipeline.predict_proba([cleaned])[0]
        classes = self.pipeline.named_steps["clf"].classes_
        top_idx = int(np.argmax(probs))
        predicted_sentiment = classes[top_idx]
        confidence = float(probs[top_idx])

        # Sarcasm / mixed linguistic correction
        has_contrast = any(word in cleaned.split() for word in MIXED_INDICATORS)
        pos_hits = [w for w in cleaned.split() if w in POSITIVE_WORDS]
        neg_hits = [w for w in cleaned.split() if w in NEGATIVE_WORDS]

        if has_contrast and len(pos_hits) > 0 and len(neg_hits) > 0 and predicted_sentiment != "MIXED":
            predicted_sentiment = "MIXED"
            confidence = max(0.68, confidence)

        # Sarcasm pattern: positive words directly preceding negative crash/broken
        if ("fantastic" in cleaned or "great" in cleaned or "brilliant" in cleaned) and ("crash" in cleaned or "broke" in cleaned or "waiting" in cleaned):
            predicted_sentiment = "NEGATIVE"
            confidence = max(0.85, confidence)

        # Decision rule assignment
        if confidence >= settings.HIGH_CONFIDENCE_THRESHOLD:
            review_status = "AUTO_CLASSIFIED"
        elif confidence >= settings.LOW_CONFIDENCE_THRESHOLD:
            review_status = "FLAGGED_FOR_REVIEW"
        else:
            review_status = "FLAGGED_FOR_REVIEW"

        explanation = self._build_explanation(cleaned, predicted_sentiment, pos_hits, neg_hits)

        return {
            "predicted_sentiment": predicted_sentiment,
            "confidence_score": round(confidence, 4),
            "model_version": self.MODEL_VERSION,
            "review_status": review_status,
            "explanation": explanation
        }

    def _heuristic_classify(self, original_text: str, cleaned_text: str) -> Dict[str, Any]:
        """High-precision heuristic classifier used prior to batch model training."""
        tokens = cleaned_text.split()
        pos_hits = [w for w in tokens if w in POSITIVE_WORDS]
        neg_hits = [w for w in tokens if w in NEGATIVE_WORDS]
        has_contrast = any(w in tokens for w in MIXED_INDICATORS)

        if has_contrast and len(pos_hits) > 0 and len(neg_hits) > 0:
            pred = "MIXED"
            conf = 0.82
        elif ("fantastic" in tokens or "great" in tokens or "brilliant" in tokens) and ("crash" in tokens or "broke" in tokens or "waiting" in tokens):
            pred = "NEGATIVE"
            conf = 0.88
        elif len(neg_hits) > len(pos_hits):
            pred = "NEGATIVE"
            conf = min(0.95, 0.65 + 0.10 * len(neg_hits))
        elif len(pos_hits) > len(neg_hits):
            pred = "POSITIVE"
            conf = min(0.95, 0.65 + 0.10 * len(pos_hits))
        else:
            pred = "NEUTRAL"
            conf = 0.65

        review_status = "AUTO_CLASSIFIED" if conf >= settings.HIGH_CONFIDENCE_THRESHOLD else "FLAGGED_FOR_REVIEW"
        explanation = self._build_explanation(cleaned_text, pred, pos_hits, neg_hits)

        return {
            "predicted_sentiment": pred,
            "confidence_score": round(conf, 4),
            "model_version": self.MODEL_VERSION,
            "review_status": review_status,
            "explanation": explanation
        }

    def _build_explanation(self, cleaned: str, sentiment: str, pos_hits: List[str], neg_hits: List[str]) -> str:
        if sentiment == "POSITIVE":
            words = list(set(pos_hits))[:4]
            return f"Driven by strong positive indicators: {', '.join(words) if words else 'favorable contextual phrasing'}"
        elif sentiment == "NEGATIVE":
            words = list(set(neg_hits))[:4]
            return f"Driven by critical dissatisfaction indicators: {', '.join(words) if words else 'adverse contextual phrasing'}"
        elif sentiment == "MIXED":
            p_words = list(set(pos_hits))[:2]
            n_words = list(set(neg_hits))[:2]
            return f"Exhibits both praise ({', '.join(p_words)}) and complaints ({', '.join(n_words)}) with contrasting conjunctions"
        else:
            return "Factual, objective inquiry with balanced phrasing and no strong polarity keywords"

    def save(self, filepath: str):
        joblib.dump({"pipeline": self.pipeline, "is_trained": self.is_trained}, filepath)

    def load(self, filepath: str):
        data = joblib.load(filepath)
        self.pipeline = data["pipeline"]
        self.is_trained = data["is_trained"]
