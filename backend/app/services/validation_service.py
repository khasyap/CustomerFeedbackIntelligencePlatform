import re
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from backend.app.models.entities import (
    Customer, Product, Channel, Survey, Theme,
    SurveyResponse, Review, SupportMessage, Ticket,
    DataQualityIssue
)
from backend.app.ml.preprocessor import TextPreprocessor

class ValidationService:
    """Enterprise Data Quality & Exception Management validation pipeline."""

    @staticmethod
    def run_full_validation(db: Session) -> Dict[str, Any]:
        """Runs all 10 automated data quality checks and records exceptions."""
        total_records_checked = 0
        issues_detected: List[DataQualityIssue] = []

        valid_customer_ids = {c.customer_id for c in db.query(Customer.customer_id).all()}
        valid_product_ids = {p.product_id for p in db.query(Product.product_id).all()}
        valid_channel_ids = {ch.channel_id for ch in db.query(Channel.channel_id).all()}
        valid_theme_ids = {t.theme_id for t in db.query(Theme.theme_id).all()}
        valid_sentiments = {"POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"}

        existing_issue_keys = {
            (iss.source_record_id, iss.issue_type)
            for iss in db.query(DataQualityIssue.source_record_id, DataQualityIssue.issue_type).all()
        }

        # 1. Validate Reviews
        reviews = db.query(Review).all()
        total_records_checked += len(reviews)
        seen_rev_texts = {}

        for rev in reviews:
            # Check 1: Empty text
            if not rev.review_text or not rev.review_text.strip():
                ValidationService._add_issue(
                    db, existing_issue_keys, issues_detected,
                    source_id=rev.review_id,
                    source_type="REVIEW",
                    issue_type="MISSING_MANDATORY_FIELD",
                    severity="HIGH",
                    expected="review_text is mandatory and must not be empty",
                    actual="review_text is empty or whitespace"
                )

            # Check 2: Missing Foreign Key
            if rev.customer_id not in valid_customer_ids:
                ValidationService._add_issue(
                    db, existing_issue_keys, issues_detected,
                    source_id=rev.review_id,
                    source_type="REVIEW",
                    issue_type="MISSING_FOREIGN_KEY",
                    severity="CRITICAL",
                    expected="customer_id must reference an existing valid customer",
                    actual=f"customer_id '{rev.customer_id}' not found in Customers table"
                )

            # Check 3: Taxonomy Violation
            if rev.ground_truth_theme_ids and rev.ground_truth_theme_ids not in valid_theme_ids:
                ValidationService._add_issue(
                    db, existing_issue_keys, issues_detected,
                    source_id=rev.review_id,
                    source_type="REVIEW",
                    issue_type="TAXONOMY_VIOLATION",
                    severity="MEDIUM",
                    expected="Assigned theme must exist in approved theme taxonomy",
                    actual=f"Theme '{rev.ground_truth_theme_ids}' does not exist in taxonomy"
                )

            # Check 4: Sentiment Contradiction
            if rev.rating == 5 and any(w in rev.review_text.lower() for w in ["garbage", "terrible", "worst", "broke on day 1"]):
                ValidationService._add_issue(
                    db, existing_issue_keys, issues_detected,
                    source_id=rev.review_id,
                    source_type="REVIEW",
                    issue_type="SENTIMENT_CONTRADICTION",
                    severity="HIGH",
                    expected="Rating of 5 should reflect positive customer sentiment",
                    actual="Rating is 5 but text contains extreme complaint language"
                )

            # Check 5: Automated PII Masking (Active Policy - auto-scrub in place)
            masked, pii_findings = TextPreprocessor.detect_and_mask_pii(rev.review_text or "")
            if pii_findings and rev.review_text != masked:
                rev.review_text = masked
                db.commit()

            # Check 6: Test Label Leakage
            if TextPreprocessor.detect_test_labels(rev.review_text or ""):
                ValidationService._add_issue(
                    db, existing_issue_keys, issues_detected,
                    source_id=rev.review_id,
                    source_type="REVIEW",
                    issue_type="TEST_LABEL_LEAKAGE",
                    severity="HIGH",
                    expected="Model input text must not contain debug prompt or test tags",
                    actual="Input contains synthetic test/debug metadata labels"
                )

        # 2. Validate Survey Responses
        responses = db.query(SurveyResponse).all()
        total_records_checked += len(responses)
        seen_responses = set()

        # Customer date lookup
        cust_dates = {c.customer_id: c.created_at for c in db.query(Customer.customer_id, Customer.created_at).all()}

        for resp in responses:
            # Check 7: Duplicate Response
            dedup_key = (resp.survey_id, resp.customer_id, resp.response_text[:40])
            if dedup_key in seen_responses:
                ValidationService._add_issue(
                    db, existing_issue_keys, issues_detected,
                    source_id=resp.response_id,
                    source_type="SURVEY_RESPONSE",
                    issue_type="DUPLICATE_RESPONSE",
                    severity="MEDIUM",
                    expected="Single survey submission per customer and survey round",
                    actual=f"Duplicate submission detected for customer '{resp.customer_id}'"
                )
            else:
                seen_responses.add(dedup_key)

            # Check 8: Invalid Date Ordering
            cust_created = cust_dates.get(resp.customer_id)
            if cust_created and resp.response_date < cust_created:
                ValidationService._add_issue(
                    db, existing_issue_keys, issues_detected,
                    source_id=resp.response_id,
                    source_type="SURVEY_RESPONSE",
                    issue_type="INVALID_DATE_ORDERING",
                    severity="MEDIUM",
                    expected="response_date must be >= customer creation date",
                    actual=f"response_date {resp.response_date.strftime('%Y-%m-%d')} is earlier than customer created_at {cust_created.strftime('%Y-%m-%d')}"
                )

            # Check 9: Invalid Sentiment Value
            if resp.ground_truth_sentiment and resp.ground_truth_sentiment not in valid_sentiments:
                ValidationService._add_issue(
                    db, existing_issue_keys, issues_detected,
                    source_id=resp.response_id,
                    source_type="SURVEY_RESPONSE",
                    issue_type="INVALID_SENTIMENT_VALUE",
                    severity="MEDIUM",
                    expected="Sentiment must be POSITIVE, NEGATIVE, NEUTRAL, or MIXED",
                    actual=f"Invalid sentiment value '{resp.ground_truth_sentiment}'"
                )

            # Check PII (Active Policy - auto-scrub in place) & Test labels in survey
            masked, pii_findings = TextPreprocessor.detect_and_mask_pii(resp.response_text or "")
            if pii_findings and resp.response_text != masked:
                resp.response_text = masked
                db.commit()

            if TextPreprocessor.detect_test_labels(resp.response_text or ""):
                ValidationService._add_issue(
                    db, existing_issue_keys, issues_detected,
                    source_id=resp.response_id,
                    source_type="SURVEY_RESPONSE",
                    issue_type="TEST_LABEL_LEAKAGE",
                    severity="HIGH",
                    expected="Text must not contain test labels",
                    actual="Contains test label tag in body"
                )

        # 3. Validate Support Messages & Tickets
        messages = db.query(SupportMessage).all()
        total_records_checked += len(messages)
        for msg in messages:
            masked, pii_findings = TextPreprocessor.detect_and_mask_pii(msg.message_text or "")
            if pii_findings and msg.message_text != masked:
                msg.message_text = masked
                db.commit()

        tickets = db.query(Ticket).all()
        total_records_checked += len(tickets)
        for tkt in tickets:
            # Check 10: Invalid Lifecycle Transition (resolved before created)
            if tkt.resolved_at and tkt.resolved_at < tkt.created_at:
                ValidationService._add_issue(
                    db, existing_issue_keys, issues_detected,
                    source_id=tkt.ticket_id,
                    source_type="TICKET",
                    issue_type="INVALID_LIFECYCLE_TRANSITION",
                    severity="HIGH",
                    expected="resolved_at must be >= ticket created_at",
                    actual=f"resolved_at {tkt.resolved_at} precedes created_at {tkt.created_at}"
                )

        db.commit()

        # Generate summary
        all_issues = db.query(DataQualityIssue).all()
        by_type = {}
        by_sev = {}
        for iss in all_issues:
            by_type[iss.issue_type] = by_type.get(iss.issue_type, 0) + 1
            by_sev[iss.severity] = by_sev.get(iss.severity, 0) + 1

        pass_rate = round(max(0.0, (total_records_checked - len(all_issues)) / max(1, total_records_checked)) * 100.0, 2)

        return {
            "total_records_checked": total_records_checked,
            "issues_found": len(all_issues),
            "issues_by_type": by_type,
            "issues_by_severity": by_sev,
            "pass_rate": pass_rate,
            "validation_timestamp": datetime.utcnow()
        }

    @staticmethod
    def _add_issue(
        db: Session,
        existing_keys: set,
        issues_detected: list,
        source_id: str,
        source_type: str,
        issue_type: str,
        severity: str,
        expected: str,
        actual: str
    ):
        if (source_id, issue_type) in existing_keys:
            return

        cnt = db.query(DataQualityIssue).count() + len(issues_detected) + 1
        iss = DataQualityIssue(
            issue_id=f"DQI-{cnt:06d}",
            source_record_id=source_id,
            source_record_type=source_type,
            issue_type=issue_type,
            severity=severity,
            expected_result=expected,
            actual_result=actual,
            detection_timestamp=datetime.utcnow(),
            resolution_status="DETECTED"
        )
        db.add(iss)
        issues_detected.append(iss)
        existing_keys.add((source_id, issue_type))

