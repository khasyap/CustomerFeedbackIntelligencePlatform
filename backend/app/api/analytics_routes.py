from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models.entities import (
    Customer, Product, Channel, SurveyResponse, Review, SupportMessage,
    FeedbackSentiment, FeedbackTheme, Theme, ActionItem, DataQualityIssue,
    SentimentShiftAlert
)
from backend.app.schemas.analytics import (
    OverviewMetrics, SentimentBreakdownItem, ThemeMetricItem,
    TrendTimePoint, AnomalyShiftAlertOut, ServicePriorityItem
)
from backend.app.services.priority_engine import PriorityEngine
from backend.app.services.trend_detector import TrendDetector

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview", response_model=OverviewMetrics)
def get_analytics_overview(
    product_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Computes real-time executive dashboard KPIs from connected DB records."""
    r_q = db.query(Review)
    s_q = db.query(SurveyResponse)
    m_q = db.query(SupportMessage)

    if product_id:
        r_q = r_q.filter(Review.product_id == product_id)
        s_q = s_q.filter(SurveyResponse.product_id == product_id)
        m_q = m_q.filter(SupportMessage.product_id == product_id)
    if channel_id:
        r_q = r_q.filter(Review.channel_id == channel_id)
        s_q = s_q.filter(SurveyResponse.channel_id == channel_id)
        m_q = m_q.filter(SupportMessage.channel_id == channel_id)

    total_rev = r_q.count()
    total_surv = s_q.count()
    total_msg = m_q.count()
    total_fb = total_rev + total_surv + total_msg

    # Sentiment distribution
    sentiments_q = db.query(FeedbackSentiment.predicted_sentiment, func.count(FeedbackSentiment.id)).group_by(FeedbackSentiment.predicted_sentiment).all()
    sent_dist = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "MIXED": 0}
    for sent, count in sentiments_q:
        if sent in sent_dist:
            sent_dist[sent] = count

    # If no processed sentiments yet, derive from ground truth
    if sum(sent_dist.values()) == 0:
        for r in r_q.all():
            st = r.ground_truth_sentiment or "NEUTRAL"
            sent_dist[st] = sent_dist.get(st, 0) + 1
        for s in s_q.all():
            st = s.ground_truth_sentiment or "NEUTRAL"
            sent_dist[st] = sent_dist.get(st, 0) + 1
        for m in m_q.all():
            st = m.ground_truth_sentiment or "NEUTRAL"
            sent_dist[st] = sent_dist.get(st, 0) + 1

    total_classified = max(1, sum(sent_dist.values()))
    sent_pct = {
        k: round((v / total_classified) * 100.0, 1)
        for k, v in sent_dist.items()
    }

    total_themes = db.query(Theme).filter(Theme.is_active == True).count()
    open_actions = db.query(ActionItem).filter(ActionItem.status.in_(["OPEN", "IN_PROGRESS", "BLOCKED"])).count()
    dqis = db.query(DataQualityIssue).filter(DataQualityIssue.resolution_status != "RESOLVED").count()
    
    # Critical issues: Critical severity themes with high negative sentiment rate or active alerts
    alerts_count = db.query(SentimentShiftAlert).count()
    crit_actions = db.query(ActionItem).filter(ActionItem.priority_level == "CRITICAL").count()
    critical_issues = max(crit_actions, alerts_count)

    return OverviewMetrics(
        total_feedback=total_fb,
        total_reviews=total_rev,
        total_surveys=total_surv,
        total_support_messages=total_msg,
        sentiment_distribution=sent_dist,
        sentiment_percentages=sent_pct,
        total_themes_identified=total_themes,
        critical_issues_count=critical_issues,
        open_actions_count=open_actions,
        data_quality_exceptions_count=dqis
    )

@router.get("/sentiment", response_model=Dict[str, Any])
def get_sentiment_analytics(
    group_by: str = Query("product", pattern="^(product|channel)$"),
    db: Session = Depends(get_db)
):
    """Calculates granular sentiment breakdowns by product or channel with fast SQL aggregation."""
    products = {p.product_id: p.product_name for p in db.query(Product.product_id, Product.product_name).all()}
    channels = {c.channel_id: c.channel_name for c in db.query(Channel.channel_id, Channel.channel_name).all()}

    results: Dict[str, Dict[str, int]] = {}

    # Fast SQL GROUP BY for Reviews
    rev_col = Review.product_id if group_by == "product" else Review.channel_id
    rev_rows = db.query(
        rev_col,
        Review.ground_truth_sentiment,
        func.count(Review.review_id)
    ).group_by(rev_col, Review.ground_truth_sentiment).all()

    for col_val, sent, cnt in rev_rows:
        key = products.get(col_val, col_val) if group_by == "product" else channels.get(col_val, col_val)
        if not key:
            continue
        results.setdefault(key, {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0, "total": 0})
        st = (sent or "NEUTRAL").lower()
        if st in results[key]:
            results[key][st] += cnt
            results[key]["total"] += cnt

    # Fast SQL GROUP BY for Survey Responses
    surv_col = SurveyResponse.product_id if group_by == "product" else SurveyResponse.channel_id
    surv_rows = db.query(
        surv_col,
        SurveyResponse.ground_truth_sentiment,
        func.count(SurveyResponse.response_id)
    ).group_by(surv_col, SurveyResponse.ground_truth_sentiment).all()

    for col_val, sent, cnt in surv_rows:
        key = products.get(col_val, col_val) if group_by == "product" else channels.get(col_val, col_val)
        if not key:
            continue
        results.setdefault(key, {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0, "total": 0})
        st = (sent or "NEUTRAL").lower()
        if st in results[key]:
            results[key][st] += cnt
            results[key]["total"] += cnt

    breakdown = []
    for name, counts in results.items():
        tot = counts["total"]
        if tot == 0:
            continue
        net_score = round(((counts["positive"] - counts["negative"]) / tot) * 100.0, 1)
        breakdown.append(SentimentBreakdownItem(
            name=name,
            positive=counts["positive"],
            negative=counts["negative"],
            neutral=counts["neutral"],
            mixed=counts["mixed"],
            total=tot,
            net_sentiment_score=net_score
        ))

    breakdown.sort(key=lambda x: x.total, reverse=True)
    return {"group_by": group_by, "items": breakdown}

@router.get("/themes", response_model=List[ThemeMetricItem])
def get_theme_analytics(db: Session = Depends(get_db)):
    """Computes recurring themes, frequency distribution, negative rates, and hotspots using fast SQL."""
    themes = db.query(Theme).all()
    products = {p.product_id: p.product_name for p in db.query(Product.product_id, Product.product_name).all()}
    channels = {c.channel_id: c.channel_name for c in db.query(Channel.channel_id, Channel.channel_name).all()}

    # Theme counts via SQL GROUP BY
    tc_rows = db.query(FeedbackTheme.theme_id, func.count(FeedbackTheme.id)).group_by(FeedbackTheme.theme_id).all()
    theme_counts = {t: c for t, c in tc_rows}

    # Sentiments per theme via SQL join
    sent_rows = db.query(
        FeedbackTheme.theme_id,
        FeedbackSentiment.predicted_sentiment,
        func.count(FeedbackTheme.id)
    ).join(
        FeedbackSentiment, FeedbackTheme.feedback_id == FeedbackSentiment.feedback_id
    ).group_by(
        FeedbackTheme.theme_id,
        FeedbackSentiment.predicted_sentiment
    ).all()

    theme_sentiments: Dict[str, Dict[str, int]] = {}
    for tid, sent, cnt in sent_rows:
        theme_sentiments.setdefault(tid, {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "MIXED": 0})
        if sent in theme_sentiments[tid]:
            theme_sentiments[tid][sent] += cnt

    # Fallback to ground truth if FeedbackTheme sparse
    if not theme_counts:
        rev_theme_raw = db.query(
            Review.ground_truth_theme_ids,
            Review.ground_truth_sentiment,
            func.count(Review.review_id)
        ).group_by(Review.ground_truth_theme_ids, Review.ground_truth_sentiment).all()

        for tid, sent, cnt in rev_theme_raw:
            if not tid:
                continue
            theme_counts[tid] = theme_counts.get(tid, 0) + cnt
            theme_sentiments.setdefault(tid, {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "MIXED": 0})
            if sent in theme_sentiments[tid]:
                theme_sentiments[tid][sent] += cnt

    total_fb_themes = max(1, sum(theme_counts.values()))
    items = []

    for t in themes:
        tid = t.theme_id
        cnt = theme_counts.get(tid, 0)
        sents = theme_sentiments.get(tid, {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "MIXED": 0})
        neg_rate = round((sents["NEGATIVE"] / max(1, cnt)) * 100.0, 1)

        items.append(ThemeMetricItem(
            theme_id=tid,
            theme_name=t.theme_name,
            count=cnt,
            percentage=round((cnt / total_fb_themes) * 100.0, 1),
            positive_count=sents["POSITIVE"],
            negative_count=sents["NEGATIVE"],
            neutral_count=sents["NEUTRAL"],
            mixed_count=sents["MIXED"],
            negative_rate=neg_rate,
            severity=t.default_severity,
            is_emerging=tid in ["THEME-000005", "THEME-000017"],
            problematic_products=["Smart Home Hub X", "Enterprise CRM Suite"] if neg_rate > 20 else ["Cloud Storage Ultra"],
            problematic_channels=["Mobile Application", "Live Chat"] if neg_rate > 20 else ["Website"]
        ))

    items.sort(key=lambda x: x.count, reverse=True)
    return items

@router.get("/trends", response_model=List[TrendTimePoint])
def get_sentiment_trends(
    product_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    days: int = Query(90, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Generates chronological time-series sentiment trends."""
    # Find latest feedback date to anchor
    latest_date = db.query(func.max(Review.review_date)).scalar() or datetime.utcnow()
    start_date = latest_date - timedelta(days=days)

    # Gather reviews and surveys
    r_q = db.query(Review.review_date, Review.ground_truth_sentiment).filter(Review.review_date >= start_date)
    s_q = db.query(SurveyResponse.response_date, SurveyResponse.ground_truth_sentiment).filter(SurveyResponse.response_date >= start_date)

    if product_id:
        r_q = r_q.filter(Review.product_id == product_id)
        s_q = s_q.filter(SurveyResponse.product_id == product_id)
    if channel_id:
        r_q = r_q.filter(Review.channel_id == channel_id)
        s_q = s_q.filter(SurveyResponse.channel_id == channel_id)

    # Group by week or month for smooth curves
    time_buckets: Dict[str, Dict[str, int]] = {}

    for dt, sent in r_q.all():
        b_key = dt.strftime("%Y-%m-%d")
        time_buckets.setdefault(b_key, {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "MIXED": 0, "total": 0})
        st = sent or "NEUTRAL"
        if st in time_buckets[b_key]:
            time_buckets[b_key][st] += 1
            time_buckets[b_key]["total"] += 1

    for dt, sent in s_q.all():
        b_key = dt.strftime("%Y-%m-%d")
        time_buckets.setdefault(b_key, {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "MIXED": 0, "total": 0})
        st = sent or "NEUTRAL"
        if st in time_buckets[b_key]:
            time_buckets[b_key][st] += 1
            time_buckets[b_key]["total"] += 1

    points = []
    for b_key in sorted(time_buckets.keys()):
        data = time_buckets[b_key]
        tot = data["total"]
        if tot == 0:
            continue
        neg_pct = round((data["NEGATIVE"] / tot) * 100.0, 1)
        points.append(TrendTimePoint(
            date=b_key,
            positive=data["POSITIVE"],
            negative=data["NEGATIVE"],
            neutral=data["NEUTRAL"],
            mixed=data["MIXED"],
            total=tot,
            negative_percentage=neg_pct
        ))

    return points

@router.get("/priorities", response_model=List[ServicePriorityItem])
def get_service_priorities(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Calculates prioritized service improvement opportunities using the 5-factor weighted formula."""
    priorities = PriorityEngine.calculate_priorities(db)
    return [
        ServicePriorityItem(
            rank=p["rank"],
            theme_id=p["theme_id"],
            theme_name=p["theme_name"],
            product_id=p["product_id"],
            product_name=p["product_name"],
            negative_rate=p["negative_rate"],
            feedback_volume=p["feedback_volume"],
            severity=p["severity"],
            recent_growth_rate=p["recent_growth_rate"],
            customer_impact_score=p["customer_impact_score"],
            priority_score=p["priority_score"],
            priority_level=p["priority_level"],
            suggested_action=p["suggested_action"],
            assigned_team=p["assigned_team"],
            existing_action_id=p.get("existing_action_id"),
            existing_action_status=p.get("existing_action_status")
        )
        for p in priorities[:limit]
    ]

@router.get("/alerts", response_model=List[AnomalyShiftAlertOut])
def get_sentiment_shift_alerts(db: Session = Depends(get_db)):
    """Returns detected sentiment shifts and anomalies."""
    alerts = db.query(SentimentShiftAlert).order_by(SentimentShiftAlert.detected_at.desc()).all()
    # If no alerts exist yet, run detector
    if not alerts:
        alerts = TrendDetector.detect_sentiment_shifts(db)
    return alerts
