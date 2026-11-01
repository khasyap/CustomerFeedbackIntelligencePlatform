from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.entities import (
    ActionItem, ActionFeedback, StateChangeEvent, Theme, Product, Review
)
from backend.app.schemas.actions import (
    ActionItemCreate, ActionItemUpdate, ActionItemOut, ActionHistoryItem, ActionFeedbackLink
)
from backend.app.services.audit_service import AuditService

router = APIRouter(prefix="/actions", tags=["Action Management"])

@router.get("", response_model=List[ActionItemOut])
def get_actions(
    status: Optional[str] = None,
    priority_level: Optional[str] = None,
    assigned_team: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieves all service improvement action items with linked themes and products."""
    query = db.query(ActionItem)
    if status:
        query = query.filter(ActionItem.status == status)
    if priority_level:
        query = query.filter(ActionItem.priority_level == priority_level)
    if assigned_team:
        query = query.filter(ActionItem.assigned_team == assigned_team)

    actions = query.order_by(ActionItem.priority_score.desc()).all()
    themes = {t.theme_id: t.theme_name for t in db.query(Theme).all()}
    products = {p.product_id: p.product_name for p in db.query(Product).all()}

    output = []
    for a in actions:
        links = db.query(ActionFeedback).filter(ActionFeedback.action_id == a.action_id).all()
        supporting = [
            ActionFeedbackLink(
                feedback_id=l.feedback_id,
                feedback_type=l.feedback_type,
                date=l.linked_date
            )
            for l in links
        ]
        output.append(ActionItemOut(
            action_id=a.action_id,
            theme_id=a.theme_id,
            theme_name=themes.get(a.theme_id, a.theme_id),
            product_id=a.product_id,
            product_name=products.get(a.product_id, a.product_id),
            priority_score=a.priority_score,
            priority_level=a.priority_level,
            problem_description=a.problem_description,
            recommended_action=a.recommended_action,
            assigned_team=a.assigned_team,
            owner=a.owner,
            status=a.status,
            expected_impact=a.expected_impact,
            actual_impact=a.actual_impact,
            created_date=a.created_date,
            due_date=a.due_date,
            resolved_date=a.resolved_date,
            supporting_feedback_count=len(supporting),
            supporting_feedbacks=supporting
        ))

    return output

@router.post("", response_model=ActionItemOut)
def create_action(body: ActionItemCreate, db: Session = Depends(get_db)):
    """Creates a new action item, links supporting feedback, and initiates audit trail."""
    act_count = db.query(ActionItem).count() + 1
    action_id = f"ACT-{act_count:06d}"

    action = ActionItem(
        action_id=action_id,
        theme_id=body.theme_id,
        product_id=body.product_id,
        priority_score=body.priority_score,
        priority_level=body.priority_level,
        problem_description=body.problem_description,
        recommended_action=body.recommended_action,
        assigned_team=body.assigned_team,
        owner=body.owner,
        status="OPEN",
        expected_impact=body.expected_impact,
        created_date=datetime.utcnow(),
        due_date=body.due_date
    )
    db.add(action)
    db.flush()

    # Link supporting feedback IDs
    for fid in (body.supporting_feedback_ids or []):
        link = ActionFeedback(
            action_id=action_id,
            feedback_id=fid,
            feedback_type="REVIEW",
            linked_date=datetime.utcnow()
        )
        db.add(link)

    # Initial state audit
    init_audit = StateChangeEvent(
        entity_type="ACTION_ITEM",
        entity_id=action_id,
        previous_state=None,
        new_state="OPEN",
        changed_by="Analyst",
        change_reason="Created action item from recommendation engine",
        change_timestamp=datetime.utcnow()
    )
    db.add(init_audit)
    db.commit()

    theme = db.query(Theme).filter(Theme.theme_id == action.theme_id).first()
    product = db.query(Product).filter(Product.product_id == action.product_id).first()

    return ActionItemOut(
        action_id=action.action_id,
        theme_id=action.theme_id,
        theme_name=theme.theme_name if theme else action.theme_id,
        product_id=action.product_id,
        product_name=product.product_name if product else action.product_id,
        priority_score=action.priority_score,
        priority_level=action.priority_level,
        problem_description=action.problem_description,
        recommended_action=action.recommended_action,
        assigned_team=action.assigned_team,
        owner=action.owner,
        status=action.status,
        expected_impact=action.expected_impact,
        actual_impact=action.actual_impact,
        created_date=action.created_date,
        due_date=action.due_date,
        resolved_date=action.resolved_date,
        supporting_feedback_count=len(body.supporting_feedback_ids or []),
        supporting_feedbacks=[]
    )

@router.patch("/{action_id}", response_model=ActionItemOut)
def update_action(
    action_id: str,
    body: ActionItemUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates action item.
    Enforces validated lifecycle transitions (OPEN -> IN_PROGRESS -> RESOLVED -> CLOSED)
    and logs historical state changes.
    """
    action = db.query(ActionItem).filter(ActionItem.action_id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail=f"Action item '{action_id}' not found")

    if body.status and body.status != action.status:
        action = AuditService.transition_action_status(
            db=db,
            action=action,
            target_status=body.status,
            changed_by="Analyst",
            reason=body.change_reason
        )

    if body.priority_score is not None:
        action.priority_score = body.priority_score
    if body.priority_level is not None:
        action.priority_level = body.priority_level
    if body.assigned_team is not None:
        action.assigned_team = body.assigned_team
    if body.owner is not None:
        action.owner = body.owner
    if body.actual_impact is not None:
        action.actual_impact = body.actual_impact
    if body.due_date is not None:
        action.due_date = body.due_date

    db.commit()
    db.refresh(action)

    theme = db.query(Theme).filter(Theme.theme_id == action.theme_id).first()
    product = db.query(Product).filter(Product.product_id == action.product_id).first()
    links = db.query(ActionFeedback).filter(ActionFeedback.action_id == action.action_id).all()

    return ActionItemOut(
        action_id=action.action_id,
        theme_id=action.theme_id,
        theme_name=theme.theme_name if theme else action.theme_id,
        product_id=action.product_id,
        product_name=product.product_name if product else action.product_id,
        priority_score=action.priority_score,
        priority_level=action.priority_level,
        problem_description=action.problem_description,
        recommended_action=action.recommended_action,
        assigned_team=action.assigned_team,
        owner=action.owner,
        status=action.status,
        expected_impact=action.expected_impact,
        actual_impact=action.actual_impact,
        created_date=action.created_date,
        due_date=action.due_date,
        resolved_date=action.resolved_date,
        supporting_feedback_count=len(links),
        supporting_feedbacks=[]
    )

@router.get("/{action_id}/history", response_model=List[ActionHistoryItem])
def get_action_history(action_id: str, db: Session = Depends(get_db)):
    """Retrieves full immutable audit history for this action item."""
    events = db.query(StateChangeEvent).filter(
        StateChangeEvent.entity_type == "ACTION_ITEM",
        StateChangeEvent.entity_id == action_id
    ).order_by(StateChangeEvent.change_timestamp.desc()).all()
    return events

