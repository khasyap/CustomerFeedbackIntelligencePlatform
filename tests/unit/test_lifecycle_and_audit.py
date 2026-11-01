import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from backend.app.database import SessionLocal
from backend.app.models.entities import ActionItem, StateChangeEvent
from backend.app.services.audit_service import AuditService

def test_action_lifecycle_transitions():
    db = SessionLocal()
    try:
        # Create a test action
        act = ActionItem(
            action_id="ACT-TEST-0001",
            theme_id="THEME-000001",
            product_id="PROD-000001",
            priority_score=85.0,
            priority_level="CRITICAL",
            problem_description="Test issue",
            recommended_action="Test fix",
            assigned_team="Engineering",
            owner="Tester",
            status="OPEN",
            expected_impact="High",
            created_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=10)
        )
        db.add(act)
        db.commit()

        # Valid transition: OPEN -> IN_PROGRESS
        act = AuditService.transition_action_status(db, act, "IN_PROGRESS", changed_by="Lead", reason="Starting work")
        assert act.status == "IN_PROGRESS"

        # Valid transition: IN_PROGRESS -> BLOCKED
        act = AuditService.transition_action_status(db, act, "BLOCKED", changed_by="Lead", reason="Waiting on supplier")
        assert act.status == "BLOCKED"

        # Valid transition: BLOCKED -> IN_PROGRESS
        act = AuditService.transition_action_status(db, act, "IN_PROGRESS", changed_by="Lead", reason="Unblocked")
        assert act.status == "IN_PROGRESS"

        # Valid transition: IN_PROGRESS -> RESOLVED
        act = AuditService.transition_action_status(db, act, "RESOLVED", changed_by="Lead", reason="Fixed")
        assert act.status == "RESOLVED"
        assert act.resolved_date is not None

        # Invalid transition: RESOLVED -> OPEN directly should raise HTTPException
        with pytest.raises(HTTPException):
            AuditService.transition_action_status(db, act, "OPEN", changed_by="Lead")

        # Verify audit history preserved
        events = db.query(StateChangeEvent).filter(StateChangeEvent.entity_id == "ACT-TEST-0001").all()
        assert len(events) >= 4

        # Clean up
        db.delete(act)
        for ev in events:
            db.delete(ev)
        db.commit()
    finally:
        db.close()
