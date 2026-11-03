import React, { useState, useEffect } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { api } from '../services/api';
import { TrendTimePoint, AnomalyShiftAlert, ProductItem } from '../types';

export const TrendDetectionPage: React.FC = () => {
  const [trends, setTrends] = useState<TrendTimePoint[]>([]);
  const [alerts, setAlerts] = useState<AnomalyShiftAlert[]>([]);
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [days, setDays] = useState(90);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [tr, al, prods] = await Promise.all([
        api.getTrends(selectedProduct, undefined, days),
        api.getAlerts(),
        api.getProducts(),
      ]);
      setTrends(tr);
      setAlerts(al);
      setProducts(prods);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedProduct, days]);

  // Baseline vs Current Period Calculations (First half vs Second half of selected window)
  const midpoint = Math.floor(trends.length / 2);
  const baselineSlice = trends.slice(0, midpoint);
  const currentSlice = trends.slice(midpoint);

  const baselineTotal = baselineSlice.reduce((acc, t) => acc + t.total, 0);
  const baselineNeg = baselineSlice.reduce((acc, t) => acc + t.negative, 0);
  const baselineRate = baselineTotal > 0 ? (baselineNeg / baselineTotal) * 100 : 0;

  const currentTotal = currentSlice.reduce((acc, t) => acc + t.total, 0);
  const currentNeg = currentSlice.reduce((acc, t) => acc + t.negative, 0);
  const currentRate = currentTotal > 0 ? (currentNeg / currentTotal) * 100 : 0;

  const totalFilteredVolume = trends.reduce((acc, t) => acc + t.total, 0);
  const ppChange = currentRate - baselineRate;
  const relChange = baselineRate > 0 ? ((currentRate - baselineRate) / baselineRate) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm">
        <div>
          <h2 className="text-lg font-bold text-white">Sentiment Trend & Anomaly Shift Detection</h2>
          <p className="text-xs text-slate-400">Time-series intelligence tracking sudden complaint surges and sentiment inflections</p>
        </div>

        <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-xs">
          <select
            value={selectedProduct}
            onChange={(e) => setSelectedProduct(e.target.value)}
            className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
          >
            <option value="">All Products (Platform-Wide)</option>
            {products.map((p) => (
              <option key={p.product_id} value={p.product_id}>
                {p.product_name}
              </option>
            ))}
          </select>

          <select
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value) || 90)}
            className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
          >
            <option value={30}>Last 30 Days</option>
            <option value={60}>Last 60 Days</option>
            <option value={90}>Last 90 Days</option>
            <option value={180}>Last 180 Days</option>
          </select>

          <button
            onClick={fetchData}
            disabled={loading}
            className="rounded-lg bg-slate-800 p-2 text-slate-300 hover:bg-slate-700 hover:text-white disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Date Window & Trend Metrics Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm">
          <span className="text-[10px] uppercase font-bold text-slate-400 block">Filtered Date Window</span>
          <span className="text-sm font-bold text-white mt-1 block">
            {trends.length > 0 ? `${trends[0].date} → ${trends[trends.length - 1].date}` : `${days} Days Range`}
          </span>
          <span className="text-[11px] text-indigo-300 mt-0.5 block font-mono">
            {totalFilteredVolume.toLocaleString()} feedback items
          </span>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm">
          <span className="text-[10px] uppercase font-bold text-slate-400 block">Baseline Dissatisfaction</span>
          <span className="text-xl font-bold text-slate-200 mt-1 block">
            {baselineRate.toFixed(1)}%
          </span>
          <span className="text-[11px] text-slate-400 mt-0.5 block">
            Baseline period (first {midpoint} days)
          </span>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm">
          <span className="text-[10px] uppercase font-bold text-slate-400 block">Current Dissatisfaction</span>
          <span className={`text-xl font-bold mt-1 block ${currentRate > baselineRate ? 'text-rose-400' : 'text-emerald-400'}`}>
            {currentRate.toFixed(1)}%
          </span>
          <span className="text-[11px] text-slate-400 mt-0.5 block">
            Current period (recent {trends.length - midpoint} days)
          </span>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm">
          <span className="text-[10px] uppercase font-bold text-slate-400 block">Trend Delta (PP vs Relative)</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className={`text-xl font-bold ${ppChange > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {ppChange >= 0 ? '+' : ''}{ppChange.toFixed(1)} pp
            </span>
            <span className={`text-xs font-semibold ${relChange > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
              ({relChange >= 0 ? '+' : ''}{relChange.toFixed(1)}% rel)
            </span>
          </div>
          <span className="text-[11px] text-slate-400 mt-0.5 block">
            Percentage-point vs Relative increase
          </span>
        </div>
      </div>

      {/* Main Trend Line Chart */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white">Chronological Polarity Trajectory</h3>
            <p className="text-xs text-slate-400">Daily frequency of Positive, Negative, Neutral and Mixed customer feedback</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20">
              Shift Threshold: ≥ 20% Surge
            </span>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trends} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Line type="monotone" dataKey="positive" stroke="#10b981" strokeWidth={2} dot={false} name="Positive" />
              <Line type="monotone" dataKey="negative" stroke="#f43f5e" strokeWidth={2.5} dot={false} name="Negative" />
              <Line type="monotone" dataKey="neutral" stroke="#64748b" strokeWidth={1.5} dot={false} name="Neutral" />
              <Line type="monotone" dataKey="mixed" stroke="#f59e0b" strokeWidth={1.5} dot={false} name="Mixed" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detected Sentiment Shift Alerts */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              Detected Sentiment-Shift Alerts ({alerts.length})
            </h3>
            <p className="text-xs text-slate-400">Triggered when negative dissatisfaction rises &gt; 20% against previous comparable period</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {alerts.length === 0 ? (
            <div className="col-span-full py-8 text-center text-xs text-slate-400">
              No critical sentiment surges currently detected. All products and channels within normal baseline thresholds.
            </div>
          ) : (
            alerts.map((al) => (
              <div
                key={al.alert_id}
                className="rounded-xl border border-slate-800 bg-slate-950 p-4 shadow-sm flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <span className="font-mono text-[10px] text-slate-400 font-semibold">{al.alert_id}</span>
                      <h4 className="text-sm font-bold text-white">{al.dimension_type}: {al.dimension_id}</h4>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                      {al.severity} SPIKE
                    </span>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed mb-3">{al.summary}</p>
                </div>

                <div className="grid grid-cols-3 gap-2 bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-400 block">Baseline Rate</span>
                    <span className="font-semibold text-slate-200">{Math.round(al.baseline_negative_rate * 100)}%</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Current Rate</span>
                    <span className="font-semibold text-rose-400">{Math.round(al.current_negative_rate * 100)}%</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Surge Ratio</span>
                    <span className="font-bold text-rose-400">+{al.percentage_change}%</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
