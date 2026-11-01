import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { RefreshCw, TrendingUp, TrendingDown, Layers, Smartphone } from 'lucide-react';
import { api } from '../services/api';
import { SentimentBreakdownItem, OverviewMetrics } from '../types';

export const SentimentAnalyticsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<OverviewMetrics | null>(null);
  const [breakdown, setBreakdown] = useState<SentimentBreakdownItem[]>([]);
  const [groupBy, setGroupBy] = useState<'product' | 'channel'>('product');
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [ov, bd] = await Promise.all([
        api.getOverview(),
        api.getSentimentBreakdown(groupBy),
      ]);
      setMetrics(ov);
      setBreakdown(bd.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [groupBy]);

  const donutData = metrics ? [
    { name: 'Positive', value: metrics.sentiment_distribution['POSITIVE'] || 0, color: '#10b981' },
    { name: 'Negative', value: metrics.sentiment_distribution['NEGATIVE'] || 0, color: '#f43f5e' },
    { name: 'Neutral', value: metrics.sentiment_distribution['NEUTRAL'] || 0, color: '#64748b' },
    { name: 'Mixed', value: metrics.sentiment_distribution['MIXED'] || 0, color: '#f59e0b' },
  ] : [];

  const chartData = breakdown.slice(0, 10).map((b) => ({
    name: b.name.length > 18 ? b.name.substring(0, 16) + '...' : b.name,
    Positive: b.positive,
    Negative: b.negative,
    Neutral: b.neutral,
    Mixed: b.mixed,
    netScore: b.net_sentiment_score
  }));

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm">
        <div>
          <h2 className="text-lg font-bold text-white">Sentiment Analytics & Net Sentiment Score (NSS)</h2>
          <p className="text-xs text-slate-400">Holistic emotional sentiment evaluation and comparative product rankings</p>
        </div>
        <div className="flex items-center gap-2 rounded-lg bg-slate-950 p-1 border border-slate-800 text-xs">
          <button
            onClick={() => setGroupBy('product')}
            className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
              groupBy === 'product' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            By Product
          </button>
          <button
            onClick={() => setGroupBy('channel')}
            className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
              groupBy === 'channel' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            By Channel
          </button>
        </div>
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Global Distribution */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <h3 className="text-sm font-bold text-white mb-1">Global Sentiment Distribution</h3>
          <p className="text-xs text-slate-400 mb-4">Total processed customer signals</p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={donutData} cx="50%" cy="50%" innerRadius={65} outerRadius={90} paddingAngle={4} dataKey="value">
                  {donutData.map((e, idx) => (
                    <Cell key={idx} fill={e.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 border-t border-slate-800 pt-3 text-xs">
            {donutData.map((d) => (
              <div key={d.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full" style={{ backgroundColor: d.color }}></span>
                  <span className="text-slate-300">{d.name}</span>
                </div>
                <span className="font-bold text-white">{d.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Stacked Sentiment Comparison Chart */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white">Sentiment Breakdown by {groupBy === 'product' ? 'Product' : 'Channel'}</h3>
              <p className="text-xs text-slate-400">Comparative volume and polarity composition</p>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} angle={-25} textAnchor="end" />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                <Bar dataKey="Positive" stackId="a" fill="#10b981" />
                <Bar dataKey="Neutral" stackId="a" fill="#64748b" />
                <Bar dataKey="Mixed" stackId="a" fill="#f59e0b" />
                <Bar dataKey="Negative" stackId="a" fill="#f43f5e" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Detailed NSS Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 shadow-xl backdrop-blur-sm overflow-hidden">
        <div className="p-4 border-b border-slate-800">
          <h3 className="text-sm font-bold text-white">Net Sentiment Score (NSS) Ranking Table</h3>
          <p className="text-xs text-slate-400">Formula: Net Sentiment Score = ((Positive - Negative) / Total) × 100</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/70 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">{groupBy === 'product' ? 'Product Name' : 'Channel Name'}</th>
                <th className="px-4 py-3">Total Volume</th>
                <th className="px-4 py-3 text-emerald-400">Positive</th>
                <th className="px-4 py-3 text-rose-400">Negative</th>
                <th className="px-4 py-3 text-slate-400">Neutral</th>
                <th className="px-4 py-3 text-amber-400">Mixed</th>
                <th className="px-4 py-3">Net Sentiment Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {breakdown.map((item, idx) => {
                const isPositive = item.net_sentiment_score > 0;
                return (
                  <tr key={idx} className="hover:bg-slate-800/40">
                    <td className="px-4 py-3 font-medium text-white">{item.name}</td>
                    <td className="px-4 py-3">{item.total.toLocaleString()}</td>
                    <td className="px-4 py-3 text-emerald-400 font-semibold">{item.positive}</td>
                    <td className="px-4 py-3 text-rose-400 font-semibold">{item.negative}</td>
                    <td className="px-4 py-3 text-slate-400">{item.neutral}</td>
                    <td className="px-4 py-3 text-amber-400">{item.mixed}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center gap-1 font-bold ${
                          isPositive ? 'text-emerald-400' : 'text-rose-400'
                        }`}
                      >
                        {isPositive ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
                        {item.net_sentiment_score > 0 ? `+${item.net_sentiment_score}` : item.net_sentiment_score}%
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

