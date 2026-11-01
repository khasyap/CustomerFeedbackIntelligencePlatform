# DATA DICTIONARY: AI-POWERED CUSTOMER FEEDBACK INTELLIGENCE PLATFORM

This document defines all master, transactional, bridge, audit, and analytical entities in the platform.

---

## 1. Customer (`customers`)
Represents synthetic customer identities interacting across digital and physical touchpoints.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `customer_id` | String(50) | Yes | Yes | No | Format: `CUST-######` | None | Yes | Immutable alphanumeric identifier | Unique customer ID |
| `full_name` | String(200) | Yes | No | No | Privacy-safe synthetic names | None | No | Non-empty string | Privacy-safe customer full name |
| `email` | String(200) | Yes | No | No | Valid email format | None | Yes | Standard email regex | Primary contact email address |
| `segment` | String(50) | Yes | No | No | `Consumer`, `SMB`, `Mid-Market`, `Enterprise` | `Consumer` | No | Approved customer segment enum | Business market segmentation |
| `country` | String(50) | Yes | No | No | Standard ISO country names | `USA` | No | Non-empty country string | Customer geographic residency |
| `loyalty_tier` | String(50) | Yes | No | No | `Bronze`, `Silver`, `Gold`, `Platinum` | `Bronze` | No | Tier values | Customer loyalty program status |
| `created_at` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Valid past or current date | Account creation timestamp |

---

## 2. Product (`products`)
Catalog of physical, digital, and service offerings evaluated by customers.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `product_id` | String(50) | Yes | Yes | No | Format: `PROD-######` | None | Yes | Immutable identifier | Unique product identifier |
| `product_name` | String(200) | Yes | No | No | Non-empty string | None | No | Min length 2 | Commercial product name |
| `category` | String(100) | Yes | No | No | 8 taxonomies: `Electronics`, `Software`, `Home Appliances`, `Financial Services`, `Telecommunications`, `Retail`, `Healthcare Services`, `Subscription Services` | None | No | Approved category enum | Market industry category |
| `sku` | String(100) | Yes | No | No | Alphanumeric SKU | None | Yes | Unique product code | Inventory stock keeping unit |
| `price` | Float | Yes | No | No | Float >= 0.0 | 0.0 | No | Non-negative numeric | Base retail or recurring price |
| `release_date` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Valid historical date | Commercial launch date |
| `is_active` | Boolean | Yes | No | No | `True`, `False` | `True` | No | Boolean flag | Active commercial availability |

---

## 3. Channel (`channels`)
Inbound feedback intake and support delivery conduits.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `channel_id` | String(50) | Yes | Yes | No | Format: `CHN-######` | None | Yes | Immutable identifier | Unique channel ID |
| `channel_name` | String(100) | Yes | No | No | 12 taxonomies (e.g. Website, Mobile App, Live Chat) | None | Yes | Unique channel title | Common channel title |
| `channel_type` | String(50) | Yes | No | No | `DIGITAL`, `DIRECT`, `VOICE`, `SOCIAL`, `THIRD_PARTY`, `COMMUNITY`, `PARTNER` | None | No | Approved channel classification | Underlying delivery medium |
| `description` | String(255) | No | No | No | Text | None | No | Optional description | Operational description |
| `is_active` | Boolean | Yes | No | No | `True`, `False` | `True` | No | Boolean | Active channel routing flag |

---

## 4. Survey (`surveys`)
Standardized satisfaction and feedback instruments.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `survey_id` | String(50) | Yes | Yes | No | Format: `SUR-2026-######` | None | Yes | Immutable identifier | Unique survey instrument ID |
| `title` | String(200) | Yes | No | No | Non-empty string | None | No | Title text | Survey campaign title |
| `description` | Text | No | No | No | Text | None | No | Optional details | Campaign objective |
| `target_audience` | String(100) | Yes | No | No | `All`, `Active Users`, `Enterprise`, `New Customers` | `All` | No | Target segment | Target survey recipient cohort |
| `is_active` | Boolean | Yes | No | No | `True`, `False` | `True` | No | Boolean | Survey collection status |
| `created_at` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Creation date | Survey deployment timestamp |

