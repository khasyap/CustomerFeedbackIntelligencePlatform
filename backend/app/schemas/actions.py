from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ActionItemBase(BaseModel):
    theme_id: str
    product_id: str
    priority_score: float = Field(..., ge=0, le=100)
    priority_level: str
    problem_description: str
    recommended_action: str
    assigned_team: str
    owner: str
    expected_impact: str
    due_date: datetime

class ActionItemCreate(ActionItemBase):
    supporting_feedback_ids: Optional[List[str]] = []

class ActionItemUpdate(BaseModel):
    priority_score: Optional[float] = None
    priority_level: Optional[str] = None
    assigned_team: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None # OPEN, IN_PROGRESS, RESOLVED, CLOSED, BLOCKED
    change_reason: Optional[str] = "Status update via UI"
    actual_impact: Optional[str] = None
    due_date: Optional[datetime] = None

class ActionFeedbackLink(BaseModel):
    feedback_id: str
    feedback_type: str
    text: Optional[str] = None
    date: Optional[datetime] = None

class ActionItemOut(BaseModel):
    action_id: str
    theme_id: str
    theme_name: Optional[str] = None
    product_id: str
    product_name: Optional[str] = None
    priority_score: float
    priority_level: str
    problem_description: str
    recommended_action: str
    assigned_team: str
    owner: str
    status: str
    expected_impact: str
    actual_impact: Optional[str] = None
    created_date: datetime
    due_date: datetime
    resolved_date: Optional[datetime] = None
    supporting_feedback_count: int = 0
    supporting_feedbacks: List[ActionFeedbackLink] = []

    class Config:
        from_attributes = True

class ActionHistoryItem(BaseModel):
    id: int
    entity_id: str
    previous_state: Optional[str] = None
    new_state: str
    changed_by: str
    change_reason: Optional[str] = None
    change_timestamp: datetime

    class Config:
        from_attributes = True

