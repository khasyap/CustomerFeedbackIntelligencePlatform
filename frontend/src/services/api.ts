import {
  OverviewMetrics, FeedbackResponse, FeedbackItem, SentimentBreakdownItem,
  ThemeMetricItem, TrendTimePoint, AnomalyShiftAlert, ServicePriorityItem,
  ActionItem, ActionHistoryItem, DataQualityIssue, ValidationSummary,
  ModelEvaluation, ProductItem, ChannelItem, ThemeItem
} from '../types';

const BASE_URL = '/api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  if (!res.ok) {
    let errorMsg = `API request failed with status ${res.status}`;
    try {
      const err = await res.json();
      if (err.detail) errorMsg = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export const api = {
  // Master data
  getProducts: () => fetchJson<ProductItem[]>('/products'),
  getChannels: () => fetchJson<ChannelItem[]>('/channels'),
  getThemes: () => fetchJson<ThemeItem[]>('/themes'),

  // Analytics
  getOverview: (productId?: string, channelId?: string) => {
    const params = new URLSearchParams();
    if (productId) params.append('product_id', productId);
    if (channelId) params.append('channel_id', channelId);
    return fetchJson<OverviewMetrics>(`/analytics/overview?${params.toString()}`);
  },
  getSentimentBreakdown: (groupBy: 'product' | 'channel') =>
    fetchJson<{ group_by: string; items: SentimentBreakdownItem[] }>(`/analytics/sentiment?group_by=${groupBy}`),
  getThemeAnalytics: () => fetchJson<ThemeMetricItem[]>('/analytics/themes'),
  getTrends: (productId?: string, channelId?: string, days: number = 90) => {
    const params = new URLSearchParams({ days: days.toString() });
    if (productId) params.append('product_id', productId);
    if (channelId) params.append('channel_id', channelId);
    return fetchJson<TrendTimePoint[]>(`/analytics/trends?${params.toString()}`);
  },
  getPriorities: (limit: number = 10) => fetchJson<ServicePriorityItem[]>(`/analytics/priorities?limit=${limit}`),
  getAlerts: () => fetchJson<AnomalyShiftAlert[]>('/analytics/alerts'),

  // Feedback explorer
  getFeedback: (params: {
    search?: string;
    product_id?: string;
    channel_id?: string;
    sentiment?: string;
    theme_id?: string;
    review_status?: string;
    feedback_type?: string;
    page?: number;
    page_size?: number;
  }) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== '') qs.append(k, v.toString());
    });
    return fetchJson<FeedbackResponse>(`/feedback?${qs.toString()}`);
  },
  getFeedbackDetail: (id: string) => fetchJson<FeedbackItem>(`/feedback/${id}`),
  correctFeedback: (id: string, body: { predicted_sentiment?: string; theme_ids?: string[]; correction_reason?: string }) =>
    fetchJson<{ message: string; feedback_id: string }>(`/feedback/${id}/correct`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),

  // Actions
  getActions: (status?: string, priority?: string) => {
    const qs = new URLSearchParams();
    if (status) qs.append('status', status);
    if (priority) qs.append('priority_level', priority);
    return fetchJson<ActionItem[]>(`/actions?${qs.toString()}`);
  },
  createAction: (body: any) =>
    fetchJson<ActionItem>('/actions', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  updateAction: (id: string, body: any) =>
    fetchJson<ActionItem>(`/actions/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
  getActionHistory: (id: string) => fetchJson<ActionHistoryItem[]>(`/actions/${id}/history`),

  // Data Quality
  getQualityIssues: (severity?: string, status?: string) => {
    const qs = new URLSearchParams();
    if (severity) qs.append('severity', severity);
    if (status) qs.append('resolution_status', status);
    return fetchJson<DataQualityIssue[]>(`/data-quality/issues?${qs.toString()}`);
  },
  validateDataQuality: () =>
    fetchJson<ValidationSummary>('/data-quality/validate', { method: 'POST' }),
  updateIssue: (id: string, status: string, notes?: string) =>
    fetchJson<DataQualityIssue>(`/data-quality/issues/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ resolution_status: status, resolution_notes: notes }),
    }),

  // AI & Processing
  runProcessingBatch: (batchSize: number = 500) =>
    fetchJson<any>(`/processing/run?batch_size=${batchSize}`, { method: 'POST' }),
  predictSentiment: (text: string) =>
    fetchJson<any>('/sentiment/predict', {
      method: 'POST',
      body: JSON.stringify({ text }),
    }),
  classifyThemes: (text: string) =>
    fetchJson<any>('/themes/classify', {
      method: 'POST',
      body: JSON.stringify({ text }),
    }),
  getProcessingHistory: () => fetchJson<any[]>('/processing/history'),

  // Evaluation
  getEvaluationMetrics: () => fetchJson<ModelEvaluation[]>('/evaluation/metrics'),
  runEvaluation: (dataset: string = 'TEST') =>
    fetchJson<ModelEvaluation[]>(`/evaluation/run?dataset=${dataset}`, { method: 'POST' }),

  // Data management
  generateData: (mode: 'starter' | 'full') =>
    fetchJson<any>(`/data/generate?mode=${mode}`, { method: 'POST' }),
  getReproducibility: () => fetchJson<any>('/data/reproducibility'),
  getOfflinePreview: (limit: number = 25) => fetchJson<any>(`/data/offline-preview?limit=${limit}`),
};