---

## 5. Theme (`themes`)
Structured taxonomy of 18 customer experience themes.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `theme_id` | String(50) | Yes | Yes | No | Format: `THEME-######` | None | Yes | Immutable identifier | Unique theme taxonomy ID |
| `theme_name` | String(100) | Yes | No | No | 18 approved themes | None | Yes | Approved taxonomy list | Formal name of theme |
| `parent_theme_id`| String(50) | No | No | Yes | References `themes.theme_id` | None | No | Valid theme ID or NULL | Hierarchical parent theme |
| `description` | Text | Yes | No | No | Text | None | No | Non-empty text | Scope and diagnostic definition |
| `keywords` | Text | Yes | No | No | Comma-delimited keywords | None | No | Min 3 keywords | NLP keyword anchors |
| `default_severity`| String(50) | Yes | No | No | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` | `MEDIUM` | No | Severity enum | Inherent business operational risk |
| `is_active` | Boolean | Yes | No | No | `True`, `False` | `True` | No | Boolean | Taxonomy active state |
| `effective_start_date` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Start date | Effective date of theme |
| `effective_end_date` | DateTime | No | No | No | ISO 8601 DateTime | None | No | Optional end date | Retirement date |

---

## 6. SentimentLabel (`sentiment_labels`)
Master polarity definitions.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `label_code` | String(50) | Yes | Yes | No | `POSITIVE`, `NEGATIVE`, `NEUTRAL`, `MIXED` | None | Yes | 4 core classes | Classification polarity class |
| `description` | String(255) | Yes | No | No | Text | None | No | Non-empty string | Human readable definition |
| `polarity_score` | Float | Yes | No | No | Numeric `[-1.0, 1.0]` | None | No | Floating point score | Quantitative polarity score |

---

## 7. SurveyResponse (`survey_responses`)
Transactional customer feedback gathered via structured survey instruments.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `response_id` | String(100) | Yes | Yes | No | `RESP-SUR-2026-######-###` | None | Yes | Immutable identifier | Unique response record ID |
| `survey_id` | String(50) | Yes | No | Yes | References `surveys.survey_id` | None | No | Valid foreign key | Linked survey campaign |
| `customer_id` | String(50) | Yes | No | Yes | References `customers.customer_id` | None | No | Valid foreign key | Submitting customer |
| `product_id` | String(50) | Yes | No | Yes | References `products.product_id` | None | No | Valid foreign key | Evaluated product |
| `channel_id` | String(50) | Yes | No | Yes | References `channels.channel_id` | None | No | Valid foreign key | Submission conduit |
| `rating` | Integer | Yes | No | No | Integer `1` to `5` | None | No | Rating integer range | Numerical CSAT rating |
| `response_text` | Text | Yes | No | No | Free-form feedback text | None | No | Non-empty string | Customer open-ended comment |
| `response_date` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | >= customer created_at | Feedback timestamp |
| `ground_truth_sentiment` | String(50) | No | No | No | `POSITIVE`, `NEGATIVE`, `NEUTRAL`, `MIXED` | None | No | Isolated label | Synthetic ground truth |
| `ground_truth_theme_ids` | String(255) | No | No | No | Theme ID or comma list | None | No | Isolated label | Synthetic theme ground truth |

---

## 8. Review (`reviews`)
Transactional customer reviews submitted on e-commerce, websites, or third-party review platforms.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `review_id` | String(50) | Yes | Yes | No | `REV-2026-######` | None | Yes | Immutable identifier | Unique review identifier |
| `customer_id` | String(50) | Yes | No | Yes | References `customers.customer_id` | None | No | Valid foreign key | Author customer ID |
| `product_id` | String(50) | Yes | No | Yes | References `products.product_id` | None | No | Valid foreign key | Reviewed product ID |
| `channel_id` | String(50) | Yes | No | Yes | References `channels.channel_id` | None | No | Valid foreign key | Publishing channel ID |
| `rating` | Integer | Yes | No | No | `1` to `5` | None | No | 1-5 rating | Star rating score |
| `title` | String(255) | No | No | No | Text | None | No | Optional review title | Headline summary |
| `review_text` | Text | Yes | No | No | Free-form text | None | No | Mandatory non-empty | Full narrative feedback |
| `review_date` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Valid date | Review publication date |
| `verified_purchase` | Boolean | Yes | No | No | `True`, `False` | `True` | No | Boolean | Verified transaction flag |
| `ground_truth_sentiment` | String(50) | No | No | No | Sentiment enum | None | No | Isolated label | Benchmark sentiment ground truth |
| `ground_truth_theme_ids` | String(255) | No | No | No | Theme ID | None | No | Isolated label | Benchmark theme ground truth |

