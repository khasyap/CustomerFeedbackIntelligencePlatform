import React, { useState, useEffect } from 'react';
import { Tag, Sparkles, AlertOctagon, TrendingDown, Layers, Search, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { ThemeMetricItem } from '../types';

export const ThemeIntelligencePage: React.FC = () => {
  const [themes, setThemes] = useState<ThemeMetricItem[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchThemes = async () => {
    setLoading(true);
    try {
      const data = await api.getThemeAnalytics();
      setThemes(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchThemes();
  }, []);

  const filteredThemes = themes.filter((t) =>
    t.theme_name.toLowerCase().includes(search.toLowerCase()) ||
    t.theme_id.toLowerCase().includes(search.toLowerCase())
  );

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'MEDIUM':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      default:
        return 'bg-slate-500/20 text-slate-300 border-slate-500/40';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm">
        <div>
          <h2 className="text-lg font-bold text-white">Theme Intelligence & Taxonomy Heatmap</h2>
          <p className="text-xs text-slate-400">18 multi-label NLP feedback themes with frequency, negative rates & affected products</p>
        </div>

        <div className="relative w-64">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search themes or IDs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-slate-800 bg-slate-950 pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-400 focus:border-indigo-500 focus:outline-hidden"
          />
        </div>
      </div>

      {/* Grid of Theme Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-full py-16 text-center text-slate-400">
            <RefreshCw className="mx-auto h-6 w-6 animate-spin text-indigo-400 mb-2" />
            Analyzing theme distributions...
          </div>
        ) : (
          filteredThemes.map((t) => (
            <div
              key={t.theme_id}
              className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm transition-all hover:border-slate-700 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <span className="font-mono text-[10px] text-indigo-400 font-semibold">{t.theme_id}</span>
                    <h3 className="text-sm font-bold text-white">{t.theme_name}</h3>
                  </div>
                  <div className="flex items-center gap-1.5">
                    {t.is_emerging && (
                      <span className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-semibold border border-amber-500/30">
                        <Sparkles className="h-2.5 w-2.5" /> Emerging
                      </span>
                    )}
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getSeverityBadge(t.severity)}`}>
                      {t.severity}
                    </span>
                  </div>
                </div>

                {/* Counts */}
                <div className="grid grid-cols-2 gap-2 my-3 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-400 block">Feedback Mentions</span>
                    <span className="text-sm font-bold text-white">{t.count.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Corpus Share</span>
                    <span className="text-sm font-bold text-indigo-300">{t.percentage}%</span>
                  </div>
                </div>

                {/* Negative sentiment rate bar */}
                <div className="space-y-1 mb-3">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-400">Negative Sentiment Rate</span>
                    <span className={`font-bold ${t.negative_rate > 35 ? 'text-rose-400' : 'text-slate-300'}`}>
                      {t.negative_rate}%
                    </span>
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        t.negative_rate > 40 ? 'bg-rose-500' : t.negative_rate > 25 ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.min(100, t.negative_rate)}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Problematic products & channels */}
              <div className="border-t border-slate-800 pt-3 text-[11px] space-y-1.5">
                <div>
                  <span className="text-slate-400 text-[10px] uppercase font-semibold">Problematic Products:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {t.problematic_products.length > 0 ? (
                      t.problematic_products.map((p, idx) => (
                        <span key={idx} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
                          {p}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-400 text-[10px]">No concentrated issues</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
