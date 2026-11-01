import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.models.entities import Review, SurveyResponse, SupportMessage, FeedbackSentiment, FeedbackTheme, ProcessingRun
from backend.app.ml.sentiment_classifier import SentimentClassifier
from backend.app.ml.theme_classifier import ThemeClassifier

def main():
    parser = argparse.ArgumentParser(description="Batch Feedback NLP Processing Engine")
    parser.add_argument("--batch-size", type=int, default=5000, help="Number of items to process")
    args = parser.parse_args()

    print("==================================================")
    print(f"Batch Feedback NLP Processing Engine (Limit: {args.batch_size})")
    print("==================================================")

    db = SessionLocal()
    try:
        sentiment_clf = SentimentClassifier()
        theme_clf = ThemeClassifier()

        existing_sent_ids = {s.feedback_id for s in db.query(FeedbackSentiment.feedback_id).all()}
        print(f"[INFO] Already processed feedbacks: {len(existing_sent_ids)}")

        processed = 0
        flagged = 0

        # Process Reviews
        revs = db.query(Review).all()
        for r in revs:
            if r.review_id in existing_sent_ids:
                continue
            text = f"{r.title + ': ' if r.title else ''}{r.review_text}"
            s_res = sentiment_clf.predict_one(text)
            t_res = theme_clf.extract_themes(text)

            fs = FeedbackSentiment(
                feedback_id=r.review_id,
                feedback_type="REVIEW",
                predicted_sentiment=s_res["predicted_sentiment"],
                confidence_score=s_res["confidence_score"],
                model_version=s_res["model_version"],
                explanation=s_res["explanation"],
                review_status=s_res["review_status"]
            )
            db.add(fs)
            if s_res["review_status"] == "FLAGGED_FOR_REVIEW":
                flagged += 1

            for th in t_res:
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

            processed += 1
            if processed >= args.batch_size:
                break

        # Process Surveys
        if processed < args.batch_size:
            survs = db.query(SurveyResponse).all()
            for s in survs:
                if s.response_id in existing_sent_ids:
                    continue
                s_res = sentiment_clf.predict_one(s.response_text)
                t_res = theme_clf.extract_themes(s.response_text)

                fs = FeedbackSentiment(
                    feedback_id=s.response_id,
                    feedback_type="SURVEY_RESPONSE",
                    predicted_sentiment=s_res["predicted_sentiment"],
                    confidence_score=s_res["confidence_score"],
                    model_version=s_res["model_version"],
                    explanation=s_res["explanation"],
                    review_status=s_res["review_status"]
                )
                db.add(fs)
                if s_res["review_status"] == "FLAGGED_FOR_REVIEW":
                    flagged += 1

                for th in t_res:
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

                processed += 1
                if processed >= args.batch_size:
                    break

        db.commit()
        print(f"[SUCCESS] Processed {processed} records ({flagged} flagged for review).")
    finally:
        db.close()

if __name__ == "__main__":
    main()
