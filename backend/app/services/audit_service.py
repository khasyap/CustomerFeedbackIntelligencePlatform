from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.models.entities import StateChangeEvent, ActionItem, ActionStatus

VALID_ACTION_TRANSITIONS = {
    "OPEN": ["IN_PROGRESS", "BLOCKED"],
    "IN_PROGRESS": ["RESOLVED", "BLOCKED"],
    "BLOCKED": ["OPEN", "IN_PROGRESS"],
    "RESOLVED": ["CLOSED", "IN_PROGRESS"], # Can reopen if issue recurs
    "CLOSED": ["IN_PROGRESS"] # Reopen
}

class AuditService:
    """Manages auditability, lineage, and validated lifecycle transitions."""

    @staticmethod
    def transition_action_status(
        db: Session,
        action: ActionItem,
        target_status: str,
        changed_by: str = "Analyst",
        reason: Optional[str] = None
    ) -> ActionItem:
        """Validates lifecycle transition and records an immutable state change audit entry."""
        current_status = action.status

        if current_status == target_status:
            return action

        allowed = VALID_ACTION_TRANSITIONS.get(current_status, [])
        if target_status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid lifecycle transition from '{current_status}' to '{target_status}'. Allowed target states: {allowed}"
            )

        # Record audit event
        audit_event = StateChangeEvent(
            entity_type="ACTION_ITEM",
            entity_id=action.action_id,
            previous_state=current_status,
            new_state=target_status,
            changed_by=changed_by,
            change_reason=reason or f"Transitioned from {current_status} to {target_status}",
            change_timestamp=datetime.utcnow()
        )
        db.add(audit_event)

        # Update action entity
        action.status = target_status
        if target_status in ["RESOLVED", "CLOSED"]:
            action.resolved_date = datetime.utcnow()
        elif target_status == "IN_PROGRESS" and current_status == "RESOLVED":
            action.resolved_date = None # Reopened

        db.commit()
        db.refresh(action)
        return action

    @staticmethod
    def record_manual_classification_correction(
        db: Session,
        feedback_id: str,
        feedback_type: str,
        old_sentiment: Optional[str],
        new_sentiment: str,
        changed_by: str = "Analyst",
        reason: Optional[str] = None
    ):
        """Records an audit trail when an analyst manually corrects AI predictions."""
        event = StateChangeEvent(
            entity_type="FEEDBACK_SENTIMENT",
            entity_id=feedback_id,
            previous_state=old_sentiment or "UNKNOWN",
            new_state=new_sentiment,
            changed_by=changed_by,
            change_reason=reason or "Manual human correction via Feedback Explorer",
            change_timestamp=datetime.utcnow()
        )
        db.add(event)
        db.commit()

