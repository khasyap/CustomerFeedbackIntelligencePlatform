from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class OverviewMetrics(BaseModel):
    total_feedback: int
    total_reviews: int
    total_surveys: int
    total_support_messages: int
    sentiment_distribution: Dict[str, int]
    sentiment_percentages: Dict[str, float]
    total_themes_identified: int
    critical_issues_count: int
    open_actions_count: int
    data_quality_exceptions_count: int

class SentimentBreakdownItem(BaseModel):
    name: str # e.g. Product name, Channel name, or Date string
    positive: int
    negative: int
    neutral: int
    mixed: int
    total: int
    net_sentiment_score: float # (Positive - Negative) / Total * 100

class ThemeMetricItem(BaseModel):
    theme_id: str
    theme_name: str
    count: int
    percentage: float
    positive_count: int
    negative_count: int
    neutral_count: int
    mixed_count: int
    negative_rate: float
    severity: str
    is_emerging: bool
    problematic_products: List[str]
    problematic_channels: List[str]

class TrendTimePoint(BaseModel):
    date: str
    positive: int
    negative: int
    neutral: int
    mixed: int
    total: int
    negative_percentage: float

class AnomalyShiftAlertOut(BaseModel):
    alert_id: str
    dimension_type: str
    dimension_id: str
    dimension_name: Optional[str] = None
    period_start: datetime
    period_end: datetime
    baseline_negative_rate: float
    current_negative_rate: float
    percentage_change: float
    feedback_volume: int
    severity: str
    summary: str
    detected_at: datetime

    class Config:
        from_attributes = True

class ServicePriorityItem(BaseModel):
    rank: int
    theme_id: str
    theme_name: str
    product_id: str
    product_name: str
    negative_rate: float
    feedback_volume: int
    severity: str
    recent_growth_rate: float
    customer_impact_score: float
    priority_score: float
    priority_level: str
    suggested_action: str
    assigned_team: str
    existing_action_id: Optional[str] = None
    existing_action_status: Optional[str] = None

