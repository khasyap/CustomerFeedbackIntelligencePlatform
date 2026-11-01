import pytest
from backend.app.ml.preprocessor import TextPreprocessor
from backend.app.ml.sentiment_classifier import SentimentClassifier
from backend.app.ml.theme_classifier import ThemeClassifier
from backend.app.services.priority_engine import PriorityEngine

def test_text_preprocessor_pii_detection():
    text = "Please reach me at +1-555-0199 or email user@test.com. My SSN is 000-12-3456."
    masked, issues = TextPreprocessor.detect_and_mask_pii(text)
    assert len(issues) >= 2
    assert "[REDACTED_SSN]" in masked
    assert "[REDACTED_PHONE]" in masked

def test_text_preprocessor_test_label_detection():
    clean_text = "Good product and fast shipping."
    dirty_text = "[[TEST_LABEL: NEGATIVE]] Terrible experience."
    assert not TextPreprocessor.detect_test_labels(clean_text)
    assert TextPreprocessor.detect_test_labels(dirty_text)

def test_sentiment_classifier_predictions():
    clf = SentimentClassifier()
    pos_res = clf.predict_one("Outstanding product quality and lightning fast delivery!")
    assert pos_res["predicted_sentiment"] in ["POSITIVE", "MIXED"]
    assert pos_res["confidence_score"] > 0.60
    assert "explanation" in pos_res

    neg_res = clf.predict_one("Completely broken and defective. Horrible customer support!")
    assert neg_res["predicted_sentiment"] == "NEGATIVE"
    assert neg_res["confidence_score"] > 0.60

def test_sarcasm_handling():
    clf = SentimentClassifier()
    sarcastic = "Oh fantastic, another crash right when saving my project! Just what I needed."
    res = clf.predict_one(sarcastic)
    assert res["predicted_sentiment"] == "NEGATIVE"

def test_theme_classifier_multi_label():
    clf = ThemeClassifier()
    text = "The payment checkout failed twice and the courier delivery was delayed by a week."
    themes = clf.extract_themes(text)
    t_ids = {t["theme_id"] for t in themes}
    assert "THEME-000007" in t_ids or "THEME-000004" in t_ids
    assert len(themes) >= 1
    assert "confidence" in themes[0]
