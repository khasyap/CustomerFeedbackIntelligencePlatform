import React, { useState, useEffect } from 'react';
import {
  MessageSquare, Star, MessageCircle, HelpCircle,
  AlertOctagon, CheckCircle2, ShieldAlert, Sparkles, Filter, RefreshCw
} from 'lucide-react';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, AreaChart, Area
} from 'recharts';
import { StatCard } from '../components/StatCard';
import { api } from '../services/api';
import { OverviewMetrics, ThemeMetricItem, TrendTimePoint, ProductItem, ChannelItem } from '../types';

export const OverviewPage: React.FC = () => {
  const [metrics, setMetrics] = useState<OverviewMetrics | null>(null);
  const [themes, setThemes] = useState<ThemeMetricItem[]>([]);
  const [trends, setTrends] = useState<TrendTimePoint[]>([]);
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [channels, setChannels] = useState<ChannelItem[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<string>('');
  const [selectedChannel, setSelectedChannel] = useState<string>('');
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [ov, th, tr, prods, chans] = await Promise.all([
        api.getOverview(selectedProduct, selectedChannel),
        api.getThemeAnalytics(),
        api.getTrends(selectedProduct, selectedChannel, 60),
        api.getProducts(),
        api.getChannels()
      ]);
      setMetrics(ov);
      setThemes(th);
      setTrends(tr);
      setProducts(prods);
      setChannels(chans);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedProduct, selectedChannel]);

  if (loading && !metrics) {
    return (
      <div className="flex h-96 items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  // Chart data
  const donutData = metrics ? [
    { name: 'Positive', value: metrics.sentiment_distribution['POSITIVE'] || 0, color: '#10b981' },
    { name: 'Negative', value: metrics.sentiment_distribution['NEGATIVE'] || 0, color: '#f43f5e' },
    { name: 'Neutral', value: metrics.sentiment_distribution['NEUTRAL'] || 0, color: '#64748b' },
    { name: 'Mixed', value: metrics.sentiment_distribution['MIXED'] || 0, color: '#f59e0b' },
  ] : [];

  const topThemesData = themes.slice(0, 7).map((t) => ({
    name: t.theme_name,
    count: t.count,
    negativeRate: t.negative_rate,
  }));

  return (
    <div className="space-y-6">
      {/* Top filter bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm">
        <div>
          <h2 className="text-lg font-bold text-white">Executive Intelligence Overview</h2>
          <p className="text-xs text-slate-400">Live consolidated feedback across surveys, reviews & support messages</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Filter className="h-3.5 w-3.5 text-indigo-400" />
            <span>Filters:</span>
          </div>

          <select
            value={selectedProduct}
            onChange={(e) => setSelectedProduct(e.target.value)}
            className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-slate-200 focus:border-indigo-500 focus:outline-hidden"
          >
            <option value="">All Products</option>
            {products.map((p) => (
              <option key={p.product_id} value={p.product_id}>
                {p.product_name}
              </option>
            ))}
          </select>

          <select
            value={selectedChannel}
            onChange={(e) => setSelectedChannel(e.target.value)}
            className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-slate-200 focus:border-indigo-500 focus:outline-hidden"
          >
            <option value="">All Channels</option>
            {channels.map((c) => (
              <option key={c.channel_id} value={c.channel_id}>
                {c.channel_name}
              </option>
            ))}
          </select>

          <button
            onClick={fetchData}
            className="rounded-lg bg-slate-800 p-2 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
            title="Refresh analytics"
          >
            <RefreshCw className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Feedback"
          value={metrics?.total_feedback.toLocaleString() || '0'}
          subtitle={`Reviews: ${metrics?.total_reviews.toLocaleString()} | Surveys: ${metrics?.total_surveys.toLocaleString()} | Messages: ${metrics?.total_support_messages.toLocaleString()}`}
          icon={<MessageSquare className="h-5 w-5" />}
          trend="+12%"
          trendType="positive"
        />
        <StatCard
          title="Positive Sentiment"
          value={`${metrics?.sentiment_percentages['POSITIVE'] || 0}%`}
          subtitle={`${(metrics?.sentiment_distribution['POSITIVE'] || 0).toLocaleString()} favorable responses`}
          icon={<Star className="h-5 w-5" />}
          trendType="positive"
          color="from-emerald-500/20 to-teal-500/20 border-emerald-500/30"
        />
        <StatCard
          title="Negative Dissatisfaction"
          value={`${metrics?.sentiment_percentages['NEGATIVE'] || 0}%`}
          subtitle={`${(metrics?.sentiment_distribution['NEGATIVE'] || 0).toLocaleString()} critical complaints`}
          icon={<AlertOctagon className="h-5 w-5" />}
          trend="+4.2%"
          trendType="negative"
          color="from-rose-500/20 to-red-500/20 border-rose-500/30"
        />
        <StatCard
          title="Critical Service Risks"
          value={metrics?.critical_issues_count || '0'}
          subtitle={`${metrics?.open_actions_count || 0} open action initiatives`}
          icon={<Sparkles className="h-5 w-5" />}
          trendType="negative"
          color="from-amber-500/20 to-orange-500/20 border-amber-500/30"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Donut Chart */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white">Sentiment Distribution</h3>
            <p className="text-xs text-slate-400">Classified across 4 distinct emotional polarity classes</p>
          </div>

          <div className="h-60 w-full my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={donutData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {donutData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs border-t border-slate-800 pt-3">
            {donutData.map((d) => (
              <div key={d.name} className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: d.color }}></span>
                <span className="text-slate-400">{d.name}:</span>
                <span className="font-bold text-white">{d.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Recurring Themes Bar Chart */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h3 className="text-sm font-bold text-white">Top Recurring Feedback Themes</h3>
              <p className="text-xs text-slate-400">Volume and severity distribution across feedback corpus</p>
            </div>
            <span className="text-xs px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-semibold border border-indigo-500/30">
              {themes.length} Themes Active
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topThemesData} layout="vertical" margin={{ top: 5, right: 30, left: 70, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" fontSize={11} />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={11} width={110} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} name="Feedback Mentions" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Chronological Trend Area Chart */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white">Customer Sentiment Trends (Timeline)</h3>
            <p className="text-xs text-slate-400">Chronological shifts in positive vs negative feedback</p>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-500"></span> Positive
            </span>
            <span className="flex items-center gap-1.5 text-rose-400">
              <span className="h-2 w-2 rounded-full bg-rose-500"></span> Negative
            </span>
          </div>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorPos" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorNeg" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
              />
              <Area type="monotone" dataKey="positive" stroke="#10b981" fillOpacity={1} fill="url(#colorPos)" name="Positive" />
              <Area type="monotone" dataKey="negative" stroke="#f43f5e" fillOpacity={1} fill="url(#colorNeg)" name="Negative" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

