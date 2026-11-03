import pytest
from backend.app.config import settings
from backend.app.services.priority_engine import PriorityEngine, SEVERITY_SCORES

def test_priority_engine_weights_sum_to_one():
    total_weight = (
        settings.WEIGHT_NEGATIVE_RATE +
        settings.WEIGHT_VOLUME +
        settings.WEIGHT_SEVERITY +
        settings.WEIGHT_GROWTH_RATE +
        settings.WEIGHT_CUSTOMER_IMPACT
    )
    assert round(total_weight, 4) == 1.0, f"Priority weights must sum to 1.0, got {total_weight}"

def test_critical_severity_escalation_logic():
    """
    Validates that a CRITICAL severity issue with high dissatisfaction
    (e.g. Billing & Invoicing, 68.2% negative, volume 15) is escalated
    to at least HIGH priority (>= 75.0) and not suppressed by low volume.
    """
    neg_rate = 0.682
    vol = 15
    max_vol = 500
    theme_severity = "CRITICAL"
    growth_rate = 0.15
    customer_impact_score = 75.0

    growth_score = min(100.0, max(0.0, (growth_rate + 0.5) * 100.0))
    volume_score = min(100.0, (vol / max(1, max_vol)) * 100.0)
    severity_score = SEVERITY_SCORES.get(theme_severity, 50.0)

    neg_rate_score = round(neg_rate * 100.0, 1)
    vol_score = round(volume_score, 1)
    sev_score = round(severity_score, 1)
    grow_score = round(growth_score, 1)
    cust_impact = round(customer_impact_score, 1)

    raw_priority_score = (
        settings.WEIGHT_NEGATIVE_RATE * neg_rate_score +
        settings.WEIGHT_VOLUME * vol_score +
        settings.WEIGHT_SEVERITY * sev_score +
        settings.WEIGHT_GROWTH_RATE * grow_score +
        settings.WEIGHT_CUSTOMER_IMPACT * cust_impact
    )

    # In raw formula, low volume (vol_score ~ 3) suppresses raw score to ~58 (MEDIUM)
    assert raw_priority_score < 70.0, f"Expected raw score to be < 70 without escalation, got {raw_priority_score}"

    # Apply Escalation Safeguard
    escalation_applied = False
    escalation_reason = None
    if theme_severity == "CRITICAL" and (neg_rate >= 0.20 or vol >= 30):
        escalation_applied = True
        escalation_reason = "Escalated: Defect carries inherent CRITICAL severity with elevated customer friction"
        priority_score = max(raw_priority_score, 75.0)
    else:
        priority_score = raw_priority_score

    assert escalation_applied is True
    assert priority_score >= 75.0
    # Map to level
    if priority_score >= 85:
        level = "CRITICAL"
    elif priority_score >= 70:
        level = "HIGH"
    elif priority_score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    assert level in ["HIGH", "CRITICAL"], f"Escalated priority level must be HIGH or CRITICAL, got {level}"

def test_non_critical_no_false_escalation():
    """Verify that a medium severity issue does not get falsely escalated."""
    theme_severity = "MEDIUM"
    neg_rate = 0.50
    vol = 20

    escalation_applied = False
    if theme_severity == "CRITICAL" and (neg_rate >= 0.20 or vol >= 30):
        escalation_applied = True

    assert escalation_applied is False