---

## 9. SupportMessage (`support_messages`)
Individual communication exchanges within a customer support ticket thread.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `message_id` | String(100) | Yes | Yes | No | `MSG-TKT-######-###` | None | Yes | Immutable identifier | Unique message identifier |
| `ticket_id` | String(50) | Yes | No | Yes | References `tickets.ticket_id` | None | No | Valid ticket FK | Parent support ticket |
| `customer_id` | String(50) | Yes | No | Yes | References `customers.customer_id` | None | No | Valid customer FK | Customer participant |
| `product_id` | String(50) | Yes | No | Yes | References `products.product_id` | None | No | Valid product FK | Product under discussion |
| `channel_id` | String(50) | Yes | No | Yes | References `channels.channel_id` | None | No | Valid channel FK | Intake support channel |
| `sender_type` | String(50) | Yes | No | No | `CUSTOMER`, `AGENT`, `SYSTEM` | `CUSTOMER` | No | Sender enum | Message originator role |
| `message_text` | Text | Yes | No | No | Message text body | None | No | Non-empty text | Content of inquiry/response |
| `message_date` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | >= ticket created_at | Message timestamp |
| `priority` | String(50) | Yes | No | No | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` | `MEDIUM` | No | Severity enum | Triage urgency |

---

## 10. ActionItem (`action_items`)
Operational service improvement work items provisioned to remediate systemic feedback issues.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `action_id` | String(50) | Yes | Yes | No | `ACT-######` | None | Yes | Immutable identifier | Action item identifier |
| `theme_id` | String(50) | Yes | No | Yes | References `themes.theme_id` | None | No | Valid theme FK | Related friction theme |
| `product_id` | String(50) | Yes | No | Yes | References `products.product_id` | None | No | Valid product FK | Target product |
| `priority_score` | Float | Yes | No | No | `0.0` to `100.0` | None | No | 5-factor weighted score | Normalized priority index |
| `priority_level` | String(50) | Yes | No | No | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` | None | No | Level enum | Action priority band |
| `problem_description` | Text | Yes | No | No | Detailed problem statement | None | No | Non-empty text | Root friction summary |
| `recommended_action` | Text | Yes | No | No | Actionable intervention plan | None | No | Non-empty text | Prescribed business action |
| `assigned_team` | String(100) | Yes | No | No | `Operations`, `Engineering`, `Support`, `Product`, `Finance`, `Marketing` | None | No | Team enum | Accountable department |
| `owner` | String(100) | Yes | No | No | Name / Title | None | No | Non-empty string | Accountable individual |
| `status` | String(50) | Yes | No | No | `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`, `BLOCKED` | `OPEN` | No | Validated transitions | Action lifecycle state |
| `expected_impact` | String(255) | Yes | No | No | Projected improvement | None | No | Non-empty string | Anticipated CSAT outcome |
| `actual_impact` | Text | No | No | No | Measured outcome | None | No | Optional notes | Realized post-intervention metric |
| `created_date` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Valid date | Action provisioning timestamp |
| `due_date` | DateTime | Yes | No | No | ISO 8601 DateTime | None | No | >= created_date | Completion target deadline |
| `resolved_date` | DateTime | No | No | No | ISO 8601 DateTime | None | No | >= created_date | Completion timestamp |

---

## 11. FeedbackTheme (`feedback_themes`)
Bridge table associating feedback records with one or more predicted or audited themes.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `id` | Integer | Yes | Yes | No | Autoincrement | None | Yes | Database PK | Bridge row ID |
| `feedback_id` | String(100) | Yes | No | No | Target feedback ID | None | No | Indexed source ID | Associated feedback record ID |
| `feedback_type` | String(50) | Yes | No | No | `SURVEY_RESPONSE`, `REVIEW`, `SUPPORT_MESSAGE` | None | No | Entity type enum | Source record entity type |
| `theme_id` | String(50) | Yes | No | Yes | References `themes.theme_id` | None | No | Valid theme FK | Associated theme ID |
| `confidence` | Float | Yes | No | No | `0.0` to `1.0` | 0.0 | No | Confidence range | Extraction confidence score |
| `classification_method` | String(50) | Yes | No | No | `KEYWORD`, `NLP_TFIDF`, `MULTI_LABEL_MODEL`, `HUMAN` | `NLP_TFIDF` | No | Method enum | Pipeline classification technique |
| `model_version` | String(50) | Yes | No | No | Model version tag | `v1.0.0` | No | Version string | Pipeline model version |
| `is_human_reviewed` | Boolean | Yes | No | No | `True`, `False` | `False` | No | Boolean | Human audit status |
| `reviewed_by` | String(100) | No | No | No | Analyst name/email | None | No | Optional auditor name | Audit user identity |
| `review_timestamp` | DateTime | No | No | No | ISO 8601 DateTime | None | No | Optional timestamp | Review timestamp |

---

## 12. FeedbackSentiment (`feedback_sentiments`)
Predictions and explanations generated by the NLP sentiment engine.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `id` | Integer | Yes | Yes | No | Autoincrement | None | Yes | Database PK | Prediction record ID |
| `feedback_id` | String(100) | Yes | No | No | Target feedback ID | None | No | Unique per feedback | Source feedback record ID |
| `feedback_type` | String(50) | Yes | No | No | `SURVEY_RESPONSE`, `REVIEW`, `SUPPORT_MESSAGE` | None | No | Entity type | Source feedback entity type |
| `predicted_sentiment` | String(50) | Yes | No | No | `POSITIVE`, `NEGATIVE`, `NEUTRAL`, `MIXED` | None | No | Sentiment class | Predicted emotional polarity |
| `confidence_score` | Float | Yes | No | No | `0.0` to `1.0` | None | No | Range 0-1 | Statistical model confidence |
| `model_version` | String(50) | Yes | No | No | Version string | `v1.0.0` | No | Version string | Deployed model version |
| `explanation` | Text | No | No | No | Explainable token reasoning | None | No | Transparent explanation | Human-readable classification basis |
| `review_status` | String(50) | Yes | No | No | `AUTO_CLASSIFIED`, `FLAGGED_FOR_REVIEW`, `HUMAN_REVIEWED` | `AUTO_CLASSIFIED` | No | Status enum | Decision threshold routing status |
| `processing_timestamp`| DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Valid timestamp | Model inference timestamp |

---

## 13. ActionFeedback (`action_feedback`)
Bridge table connecting action items to their supporting customer feedback records.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `id` | Integer | Yes | Yes | No | Autoincrement | None | Yes | Database PK | Link identifier |
| `action_id` | String(50) | Yes | No | Yes | References `action_items.action_id` | None | No | Valid action FK | Parent action item |
| `feedback_id` | String(100) | Yes | No | No | Feedback record ID | None | No | Source record ID | Supporting feedback evidence |
| `feedback_type` | String(50) | Yes | No | No | Entity type enum | None | No | Source type | Source record entity type |
| `linked_date` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Valid timestamp | Date evidence was linked |

---

## 14. Ticket (`tickets`)
Parent customer support case containing multiple sequential support messages.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `ticket_id` | String(50) | Yes | Yes | No | `TKT-######` | None | Yes | Immutable identifier | Support case number |
| `customer_id` | String(50) | Yes | No | Yes | References `customers.customer_id` | None | No | Valid customer FK | Requesting customer |
| `product_id` | String(50) | Yes | No | Yes | References `products.product_id` | None | No | Valid product FK | Target product |
| `channel_id` | String(50) | Yes | No | Yes | References `channels.channel_id` | None | No | Valid channel FK | Intake channel |
| `subject` | String(255) | Yes | No | No | Case subject line | None | No | Non-empty string | Case headline |
| `status` | String(50) | Yes | No | No | `NEW`, `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` | `NEW` | No | Case status enum | Case resolution status |
| `created_at` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Case opened date | Ticket submission date |
| `resolved_at` | DateTime | No | No | No | ISO 8601 DateTime | None | No | >= created_at | Ticket resolution date |

