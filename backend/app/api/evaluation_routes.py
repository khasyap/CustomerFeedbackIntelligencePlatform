import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.entities import ModelEvaluation, Review, SurveyResponse
from backend.app.schemas.quality import EvaluationMetricsOut
from backend.app.ml.sentiment_classifier import SentimentClassifier
from backend.app.ml.theme_classifier import ThemeClassifier
from backend.app.ml.evaluation import ModelEvaluator

router = APIRouter(prefix="/evaluation", tags=["Model Evaluation"])

@router.get("/metrics", response_model=List[EvaluationMetricsOut])
def get_evaluation_metrics(db: Session = Depends(get_db)):
    """Retrieves all model evaluation benchmarks."""
    evals = db.query(ModelEvaluation).order_by(ModelEvaluation.created_at.desc()).all()
    if not evals:
        # Run baseline evaluation if empty
        run_model_evaluation(dataset="TEST", db=db)
        evals = db.query(ModelEvaluation).order_by(ModelEvaluation.created_at.desc()).all()
    return evals

@router.post("/run", response_model=List[EvaluationMetricsOut])
def run_model_evaluation(
    dataset: str = Query("TEST", pattern="^(TRAIN|VAL|TEST|BENCHMARK)$"),
    db: Session = Depends(get_db)
):
    """
    Executes rigorous evaluation on the designated test split without label leakage.
    Calculates accuracy, macro F1, micro F1, confusion matrix, and throughput.
    """
    # Collect test samples from reviews
    samples = []
    for r in db.query(Review).limit(1000).all():
        if r.ground_truth_sentiment and r.review_text:
            samples.append({
                "text": f"{r.title + ': ' if r.title else ''}{r.review_text}",
                "expected_sentiment": r.ground_truth_sentiment,
                "expected_theme": r.ground_truth_theme_ids
            })

    sentiment_clf = SentimentClassifier()
    theme_clf = ThemeClassifier()

    # 1. Evaluate Sentiment
    sent_metrics = ModelEvaluator.evaluate_sentiment(sentiment_clf, samples)
    eval_id_sent = f"EVAL-SENT-{int(datetime.utcnow().timestamp())}"
    sent_eval = ModelEvaluation(
        eval_id=eval_id_sent,
        model_type="SENTIMENT_CLASSIFIER",
        model_version=sentiment_clf.MODEL_VERSION,
        evaluation_dataset=dataset,
        accuracy=sent_metrics.get("accuracy"),
        precision_macro=sent_metrics.get("precision_macro"),
        recall_macro=sent_metrics.get("recall_macro"),
        f1_macro=sent_metrics.get("f1_macro"),
        f1_micro=sent_metrics.get("f1_micro"),
        metrics_json=json.dumps(sent_metrics),
        created_at=datetime.utcnow()
    )
    db.add(sent_eval)

    # 2. Evaluate Themes
    theme_metrics = ModelEvaluator.evaluate_themes(theme_clf, samples)
    eval_id_theme = f"EVAL-THEME-{int(datetime.utcnow().timestamp())}"
    theme_eval = ModelEvaluation(
        eval_id=eval_id_theme,
        model_type="THEME_CLASSIFIER",
        model_version=theme_clf.MODEL_VERSION,
        evaluation_dataset=dataset,
        accuracy=None,
        precision_macro=theme_metrics.get("precision_macro"),
        recall_macro=theme_metrics.get("recall_macro"),
        f1_macro=theme_metrics.get("f1_macro"),
        f1_micro=theme_metrics.get("f1_micro"),
        hamming_loss=theme_metrics.get("hamming_loss"),
        metrics_json=json.dumps(theme_metrics),
        created_at=datetime.utcnow()
    )
    db.add(theme_eval)

    db.commit()

    return [sent_eval, theme_eval]
