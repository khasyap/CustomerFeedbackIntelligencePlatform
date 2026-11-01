import json
import time
from typing import Dict, List, Any
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, hamming_loss
)
from backend.app.ml.sentiment_classifier import SentimentClassifier
from backend.app.ml.theme_classifier import ThemeClassifier

class ModelEvaluator:
    """Computes comprehensive scientific evaluation metrics for sentiment and theme models."""

    @staticmethod
    def evaluate_sentiment(
        classifier: SentimentClassifier,
        test_samples: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluates sentiment classifier on an evaluation dataset.
        test_samples: list of dicts with 'text', 'expected_sentiment'
        """
        start_time = time.time()
        y_true = []
        y_pred = []
        confidences = []
        review_count = 0

        for item in test_samples:
            true_label = item.get("expected_sentiment")
            if not true_label or true_label not in ["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"]:
                continue
            text = item.get("text", "")
            res = classifier.predict_one(text)
            
            y_true.append(true_label)
            y_pred.append(res["predicted_sentiment"])
            confidences.append(res["confidence_score"])
            if res["review_status"] == "FLAGGED_FOR_REVIEW":
                review_count += 1

        elapsed = time.time() - start_time
        n_samples = len(y_true)
        if n_samples == 0:
            return {"error": "No valid evaluation samples provided"}

        labels = ["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"]
        acc = float(accuracy_score(y_true, y_pred))
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
            y_true, y_pred, labels=labels, average="macro", zero_division=0
        )
        p_micro, r_micro, f1_micro, _ = precision_recall_fscore_support(
            y_true, y_pred, labels=labels, average="micro", zero_division=0
        )
        p_per, r_per, f1_per, sup_per = precision_recall_fscore_support(
            y_true, y_pred, labels=labels, average=None, zero_division=0
        )
        cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()

        per_class = {}
        for idx, lbl in enumerate(labels):
            per_class[lbl] = {
                "precision": round(float(p_per[idx]), 4),
                "recall": round(float(r_per[idx]), 4),
                "f1_score": round(float(f1_per[idx]), 4),
                "support": int(sup_per[idx])
            }

        return {
            "model_type": "SENTIMENT_CLASSIFIER",
            "model_version": classifier.MODEL_VERSION,
            "total_samples": n_samples,
            "accuracy": round(acc, 4),
            "precision_macro": round(float(p_macro), 4),
            "recall_macro": round(float(r_macro), 4),
            "f1_macro": round(float(f1_macro), 4),
            "f1_micro": round(float(f1_micro), 4),
            "confusion_matrix": {
                "labels": labels,
                "matrix": cm
            },
            "per_class_metrics": per_class,
            "operational_metrics": {
                "total_processing_seconds": round(elapsed, 4),
                "throughput_records_per_second": round(n_samples / max(0.001, elapsed), 1),
                "average_confidence": round(float(np.mean(confidences)), 4),
                "human_review_rate": round(review_count / n_samples, 4)
            }
        }

    @staticmethod
    def evaluate_themes(
        classifier: ThemeClassifier,
        test_samples: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluates multi-label theme extraction against expected theme ground truth.
        """
        start_time = time.time()
        theme_ids = sorted(list(classifier.themes.keys()))
        theme_to_idx = {tid: i for i, tid in enumerate(theme_ids)}

        y_true_binary = []
        y_pred_binary = []

        for item in test_samples:
            expected_tid = item.get("expected_theme")
            if not expected_tid or expected_tid not in theme_to_idx:
                continue

            text = item.get("text", "")
            extracted = classifier.extract_themes(text)
            pred_tids = {e["theme_id"] for e in extracted}

            t_vec = [0] * len(theme_ids)
            t_vec[theme_to_idx[expected_tid]] = 1

            p_vec = [0] * len(theme_ids)
            for pt in pred_tids:
                if pt in theme_to_idx:
                    p_vec[theme_to_idx[pt]] = 1

            y_true_binary.append(t_vec)
            y_pred_binary.append(p_vec)

        elapsed = time.time() - start_time
        n_samples = len(y_true_binary)
        if n_samples == 0:
            return {"error": "No valid theme evaluation samples"}

        h_loss = float(hamming_loss(y_true_binary, y_pred_binary))
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
            y_true_binary, y_pred_binary, average="macro", zero_division=0
        )
        p_micro, r_micro, f1_micro, _ = precision_recall_fscore_support(
            y_true_binary, y_pred_binary, average="micro", zero_division=0
        )

        return {
            "model_type": "THEME_CLASSIFIER",
            "model_version": classifier.MODEL_VERSION,
            "total_samples": n_samples,
            "precision_macro": round(float(p_macro), 4),
            "recall_macro": round(float(r_macro), 4),
            "f1_macro": round(float(f1_macro), 4),
            "f1_micro": round(float(f1_micro), 4),
            "hamming_loss": round(h_loss, 4),
            "operational_metrics": {
                "total_processing_seconds": round(elapsed, 4),
                "throughput_records_per_second": round(n_samples / max(0.001, elapsed), 1)
            }
        }