---

## 15. StateChangeEvent (`state_change_events`)
Immutable audit log recording all lifecycle and classification state transitions.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `id` | Integer | Yes | Yes | No | Autoincrement | None | Yes | Database PK | Event log ID |
| `entity_type` | String(50) | Yes | No | No | `ACTION_ITEM`, `TICKET`, `FEEDBACK_SENTIMENT`, `FEEDBACK_THEME` | None | No | Entity type enum | Target audited entity |
| `entity_id` | String(100) | Yes | No | No | Primary key of target entity | None | No | Non-empty string | Target entity record ID |
| `previous_state` | String(100) | No | No | No | Prior state value | None | No | Prior value | Pre-transition status |
| `new_state` | String(100) | Yes | No | No | New state value | None | No | Valid target state | Post-transition status |
| `changed_by` | String(100) | Yes | No | No | Analyst name or `SYSTEM` | `SYSTEM` | No | User/Service ID | Identity initiating transition |
| `change_reason` | Text | No | No | No | Explanatory note | None | No | Optional explanation | Business rationale for transition |
| `change_timestamp` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Immutable timestamp | Transition event timestamp |

---

## 16. DataQualityIssue (`data_quality_issues`)
Explicitly tracked data anomalies, validation violations, and exceptions.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `issue_id` | String(50) | Yes | Yes | No | `DQI-######` | None | Yes | Immutable identifier | Exception tracking ID |
| `source_record_id` | String(100) | Yes | No | No | Target entity record ID | None | No | Non-empty string | Corrupted source record ID |
| `source_record_type`| String(50) | Yes | No | No | Entity type | None | No | Entity type enum | Source record entity type |
| `issue_type` | String(100) | Yes | No | No | 10 anomaly types | None | No | Approved anomaly enum | Anomaly category |
| `severity` | String(50) | Yes | No | No | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` | `MEDIUM` | No | Severity enum | Data quality risk severity |
| `expected_result` | Text | Yes | No | No | Normative business rule statement | None | No | Non-empty string | Expected compliant state |
| `actual_result` | Text | Yes | No | No | Observed violation details | None | No | Non-empty string | Observed erroneous state |
| `detection_timestamp` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Detection date | When anomaly was detected |
| `resolution_status` | String(50) | Yes | No | No | `DETECTED`, `INVESTIGATING`, `RESOLVED`, `IGNORED` | `DETECTED` | No | Status enum | Remediation workflow status |
| `resolution_notes` | Text | No | No | No | Remediation notes | None | No | Optional notes | Resolution audit explanation |

---

## 17. ProcessingRun (`processing_runs`)
Telemetry and execution logs for batch inference, training, and streaming pipelines.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `run_id` | String(50) | Yes | Yes | No | `RUN-######` | None | Yes | Immutable identifier | Processing execution run ID |
| `run_type` | String(50) | Yes | No | No | `BATCH_INFERENCE`, `REALTIME_STREAM`, `RETRAINING`, `VALIDATION` | None | No | Run type enum | Type of pipeline execution |
| `start_time` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Start timestamp | Job start timestamp |
| `end_time` | DateTime | No | No | No | ISO 8601 DateTime | None | No | >= start_time | Job completion timestamp |
| `records_processed` | Integer | Yes | No | No | Integer >= 0 | 0 | No | Non-negative count | Total volume processed |
| `records_flagged` | Integer | Yes | No | No | Integer >= 0 | 0 | No | Non-negative count | Items flagged for review |
| `status` | String(50) | Yes | No | No | `PENDING`, `RUNNING`, `COMPLETED`, `FAILED` | `PENDING` | No | Run status enum | Pipeline completion status |
| `config_json` | Text | No | No | No | JSON configuration payload | None | No | Valid JSON string | Run hyperparameters & config |

