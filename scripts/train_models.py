import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from backend.app.config import settings
from backend.app.ml.sentiment_classifier import SentimentClassifier
from backend.app.ml.preprocessor import TextPreprocessor

def train_sentiment_model():
    print("[INFO] Starting Sentiment Model Training...")
    csv_path = os.path.join(settings.DATA_DIR, "ground_truth", "ground_truth.csv")
    if not os.path.exists(csv_path):
        print(f"[ERROR] Ground truth file not found at {csv_path}. Run generate_data.py first.")
        return

    df = pd.read_csv(csv_path)
    # Strictly filter to TRAIN split and valid labels
    train_df = df[(df["evaluation_category"] == "TRAIN") & (df["expected_sentiment"].isin(["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"]))]
    print(f"[INFO] Training set size: {len(train_df)} samples")

    # Load text from database or transactions
    from backend.app.database import SessionLocal
    from backend.app.models.entities import Review, SurveyResponse, SupportMessage
    db = SessionLocal()
    try:
        rev_texts = {r.review_id: f"{r.title + ': ' if r.title else ''}{r.review_text}" for r in db.query(Review.review_id, Review.title, Review.review_text).all()}
        surv_texts = {s.response_id: s.response_text for s in db.query(SurveyResponse.response_id, SurveyResponse.response_text).all()}
        msg_texts = {m.message_id: m.message_text for m in db.query(SupportMessage.message_id, SupportMessage.message_text).all()}
        all_texts = {**rev_texts, **surv_texts, **msg_texts}
    finally:
        db.close()

    texts = []
    labels = []
    for _, row in train_df.iterrows():
        rid = row["record_id"]
        t = all_texts.get(rid)
        if t and t.strip():
            texts.append(t)
            labels.append(row["expected_sentiment"])

    print(f"[INFO] Assembled {len(texts)} text-label training pairs.")
    clf = SentimentClassifier()
    clf.train(texts, labels)
    
    model_path = os.path.join(os.path.dirname(__file__), "../backend/app/ml/sentiment_model.joblib")
    clf.save(model_path)
    print(f"[SUCCESS] Trained model saved successfully to {model_path}!")

if __name__ == "__main__":
    train_sentiment_model()
