# REST API DOCUMENTATION: CUSTOMER FEEDBACK INTELLIGENCE PLATFORM

All API endpoints are prefixed with `/api` and adhere to RESTful conventions with standard HTTP status codes, structured JSON error payloads, and Pydantic validation.

Interactive OpenAPI documentation is live at `http://localhost:8000/docs`.

---

## 1. Master Data Endpoints

### `GET /api/customers`
Retrieves paginated master customer records.
- **Query Parameters**:
  - `segment` (string, optional): Filter by `Consumer`, `SMB`, `Mid-Market`, `Enterprise`.
  - `limit` (integer, default: 100): Page limit (1-1000).
- **Response**: Array of `CustomerBase` objects.

### `GET /api/products`
Catalog of products evaluated by customer feedback.
- **Query Parameters**:
  - `category` (string, optional): One of the 8 product taxonomies.
  - `is_active` (boolean, optional): Filter active/inactive products.
- **Response**: Array of `ProductBase` objects.

### `GET /api/channels`
Feedback intake channels.
- **Query Parameters**:
  - `channel_type` (string, optional): `DIGITAL`, `DIRECT`, `VOICE`, `SOCIAL`, `THIRD_PARTY`, etc.
- **Response**: Array of `ChannelBase` objects.

### `GET /api/themes`
Structured 18-theme customer experience taxonomy.
- **Response**: Array of `ThemeBase` objects with keywords, descriptions, and default severities.

---

## 2. Feedback Explorer Endpoints

### `GET /api/feedback`
Consolidated search, filtering, and pagination across Reviews, Survey Responses, and Support Messages.
- **Query Parameters**:
  - `search` (string, optional): Full-text search across feedback text, titles, or record IDs.
  - `product_id` (string, optional): Filter by product (e.g. `PROD-000001`).
  - `channel_id` (string, optional): Filter by channel (e.g. `CHN-000001`).
  - `sentiment` (string, optional): `POSITIVE`, `NEGATIVE`, `NEUTRAL`, `MIXED`.
  - `theme_id` (string, optional): Target theme ID (e.g. `THEME-000001`).
  - `review_status` (string, optional): `AUTO_CLASSIFIED`, `FLAGGED_FOR_REVIEW`, `HUMAN_REVIEWED`.
  - `feedback_type` (string, optional): `REVIEW`, `SURVEY_RESPONSE`, `SUPPORT_MESSAGE`.
  - `page` (int, default: 1): Page number.
  - `page_size` (int, default: 25): Results per page.
- **Response**:
  ```json
  {
    "items": [
      {
        "feedback_id": "REV-2026-000001",
        "feedback_type": "REVIEW",
        "customer_id": "CUST-000012",
        "customer_name": "Aarav Sharma",
        "product_id": "PROD-000001",
        "product_name": "Aura UltraBook Pro 16",
        "channel_id": "CHN-000001",
        "channel_name": "Website",
        "text": "The build quality exceeded all expectations! Premium finish.",
        "rating": 5,
        "date": "2026-04-12T14:30:00",
        "predicted_sentiment": "POSITIVE",
        "confidence_score": 0.985,
        "explanation": "Driven by strong positive indicators: exceeded, premium, expectations",
        "review_status": "AUTO_CLASSIFIED",
        "themes": ["Product Quality"],
        "quality_issues": []
      }
    ],
    "total": 12009,
    "page": 1,
    "page_size": 25,
    "total_pages": 481
  }
  ```

### `GET /api/feedback/{id}`
Returns complete traceability metadata for a single feedback record, including original text, source customer, model prediction reasoning, and data quality flags.

### `PATCH /api/feedback/{id}/correct`
Allows analysts to manually override AI predictions.
- **Payload**:
  ```json
  {
    "predicted_sentiment": "NEGATIVE",
    "theme_ids": ["THEME-000001"],
    "reviewed_by": "Senior Analyst",
    "correction_reason": "Sarcastic statement missed by baseline model"
  }
  ```
- **Auditing**: Creates an immutable record in `state_change_events` preserving historical predictions.

---

## 3. Analytics Endpoints

### `GET /api/analytics/overview`
Aggregated executive KPIs:
- `total_feedback`, `total_reviews`, `total_surveys`, `total_support_messages`
- `sentiment_distribution`, `sentiment_percentages`
- `total_themes_identified`, `critical_issues_count`, `open_actions_count`, `data_quality_exceptions_count`