---

## 18. ModelEvaluation (`model_evaluations`)
Empirical scientific evaluation metrics calculated on holdout splits.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `eval_id` | String(50) | Yes | Yes | No | `EVAL-######` | None | Yes | Immutable identifier | Evaluation benchmark run ID |
| `model_type` | String(50) | Yes | No | No | `SENTIMENT_CLASSIFIER`, `THEME_CLASSIFIER` | None | No | Model type enum | Evaluated model category |
| `model_version` | String(50) | Yes | No | No | Version string | None | No | Version string | Evaluated model release tag |
| `evaluation_dataset`| String(50) | Yes | No | No | `TRAIN`, `VAL`, `TEST`, `HUMAN_REVIEWED`, `BENCHMARK` | None | No | Split enum | Evaluated data split |
| `accuracy` | Float | No | No | No | Float `0.0` to `1.0` | None | No | Optional accuracy | Classification accuracy |
| `precision_macro` | Float | No | No | No | Float `0.0` to `1.0` | None | No | Range 0-1 | Macro-averaged precision |
| `recall_macro` | Float | No | No | No | Float `0.0` to `1.0` | None | No | Range 0-1 | Macro-averaged recall |
| `f1_macro` | Float | No | No | No | Float `0.0` to `1.0` | None | No | Range 0-1 | Macro-averaged F1 score |
| `f1_micro` | Float | No | No | No | Float `0.0` to `1.0` | None | No | Range 0-1 | Micro-averaged F1 score |
| `hamming_loss` | Float | No | No | No | Float `0.0` to `1.0` | None | No | Multi-label loss | Fraction of wrong labels |
| `metrics_json` | Text | No | No | No | Serialized JSON dictionary | None | No | Valid JSON string | Detailed confusion matrix & class metrics |
| `created_at` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Timestamp | Benchmark run creation date |

