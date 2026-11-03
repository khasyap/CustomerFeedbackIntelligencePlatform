import os
import re
import joblib
from typing import Dict, List, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from backend.app.ml.preprocessor import TextPreprocessor
from backend.app.services.data_generator import THEME_TAXONOMY

class ThemeClassifier:
    """Production Multi-Label Theme Extraction Engine with Supervised ML and Regex Fallback."""

    MODEL_VERSION = "v1.2.0-supervised-multilabel"

    def __init__(self):
        self.themes = {t["id"]: t for t in THEME_TAXONOMY}
        self.theme_ids = [t["id"] for t in THEME_TAXONOMY]
        
        # Precompile exact word-boundary regexes to prevent substring false-positives
        self.theme_regexes: Dict[str, List[re.Pattern]] = {
            t["id"]: [re.compile(r'\b' + re.escape(k.strip().lower()) + r'\b') for k in t["keywords"].split(",") if k.strip()]
            for t in THEME_TAXONOMY
        }
        
        # Unsupervised similarity matrix fallback
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        theme_docs = [
            f"{t['name']} {t.get('desc', t.get('description', ''))} {t['keywords']}"
            for t in THEME_TAXONOMY
        ]
        self.theme_matrix = self.vectorizer.fit_transform(theme_docs)

        # Supervised ML pipeline
        self.pipeline = None
        self.is_trained = False

        model_path = os.path.join(os.path.dirname(__file__), "theme_model.joblib")
        if os.path.exists(model_path):
            try:
                data = joblib.load(model_path)
                self.pipeline = data.get("pipeline")
                self.is_trained = data.get("is_trained", False)
            except Exception:
                self.is_trained = False

    def train(self, texts: List[str], labels: List[str]):
        """Trains supervised multi-class / multi-label model on train split."""
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        from backend.app.config import settings

        cleaned_texts = [TextPreprocessor.clean_for_ml(t) for t in texts]
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=15000, sublinear_tf=True)),
            ('clf', LogisticRegression(C=1.0, max_iter=500, class_weight='balanced', random_state=settings.RANDOM_SEED))
        ])
        self.pipeline.fit(cleaned_texts, labels)
        self.is_trained = True

    def extract_themes(self, text: str, min_confidence: float = 0.20) -> List[Dict[str, Any]]:
        """
        Extracts one or more themes with calibrated confidence scores.
        Uses supervised ML pipeline when trained, with regex word-boundary fallback.
        """
        if not text or not text.strip():
            return []

        cleaned = TextPreprocessor.clean_for_ml(text).lower()

        # 1. Supervised Pipeline Inference
        if self.is_trained and self.pipeline:
            try:
                probs = self.pipeline.predict_proba([cleaned])[0]
                classes = self.pipeline.classes_
                top_indices = probs.argsort()[::-1][:2]

                results = []
                for idx in top_indices:
                    p = float(probs[idx])
                    if p >= min_confidence:
                        tid = classes[idx]
                        results.append({
                            "theme_id": tid,
                            "theme_name": self.themes[tid]["name"],
                            "confidence": round(p, 4),
                            "classification_method": "SUPERVISED_TFIDF_LOGREG",
                            "model_version": self.MODEL_VERSION,
                            "is_unknown": False
                        })
                if results:
                    return results
            except Exception:
                pass

        # 2. Heuristic word-boundary regex + Cosine Similarity fallback
        scores: Dict[str, float] = {}
        methods: Dict[str, str] = {}

        for tid, pats in self.theme_regexes.items():
            matches = [p for p in pats if p.search(cleaned)]
            if matches:
                conf = min(0.95, 0.50 + len(matches) * 0.20)
                scores[tid] = conf
                methods[tid] = "KEYWORD_REGEX"

        try:
            text_vec = self.vectorizer.transform([cleaned])
            similarities = (text_vec * self.theme_matrix.T).toarray()[0]
            for idx, sim in enumerate(similarities):
                tid = self.theme_ids[idx]
                if sim > 0.25:
                    tfidf_conf = min(0.92, float(sim) * 1.6)
                    if tid in scores:
                        scores[tid] = round(max(scores[tid], (scores[tid] + tfidf_conf) / 2.0), 3)
                        methods[tid] = "HYBRID_FUSION"
                    elif sim > 0.35:
                        scores[tid] = round(tfidf_conf, 3)
                        methods[tid] = "NLP_TFIDF"
        except Exception:
            pass

        results = []
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
        for tid, conf in ranked:
            if conf >= 0.35:
                results.append({
                    "theme_id": tid,
                    "theme_name": self.themes[tid]["name"],
                    "confidence": conf,
                    "classification_method": methods.get(tid, "NLP_TFIDF"),
                    "model_version": self.MODEL_VERSION,
                    "is_unknown": False
                })

        return results
