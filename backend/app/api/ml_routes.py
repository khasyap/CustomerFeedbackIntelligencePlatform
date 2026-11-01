from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.database import get_db
from backend.app.models.entities import (
    Review, SurveyResponse, SupportMessage, FeedbackSentiment,
    FeedbackTheme, ProcessingRun
)
from backend.app.ml.sentiment_classifier import SentimentClassifier
from backend.app.ml.theme_classifier import ThemeClassifier

router = APIRouter(tags=["AI Processing"])

# Singleton instances for API inference
sentiment_model = SentimentClassifier()
theme_model = ThemeClassifier()

class SingleTextRequest(BaseModel):
    text: str

class ProcessingRunOut(BaseModel):
    run_id: str
    run_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    records_processed: int
    records_flagged: int
    status: str
    config_json: Optional[str] = None

    class Config:
        from_attributes = True

@router.post("/sentiment/predict")
def predict_sentiment_single(req: SingleTextRequest):
    """Ad-hoc single text sentiment inference with explanations and confidence review flag."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    return sentiment_model.predict_one(req.text)

@router.post("/themes/classify")
def classify_themes_single(req: SingleTextRequest):
    """Ad-hoc single text multi-label theme extraction."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    return theme_model.extract_themes(req.text)

@router.post("/processing/run")
def trigger_processing_run(
    batch_size: int = Query(2000, ge=10, le=10000),
    db: Session = Depends(get_db)
):
    """
    Executes batch NLP processing pipeline across unprocessed reviews, surveys, and support messages.
    Records predicted sentiments, extracted themes, and execution run telemetry.
    """
    run_id = f"RUN-{db.query(ProcessingRun).count() + 1:06d}"
    proc_run = ProcessingRun(
        run_id=run_id,
        run_type="BATCH_INFERENCE",
        start_time=datetime.utcnow(),
        status="RUNNING",
        records_processed=0,
        records_flagged=0,
        config_json=f'{{"batch_size": {batch_size}, "model": "{sentiment_model.MODEL_VERSION}"}}'
    )
    db.add(proc_run)
    db.commit()

    # Find feedbacks without sentiments
    processed_count = 0
    flagged_count = 0

    existing_sent_ids = {s.feedback_id for s in db.query(FeedbackSentiment.feedback_id).all()}

    # 1. Process Reviews
    revs = db.query(Review).all()
    for r in revs:
        if r.review_id in existing_sent_ids:
            continue
        text = f"{r.title + ': ' if r.title else ''}{r.review_text}"
        sent_res = sentiment_model.predict_one(text)
        themes_res = theme_model.extract_themes(text)

        fs = FeedbackSentiment(
            feedback_id=r.review_id,
            feedback_type="REVIEW",
            predicted_sentiment=sent_res["predicted_sentiment"],
            confidence_score=sent_res["confidence_score"],
            model_version=sent_res["model_version"],
            explanation=sent_res["explanation"],
            review_status=sent_res["review_status"],
            processing_timestamp=datetime.utcnow()
        )
        db.add(fs)
        if sent_res["review_status"] == "FLAGGED_FOR_REVIEW":
            flagged_count += 1

        for th in themes_res:
            ft = FeedbackTheme(
                feedback_id=r.review_id,
                feedback_type="REVIEW",
                theme_id=th["theme_id"],
                confidence=th["confidence"],
                classification_method=th["classification_method"],
                model_version=th["model_version"],
                is_human_reviewed=False
            )
            db.add(ft)

        processed_count += 1
        if processed_count >= batch_size:
            break

    # 2. Process Surveys if batch quota remaining
    if processed_count < batch_size:
        survs = db.query(SurveyResponse).all()
        for s in survs:
            if s.response_id in existing_sent_ids:
                continue
            sent_res = sentiment_model.predict_one(s.response_text)
            themes_res = theme_model.extract_themes(s.response_text)

            fs = FeedbackSentiment(
                feedback_id=s.response_id,
                feedback_type="SURVEY_RESPONSE",
                predicted_sentiment=sent_res["predicted_sentiment"],
                confidence_score=sent_res["confidence_score"],
                model_version=sent_res["model_version"],
                explanation=sent_res["explanation"],
                review_status=sent_res["review_status"],
                processing_timestamp=datetime.utcnow()
            )
            db.add(fs)
            if sent_res["review_status"] == "FLAGGED_FOR_REVIEW":
                flagged_count += 1

            for th in themes_res:
                ft = FeedbackTheme(
                    feedback_id=s.response_id,
                    feedback_type="SURVEY_RESPONSE",
                    theme_id=th["theme_id"],
                    confidence=th["confidence"],
                    classification_method=th["classification_method"],
                    model_version=th["model_version"],
                    is_human_reviewed=False
                )
                db.add(ft)

            processed_count += 1
            if processed_count >= batch_size:
                break

    # 3. Process Support Messages
    if processed_count < batch_size:
        msgs = db.query(SupportMessage).all()
        for m in msgs:
            if m.message_id in existing_sent_ids:
                continue
            sent_res = sentiment_model.predict_one(m.message_text)
            themes_res = theme_model.extract_themes(m.message_text)

            fs = FeedbackSentiment(
                feedback_id=m.message_id,
                feedback_type="SUPPORT_MESSAGE",
                predicted_sentiment=sent_res["predicted_sentiment"],
                confidence_score=sent_res["confidence_score"],
                model_version=sent_res["model_version"],
                explanation=sent_res["explanation"],
                review_status=sent_res["review_status"],
                processing_timestamp=datetime.utcnow()
            )
            db.add(fs)
            if sent_res["review_status"] == "FLAGGED_FOR_REVIEW":
                flagged_count += 1

            for th in themes_res:
                ft = FeedbackTheme(
                    feedback_id=m.message_id,
                    feedback_type="SUPPORT_MESSAGE",
                    theme_id=th["theme_id"],
                    confidence=th["confidence"],
                    classification_method=th["classification_method"],
                    model_version=th["model_version"],
                    is_human_reviewed=False
                )
                db.add(ft)

            processed_count += 1
            if processed_count >= batch_size:
                break

    proc_run.status = "COMPLETED"
    proc_run.end_time = datetime.utcnow()
    proc_run.records_processed = processed_count
    proc_run.records_flagged = flagged_count

    db.commit()

    return {
        "run_id": run_id,
        "status": "COMPLETED",
        "records_processed": processed_count,
        "records_flagged": flagged_count,
        "model_version": sentiment_model.MODEL_VERSION
    }

@router.get("/processing/history", response_model=List[ProcessingRunOut])
def get_processing_history(db: Session = Depends(get_db)):
    """Fetches execution logs and performance metrics for all processing runs."""
    return db.query(ProcessingRun).order_by(ProcessingRun.start_time.desc()).all()
