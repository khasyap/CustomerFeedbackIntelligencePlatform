import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.models.entities import Review
from backend.app.ml.sentiment_classifier import SentimentClassifier
from backend.app.ml.theme_classifier import ThemeClassifier
from backend.app.ml.evaluation import ModelEvaluator

def main():
    print("==================================================")
    print("Model Evaluation & Empirical Benchmark Suite")
    print("==================================================")
    db = SessionLocal()
    try:
        samples = []
        for r in db.query(Review).limit(1000).all():
            if r.ground_truth_sentiment and r.review_text:
                samples.append({
                    "text": f"{r.title + ': ' if r.title else ''}{r.review_text}",
                    "expected_sentiment": r.ground_truth_sentiment,
                    "expected_theme": r.ground_truth_theme_ids
                })

        print(f"[INFO] Evaluating on {len(samples)} holdout records...")
        sent_clf = SentimentClassifier()
        theme_clf = ThemeClassifier()

        sent_eval = ModelEvaluator.evaluate_sentiment(sent_clf, samples)
        print("\n--- SENTIMENT CLASSIFICATION BENCHMARK ---")
        print(f"Accuracy:        {sent_eval['accuracy'] * 100:.2f}%")
        print(f"Macro Precision: {sent_eval['precision_macro'] * 100:.2f}%")
        print(f"Macro Recall:    {sent_eval['recall_macro'] * 100:.2f}%")
        print(f"Macro F1-Score:  {sent_eval['f1_macro'] * 100:.2f}%")
        print(f"Throughput:      {sent_eval['operational_metrics']['throughput_records_per_second']} records/sec")

        theme_eval = ModelEvaluator.evaluate_themes(theme_clf, samples)
        print("\n--- MULTI-LABEL THEME CLASSIFICATION BENCHMARK ---")
        print(f"Macro Precision: {theme_eval['precision_macro'] * 100:.2f}%")
        print(f"Macro Recall:    {theme_eval['recall_macro'] * 100:.2f}%")
        print(f"Macro F1-Score:  {theme_eval['f1_macro'] * 100:.2f}%")
        print(f"Hamming Loss:    {theme_eval['hamming_loss']:.4f}")
        print(f"Throughput:      {theme_eval['operational_metrics']['throughput_records_per_second']} records/sec")

        out_path = os.path.join(os.path.dirname(__file__), "../data/evaluation/evaluation_benchmark.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            json.dump({"sentiment": sent_eval, "theme": theme_eval}, f, indent=2)
        print(f"\n[SUCCESS] Full benchmark metrics saved to {out_path}")
    finally:
        db.close()

if __name__ == "__main__":
    main()

