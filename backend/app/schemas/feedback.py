from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class CustomerBase(BaseModel):
    customer_id: str
    full_name: str
    email: str
    segment: str
    country: str
    loyalty_tier: str
    created_at: datetime

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    product_id: str
    product_name: str
    category: str
    sku: str
    price: float
    release_date: datetime
    is_active: bool

    class Config:
        from_attributes = True

class ChannelBase(BaseModel):
    channel_id: str
    channel_name: str
    channel_type: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class ThemeBase(BaseModel):
    theme_id: str
    theme_name: str
    parent_theme_id: Optional[str] = None
    description: str
    keywords: str
    default_severity: str
    is_active: bool
    effective_start_date: datetime
    effective_end_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class SurveyBase(BaseModel):
    survey_id: str
    title: str
    description: Optional[str] = None
    target_audience: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class FeedbackItemOut(BaseModel):
    feedback_id: str
    feedback_type: str # SURVEY_RESPONSE, REVIEW, SUPPORT_MESSAGE
    customer_id: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_segment: Optional[str] = None
    product_id: str
    product_name: Optional[str] = None
    product_category: Optional[str] = None
    channel_id: str
    channel_name: Optional[str] = None
    text: str
    rating: Optional[int] = None
    date: datetime
    predicted_sentiment: Optional[str] = None
    confidence_score: Optional[float] = None
    explanation: Optional[str] = None
    review_status: Optional[str] = None
    themes: List[str] = []
    theme_confidences: List[float] = []
    quality_issues: List[str] = []
    ground_truth_sentiment: Optional[str] = None
    ground_truth_themes: Optional[str] = None

class FeedbackCorrectionRequest(BaseModel):
    predicted_sentiment: Optional[str] = None
    theme_ids: Optional[List[str]] = None
    reviewed_by: str = "Analyst"
    correction_reason: Optional[str] = None

class BatchInferenceRequest(BaseModel):
    feedback_ids: Optional[List[str]] = None
    feedback_type: Optional[str] = None # SURVEY_RESPONSE, REVIEW, SUPPORT_MESSAGE, or ALL
    limit: Optional[int] = 1000

