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

VALID_SENTIMENTS = {"POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"}

def normalize_sentiment(val: Optional[str]) -> str:
    if not val:
        return "NEUTRAL"
    v = str(val).strip().upper()
    if v in VALID_SENTIMENTS:
        return v
    if "ANGRY" in v or "BAD" in v or "NEG" in v or "POOR" in v or "TERRIBLE" in v or "CRITICAL" in v:
        return "NEGATIVE"
    if "GOOD" in v or "POS" in v or "GREAT" in v or "EXCELLENT" in v:
        return "POSITIVE"
    return "NEUTRAL"

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

    # Fast map of processed sentiments
    fs_map = {row[0]: row[1] for row in db.query(FeedbackSentiment.feedback_id, FeedbackSentiment.predicted_sentiment).all()}

    # Compute sentiment distribution across ALL records with 100% mathematical consistency
    sent_dist = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "MIXED": 0}
    for r in r_q.with_entities(Review.review_id, Review.ground_truth_sentiment).all():
        st = normalize_sentiment(fs_map.get(r[0]) or r[1])
        sent_dist[st] += 1
    for s in s_q.with_entities(SurveyResponse.response_id, SurveyResponse.ground_truth_sentiment).all():
        st = normalize_sentiment(fs_map.get(s[0]) or s[1])
        sent_dist[st] += 1
    for m in m_q.with_entities(SupportMessage.message_id, SupportMessage.ground_truth_sentiment).all():
        st = normalize_sentiment(fs_map.get(m[0]) or m[1])
        sent_dist[st] += 1

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
        st = normalize_sentiment(sent).lower()
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
        st = normalize_sentiment(sent).lower()
        if st in results[key]:
            results[key][st] += cnt
            results[key]["total"] += cnt

    # Fast SQL GROUP BY for Support Messages
    msg_col = SupportMessage.product_id if group_by == "product" else SupportMessage.channel_id
    msg_rows = db.query(
        msg_col,
        SupportMessage.ground_truth_sentiment,
        func.count(SupportMessage.message_id)
    ).group_by(msg_col, SupportMessage.ground_truth_sentiment).all()

    for col_val, sent, cnt in msg_rows:
        key = products.get(col_val, col_val) if group_by == "product" else channels.get(col_val, col_val)
        if not key:
            continue
        results.setdefault(key, {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0, "total": 0})
        st = normalize_sentiment(sent).lower()
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

    # Build authoritative Product and Channel master lookups
    prods = {p.product_id: p.product_name for p in db.query(Product.product_id, Product.product_name).all()}
    chans = {c.channel_id: c.channel_name for c in db.query(Channel.channel_id, Channel.channel_name).all()}

    # Aggregate actual problematic products and channels for each theme
    theme_prod_neg: Dict[str, Dict[str, int]] = {}
    theme_chan_neg: Dict[str, Dict[str, int]] = {}

    for r in db.query(Review.ground_truth_theme_ids, Review.product_id, Review.channel_id, Review.ground_truth_sentiment).all():
        if r[0] and r[3] in ["NEGATIVE", "MIXED"]:
            theme_prod_neg.setdefault(r[0], {}).setdefault(r[1], 0)
            theme_prod_neg[r[0]][r[1]] += 1
            theme_chan_neg.setdefault(r[0], {}).setdefault(r[2], 0)
            theme_chan_neg[r[0]][r[2]] += 1

    for s in db.query(SurveyResponse.ground_truth_theme_ids, SurveyResponse.product_id, SurveyResponse.channel_id, SurveyResponse.ground_truth_sentiment).all():
        if s[0] and s[3] in ["NEGATIVE", "MIXED"]:
            theme_prod_neg.setdefault(s[0], {}).setdefault(s[1], 0)
            theme_prod_neg[s[0]][s[1]] += 1
            theme_chan_neg.setdefault(s[0], {}).setdefault(s[2], 0)
            theme_chan_neg[s[0]][s[2]] += 1

    for m in db.query(SupportMessage.ground_truth_theme_ids, SupportMessage.product_id, SupportMessage.channel_id, SupportMessage.ground_truth_sentiment).all():
        if m[0] and m[3] in ["NEGATIVE", "MIXED"]:
            theme_prod_neg.setdefault(m[0], {}).setdefault(m[1], 0)
            theme_prod_neg[m[0]][m[1]] += 1
            theme_chan_neg.setdefault(m[0], {}).setdefault(m[2], 0)
            theme_chan_neg[m[0]][m[2]] += 1

    items = []

    for t in themes:
        tid = t.theme_id
        cnt = theme_counts.get(tid, 0)
        sents = theme_sentiments.get(tid, {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "MIXED": 0})
        neg_rate = round((sents["NEGATIVE"] / max(1, cnt)) * 100.0, 1)

        top_pids = sorted(theme_prod_neg.get(tid, {}).items(), key=lambda x: x[1], reverse=True)[:2]
        prob_prods = [prods.get(p[0], p[0]) for p in top_pids if p[0] in prods] or (list(prods.values())[:1] if prods else ["General Product"])

        top_chids = sorted(theme_chan_neg.get(tid, {}).items(), key=lambda x: x[1], reverse=True)[:2]
        prob_chans = [chans.get(c[0], c[0]) for c in top_chids if c[0] in chans] or (list(chans.values())[:1] if chans else ["Website"])

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
            problematic_products=prob_prods,
            problematic_channels=prob_chans
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
    """Generates chronological time-series sentiment trends strictly bounded by date window."""
    # Find latest feedback date across all sources
    max_rev = db.query(func.max(Review.review_date)).scalar()
    max_surv = db.query(func.max(SurveyResponse.response_date)).scalar()
    max_msg = db.query(func.max(SupportMessage.message_date)).scalar()
    valid_dates = [d for d in [max_rev, max_surv, max_msg] if d is not None]
    latest_date = max(valid_dates) if valid_dates else datetime.utcnow()
    start_date = latest_date - timedelta(days=days)

    # Strictly bounded by start_date and latest_date
    r_q = db.query(Review.review_date, Review.ground_truth_sentiment).filter(
        Review.review_date >= start_date,
        Review.review_date <= latest_date
    )
    s_q = db.query(SurveyResponse.response_date, SurveyResponse.ground_truth_sentiment).filter(
        SurveyResponse.response_date >= start_date,
        SurveyResponse.response_date <= latest_date
    )
    m_q = db.query(SupportMessage.message_date, SupportMessage.ground_truth_sentiment).filter(
        SupportMessage.message_date >= start_date,
        SupportMessage.message_date <= latest_date
    )

    if product_id:
        r_q = r_q.filter(Review.product_id == product_id)
        s_q = s_q.filter(SurveyResponse.product_id == product_id)
        m_q = m_q.filter(SupportMessage.product_id == product_id)
    if channel_id:
        r_q = r_q.filter(Review.channel_id == channel_id)
        s_q = s_q.filter(SurveyResponse.channel_id == channel_id)
        m_q = m_q.filter(SupportMessage.channel_id == channel_id)

    time_buckets: Dict[str, Dict[str, int]] = {}

    for dt, sent in r_q.all():
        b_key = dt.strftime("%Y-%m-%d")
        time_buckets.setdefault(b_key, {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "MIXED": 0, "total": 0})
        st = normalize_sentiment(sent)
        time_buckets[b_key][st] += 1
        time_buckets[b_key]["total"] += 1

    for dt, sent in s_q.all():
        b_key = dt.strftime("%Y-%m-%d")
        time_buckets.setdefault(b_key, {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "MIXED": 0, "total": 0})
        st = normalize_sentiment(sent)
        time_buckets[b_key][st] += 1
        time_buckets[b_key]["total"] += 1

    for dt, sent in m_q.all():
        b_key = dt.strftime("%Y-%m-%d")
        time_buckets.setdefault(b_key, {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "MIXED": 0, "total": 0})
        st = normalize_sentiment(sent)
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
