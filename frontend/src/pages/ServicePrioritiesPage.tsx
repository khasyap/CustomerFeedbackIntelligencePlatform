import React, { useState, useEffect } from 'react';
import { Sparkles, ArrowRight, CheckCircle2, AlertOctagon, HelpCircle, Plus } from 'lucide-react';
import { api } from '../services/api';
import { ServicePriorityItem, ThemeItem, ProductItem } from '../types';
import { CreateActionModal } from '../components/CreateActionModal';

export const ServicePrioritiesPage: React.FC = () => {
  const [priorities, setPriorities] = useState<ServicePriorityItem[]>([]);
  const [themes, setThemes] = useState<ThemeItem[]>([]);
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal state
  const [modalItem, setModalItem] = useState<ServicePriorityItem | null>(null);

  const fetchPriorities = async () => {
    setLoading(true);
    try {
      const [pr, th, prods] = await Promise.all([
        api.getPriorities(15),
        api.getThemes(),
        api.getProducts(),
      ]);
      setPriorities(pr);
      setThemes(th);
      setProducts(prods);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPriorities();
  }, []);

  const getPriorityBadge = (lvl: string) => {
    switch (lvl) {
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
      {/* Header and Formula Explanation Card */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-sm space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-indigo-400" />
              Service Improvement Priority & Recommendation Engine
            </h2>
            <p className="text-xs text-slate-400">Algorithmic prioritization ranking themes and products by customer risk and business impact</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
            5-Factor Weighted Model
          </span>
        </div>

        {/* Formula display */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 bg-slate-950/80 p-3 rounded-lg border border-slate-800 text-[11px]">
          <div className="border-r border-slate-800 pr-2">
            <span className="text-slate-400 block font-medium">35% Weight</span>
            <span className="font-semibold text-rose-400">Negative Sentiment Rate</span>
          </div>
          <div className="border-r border-slate-800 pr-2">
            <span className="text-slate-400 block font-medium">25% Weight</span>
            <span className="font-semibold text-indigo-300">Feedback Volume</span>
          </div>
          <div className="border-r border-slate-800 pr-2">
            <span className="text-slate-400 block font-medium">20% Weight</span>
            <span className="font-semibold text-amber-300">Issue Severity</span>
          </div>
          <div className="border-r border-slate-800 pr-2">
            <span className="text-slate-400 block font-medium">10% Weight</span>
            <span className="font-semibold text-cyan-300">Recent Growth Rate</span>
          </div>
          <div>
            <span className="text-slate-400 block font-medium">10% Weight</span>
            <span className="font-semibold text-teal-300">Customer Impact</span>
          </div>
        </div>
      </div>

      {/* Priorities List Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 shadow-xl backdrop-blur-sm overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-bold text-white">Ranked Service Improvement Opportunities</h3>
          <span className="text-xs text-slate-400">Top {priorities.length} Ranked Interventions</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/70 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Rank & Score</th>
                <th className="px-4 py-3">Priority Level</th>
                <th className="px-4 py-3">Theme & Product</th>
                <th className="px-4 py-3">Dissatisfaction Metrics</th>
                <th className="px-4 py-3">Actionable Recommendation</th>
                <th className="px-4 py-3">Assigned Team</th>
                <th className="px-4 py-3 text-right">Initiative</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {priorities.map((item) => (
                <tr key={`${item.theme_id}-${item.product_id}`} className="hover:bg-slate-800/40">
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-slate-800 font-bold text-xs text-indigo-300">
                        #{item.rank}
                      </span>
                      <span className="font-mono font-bold text-white text-sm">{item.priority_score}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getPriorityBadge(item.priority_level)}`}>
                      {item.priority_level}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-bold text-white">{item.theme_name}</div>
                    <div className="text-[11px] text-slate-400">{item.product_name}</div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="text-[11px] font-semibold text-rose-400">
                      {item.negative_rate}% Negative
                    </div>
                    <div className="text-[10px] text-slate-400">
                      {item.feedback_volume} complaints | {item.severity}
                    </div>
                  </td>
                  <td className="px-4 py-3 max-w-sm">
                    <p className="text-slate-200 text-xs leading-relaxed">{item.suggested_action}</p>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className="rounded bg-slate-800 px-2 py-1 text-[11px] font-medium text-slate-300">
                      {item.assigned_team}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right whitespace-nowrap">
                    {item.existing_action_id ? (
                      <span className="inline-flex items-center gap-1 rounded-md bg-emerald-500/10 px-2 py-1 text-[11px] font-medium text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="h-3 w-3" />
                        {item.existing_action_id} ({item.existing_action_status})
                      </span>
                    ) : (
                      <button
                        onClick={() => setModalItem(item)}
                        className="inline-flex items-center gap-1 rounded-lg bg-indigo-600 px-2.5 py-1 text-[11px] font-semibold text-white hover:bg-indigo-500 transition-colors"
                      >
                        <Plus className="h-3.5 w-3.5" />
                        Provision Action
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Provision Action Modal */}
      {modalItem && (
        <CreateActionModal
          initialThemeId={modalItem.theme_id}
          initialProductId={modalItem.product_id}
          initialPriority={modalItem.priority_level}
          initialAction={modalItem.suggested_action}
          initialTeam={modalItem.assigned_team}
          themes={themes}
          products={products}
          onClose={() => setModalItem(null)}
          onSuccess={() => fetchPriorities()}
        />
      )}
    </div>
  );
};
