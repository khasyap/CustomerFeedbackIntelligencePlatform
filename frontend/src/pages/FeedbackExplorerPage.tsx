import React, { useState, useEffect } from 'react';
import {
  Search, Filter, ChevronLeft, ChevronRight, Eye, ShieldAlert,
  Sparkles, CheckCircle2, AlertCircle, RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { FeedbackItem, FeedbackResponse, ProductItem, ChannelItem, Sentiment } from '../types';
import { FeedbackDetailModal } from '../components/FeedbackDetailModal';

export const FeedbackExplorerPage: React.FC = () => {
  const [data, setData] = useState<FeedbackResponse | null>(null);
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [channels, setChannels] = useState<ChannelItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [selectedProduct, setSelectedProduct] = useState('');
  const [selectedChannel, setSelectedChannel] = useState('');
  const [selectedSentiment, setSelectedSentiment] = useState('');
  const [selectedSource, setSelectedSource] = useState('');
  const [selectedReviewStatus, setSelectedReviewStatus] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Drilldown modal state
  const [selectedFeedback, setSelectedFeedback] = useState<FeedbackItem | null>(null);

  const fetchFeedback = async () => {
    setLoading(true);
    try {
      const res = await api.getFeedback({
        search,
        product_id: selectedProduct,
        channel_id: selectedChannel,
        sentiment: selectedSentiment,
        feedback_type: selectedSource,
        review_status: selectedReviewStatus,
        page,
        page_size: pageSize
      });
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    Promise.all([api.getProducts(), api.getChannels()]).then(([prods, chans]) => {
      setProducts(prods);
      setChannels(chans);
    });
  }, []);

  useEffect(() => {
    fetchFeedback();
  }, [search, selectedProduct, selectedChannel, selectedSentiment, selectedSource, selectedReviewStatus, page]);

  const getSentimentBadge = (sent: string) => {
    switch (sent) {
      case 'POSITIVE':
        return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
      case 'NEGATIVE':
        return 'bg-rose-500/15 text-rose-400 border-rose-500/30';
      case 'MIXED':
        return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
      default:
        return 'bg-slate-500/15 text-slate-300 border-slate-500/30';
    }
  };

  return (
    <div className="space-y-4">
      {/* Header and Filter Controls */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-white">Searchable Feedback Explorer</h2>
            <p className="text-xs text-slate-400">Traceable audit records with predicted sentiments, themes, and source metadata</p>
          </div>
          <div className="text-xs font-semibold text-slate-400">
            {data ? `${data.total.toLocaleString()} Records Indexed` : 'Loading...'}
          </div>
        </div>

        {/* Filter controls row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-6 gap-2 text-xs">
          {/* Search */}
          <div className="relative md:col-span-2">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search feedback text, title, or ID..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 pl-8 pr-3 py-1.5 text-slate-200 placeholder-slate-400 focus:border-indigo-500 focus:outline-hidden"
            />
          </div>

          {/* Sentiment Filter */}
          <select
            value={selectedSentiment}
            onChange={(e) => {
              setSelectedSentiment(e.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1.5 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
          >
            <option value="">All Sentiments</option>
            <option value="POSITIVE">Positive</option>
            <option value="NEGATIVE">Negative</option>
            <option value="NEUTRAL">Neutral</option>
            <option value="MIXED">Mixed</option>
          </select>

          {/* Product Filter */}
          <select
            value={selectedProduct}
            onChange={(e) => {
              setSelectedProduct(e.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1.5 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
          >
            <option value="">All Products</option>
            {products.map((p) => (
              <option key={p.product_id} value={p.product_id}>
                {p.product_name}
              </option>
            ))}
          </select>

          {/* Channel Filter */}
          <select
            value={selectedChannel}
            onChange={(e) => {
              setSelectedChannel(e.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1.5 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
          >
            <option value="">All Channels</option>
            {channels.map((c) => (
              <option key={c.channel_id} value={c.channel_id}>
                {c.channel_name}
              </option>
            ))}
          </select>

          {/* Source Type Filter */}
          <select
            value={selectedSource}
            onChange={(e) => {
              setSelectedSource(e.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1.5 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
          >
            <option value="">All Sources</option>
            <option value="REVIEW">Reviews</option>
            <option value="SURVEY_RESPONSE">Surveys</option>
            <option value="SUPPORT_MESSAGE">Support Messages</option>
          </select>
        </div>
      </div>

      {/* Table view */}
      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 shadow-xl backdrop-blur-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="border-b border-slate-800 bg-slate-950/70 text-[11px] uppercase tracking-wider text-slate-400">
              <tr>
                <th className="px-4 py-3">Feedback ID & Source</th>
                <th className="px-4 py-3">Customer</th>
                <th className="px-4 py-3">Product & Channel</th>
                <th className="px-4 py-3">Feedback Statement</th>
                <th className="px-4 py-3">Sentiment & Score</th>
                <th className="px-4 py-3">Themes</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-normal">
              {loading && !data ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <RefreshCw className="mx-auto h-6 w-6 animate-spin text-indigo-400 mb-2" />
                    Loading feedback repository...
                  </td>
                </tr>
              ) : !data || data.items.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    No feedback records match the active filter criteria.
                  </td>
                </tr>
              ) : (
                data.items.map((item) => (
                  <tr
                    key={item.feedback_id}
                    className="hover:bg-slate-800/40 transition-colors cursor-pointer"
                    onClick={() => setSelectedFeedback(item)}
                  >
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="font-mono text-xs font-semibold text-indigo-300">
                        {item.feedback_id}
                      </div>
                      <div className="text-[10px] text-slate-400">{item.feedback_type}</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="font-medium text-slate-200">{item.customer_name}</div>
                      <div className="text-[10px] text-slate-400">{item.customer_segment}</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="font-medium text-slate-200">{item.product_name}</div>
                      <div className="text-[10px] text-slate-400">{item.channel_name}</div>
                    </td>
                    <td className="px-4 py-3 max-w-xs truncate" title={item.text}>
                      {item.text}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold border ${getSentimentBadge(item.predicted_sentiment)}`}>
                        {item.predicted_sentiment}
                      </span>
                      <div className="text-[10px] text-slate-400 mt-0.5">
                        Conf: {Math.round(item.confidence_score * 100)}%
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {item.themes.slice(0, 2).map((t, idx) => (
                          <span
                            key={idx}
                            className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-300 border border-slate-700 whitespace-nowrap"
                          >
                            {t}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {item.quality_issues && item.quality_issues.length > 0 ? (
                        <span className="flex items-center gap-1 text-[10px] text-rose-400 font-semibold" title={item.quality_issues.join(', ')}>
                          <ShieldAlert className="h-3.5 w-3.5 text-rose-400" />
                          Anomaly
                        </span>
                      ) : item.review_status === 'HUMAN_REVIEWED' ? (
                        <span className="text-[10px] text-indigo-400 font-medium">Audited</span>
                      ) : (
                        <span className="text-[10px] text-slate-400">Auto</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedFeedback(item);
                        }}
                        className="rounded-lg bg-slate-800 px-2.5 py-1 text-[11px] font-medium text-slate-300 hover:bg-indigo-600 hover:text-white transition-colors"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        {data && (
          <div className="flex items-center justify-between border-t border-slate-800 px-4 py-3 text-xs text-slate-400">
            <div>
              Showing page <span className="font-semibold text-white">{data.page}</span> of{' '}
              <span className="font-semibold text-white">{data.total_pages}</span> ({data.total.toLocaleString()} total records)
            </div>
            <div className="flex items-center gap-2">
              <button
                disabled={data.page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="rounded-lg border border-slate-800 p-1.5 text-slate-300 hover:bg-slate-800 disabled:opacity-40"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                disabled={data.page >= data.total_pages}
                onClick={() => setPage((p) => p + 1)}
                className="rounded-lg border border-slate-800 p-1.5 text-slate-300 hover:bg-slate-800 disabled:opacity-40"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Drill-down modal */}
      {selectedFeedback && (
        <FeedbackDetailModal
          feedback={selectedFeedback}
          onClose={() => setSelectedFeedback(null)}
          onCorrectionSuccess={() => fetchFeedback()}
        />
      )}
    </div>
  );
};
