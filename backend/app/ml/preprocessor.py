import re
import unicodedata
from typing import Dict, List, Tuple

# PII Regex Patterns
REGEX_PHONE = re.compile(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}')
REGEX_EMAIL = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
REGEX_SSN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
REGEX_CREDIT_CARD = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')
REGEX_TEST_LABEL = re.compile(r'\[\[TEST_LABEL:[^\]]+\]\]|\[DEBUG_GROUND_TRUTH\]', re.IGNORECASE)

class TextPreprocessor:
    """Handles multilingual text normalization, tokenization, PII detection & masking."""

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        # Unicode normalization
        text = unicodedata.normalize("NFKD", text)
        # Standardize quotes and hyphens
        text = text.replace("’", "'").replace("“", '"').replace("”", '"')
        return text.strip()

    @staticmethod
    def detect_and_mask_pii(text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Detects sensitive personal identity information and masks it safely."""
        issues = []
        masked_text = text

        if REGEX_SSN.search(masked_text):
            issues.append({"type": "PII_LEAKAGE", "detail": "SSN detected in feedback text"})
            masked_text = REGEX_SSN.sub("[REDACTED_SSN]", masked_text)

        if REGEX_CREDIT_CARD.search(masked_text):
            issues.append({"type": "PII_LEAKAGE", "detail": "Credit card number detected in feedback text"})
            masked_text = REGEX_CREDIT_CARD.sub("[REDACTED_CARD]", masked_text)

        if REGEX_EMAIL.search(masked_text):
            issues.append({"type": "PII_LEAKAGE", "detail": "Direct email address found in feedback body"})
            masked_text = REGEX_EMAIL.sub("[REDACTED_EMAIL]", masked_text)

        if REGEX_PHONE.search(masked_text):
            match = REGEX_PHONE.search(masked_text)
            digits = re.sub(r'\D', '', match.group(0))
            if len(digits) >= 7:
                issues.append({"type": "PII_LEAKAGE", "detail": "Telephone number found in feedback text"})
                masked_text = REGEX_PHONE.sub("[REDACTED_PHONE]", masked_text)

        return masked_text, issues

    @staticmethod
    def detect_test_labels(text: str) -> bool:
        """Flags accidental debug or test label leaks."""
        return bool(REGEX_TEST_LABEL.search(text))

    @staticmethod
    def clean_for_ml(text: str) -> str:
        """Removes punctuation and normalizes for bag-of-words / n-gram TF-IDF."""
        if not text:
            return ""
        text = text.lower()
        # Keep letters, numbers, spaces, and basic accented characters
        text = re.sub(r'[^a-zA-Z0-9\u00C0-\u017F\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
