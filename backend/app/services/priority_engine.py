from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.config import settings
from backend.app.models.entities import (
    Theme, Product, Review, SurveyResponse, SupportMessage,
    ActionItem, FeedbackTheme, FeedbackSentiment, ActionFeedback
)

ACTION_PLAYBOOK = {
    "THEME-000001": { # Product Quality
        "problem": "Recurring hardware quality flaws and premature component wear.",
        "action": "Enforce strict incoming QC tolerances at supplier assembly plants and replace brittle plastic molds with reinforced composites.",
        "team": "Engineering",
        "impact": "Reduces defective product returns by an estimated 45% within 60 days."
    },
    "THEME-000002": { # Pricing
        "problem": "Negative perception of renewal price hike and subscription cost transparency.",
        "action": "Publish transparent tiered billing guidelines and introduce annual loyalty discount lock-ins.",
        "team": "Marketing",
        "impact": "Improves renewal conversion by 18% and reduces pricing churn."
    },
    "THEME-000003": { # Customer Support
        "problem": "Extended wait times and unhelpful escalation paths on live chat and phone.",
        "action": "Deploy intelligent AI tier-1 routing, augment staffing during peak hours, and conduct mandatory de-escalation training.",
        "team": "Support",
        "impact": "Decreases first-response time to under 2 minutes and lifts CSAT from 3.2 to 4.6."
    },
    "THEME-000004": { # Delivery Experience
        "problem": "Frequent shipment delays, lack of tracking visibility, and transit packaging damage.",
        "action": "Audit regional 3PL courier SLAs, switch underperforming zones to premier carriers, and add corner foam protection.",
        "team": "Operations",
        "impact": "Reduces transit damage claims by 60% and guarantees 98% on-time delivery."
    },
    "THEME-000005": { # Application Performance
        "problem": "Memory leaks and high CPU usage causing frequent crashes and slow dashboard renders.",
        "action": "Profile client memory consumption, refactor heavy table virtualizers, and implement edge caching.",
        "team": "Engineering",
        "impact": "Reduces client crash rate from 2.4% to < 0.2% and speeds up load times by 3x."
    },
    "THEME-000006": { # User Experience
        "problem": "Confusing settings navigation and cluttered mobile interface.",
        "action": "Redesign mobile layout following modern design system guidelines and streamline profile settings to 2 clicks.",
        "team": "Product",
        "impact": "Decreases task completion time by 40% and boosts usability score."
    },
    "THEME-000007": { # Payment Issues
        "problem": "Spike in double charges and false credit card declines during checkout.",
        "action": "Implement idempotent checkout tokens and configure automated secondary payment gateway failover.",
        "team": "Finance",
        "impact": "Recovers $120k in abandoned cart transactions and eliminates double billing."
    },
    "THEME-000008": { # Refunds
        "problem": "Excessive 3-week delays in processing returned merchandise refunds.",
        "action": "Automate return receipt scanning at warehouse to trigger instant reimbursement upon carrier scan.",
        "team": "Finance",
        "impact": "Reduces refund processing duration from 21 days to under 48 hours."
    },
    "THEME-000009": { # Account Management
        "problem": "2FA SMS delivery failures locking customers out of their accounts.",
        "action": "Integrate WebAuthn/TOTP authenticator app support and add redundant SMS delivery providers.",
        "team": "Engineering",
        "impact": "Reduces account lockout tickets by 75%."
    },
    "THEME-000010": { # Documentation
        "problem": "Outdated API reference and missing troubleshooting guides.",
        "action": "Revamp developer docs with interactive OpenAPI sandbox and generate step-by-step onboarding walkthroughs.",
        "team": "Product",
        "impact": "Reduces integration support tickets by 30%."
    },
    "THEME-000011": { # Product Reliability
        "problem": "Unscheduled service interruptions and random device restarts.",
        "action": "Conduct chaos testing, harden failover database clusters, and implement auto-restart watchdog.",
        "team": "Engineering",
        "impact": "Guarantees 99.95% system availability."
    },
    "THEME-000012": { # Feature Requests
        "problem": "Demand for automated CSV/Excel reporting exports across enterprise teams.",
        "action": "Prioritize asynchronous background report generator in the upcoming sprint release.",
        "team": "Product",
        "impact": "Closes top customer feature request and increases enterprise contract expansions."
    },
    "THEME-000013": { # Security and Privacy
        "problem": "Customer concern over unnecessary mobile background location permissions.",
        "action": "Audit mobile app permission manifests, remove background geolocation, and update privacy disclosures.",
        "team": "Engineering",
        "impact": "Restores customer trust and ensures strict compliance with GDPR/CCPA."
    },
    "THEME-000014": { # Availability
        "problem": "Flagship items constantly out of stock with unpredictable backorders.",
        "action": "Improve demand forecasting with dynamic buffer stock calculations across regional warehouses.",
        "team": "Operations",
        "impact": "Eliminates stock-outs for top 5 revenue-generating SKUs."
    },
    "THEME-000015": { # Communication
        "problem": "Customers uninformed during outages and spammed with uncoordinated emails.",
        "action": "Implement a public real-time incident status page and unify marketing email preference centers.",
        "team": "Marketing",
        "impact": "Lifts customer trust index and reduces email unsubscribes by 50%."
    },
    "THEME-000016": { # Installation
        "problem": "Confusing assembly diagrams and failed Bluetooth pairing out of the box.",
        "action": "Include QR code with animated 3D video setup guide and simplify BLE pairing handshake.",
        "team": "Support",
        "impact": "Reduces initial setup support calls by 55%."
    },
    "THEME-000017": { # Technical Issues
        "problem": "Firmware regression bug throwing uncaught null pointer exceptions.",
        "action": "Deploy hotfix patch v2.4.1 to staging, run automated regression suite, and roll out canary release.",
        "team": "Engineering",
        "impact": "Eliminates fatal crash exceptions for 100% of active sessions."
    },
    "THEME-000018": { # Subscription Management
        "problem": "Friction in cancellation flow and unexpected automatic renewals.",
        "action": "Implement self-service cancel button in account settings and send advance renewal reminders 7 days ahead.",
        "team": "Product",
        "impact": "Eliminates chargeback disputes and complies with FTC negative option rules."
    }
}

