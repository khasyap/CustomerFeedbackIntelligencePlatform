from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.entities import (
    SurveyResponse, Review, SupportMessage, FeedbackSentiment,
    SentimentShiftAlert, Product, Channel, Theme
)

class TrendDetector:
    """Time-series sentiment aggregation and automated shift detection engine."""

    @staticmethod
    def detect_sentiment_shifts(
        db: Session,
        current_days: int = 30,
        baseline_days: int = 30,
        min_volume: int = 5,
        threshold_increase: float = 0.20 # 20% relative increase in negative rate
    ) -> List[Dict[str, Any]]:
        """
        Detects significant shifts in negative sentiment across Products, Channels, and Themes.
        Creates SentimentShiftAlert records in DB when detected.
        """
        now = datetime.utcnow()
        # Find latest feedback date in DB to support backdated synthetic datasets
        latest_rev = db.query(func.max(Review.review_date)).scalar()
        if latest_rev:
            now = latest_rev

        curr_start = now - timedelta(days=current_days)
        base_start = curr_start - timedelta(days=baseline_days)

        # Collect reviews & survey responses in both periods
        # We query unified feedback items
        detected_alerts = []

        # 1. Product Shifts
        products = db.query(Product).all()
        for prod in products:
            curr_stats = TrendDetector._get_product_stats(db, prod.product_id, curr_start, now)
            base_stats = TrendDetector._get_product_stats(db, prod.product_id, base_start, curr_start)

            if curr_stats["volume"] >= min_volume and base_stats["volume"] >= min_volume:
                base_neg_rate = base_stats["negative_rate"]
                curr_neg_rate = curr_stats["negative_rate"]
                
                # Check for significant spike
                # e.g. baseline 0.25 -> current 0.40 (relative change = (0.40 - 0.25)/0.25 = +60%)
                if base_neg_rate > 0:
                    rel_change = (curr_neg_rate - base_neg_rate) / base_neg_rate
                else:
                    rel_change = 1.0 if curr_neg_rate > 0.15 else 0.0

                if rel_change >= threshold_increase and curr_neg_rate > 0.25:
                    alert_id = f"SFT-PROD-{prod.product_id}-{int(now.timestamp())}"
                    severity = "CRITICAL" if curr_neg_rate > 0.50 or rel_change > 0.50 else "HIGH"
                    summary = (
                        f"Spike in negative sentiment detected for {prod.product_name} ({prod.product_id}). "
                        f"Negative rate increased by {round(rel_change * 100, 1)}% "
                        f"(from {round(base_neg_rate * 100, 1)}% to {round(curr_neg_rate * 100, 1)}%) "
                        f"across {curr_stats['volume']} feedback items in the last 30 days."
                    )
                    
                    # Check if already exists in DB
                    existing = db.query(SentimentShiftAlert).filter(
                        SentimentShiftAlert.dimension_type == "PRODUCT",
                        SentimentShiftAlert.dimension_id == prod.product_id,
                        SentimentShiftAlert.period_start == curr_start
                    ).first()

                    if not existing:
                        alert = SentimentShiftAlert(
                            alert_id=alert_id,
                            dimension_type="PRODUCT",
                            dimension_id=prod.product_id,
                            period_start=curr_start,
                            period_end=now,
                            baseline_negative_rate=round(base_neg_rate, 4),
                            current_negative_rate=round(curr_neg_rate, 4),
                            percentage_change=round(rel_change * 100.0, 2),
                            feedback_volume=curr_stats["volume"],
                            severity=severity,
                            summary=summary,
                            detected_at=datetime.utcnow()
                        )
                        db.add(alert)
                        db.commit()
                        detected_alerts.append(alert)
                    else:
                        detected_alerts.append(existing)

        # 2. Overall Platform Trend
        overall_curr = TrendDetector._get_overall_stats(db, curr_start, now)
        overall_base = TrendDetector._get_overall_stats(db, base_start, curr_start)
        if overall_curr["volume"] >= min_volume and overall_base["volume"] >= min_volume:
            base_neg_rate = overall_base["negative_rate"]
            curr_neg_rate = overall_curr["negative_rate"]
            rel_change = (curr_neg_rate - base_neg_rate) / max(0.01, base_neg_rate)
            if rel_change >= threshold_increase:
                alert_id = f"SFT-OVERALL-{int(now.timestamp())}"
                existing = db.query(SentimentShiftAlert).filter(
                    SentimentShiftAlert.dimension_type == "OVERALL",
                    SentimentShiftAlert.period_start == curr_start
                ).first()
                if not existing:
                    alert = SentimentShiftAlert(
                        alert_id=alert_id,
                        dimension_type="OVERALL",
                        dimension_id="ALL",
                        period_start=curr_start,
                        period_end=now,
                        baseline_negative_rate=round(base_neg_rate, 4),
                        current_negative_rate=round(curr_neg_rate, 4),
                        percentage_change=round(rel_change * 100.0, 2),
                        feedback_volume=overall_curr["volume"],
                        severity="CRITICAL" if rel_change > 0.40 else "HIGH",
                        summary=f"Platform-wide negative sentiment surged by {round(rel_change * 100, 1)}% compared to prior month.",
                        detected_at=datetime.utcnow()
                    )
                    db.add(alert)
                    db.commit()
                    detected_alerts.append(alert)

        return detected_alerts

    @staticmethod
    def _get_product_stats(db: Session, product_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculates volume and negative sentiment rate for a product in a date window."""
        revs = db.query(Review.review_id, Review.rating).filter(
            Review.product_id == product_id,
            Review.review_date >= start_date,
            Review.review_date <= end_date
        ).all()
        
        survs = db.query(SurveyResponse.response_id, SurveyResponse.rating).filter(
            SurveyResponse.product_id == product_id,
            SurveyResponse.response_date >= start_date,
            SurveyResponse.response_date <= end_date
        ).all()

        total = len(revs) + len(survs)
        if total == 0:
            return {"volume": 0, "negative_rate": 0.0}

        # Check negative feedbacks (rating <= 2)
        neg_count = sum(1 for r in revs if r.rating <= 2) + sum(1 for s in survs if s.rating <= 2)
        return {
            "volume": total,
            "negative_rate": neg_count / total
        }

    @staticmethod
    def _get_overall_stats(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        revs = db.query(Review.rating).filter(
            Review.review_date >= start_date,
            Review.review_date <= end_date
        ).all()
        survs = db.query(SurveyResponse.rating).filter(
            SurveyResponse.response_date >= start_date,
            SurveyResponse.response_date <= end_date
        ).all()

        total = len(revs) + len(survs)
        if total == 0:
            return {"volume": 0, "negative_rate": 0.0}

        neg_count = sum(1 for r in revs if r.rating <= 2) + sum(1 for s in survs if s.rating <= 2)
        return {
            "volume": total,
            "negative_rate": neg_count / total
        }
