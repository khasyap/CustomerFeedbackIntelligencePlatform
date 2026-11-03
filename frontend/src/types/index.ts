export type Sentiment = 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL' | 'MIXED';
export type ActionStatus = 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED' | 'BLOCKED';
export type PriorityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export interface OverviewMetrics {
  total_feedback: number;
  total_reviews: number;
  total_surveys: number;
  total_support_messages: number;
  sentiment_distribution: Record<string, number>;
  sentiment_percentages: Record<string, number>;
  total_themes_identified: number;
  critical_issues_count: number;
  open_actions_count: number;
  data_quality_exceptions_count: number;
}

export interface FeedbackItem {
  feedback_id: string;
  feedback_type: string;
  customer_id: string;
  customer_name?: string;
  customer_email?: string;
  customer_segment?: string;
  product_id: string;
  product_name?: string;
  product_category?: string;
  channel_id: string;
  channel_name?: string;
  text: string;
  rating?: number;
  date: string;
  predicted_sentiment: Sentiment;
  confidence_score: number;
  explanation?: string;
  review_status: string;
  themes: string[];
  theme_confidences: number[];
  quality_issues: string[];
  ground_truth_sentiment?: string;
  ground_truth_themes?: string;
}

export interface FeedbackResponse {
  items: FeedbackItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface SentimentBreakdownItem {
  name: string;
  positive: number;
  negative: number;
  neutral: number;
  mixed: number;
  total: number;
  net_sentiment_score: number;
}

export interface ThemeMetricItem {
  theme_id: string;
  theme_name: string;
  count: number;
  percentage: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  mixed_count: number;
  negative_rate: number;
  severity: string;
  is_emerging: boolean;
  problematic_products: string[];
  problematic_channels: string[];
}

export interface TrendTimePoint {
  date: string;
  positive: number;
  negative: number;
  neutral: number;
  mixed: number;
  total: number;
  negative_percentage: number;
}

export interface AnomalyShiftAlert {
  alert_id: string;
  dimension_type: string;
  dimension_id: string;
  dimension_name?: string;
  period_start: string;
  period_end: string;
  baseline_negative_rate: number;
  current_negative_rate: number;
  percentage_change: number;
  feedback_volume: number;
  severity: string;
  summary: string;
  detected_at: string;
}

export interface ServicePriorityItem {
  rank: number;
  theme_id: string;
  theme_name: string;
  product_id: string;
  product_name: string;
  negative_rate: number;
  feedback_volume: number;
  severity: string;
  recent_growth_rate: number;
  customer_impact_score: number;
  priority_score: number;
  priority_level: PriorityLevel;
  suggested_action: string;
  assigned_team: string;
  negative_rate_score?: number;
  volume_score?: number;
  severity_score?: number;
  growth_score?: number;
  customer_impact_factor?: number;
  escalation_applied?: boolean;
  escalation_reason?: string;
  existing_action_id?: string;
  existing_action_status?: string;
}

export interface ActionItem {
  action_id: string;
  theme_id: string;
  theme_name?: string;
  product_id: string;
  product_name?: string;
  priority_score: number;
  priority_level: PriorityLevel;
  problem_description: string;
  recommended_action: string;
  assigned_team: string;
  owner: string;
  status: ActionStatus;
  expected_impact: string;
  actual_impact?: string;
  created_date: string;
  due_date: string;
  resolved_date?: string;
  supporting_feedback_count: number;
}

export interface ActionHistoryItem {
  id: number;
  entity_id: string;
  previous_state?: string;
  new_state: string;
  changed_by: string;
  change_reason?: string;
  change_timestamp: string;
}

export interface DataQualityIssue {
  issue_id: string;
  source_record_id: string;
  source_record_type: string;
  issue_type: string;
  severity: string;
  expected_result: string;
  actual_result: string;
  detection_timestamp: string;
  resolution_status: string;
  resolution_notes?: string;
}

export interface ValidationSummary {
  total_records_checked: number;
  issues_found: number;
  issues_by_type: Record<string, number>;
  issues_by_severity: Record<string, number>;
  pass_rate: number;
  validation_timestamp: string;
}

export interface ModelEvaluation {
  eval_id: string;
  model_type: string;
  model_version: string;
  evaluation_dataset: string;
  accuracy?: number;
  precision_macro?: number;
  recall_macro?: number;
  f1_macro?: number;
  f1_micro?: number;
  hamming_loss?: number;
  metrics_json?: string;
  created_at: string;
}

export interface ProductItem {
  product_id: string;
  product_name: string;
  category: string;
  sku: string;
  price: number;
}

export interface ChannelItem {
  channel_id: string;
  channel_name: string;
  channel_type: string;
}

export interface ThemeItem {
  theme_id: string;
  theme_name: string;
  default_severity: string;
}

