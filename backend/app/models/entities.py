import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, Index, UniqueConstraint, Enum
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

# Enumerations
class SentimentType(str, enum.Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"

class ActionStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    BLOCKED = "BLOCKED"

class PriorityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ReviewStatus(str, enum.Enum):
    AUTO_CLASSIFIED = "AUTO_CLASSIFIED"
    FLAGGED_FOR_REVIEW = "FLAGGED_FOR_REVIEW"
    HUMAN_REVIEWED = "HUMAN_REVIEWED"

class DataQualitySeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class DataQualityStatus(str, enum.Enum):
    DETECTED = "DETECTED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"

# 1. Customer Entity
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(50), primary_key=True, index=True) # e.g. CUST-000001
    full_name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True, index=True)
    segment = Column(String(50), nullable=False, default="Consumer") # Consumer, SMB, Mid-Market, Enterprise
    country = Column(String(50), nullable=False, default="USA")
    loyalty_tier = Column(String(50), nullable=False, default="Bronze") # Bronze, Silver, Gold, Platinum
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    survey_responses = relationship("SurveyResponse", back_populates="customer", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="customer", cascade="all, delete-orphan")
    support_messages = relationship("SupportMessage", back_populates="customer", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="customer", cascade="all, delete-orphan")

# 2. Product Entity
class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True, index=True) # e.g. PROD-000001
    product_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    sku = Column(String(100), nullable=False, unique=True)
    price = Column(Float, nullable=False, default=0.0)
    release_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    survey_responses = relationship("SurveyResponse", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    support_messages = relationship("SupportMessage", back_populates="product")
    tickets = relationship("Ticket", back_populates="product")
    actions = relationship("ActionItem", back_populates="product")

# 3. Channel Entity
class Channel(Base):
    __tablename__ = "channels"

    channel_id = Column(String(50), primary_key=True, index=True) # e.g. CHN-000001
    channel_name = Column(String(100), nullable=False, unique=True)
    channel_type = Column(String(50), nullable=False) # DIGITAL, DIRECT, VOICE, SOCIAL, THIRD_PARTY
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    survey_responses = relationship("SurveyResponse", back_populates="channel")
    reviews = relationship("Review", back_populates="channel")
    support_messages = relationship("SupportMessage", back_populates="channel")
    tickets = relationship("Ticket", back_populates="channel")

# 4. Survey Entity
class Survey(Base):
    __tablename__ = "surveys"

    survey_id = Column(String(50), primary_key=True, index=True) # e.g. SUR-2026-000001
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    target_audience = Column(String(100), nullable=False, default="All")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    responses = relationship("SurveyResponse", back_populates="survey", cascade="all, delete-orphan")

# 5. Theme Entity
class Theme(Base):
    __tablename__ = "themes"

    theme_id = Column(String(50), primary_key=True, index=True) # e.g. THEME-000001
    theme_name = Column(String(100), nullable=False, unique=True, index=True)
    parent_theme_id = Column(String(50), ForeignKey("themes.theme_id"), nullable=True)
    description = Column(Text, nullable=False)
    keywords = Column(Text, nullable=False) # Comma-separated search keywords
    default_severity = Column(String(50), nullable=False, default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    is_active = Column(Boolean, nullable=False, default=True)
    effective_start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    effective_end_date = Column(DateTime, nullable=True)

    # Relationships
    sub_themes = relationship("Theme", backref="parent_theme", remote_side=[theme_id])
    feedback_themes = relationship("FeedbackTheme", back_populates="theme")
    actions = relationship("ActionItem", back_populates="theme")

# 6. SentimentLabel Entity
class SentimentLabel(Base):
    __tablename__ = "sentiment_labels"

    label_code = Column(String(50), primary_key=True) # POSITIVE, NEGATIVE, NEUTRAL, MIXED
    description = Column(String(255), nullable=False)
    polarity_score = Column(Float, nullable=False) # e.g. 1.0, -1.0, 0.0, 0.2

# 7. SurveyResponse Entity
class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    response_id = Column(String(100), primary_key=True, index=True) # RESP-SUR-2026-000001-001
    survey_id = Column(String(50), ForeignKey("surveys.survey_id"), nullable=False, index=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False, index=True)
    channel_id = Column(String(50), ForeignKey("channels.channel_id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False) # 1 - 5 or NPS
    response_text = Column(Text, nullable=False)
    response_date = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    
    # Ground truth (isolated from model features)
    ground_truth_sentiment = Column(String(50), nullable=True)
    ground_truth_theme_ids = Column(String(255), nullable=True)

    # Relationships
    survey = relationship("Survey", back_populates="responses")
    customer = relationship("Customer", back_populates="survey_responses")
    product = relationship("Product", back_populates="survey_responses")
    channel = relationship("Channel", back_populates="survey_responses")

# 8. Review Entity
class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(String(50), primary_key=True, index=True) # REV-2026-000001
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False, index=True)
    channel_id = Column(String(50), ForeignKey("channels.channel_id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False) # 1 - 5
    title = Column(String(255), nullable=True)
    review_text = Column(Text, nullable=False)
    review_date = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    verified_purchase = Column(Boolean, nullable=False, default=True)

    # Ground truth
    ground_truth_sentiment = Column(String(50), nullable=True)
    ground_truth_theme_ids = Column(String(255), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    channel = relationship("Channel", back_populates="reviews")

# 14. Ticket Entity (Parent to SupportMessage)
class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(String(50), primary_key=True, index=True) # TKT-000001
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False, index=True)
    channel_id = Column(String(50), ForeignKey("channels.channel_id"), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="NEW") # NEW, OPEN, ASSIGNED, RESOLVED, CLOSED
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="tickets")
    product = relationship("Product", back_populates="tickets")
    channel = relationship("Channel", back_populates="tickets")
    messages = relationship("SupportMessage", back_populates="ticket", cascade="all, delete-orphan")

# 9. SupportMessage Entity
class SupportMessage(Base):
    __tablename__ = "support_messages"

    message_id = Column(String(100), primary_key=True, index=True) # MSG-TKT-000001-001
    ticket_id = Column(String(50), ForeignKey("tickets.ticket_id"), nullable=False, index=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False, index=True)
    channel_id = Column(String(50), ForeignKey("channels.channel_id"), nullable=False, index=True)
    sender_type = Column(String(50), nullable=False, default="CUSTOMER") # CUSTOMER, AGENT, SYSTEM
    message_text = Column(Text, nullable=False)
    message_date = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    priority = Column(String(50), nullable=False, default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL

    # Ground truth
    ground_truth_sentiment = Column(String(50), nullable=True)
    ground_truth_theme_ids = Column(String(255), nullable=True)

    # Relationships
    ticket = relationship("Ticket", back_populates="messages")
    customer = relationship("Customer", back_populates="support_messages")
    product = relationship("Product", back_populates="support_messages")
    channel = relationship("Channel", back_populates="support_messages")

# 10. ActionItem Entity
class ActionItem(Base):
    __tablename__ = "action_items"

    action_id = Column(String(50), primary_key=True, index=True) # ACT-000001
    theme_id = Column(String(50), ForeignKey("themes.theme_id"), nullable=False, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False, index=True)
    priority_score = Column(Float, nullable=False) # 0 - 100
    priority_level = Column(String(50), nullable=False) # CRITICAL, HIGH, MEDIUM, LOW
    problem_description = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    assigned_team = Column(String(100), nullable=False) # Operations, Engineering, Support, Product, Finance, Marketing
    owner = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="OPEN") # OPEN, IN_PROGRESS, RESOLVED, CLOSED, BLOCKED
    expected_impact = Column(String(255), nullable=False)
    actual_impact = Column(Text, nullable=True)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    resolved_date = Column(DateTime, nullable=True)

    # Relationships
    theme = relationship("Theme", back_populates="actions")
    product = relationship("Product", back_populates="actions")
    feedbacks = relationship("ActionFeedback", back_populates="action", cascade="all, delete-orphan")

# 11. FeedbackTheme Bridge Entity
class FeedbackTheme(Base):
    __tablename__ = "feedback_themes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feedback_id = Column(String(100), nullable=False, index=True)
    feedback_type = Column(String(50), nullable=False, index=True) # SURVEY_RESPONSE, REVIEW, SUPPORT_MESSAGE
    theme_id = Column(String(50), ForeignKey("themes.theme_id"), nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=0.0)
    classification_method = Column(String(50), nullable=False, default="NLP_TFIDF") # KEYWORD, NLP_TFIDF, MULTI_LABEL_MODEL, HUMAN
    model_version = Column(String(50), nullable=False, default="v1.0.0")
    is_human_reviewed = Column(Boolean, nullable=False, default=False)
    reviewed_by = Column(String(100), nullable=True)
    review_timestamp = Column(DateTime, nullable=True)

    # Relationships
    theme = relationship("Theme", back_populates="feedback_themes")

    __table_args__ = (
        Index("ix_feedback_theme_unique", "feedback_id", "feedback_type", "theme_id", unique=True),
    )

# 12. FeedbackSentiment Entity
class FeedbackSentiment(Base):
    __tablename__ = "feedback_sentiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feedback_id = Column(String(100), nullable=False, index=True)
    feedback_type = Column(String(50), nullable=False, index=True) # SURVEY_RESPONSE, REVIEW, SUPPORT_MESSAGE
    predicted_sentiment = Column(String(50), nullable=False, index=True) # POSITIVE, NEGATIVE, NEUTRAL, MIXED
    confidence_score = Column(Float, nullable=False)
    model_version = Column(String(50), nullable=False, default="v1.0.0")
    explanation = Column(Text, nullable=True)
    review_status = Column(String(50), nullable=False, default="AUTO_CLASSIFIED") # AUTO_CLASSIFIED, FLAGGED_FOR_REVIEW, HUMAN_REVIEWED
    processing_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_feedback_sentiment_unique", "feedback_id", "feedback_type", unique=True),
    )

# 13. ActionFeedback Bridge Entity
class ActionFeedback(Base):
    __tablename__ = "action_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action_id = Column(String(50), ForeignKey("action_items.action_id"), nullable=False, index=True)
    feedback_id = Column(String(100), nullable=False, index=True)
    feedback_type = Column(String(50), nullable=False)
    linked_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    action = relationship("ActionItem", back_populates="feedbacks")

    __table_args__ = (
        Index("ix_action_feedback_unique", "action_id", "feedback_id", "feedback_type", unique=True),
    )

# 15. StateChangeEvent Entity (Audit)
class StateChangeEvent(Base):
    __tablename__ = "state_change_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False, index=True) # ACTION_ITEM, TICKET, FEEDBACK_SENTIMENT, FEEDBACK_THEME
    entity_id = Column(String(100), nullable=False, index=True)
    previous_state = Column(String(100), nullable=True)
    new_state = Column(String(100), nullable=False)
    changed_by = Column(String(100), nullable=False, default="SYSTEM")
    change_reason = Column(Text, nullable=True)
    change_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

# 16. DataQualityIssue Entity
class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    issue_id = Column(String(50), primary_key=True, index=True) # DQI-000001
    source_record_id = Column(String(100), nullable=False, index=True)
    source_record_type = Column(String(50), nullable=False)
    issue_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(50), nullable=False, default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    expected_result = Column(Text, nullable=False)
    actual_result = Column(Text, nullable=False)
    detection_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    resolution_status = Column(String(50), nullable=False, default="DETECTED") # DETECTED, INVESTIGATING, RESOLVED, IGNORED
    resolution_notes = Column(Text, nullable=True)

# 17. ProcessingRun Entity
class ProcessingRun(Base):
    __tablename__ = "processing_runs"

    run_id = Column(String(50), primary_key=True, index=True) # RUN-000001
    run_type = Column(String(50), nullable=False) # BATCH_INFERENCE, REALTIME_STREAM, RETRAINING, VALIDATION
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    records_processed = Column(Integer, nullable=False, default=0)
    records_flagged = Column(Integer, nullable=False, default=0)
    status = Column(String(50), nullable=False, default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED
    config_json = Column(Text, nullable=True)

# 18. ModelEvaluation Entity
class ModelEvaluation(Base):
    __tablename__ = "model_evaluations"

    eval_id = Column(String(50), primary_key=True, index=True) # EVAL-000001
    model_type = Column(String(50), nullable=False) # SENTIMENT_CLASSIFIER, THEME_CLASSIFIER
    model_version = Column(String(50), nullable=False)
    evaluation_dataset = Column(String(50), nullable=False) # TRAIN, VAL, TEST, HUMAN_REVIEWED, BENCHMARK
    accuracy = Column(Float, nullable=True)
    precision_macro = Column(Float, nullable=True)
    recall_macro = Column(Float, nullable=True)
    f1_macro = Column(Float, nullable=True)
    f1_micro = Column(Float, nullable=True)
    hamming_loss = Column(Float, nullable=True)
    metrics_json = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

# 19. SentimentShiftAlert Entity
class SentimentShiftAlert(Base):
    __tablename__ = "sentiment_shift_alerts"

    alert_id = Column(String(50), primary_key=True, index=True) # SFT-000001
    dimension_type = Column(String(50), nullable=False) # PRODUCT, CHANNEL, THEME, OVERALL
    dimension_id = Column(String(100), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    baseline_negative_rate = Column(Float, nullable=False)
    current_negative_rate = Column(Float, nullable=False)
    percentage_change = Column(Float, nullable=False)
    feedback_volume = Column(Integer, nullable=False)
    severity = Column(String(50), nullable=False, default="HIGH") # HIGH, CRITICAL
    summary = Column(Text, nullable=False)
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
