import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from backend.app.config import settings
from backend.app.ml.sentiment_classifier import SentimentClassifier
from backend.app.ml.preprocessor import TextPreprocessor
from backend.app.database import SessionLocal
from backend.app.models.entities import Review, SurveyResponse, SupportMessage

def train_all_models():
    print("[INFO] Starting Full Model Training Suite...")
    csv_path = os.path.join(settings.DATA_DIR, "ground_truth", "ground_truth.csv")
    if not os.path.exists(csv_path):
        print(f"[ERROR] Ground truth not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    train_df = df[df["evaluation_category"] == "TRAIN"]
    print(f"[INFO] Train split rows: {len(train_df)}")

    # Load texts from DB
    db = SessionLocal()
    try:
        rev_texts = {r.review_id: f"{r.title + ': ' if r.title else ''}{r.review_text}" for r in db.query(Review.review_id, Review.title, Review.review_text).all()}
        surv_texts = {s.response_id: s.response_text for s in db.query(SurveyResponse.response_id, SurveyResponse.response_text).all()}
        msg_texts = {m.message_id: m.message_text for m in db.query(SupportMessage.message_id, SupportMessage.message_text).all()}
        all_texts = {**rev_texts, **surv_texts, **msg_texts}
    finally:
        db.close()

    # 1. Train Sentiment Model
    print("[INFO] Training Sentiment Classifier...")
    sent_train = train_df[train_df["expected_sentiment"].isin(["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"])]
    sent_texts = [all_texts[r] for r in sent_train["record_id"] if r in all_texts]
    sent_labels = [row["expected_sentiment"] for _, row in sent_train.iterrows() if row["record_id"] in all_texts]

    sent_clf = SentimentClassifier()
    sent_clf.train(sent_texts, sent_labels)
    sent_model_path = os.path.join(os.path.dirname(__file__), "../backend/app/ml/sentiment_model.joblib")
    sent_clf.save(sent_model_path)
    print(f"[SUCCESS] Sentiment model saved to {sent_model_path} ({len(sent_texts)} samples)")

    # 2. Train Theme Model
    print("[INFO] Training Multi-Label Theme Classifier...")
    theme_train = train_df[train_df["expected_theme"].notna()]
    theme_texts = [TextPreprocessor.clean_for_ml(all_texts[r]) for r in theme_train["record_id"] if r in all_texts]
    theme_labels = [row["expected_theme"] for _, row in theme_train.iterrows() if row["record_id"] in all_texts]

    theme_pipe = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=15000, sublinear_tf=True)),
        ('clf', LogisticRegression(C=1.0, max_iter=500, class_weight='balanced', random_state=settings.RANDOM_SEED))
    ])
    theme_pipe.fit(theme_texts, theme_labels)
    theme_model_path = os.path.join(os.path.dirname(__file__), "../backend/app/ml/theme_model.joblib")
    joblib.dump({"pipeline": theme_pipe, "is_trained": True}, theme_model_path)
    print(f"[SUCCESS] Theme model saved to {theme_model_path} ({len(theme_texts)} samples)")

if __name__ == "__main__":
    train_all_models()
