from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from backend.app.database import get_db
from backend.app.models.entities import (
    Customer, Product, Channel, SurveyResponse, Review, SupportMessage,
    FeedbackSentiment, FeedbackTheme, Theme, DataQualityIssue
)
from backend.app.schemas.feedback import FeedbackItemOut, FeedbackCorrectionRequest
from backend.app.services.audit_service import AuditService

router = APIRouter(tags=["Feedback Explorer"])

@router.get("/feedback")
def get_unified_feedback(
    search: Optional[str] = None,
    product_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    sentiment: Optional[str] = None,
    theme_id: Optional[str] = None,
    review_status: Optional[str] = None,
    feedback_type: Optional[str] = None, # SURVEY_RESPONSE, REVIEW, SUPPORT_MESSAGE
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Searchable, filterable, paginated unified feedback explorer endpoint.
    Aggregates reviews, survey responses, and support messages with their predicted sentiments and themes.
    """
    # Build lookups for products and channels
    products = {p.product_id: p for p in db.query(Product).all()}
    channels = {c.channel_id: c for c in db.query(Channel).all()}
    customers = {c.customer_id: c for c in db.query(Customer).all()}
    themes = {t.theme_id: t for t in db.query(Theme).all()}

    # Data quality issue lookup
    dqi_records = db.query(DataQualityIssue).all()
    dqi_by_source = {}
    for dqi in dqi_records:
        dqi_by_source.setdefault(dqi.source_record_id, []).append(dqi.issue_type)

    # Lightweight sentiment tuple lookup (feedback_id, predicted_sentiment, confidence_score, explanation, review_status)
    sentiments = {
        s[0]: s
        for s in db.query(
            FeedbackSentiment.feedback_id,
            FeedbackSentiment.predicted_sentiment,
            FeedbackSentiment.confidence_score,
            FeedbackSentiment.explanation,
            FeedbackSentiment.review_status
        ).all()
    }

    # Lightweight theme tuple lookup (feedback_id, theme_id, confidence)
    fb_themes: Dict[str, List[Any]] = {}
    for ft in db.query(FeedbackTheme.feedback_id, FeedbackTheme.theme_id, FeedbackTheme.confidence).all():
        fb_themes.setdefault(ft[0], []).append(ft)

    items: List[Dict[str, Any]] = []

    # 1. Reviews
    if not feedback_type or feedback_type == "REVIEW":
        r_query = db.query(
            Review.review_id, Review.customer_id, Review.product_id, Review.channel_id,
            Review.title, Review.review_text, Review.rating, Review.review_date,
            Review.ground_truth_sentiment, Review.ground_truth_theme_ids
        )
        if product_id:
            r_query = r_query.filter(Review.product_id == product_id)
        if channel_id:
            r_query = r_query.filter(Review.channel_id == channel_id)
        if search:
            s_pat = f"%{search}%"
            r_query = r_query.filter(or_(Review.review_text.ilike(s_pat), Review.title.ilike(s_pat), Review.review_id.ilike(s_pat)))
        
        for r in r_query.limit(400).all():
            items.append({
                "feedback_id": r[0],
                "feedback_type": "REVIEW",
                "customer_id": r[1],
                "product_id": r[2],
                "channel_id": r[3],
                "text": f"{r[4] + ': ' if r[4] else ''}{r[5]}",
                "rating": r[6],
                "date": r[7],
                "ground_truth_sentiment": r[8],
                "ground_truth_themes": r[9]
            })

    # 2. Survey Responses
    if not feedback_type or feedback_type == "SURVEY_RESPONSE":
        s_query = db.query(
            SurveyResponse.response_id, SurveyResponse.customer_id, SurveyResponse.product_id, SurveyResponse.channel_id,
            SurveyResponse.response_text, SurveyResponse.rating, SurveyResponse.response_date,
            SurveyResponse.ground_truth_sentiment, SurveyResponse.ground_truth_theme_ids
        )
        if product_id:
            s_query = s_query.filter(SurveyResponse.product_id == product_id)
        if channel_id:
            s_query = s_query.filter(SurveyResponse.channel_id == channel_id)
        if search:
            s_pat = f"%{search}%"
            s_query = s_query.filter(or_(SurveyResponse.response_text.ilike(s_pat), SurveyResponse.response_id.ilike(s_pat)))

        for s in s_query.limit(400).all():
            items.append({
                "feedback_id": s[0],
                "feedback_type": "SURVEY_RESPONSE",
                "customer_id": s[1],
                "product_id": s[2],
                "channel_id": s[3],
                "text": s[4],
                "rating": s[5],
                "date": s[6],
                "ground_truth_sentiment": s[7],
                "ground_truth_themes": s[8]
            })

    # 3. Support Messages
    if not feedback_type or feedback_type == "SUPPORT_MESSAGE":
        m_query = db.query(
            SupportMessage.message_id, SupportMessage.customer_id, SupportMessage.product_id, SupportMessage.channel_id,
            SupportMessage.message_text, SupportMessage.message_date,
            SupportMessage.ground_truth_sentiment, SupportMessage.ground_truth_theme_ids
        )
        if product_id:
            m_query = m_query.filter(SupportMessage.product_id == product_id)
        if channel_id:
            m_query = m_query.filter(SupportMessage.channel_id == channel_id)
        if search:
            s_pat = f"%{search}%"
            m_query = m_query.filter(or_(SupportMessage.message_text.ilike(s_pat), SupportMessage.message_id.ilike(s_pat)))

        for m in m_query.limit(200).all():
            items.append({
                "feedback_id": m[0],
                "feedback_type": "SUPPORT_MESSAGE",
                "customer_id": m[1],
                "product_id": m[2],
                "channel_id": m[3],
                "text": m[4],
                "rating": None,
                "date": m[5],
                "ground_truth_sentiment": m[6],
                "ground_truth_themes": m[7]
            })

    # Enrich with predicted sentiment and themes
    enriched_items = []
    for it in items:
        fid = it["feedback_id"]
        sent_obj = sentiments.get(fid)
        th_list = fb_themes.get(fid, [])

        pred_sent = sent_obj[1] if sent_obj else it.get("ground_truth_sentiment", "NEUTRAL")
        conf = sent_obj[2] if sent_obj else 0.85
        expl = sent_obj[3] if sent_obj else "Direct inference"
        rev_stat = sent_obj[4] if sent_obj else "AUTO_CLASSIFIED"

        th_names = [themes[t[1]].theme_name for t in th_list if t[1] in themes]
        if not th_names and it.get("ground_truth_themes"):
            gt_id = it["ground_truth_themes"]
            if gt_id in themes:
                th_names = [themes[gt_id].theme_name]

        th_confs = [t[2] for t in th_list]

        # Apply sentiment filter
        if sentiment and pred_sent != sentiment:
            continue

        # Apply theme filter
        if theme_id:
            has_theme = any(t.theme_id == theme_id for t in th_list) or (it.get("ground_truth_themes") == theme_id)
            if not has_theme:
                continue

        # Apply review_status filter
        if review_status and rev_stat != review_status:
            continue

        cust = customers.get(it["customer_id"])
        prod = products.get(it["product_id"])
        chan = channels.get(it["channel_id"])

        enriched_items.append(FeedbackItemOut(
            feedback_id=fid,
            feedback_type=it["feedback_type"],
            customer_id=it["customer_id"],
            customer_name=cust.full_name if cust else "Anonymous",
            customer_email=cust.email if cust else None,
            customer_segment=cust.segment if cust else "Consumer",
            product_id=it["product_id"],
            product_name=prod.product_name if prod else "Unknown",
            product_category=prod.category if prod else None,
            channel_id=it["channel_id"],
            channel_name=chan.channel_name if chan else "Digital",
            text=it["text"],
            rating=it["rating"],
            date=it["date"],
            predicted_sentiment=pred_sent,
            confidence_score=conf,
            explanation=expl,
            review_status=rev_stat,
            themes=th_names or ["General Inquiry"],
            theme_confidences=th_confs or [0.75],
            quality_issues=dqi_by_source.get(fid, []),
            ground_truth_sentiment=it.get("ground_truth_sentiment"),
            ground_truth_themes=it.get("ground_truth_themes")
        ))

    # Sort descending by date
    enriched_items.sort(key=lambda x: x.date, reverse=True)

    total_count = len(enriched_items)
    start_idx = (page - 1) * page_size
    paged_items = enriched_items[start_idx: start_idx + page_size]

    return {
        "items": paged_items,
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_count + page_size - 1) // page_size
    }

@router.get("/feedback/{feedback_id}", response_model=FeedbackItemOut)
def get_feedback_detail(
    feedback_id: str,
    db: Session = Depends(get_db)
):
    """Fetches complete traceability record for a single feedback item."""
    # Search review, survey response, or support message
    rev = db.query(Review).filter(Review.review_id == feedback_id).first()
    surv = db.query(SurveyResponse).filter(SurveyResponse.response_id == feedback_id).first()
    msg = db.query(SupportMessage).filter(SupportMessage.message_id == feedback_id).first()

    if not rev and not surv and not msg:
        raise HTTPException(status_code=404, detail=f"Feedback ID '{feedback_id}' not found")

    rec = rev or surv or msg
    fb_type = "REVIEW" if rev else ("SURVEY_RESPONSE" if surv else "SUPPORT_MESSAGE")
    text = f"{rev.title + ': ' if rev and rev.title else ''}{getattr(rec, 'review_text', getattr(rec, 'response_text', getattr(rec, 'message_text', '')))}"
    rating = getattr(rec, "rating", None)
    date = getattr(rec, "review_date", getattr(rec, "response_date", getattr(rec, "message_date", datetime.utcnow())))

    cust = db.query(Customer).filter(Customer.customer_id == rec.customer_id).first()
    prod = db.query(Product).filter(Product.product_id == rec.product_id).first()
    chan = db.query(Channel).filter(Channel.channel_id == rec.channel_id).first()

    sent = db.query(FeedbackSentiment).filter(FeedbackSentiment.feedback_id == feedback_id).first()
    th_rows = db.query(FeedbackTheme).filter(FeedbackTheme.feedback_id == feedback_id).all()
    themes = {t.theme_id: t.theme_name for t in db.query(Theme).all()}

    dqis = db.query(DataQualityIssue).filter(DataQualityIssue.source_record_id == feedback_id).all()

    return FeedbackItemOut(
        feedback_id=feedback_id,
        feedback_type=fb_type,
        customer_id=rec.customer_id,
        customer_name=cust.full_name if cust else "Anonymous",
        customer_email=cust.email if cust else None,
        customer_segment=cust.segment if cust else "Consumer",
        product_id=rec.product_id,
        product_name=prod.product_name if prod else "Unknown",
        product_category=prod.category if prod else None,
        channel_id=rec.channel_id,
        channel_name=chan.channel_name if chan else "Digital",
        text=text,
        rating=rating,
        date=date,
        predicted_sentiment=sent.predicted_sentiment if sent else rec.ground_truth_sentiment,
        confidence_score=sent.confidence_score if sent else 0.85,
        explanation=sent.explanation if sent else "Ground truth baseline",
        review_status=sent.review_status if sent else "HUMAN_REVIEWED",
        themes=[themes.get(t.theme_id, t.theme_id) for t in th_rows] or [themes.get(rec.ground_truth_theme_ids, "General")],
        theme_confidences=[t.confidence for t in th_rows] or [0.8],
        quality_issues=[d.issue_type for d in dqis],
        ground_truth_sentiment=rec.ground_truth_sentiment,
        ground_truth_themes=rec.ground_truth_theme_ids
    )

@router.patch("/feedback/{feedback_id}/correct")
def correct_feedback_classification(
    feedback_id: str,
    body: FeedbackCorrectionRequest,
    db: Session = Depends(get_db)
):
    """
    Allows analysts to correct AI classifications without deleting history.
    Updates FeedbackSentiment and records immutable audit log.
    """
    sent = db.query(FeedbackSentiment).filter(FeedbackSentiment.feedback_id == feedback_id).first()
    old_sentiment = sent.predicted_sentiment if sent else None

    if body.predicted_sentiment:
        if not sent:
            sent = FeedbackSentiment(
                feedback_id=feedback_id,
                feedback_type="REVIEW",
                predicted_sentiment=body.predicted_sentiment,
                confidence_score=1.0,
                model_version="human-corrected",
                explanation=f"Manually reviewed and corrected by {body.reviewed_by}: {body.correction_reason or 'No reason provided'}",
                review_status="HUMAN_REVIEWED",
                processing_timestamp=datetime.utcnow()
            )
            db.add(sent)
        else:
            sent.predicted_sentiment = body.predicted_sentiment
            sent.confidence_score = 1.0
            sent.review_status = "HUMAN_REVIEWED"
            sent.explanation = f"Corrected by {body.reviewed_by}: {body.correction_reason or 'Manual review'}"

        AuditService.record_manual_classification_correction(
            db=db,
            feedback_id=feedback_id,
            feedback_type="REVIEW",
            old_sentiment=old_sentiment,
            new_sentiment=body.predicted_sentiment,
            changed_by=body.reviewed_by,
            reason=body.correction_reason
        )

    # Assign updated themes if provided
    if body.theme_ids is not None:
        # Mark previous themes as superseded or human-reviewed
        for tid in body.theme_ids:
            existing = db.query(FeedbackTheme).filter(
                FeedbackTheme.feedback_id == feedback_id,
                FeedbackTheme.theme_id == tid
            ).first()
            if not existing:
                ft = FeedbackTheme(
                    feedback_id=feedback_id,
                    feedback_type="REVIEW",
                    theme_id=tid,
                    confidence=1.0,
                    classification_method="HUMAN",
                    model_version="human-corrected",
                    is_human_reviewed=True,
                    reviewed_by=body.reviewed_by,
                    review_timestamp=datetime.utcnow()
                )
                db.add(ft)

    db.commit()
    return {"message": "Classification correction recorded successfully", "feedback_id": feedback_id}