---

## 19. SentimentShiftAlert (`sentiment_shift_alerts`)
Time-series anomaly alerts triggered upon significant spikes in customer dissatisfaction.

| Field Name | Data Type | Required? | PK? | FK? | Allowed Values | Default | Unique? | Validation Rules | Business Meaning |
|---|---|---|---|---|---|---|---|---|---|
| `alert_id` | String(50) | Yes | Yes | No | `SFT-######` | None | Yes | Immutable identifier | Unique shift alert ID |
| `dimension_type` | String(50) | Yes | No | No | `PRODUCT`, `CHANNEL`, `THEME`, `OVERALL` | None | No | Dimension enum | Affected business dimension |
| `dimension_id` | String(100) | Yes | No | No | Entity ID or `ALL` | None | No | Non-empty string | Target entity identifier |
| `period_start` | DateTime | Yes | No | No | ISO 8601 DateTime | None | No | Valid date | Evaluation window start |
| `period_end` | DateTime | Yes | No | No | ISO 8601 DateTime | None | No | > period_start | Evaluation window end |
| `baseline_negative_rate` | Float | Yes | No | No | Float `0.0` to `1.0` | None | No | Negative rate | Historical negative baseline |
| `current_negative_rate` | Float | Yes | No | No | Float `0.0` to `1.0` | None | No | Negative rate | Current period negative rate |
| `percentage_change` | Float | Yes | No | No | Float percentage | None | No | Relative jump % | Surge percentage (e.g. +60%) |
| `feedback_volume` | Integer | Yes | No | No | Integer >= min_volume | None | No | Minimum volume | Sample size in current period |
| `severity` | String(50) | Yes | No | No | `HIGH`, `CRITICAL` | `HIGH` | No | Alert severity | Risk level of dissatisfaction surge |
| `summary` | Text | Yes | No | No | Descriptive diagnostic summary | None | No | Non-empty text | Alert narrative and explanation |
| `detected_at` | DateTime | Yes | No | No | ISO 8601 DateTime | `utcnow()` | No | Valid timestamp | Alert detection timestamp |