### `GET /api/analytics/sentiment`
Net Sentiment Score (NSS) rankings grouped by `product` or `channel`.
- **Query Parameter**: `group_by=product` or `group_by=channel`.
- **Response**:
  ```json
  {
    "group_by": "product",
    "items": [
      {
        "name": "Aura UltraBook Pro 16",
        "positive": 412,
        "negative": 120,
        "neutral": 85,
        "mixed": 35,
        "total": 652,
        "net_sentiment_score": 44.8
      }
    ]
  }
  ```

### `GET /api/analytics/themes`
Theme frequency, percentage share, negative rates, and top problematic products.

### `GET /api/analytics/trends`
Chronological time-series points (daily/monthly counts of positive, negative, neutral, and mixed sentiments).

### `GET /api/analytics/priorities`
Ranked service improvement priorities computed using the 5-factor weighted formula.

### `GET /api/analytics/alerts`
Active sentiment-shift alerts triggered by sudden surges in negative feedback.

---

## 4. AI & NLP Processing Endpoints

### `POST /api/sentiment/predict`
Ad-hoc single text sentiment inference.
- **Payload**: `{"text": "The checkout page charged my card twice!"}`
- **Response**:
  ```json
  {
    "predicted_sentiment": "NEGATIVE",
    "confidence_score": 0.94,
    "model_version": "v1.2.0-tfidf-logreg",
    "review_status": "AUTO_CLASSIFIED",
    "explanation": "Driven by critical dissatisfaction indicators: charged, failed, twice"
  }
  ```

### `POST /api/themes/classify`
Ad-hoc multi-label theme extraction.
- **Payload**: `{"text": "App freezes constantly and courier delivered 5 days late."}`
- **Response**:
  ```json
  [
    {
      "theme_id": "THEME-000005",
      "theme_name": "Application Performance",
      "confidence": 0.88,
      "classification_method": "HYBRID_FUSION"
    },
    {
      "theme_id": "THEME-000004",
      "theme_name": "Delivery Experience",
      "confidence": 0.82,
      "classification_method": "KEYWORD_MATCH"
    }
  ]
  ```

### `POST /api/processing/run`
Batch asynchronous or synchronous inference pipeline over unprocessed database feedback records.
- **Query Parameter**: `batch_size` (int, default: 2000).

---

## 5. Action Management Endpoints

### `GET /api/actions`
Lists all service improvement action items.
- **Query Parameters**: `status`, `priority_level`, `assigned_team`.

### `POST /api/actions`
Provisions a new action item.
- **Payload**:
  ```json
  {
    "theme_id": "THEME-000004",
    "product_id": "PROD-000001",
    "priority_score": 88.5,
    "priority_level": "CRITICAL",
    "problem_description": "Shipment transit damages reported across 45 units",
    "recommended_action": "Switch regional courier and add corner foam packaging",
    "assigned_team": "Operations",
    "owner": "Logistics Lead",
    "expected_impact": "Reduce shipping complaints by 60%",
    "due_date": "2026-11-20T00:00:00Z",
    "supporting_feedback_ids": ["REV-2026-000012", "RESP-SUR-2026-000045-001"]
  }
  ```

### `PATCH /api/actions/{action_id}`
Validates lifecycle transition and records audit event.
- **Valid Transitions**:
  - `OPEN` -> `IN_PROGRESS`, `BLOCKED`
  - `IN_PROGRESS` -> `RESOLVED`, `BLOCKED`
  - `BLOCKED` -> `OPEN`, `IN_PROGRESS`
  - `RESOLVED` -> `CLOSED`, `IN_PROGRESS`
  - `CLOSED` -> `IN_PROGRESS`

### `GET /api/actions/{action_id}/history`
Fetches all immutable historical `StateChangeEvent` records for that action item.

---

## 6. Data Quality & Exception Management

### `GET /api/data-quality/issues`
Lists detected data anomalies. Filter by `severity` and `resolution_status`.

### `POST /api/data-quality/validate`
Triggers an automated scan across all 10 integrity rules, returning pass rates and error breakdowns.

### `PATCH /api/data-quality/issues/{issue_id}`
Updates resolution status (`DETECTED`, `INVESTIGATING`, `RESOLVED`, `IGNORED`) and resolution notes.

---

## 7. Model Evaluation & Benchmark Endpoints

### `GET /api/evaluation/metrics`
Retrieves benchmark metrics across Sentiment and Theme classifiers.

### `POST /api/evaluation/run`
Runs evaluation against the holdout `TEST` split, calculating precision, recall, macro F1, micro F1, Hamming loss, and confusion matrix.
