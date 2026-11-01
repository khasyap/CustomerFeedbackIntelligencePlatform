from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel

class DataQualityIssueOut(BaseModel):
    issue_id: str
    source_record_id: str
    source_record_type: str
    issue_type: str
    severity: str
    expected_result: str
    actual_result: str
    detection_timestamp: datetime
    resolution_status: str
    resolution_notes: Optional[str] = None

    class Config:
        from_attributes = True

class DataQualityIssueUpdate(BaseModel):
    resolution_status: str # DETECTED, INVESTIGATING, RESOLVED, IGNORED
    resolution_notes: Optional[str] = None

class DataQualityValidationSummary(BaseModel):
    total_records_checked: int
    issues_found: int
    issues_by_type: Dict[str, int]
    issues_by_severity: Dict[str, int]
    pass_rate: float
    validation_timestamp: datetime

class EvaluationMetricsOut(BaseModel):
    eval_id: str
    model_type: str
    model_version: str
    evaluation_dataset: str
    accuracy: Optional[float] = None
    precision_macro: Optional[float] = None
    recall_macro: Optional[float] = None
    f1_macro: Optional[float] = None
    f1_micro: Optional[float] = None
    hamming_loss: Optional[float] = None
    metrics_json: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

