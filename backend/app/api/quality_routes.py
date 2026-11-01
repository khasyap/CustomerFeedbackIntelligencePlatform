from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.entities import DataQualityIssue
from backend.app.schemas.quality import (
    DataQualityIssueOut, DataQualityIssueUpdate, DataQualityValidationSummary
)
from backend.app.services.validation_service import ValidationService

router = APIRouter(prefix="/data-quality", tags=["Data Quality"])

@router.get("/issues", response_model=List[DataQualityIssueOut])
def get_quality_issues(
    severity: Optional[str] = None,
    resolution_status: Optional[str] = None,
    issue_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieves detected data quality issues and anomalies."""
    query = db.query(DataQualityIssue)
    if severity:
        query = query.filter(DataQualityIssue.severity == severity)
    if resolution_status:
        query = query.filter(DataQualityIssue.resolution_status == resolution_status)
    if issue_type:
        query = query.filter(DataQualityIssue.issue_type == issue_type)

    return query.order_by(DataQualityIssue.detection_timestamp.desc()).all()

@router.post("/validate", response_model=DataQualityValidationSummary)
def run_validation_pipeline(db: Session = Depends(get_db)):
    """Triggers end-to-end automated data quality scan across all tables and rules."""
    summary = ValidationService.run_full_validation(db)
    return summary

@router.patch("/issues/{issue_id}", response_model=DataQualityIssueOut)
def update_issue_status(
    issue_id: str,
    body: DataQualityIssueUpdate,
    db: Session = Depends(get_db)
):
    """Updates exception resolution status (INVESTIGATING, RESOLVED, IGNORED) and resolution notes."""
    issue = db.query(DataQualityIssue).filter(DataQualityIssue.issue_id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue ID '{issue_id}' not found")

    issue.resolution_status = body.resolution_status
    if body.resolution_notes is not None:
        issue.resolution_notes = body.resolution_notes

    db.commit()
    db.refresh(issue)
    return issue

