import React, { useState } from 'react';
import { X, CheckCircle, AlertTriangle, ShieldAlert, Sparkles, User, Tag, Calendar, Building2 } from 'lucide-react';
import { FeedbackItem, Sentiment } from '../types';
import { api } from '../services/api';

interface FeedbackDetailModalProps {
  feedback: FeedbackItem | null;
  onClose: () => void;
  onCorrectionSuccess?: () => void;
}

export const FeedbackDetailModal: React.FC<FeedbackDetailModalProps> = ({
  feedback,
  onClose,
  onCorrectionSuccess
}) => {
  if (!feedback) return null;

  const [selectedSentiment, setSelectedSentiment] = useState<Sentiment>(feedback.predicted_sentiment);
  const [reason, setReason] = useState('');
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSaveCorrection = async () => {
    setSaving(true);
    setErrorMsg('');
    try {
      await api.correctFeedback(feedback.feedback_id, {
        predicted_sentiment: selectedSentiment,
        correction_reason: reason || 'Manual adjustment via Feedback Explorer'
      });
      setSuccessMsg('Classification successfully corrected and audited!');
      setTimeout(() => {
        if (onCorrectionSuccess) onCorrectionSuccess();
        onClose();
      }, 1000);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to save correction');
    } finally {
      setSaving(false);
    }
  };

  const getSentimentBadge = (sent: string) => {
    switch (sent) {
      case 'POSITIVE':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'NEGATIVE':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
      case 'MIXED':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      default:
        return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-3 sm:p-4">
      <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 p-4 sm:p-6 shadow-2xl overflow-y-auto max-h-[90vh]">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2.5">
            <span className="font-mono text-xs px-2 py-1 rounded bg-slate-800 text-indigo-300 font-bold border border-slate-700">
              {feedback.feedback_id}
            </span>
            <span className="text-xs uppercase tracking-wider text-slate-400">
              {feedback.feedback_type}
            </span>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="mt-4 space-y-4 text-xs">
          {/* Metadata chips */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            <div>
              <p className="text-[10px] text-slate-400">Customer</p>
              <p className="font-medium text-slate-200">{feedback.customer_name || feedback.customer_id}</p>
            </div>
            <div>
              <p className="text-[10px] text-slate-400">Product</p>
              <p className="font-medium text-slate-200">{feedback.product_name || feedback.product_id}</p>
            </div>
            <div>
              <p className="text-[10px] text-slate-400">Channel</p>
              <p className="font-medium text-slate-200">{feedback.channel_name || feedback.channel_id}</p>
            </div>
            <div>
              <p className="text-[10px] text-slate-400">Date</p>
              <p className="font-medium text-slate-200">{new Date(feedback.date).toLocaleDateString()}</p>
            </div>
          </div>

          {/* Text block */}
          <div>
            <label className="text-[11px] font-semibold text-slate-400 block mb-1">Feedback Statement</label>
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-sm leading-relaxed">
              "{feedback.text}"
            </div>
          </div>

          {/* AI Explanation & Confidence */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[11px] font-semibold text-slate-400">Predicted Sentiment</span>
                <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${getSentimentBadge(feedback.predicted_sentiment)}`}>
                  {feedback.predicted_sentiment} ({Math.round(feedback.confidence_score * 100)}%)
                </span>
              </div>
              <p className="text-slate-400 text-[11px] mt-1">{feedback.explanation || 'Analyzed via TF-IDF sentiment pipeline'}</p>
              <div className="mt-2 text-[10px] text-indigo-400">Review Status: {feedback.review_status}</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800">
              <span className="text-[11px] font-semibold text-slate-400 block mb-1.5">Extracted Themes</span>
              <div className="flex flex-wrap gap-1.5">
                {feedback.themes.map((th, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 font-medium text-[11px]"
                  >
                    {th}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Data Quality Issues if any */}
          {feedback.quality_issues && feedback.quality_issues.length > 0 && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300">
              <div className="flex items-center gap-1.5 font-semibold text-[11px]">
                <ShieldAlert className="h-4 w-4 text-rose-400" />
                Data Quality Flags
              </div>
              <ul className="list-disc list-inside mt-1 space-y-0.5 text-[11px]">
                {feedback.quality_issues.map((iss, i) => (
                  <li key={i}>{iss}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Analyst Correction Form */}
          <div className="border-t border-slate-800 pt-3">
            <h4 className="text-xs font-bold text-slate-200 mb-2 flex items-center gap-1.5">
              <Sparkles className="h-4 w-4 text-amber-400" />
              Manual Classification Override (Audited)
            </h4>
            <div className="grid grid-cols-4 gap-2 mb-2">
              {(['POSITIVE', 'NEGATIVE', 'NEUTRAL', 'MIXED'] as Sentiment[]).map((sent) => (
                <button
                  key={sent}
                  type="button"
                  onClick={() => setSelectedSentiment(sent)}
                  className={`py-1.5 rounded-lg border text-xs font-semibold transition-all ${
                    selectedSentiment === sent
                      ? 'border-indigo-500 bg-indigo-600 text-white shadow-md'
                      : 'border-slate-800 bg-slate-950 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {sent}
                </button>
              ))}
            </div>

            <input
              type="text"
              placeholder="Reason for correction (required for compliance audit trail)..."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-200 placeholder-slate-400 focus:border-indigo-500 focus:outline-hidden"
            />

            {successMsg && <p className="mt-2 text-xs text-emerald-400 font-medium">{successMsg}</p>}
            {errorMsg && <p className="mt-2 text-xs text-rose-400 font-medium">{errorMsg}</p>}

            <div className="mt-3 flex justify-end gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-1.5 rounded-lg border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800 text-xs font-medium"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={saving}
                onClick={handleSaveCorrection}
                className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-colors disabled:opacity-50"
              >
                {saving ? 'Recording Audit...' : 'Save Correction'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

