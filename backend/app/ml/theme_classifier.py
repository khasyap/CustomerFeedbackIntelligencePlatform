import re
from typing import Dict, List, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from backend.app.ml.preprocessor import TextPreprocessor
from backend.app.services.data_generator import THEME_TAXONOMY

class ThemeClassifier:
    """Multi-label theme extraction engine using hybrid keyword matching and vector similarity."""

    MODEL_VERSION = "v1.1.0-hybrid-multilabel"

    def __init__(self):
        self.themes = {t["id"]: t for t in THEME_TAXONOMY}
        self.theme_keywords: Dict[str, List[str]] = {
            t["id"]: [k.strip().lower() for k in t["keywords"].split(",") if k.strip()]
            for t in THEME_TAXONOMY
        }
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        # Build theme reference documents from descriptions and keywords
        theme_docs = [
            f"{t['name']} {t.get('desc', t.get('description', ''))} {t['keywords']}"
            for t in THEME_TAXONOMY
        ]
        self.theme_ids = [t["id"] for t in THEME_TAXONOMY]
        self.theme_matrix = self.vectorizer.fit_transform(theme_docs)

    def extract_themes(self, text: str, min_confidence: float = 0.25) -> List[Dict[str, Any]]:
        """
        Extracts one or more themes with confidence scores.
        Detects unknown themes if no theme meets minimum threshold.
        """
        if not text or not text.strip():
            return []

        cleaned = TextPreprocessor.clean_for_ml(text).lower()
        tokens = set(cleaned.split())

        scores: Dict[str, float] = {}
        methods: Dict[str, str] = {}

        # 1. Keyword-based matching
        for tid, kws in self.theme_keywords.items():
            matches = [kw for kw in kws if kw in cleaned]
            if matches:
                # Confidence proportional to keyword matches
                conf = min(0.95, 0.45 + len(matches) * 0.20)
                scores[tid] = conf
                methods[tid] = "KEYWORD_MATCH"

        # 2. Vector Cosine Similarity against Theme Profiles
        try:
            text_vec = self.vectorizer.transform([cleaned])
            similarities = (text_vec * self.theme_matrix.T).toarray()[0]
            for idx, sim in enumerate(similarities):
                tid = self.theme_ids[idx]
                if sim > 0.15:
                    tfidf_conf = min(0.92, float(sim) * 1.5)
                    if tid in scores:
                        # Combine keyword & vector score
                        scores[tid] = round(max(scores[tid], (scores[tid] + tfidf_conf) / 2.0), 3)
                        methods[tid] = "HYBRID_FUSION"
                    else:
                        scores[tid] = round(tfidf_conf, 3)
                        methods[tid] = "NLP_TFIDF"
        except Exception:
            pass

        # Filter and rank
        results = []
        for tid, conf in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if conf >= min_confidence:
                results.append({
                    "theme_id": tid,
                    "theme_name": self.themes[tid]["name"],
                    "confidence": conf,
                    "classification_method": methods.get(tid, "NLP_TFIDF"),
                    "model_version": self.MODEL_VERSION,
                    "is_unknown": False
                })

        # Unknown theme detection fallback
        if not results:
            results.append({
                "theme_id": "THEME-000017", # Fallback to Technical Issues or Flag as unclassified
                "theme_name": "Technical Issues",
                "confidence": 0.20,
                "classification_method": "FALLBACK_HEURISTIC",
                "model_version": self.MODEL_VERSION,
                "is_unknown": True
            })

        return results