SEVERITY_SCORES = {
    "CRITICAL": 100.0,
    "HIGH": 75.0,
    "MEDIUM": 50.0,
    "LOW": 25.0
}

class PriorityEngine:
    """Calculates evidence-based service improvement priorities using weighted formula."""

    _CACHE = None
    _CACHE_TIME = None

    @classmethod
    def calculate_priorities(cls, db: Session, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Calculates priority score for each Theme-Product pair.
        Priority Score =
            35% Negative Sentiment Rate
          + 25% Feedback Volume
          + 20% Issue Severity
          + 10% Recent Growth Rate
          + 10% Customer Impact
        """
        now = datetime.utcnow()
        if not force_refresh and cls._CACHE and cls._CACHE_TIME and (now - cls._CACHE_TIME).total_seconds() < 60:
            return cls._CACHE

        themes = db.query(Theme).filter(Theme.is_active == True).all()
        products = db.query(Product).filter(Product.is_active == True).all()
        
        # Load all existing action items to link status
        existing_actions = {
            f"{a.theme_id}:{a.product_id}": a
            for a in db.query(ActionItem).all()
        }

        # Calculate max volume to normalize
        all_feedback_themes = db.query(
            FeedbackTheme.theme_id,
            func.count(FeedbackTheme.id).label("count")
        ).group_by(FeedbackTheme.theme_id).all()
        
        max_vol = max([c.count for c in all_feedback_themes] or [100])

        priorities = []

        # Pre-gather all feedback themes by theme_id once
        theme_fb_map: Dict[str, List[str]] = {}
        for ft in db.query(FeedbackTheme.theme_id, FeedbackTheme.feedback_id).all():
            theme_fb_map.setdefault(ft[0], []).append(ft[1])

        # Pre-gather feedback sentiments once
        sentiment_lookup = {
            s.feedback_id: (s.predicted_sentiment, s.processing_timestamp)
            for s in db.query(FeedbackSentiment.feedback_id, FeedbackSentiment.predicted_sentiment, FeedbackSentiment.processing_timestamp).all()
        }

        for theme in themes:
            playbook = ACTION_PLAYBOOK.get(theme.theme_id, {
                "problem": f"Customer friction observed regarding {theme.theme_name}.",
                "action": f"Review team procedures and resolve issues related to {theme.theme_name}.",
                "team": "Operations",
                "impact": "Improves overall customer satisfaction."
            })
            severity_score = SEVERITY_SCORES.get(theme.default_severity, 50.0)
            fb_ids = theme_fb_map.get(theme.theme_id, [])

            # Analyze for top problematic products
            for prod in products:
                # If no FeedbackTheme rows yet, gather from Review/Survey ground truth
                if not fb_ids:
                    matching_revs = db.query(Review.review_id, Review.ground_truth_sentiment).filter(
                        Review.product_id == prod.product_id,
                        Review.ground_truth_theme_ids == theme.theme_id
                    ).all()
                    matching_survs = db.query(SurveyResponse.response_id, SurveyResponse.ground_truth_sentiment).filter(
                        SurveyResponse.product_id == prod.product_id,
                        SurveyResponse.ground_truth_theme_ids == theme.theme_id
                    ).all()
                    
                    vol = len(matching_revs) + len(matching_survs)
                    if vol == 0:
                        continue
                    curr_fb_ids = [r[0] for r in matching_revs] + [s[0] for s in matching_survs]
                    neg_count = sum(1 for r in matching_revs if r[1] in ["NEGATIVE", "MIXED"]) + sum(1 for s in matching_survs if s[1] in ["NEGATIVE", "MIXED"])
                    neg_rate = neg_count / max(1, vol)
                    growth_rate = 0.15
                else:
                    curr_fb_ids = fb_ids
                    matched_sents = [sentiment_lookup[fid] for fid in curr_fb_ids if fid in sentiment_lookup]
                    if not matched_sents:
                        continue

                    vol = len(matched_sents)
                    neg_count = sum(1 for s in matched_sents if s[0] in ["NEGATIVE", "MIXED"])
                    neg_rate = neg_count / max(1, vol)

                    # Growth rate: compare last 30 days vs prior 30 days
                    recent_count = sum(1 for s in matched_sents if (now - s[1]).days <= 30)
                    prior_count = sum(1 for s in matched_sents if 30 < (now - s[1]).days <= 60)
                    if prior_count > 0:
                        growth_rate = (recent_count - prior_count) / prior_count
                    else:
                        growth_rate = 0.2 if recent_count > 0 else 0.0

                growth_score = min(100.0, max(0.0, (growth_rate + 0.5) * 100.0))
                volume_score = min(100.0, (vol / max(1, max_vol)) * 100.0)
                customer_impact_score = 75.0 # Average enterprise/mid-market weight

                # Compute individual factor scores (0-100 normalized)
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
                raw_priority_score = round(min(100.0, max(0.0, raw_priority_score)), 1)

                # Escalation Rule for Critical Severity:
                # If an issue carries inherent CRITICAL severity with non-trivial customer friction (neg_rate >= 20% or vol >= 30),
                # escalate priority floor to at least HIGH (75.0) to eliminate Critical-severity / Medium-priority disconnects.
                escalation_applied = False
                escalation_reason = None
                if theme.default_severity == "CRITICAL" and (neg_rate >= 0.20 or vol >= 30):
                    escalation_applied = True
                    escalation_reason = "Escalated: Defect carries inherent CRITICAL severity with elevated customer friction"
                    priority_score = max(raw_priority_score, 75.0)
                else:
                    priority_score = raw_priority_score

                # Determine Priority Level based on final score
                if priority_score >= 85:
                    level = "CRITICAL"
                elif priority_score >= 70:
                    level = "HIGH"
                elif priority_score >= 40:
                    level = "MEDIUM"
                else:
                    level = "LOW"

                key = f"{theme.theme_id}:{prod.product_id}"
                act = existing_actions.get(key)

                priorities.append({
                    "theme_id": theme.theme_id,
                    "theme_name": theme.theme_name,
                    "product_id": prod.product_id,
                    "product_name": prod.product_name,
                    "negative_rate": round(neg_rate * 100.0, 1),
                    "feedback_volume": vol,
                    "severity": theme.default_severity,
                    "recent_growth_rate": round(growth_rate * 100.0, 1),
                    "customer_impact_score": customer_impact_score,
                    "negative_rate_score": neg_rate_score,
                    "volume_score": vol_score,
                    "severity_score": sev_score,
                    "growth_score": grow_score,
                    "customer_impact_factor": cust_impact,
                    "escalation_applied": escalation_applied,
                    "escalation_reason": escalation_reason,
                    "priority_score": priority_score,
                    "priority_level": level,
                    "suggested_action": playbook["action"],
                    "problem_description": playbook["problem"],
                    "assigned_team": playbook["team"],
                    "expected_impact": playbook["impact"],
                    "existing_action_id": act.action_id if act else None,
                    "existing_action_status": act.status if act else None,
                    "supporting_feedback_ids": fb_ids[:10]
                })

        # Sort descending by priority score and assign rank
        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        for idx, p in enumerate(priorities, start=1):
            p["rank"] = idx

        cls._CACHE = priorities
        cls._CACHE_TIME = datetime.utcnow()
        return priorities

    @staticmethod
    def auto_create_action_items(db: Session, top_n: int = 5) -> List[ActionItem]:
        """Automatically provisions action items for critical issues exceeding thresholds."""
        priorities = PriorityEngine.calculate_priorities(db)
        created_actions = []

        now = datetime.utcnow()
        for p in priorities[:top_n]:
            if p["existing_action_id"]:
                continue # Already has action item

            act_id = f"ACT-{db.query(ActionItem).count() + 1:06d}"
            action = ActionItem(
                action_id=act_id,
                theme_id=p["theme_id"],
                product_id=p["product_id"],
                priority_score=p["priority_score"],
                priority_level=p["priority_level"],
                problem_description=p["problem_description"],
                recommended_action=p["suggested_action"],
                assigned_team=p["assigned_team"],
                owner=f"{p['assigned_team']} Lead",
                status="OPEN",
                expected_impact=p["expected_impact"],
                created_date=now,
                due_date=now + timedelta(days=21)
            )
            db.add(action)
            db.flush()

            # Link supporting feedbacks
            for fb_id in p.get("supporting_feedback_ids", []):
                link = ActionFeedback(
                    action_id=act_id,
                    feedback_id=fb_id,
                    feedback_type="REVIEW",
                    linked_date=now
                )
                db.add(link)

            db.commit()
            created_actions.append(action)

        return created_actions
