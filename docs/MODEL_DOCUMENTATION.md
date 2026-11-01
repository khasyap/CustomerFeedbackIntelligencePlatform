# MODEL DOCUMENTATION: NLP SENTIMENT & THEME INTELLIGENCE ENGINE

This document details the machine learning architectures, statistical formulations, feature engineering pipelines, evaluation benchmarks, and operational decision boundaries implemented in the platform.

---

## 1. Pipeline Architecture Overview

The platform implements a multi-stage NLP pipeline designed for high throughput, reproducibility, explainability, and zero label leakage:

```
[Raw Feedback Input (Review / Survey / Support Message)]
                       │
                       ▼
[Text Normalization & Unicode Standardization]
                       │
                       ▼
[PII Detection & Redaction (SSN, Cards, Phones, Emails)]
                       │
                       ▼
[Tokenization & Sublinear TF-IDF Feature Extraction (n-grams: 1, 2)]
         ┌─────────────┴─────────────┐
         ▼                           ▼
[Sentiment Classifier]        [Multi-Label Theme Engine]
- Logistic Regression          - Keyword Anchor Matcher
- Balanced Class Weighting     - TF-IDF Cosine Similarity
- Sarcasm & Contrast Heuristics- Hybrid Confidence Fusion
         │                           │
         ▼                           ▼
[Confidence Decision Engine]   [Unknown Theme Detection]
- High (≥ 0.75): AUTO          - Bridge to FeedbackTheme
- Mid/Low (< 0.75): FLAGGED    - Human Review Tracking
         │                           │
         └─────────────┬─────────────┘
                       ▼
[Explainable Classification Payload & Audit Logging]
```

---

## 2. Sentiment Classification Model

### Architecture & Specification
- **Model Type**: Multi-Class Logistic Regression with L2 Regularization
- **Feature Representation**: Term Frequency-Inverse Document Frequency (TF-IDF)
- **N-Gram Range**: `(1, 2)` (unigrams and bigrams)
- **Sublinear TF Scaling**: `True` ($1 + \log(\text{tf})$)
- **Vocabulary Size**: Max 10,000 features
- **Class Balance**: `class_weight='balanced'`
- **Random State**: Fixed seed `20261022`
- **Model Version**: `v1.2.0-tfidf-logreg`

### Target Classes
1. `POSITIVE` ($\text{Polarity} = +1.0$)
2. `NEGATIVE` ($\text{Polarity} = -1.0$)
3. `NEUTRAL` ($\text{Polarity} = 0.0$)
4. `MIXED` ($\text{Polarity} = +0.1$)

### Decision Boundary & Human Review Rules
Confidence scores $P(\hat{y} \mid x) = \max_c P(y = c \mid x)$ govern the review lifecycle:
- **High Confidence ($\ge 0.75$)**: Status assigned as `AUTO_CLASSIFIED`. Directly approved for downstream dashboards.
- **Medium Confidence ($0.45 \le P < 0.75$)**: Status assigned as `FLAGGED_FOR_REVIEW`. Available on dashboards but highlighted for analyst verification.
- **Low Confidence ($< 0.45$)**: Status assigned as `FLAGGED_FOR_REVIEW`. Diverted to the Feedback Explorer audit queue.

### Explainability Mechanism
For each prediction, token coefficients from the classifier weights are ranked against the tokens present in the document. The top positive, negative, or contrastive tokens are formatted into human-readable explanations (e.g. *"Driven by critical dissatisfaction indicators: defective, broke, unhelpful"*).

---

## 3. Multi-Label Theme Extraction Engine

### Architecture & Specification
- **Engine Type**: Hybrid Multi-Label Extraction combining Lexical Anchors and Document Vector Cosine Proximity.
- **Taxonomy**: 18 pre-registered themes.
- **Taxonomy Document Matrix**: Reference profile constructed from theme names, keywords, and domain definitions.
- **Vector Metric**: Cosine similarity:
  $$\text{Sim}(d, t) = \frac{\mathbf{v}_d \cdot \mathbf{v}_t}{\|\mathbf{v}_d\| \|\mathbf{v}_t\|}$$
- **Hybrid Fusion**:
  $$\text{Conf}(t) = \max\left(\text{Conf}_{\text{keyword}}(t), \, \frac{\text{Conf}_{\text{keyword}}(t) + 1.5 \cdot \text{Sim}(d, t)}{2}\right)$$
- **Unknown Theme Detection**: When no theme satisfies the minimum threshold ($\ge 0.25$), the engine flags the record as an anomaly or unclassified theme for human triage.

---

## 4. Empirical Evaluation Benchmarks

Evaluated on 1,000 holdout records from the strictly isolated `TEST` split (seed `20261022`):

### Sentiment Classifier Performance
- **Accuracy**: $99.70\%$
- **Macro Precision**: $99.58\%$
- **Macro Recall**: $99.78\%$
- **Macro F1-Score**: $99.68\%$
- **Micro F1-Score**: $99.70\%$
- **Operational Throughput**: $935.9 \text{ records/second}$

#### Confusion Matrix
| True \ Predicted | POSITIVE | NEGATIVE | NEUTRAL | MIXED |
|---|---|---|---|---|
| **POSITIVE** | 448 | 0 | 0 | 0 |
| **NEGATIVE** | 0 | 258 | 0 | 0 |
| **NEUTRAL** | 0 | 1 | 154 | 0 |
| **MIXED** | 1 | 1 | 0 | 138 |

### Multi-Label Theme Classifier Performance
- **Macro Precision**: $43.37\%$
- **Macro Recall**: $88.61\%$
- **Macro F1-Score**: $54.81\%$
- **Hamming Loss**: $0.1117$
- **Operational Throughput**: $801.6 \text{ records/second}$

---

## 5. Multilingual and Edge-Case Capabilities

- **Hindi / Hinglish**: Supports code-switching statements (e.g., *"Product bohot achha hai lekin delivery service slow thi"* correctly classified as `MIXED` with `Delivery Experience`).
- **European Languages**: Preprocessing normalizes accented characters in Spanish (*"Excelente calidad"*), French (*"Interface très intuitive"*), and German (*"Kundenservice hat schnell geholfen"*).
- **Sarcasm Handling**: Detects high-praise tokens juxtaposed with fatal regression keywords (e.g., *"Oh great, another crash..."* correctly routed to `NEGATIVE`).

---

## 6. Model Limitations & Future Roadmap

1. **Idiomatic Subtlety**: Extremely subtle sarcasm without overt contrast words may receive lower confidence scores, safely triggering human review.
2. **Transformer Integration**: A lightweight DistilBERT / RoBERTa encoder can be enabled in environments with GPU availability for deeper contextual embeddings.
