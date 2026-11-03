import React, { useState, useEffect } from 'react';
import { Sparkles, ArrowRight, CheckCircle2, AlertOctagon, HelpCircle, Plus, ShieldAlert, Info } from 'lucide-react';
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

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-red-950/60 text-red-400 border-red-500/40';
      case 'HIGH':
        return 'bg-amber-950/60 text-amber-400 border-amber-500/40';
      case 'MEDIUM':
        return 'bg-sky-950/60 text-sky-400 border-sky-500/40';
      default:
        return 'bg-slate-900 text-slate-400 border-slate-700';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header and Formula Explanation Card */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-indigo-400" />
              Service Improvement Priority & Recommendation Engine
            </h2>
            <p className="text-xs text-slate-400">Algorithmic prioritization ranking themes and products by customer risk and business impact</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
              5-Factor Weighted Model (∑ = 100%)
            </span>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-300 border border-rose-500/20 flex items-center gap-1">
              <ShieldAlert className="h-3.5 w-3.5" />
              Critical Escalation Safeguard
            </span>
          </div>
        </div>

        {/* Severity vs Priority Conceptual Framework Callout */}
        <div className="rounded-lg border border-slate-800 bg-slate-950/90 p-3.5 text-xs text-slate-300 space-y-2">
          <div className="flex items-center gap-2 font-semibold text-indigo-300">
            <Info className="h-4 w-4 text-indigo-400 shrink-0" />
            <span>Severity vs. Priority Architecture Distinction</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-[11px] text-slate-400 pl-6">
            <div>
              <span className="font-bold text-slate-200 block mb-0.5">Inherent Defect Severity (Technical/Impact):</span>
              Measures the intrinsic potential damage of the failure (e.g. data loss, payment failure, security vulnerability), independent of report volume.
            </div>
            <div>
              <span className="font-bold text-slate-200 block mb-0.5">Operational Urgency Priority (Triage Rank):</span>
              Calculated across 5 weighted factors. An automated escalation safeguard guarantees that Critical-severity issues with significant dissatisfaction cannot be deprioritized by low volume.
            </div>
          </div>
        </div>

        {/* Formula display */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2 bg-slate-950/80 p-3 rounded-lg border border-slate-800 text-[11px]">
          <div className="border-r border-slate-800 pr-2">
            <span className="text-slate-400 block font-medium">35% Weight</span>
            <span className="font-semibold text-rose-400">Negative Sentiment Rate</span>
            <span className="text-[10px] text-slate-500 block">Dissatisfaction % in theme</span>
          </div>
          <div className="border-r border-slate-800 pr-2">
            <span className="text-slate-400 block font-medium">25% Weight</span>
            <span className="font-semibold text-indigo-300">Feedback Volume</span>
            <span className="text-[10px] text-slate-500 block">Total complaint density</span>
          </div>
          <div className="border-r border-slate-800 pr-2">
            <span className="text-slate-400 block font-medium">20% Weight</span>
            <span className="font-semibold text-amber-300">Issue Severity</span>
            <span className="text-[10px] text-slate-500 block">Critical: 100, High: 75, Med: 50</span>
          </div>
          <div className="border-r border-slate-800 pr-2">
            <span className="text-slate-400 block font-medium">10% Weight</span>
            <span className="font-semibold text-cyan-300">Recent Growth Rate</span>
            <span className="text-[10px] text-slate-500 block">7-day escalation trend</span>
          </div>
          <div>
            <span className="text-slate-400 block font-medium">10% Weight</span>
            <span className="font-semibold text-teal-300">Customer Impact</span>
            <span className="text-[10px] text-slate-500 block">Tier & ARR exposure</span>
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
                <th className="px-4 py-3">Inherent Severity</th>
                <th className="px-4 py-3">Theme & Product</th>
                <th className="px-4 py-3">Dissatisfaction & Factor Breakdown</th>
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
                      <div className="flex flex-col">
                        <span className="font-mono font-bold text-white text-sm">{item.priority_score}</span>
                        {item.escalation_applied && (
                          <span
                            title={item.escalation_reason || 'Escalated by Critical severity rule'}
                            className="inline-flex items-center gap-0.5 text-[9px] font-bold text-rose-400 bg-rose-950/50 px-1 rounded border border-rose-800"
                          >
                            <ShieldAlert className="h-2.5 w-2.5" /> ESCALATED
                          </span>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getPriorityBadge(item.priority_level)}`}>
                      {item.priority_level}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getSeverityBadge(item.severity)}`}>
                      {item.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-bold text-white">{item.theme_name}</div>
                    <div className="text-[11px] text-slate-400">{item.product_name}</div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="text-[11px] font-semibold text-rose-400">
                      {item.negative_rate}% Negative ({item.feedback_volume} complaints)
                    </div>
                    {/* Factor Breakdown pills */}
                    <div className="flex items-center gap-1.5 mt-1 text-[10px] text-slate-400 font-mono">
                      <span title={`Negative Sentiment Contribution (35%): ${item.negative_rate_score ?? 0} pts`} className="bg-slate-950 px-1 py-0.5 rounded border border-slate-800">
                        Neg: {item.negative_rate_score ?? 0}
                      </span>
                      <span title={`Volume Contribution (25%): ${item.volume_score ?? 0} pts`} className="bg-slate-950 px-1 py-0.5 rounded border border-slate-800">
                        Vol: {item.volume_score ?? 0}
                      </span>
                      <span title={`Severity Contribution (20%): ${item.severity_score ?? 0} pts`} className="bg-slate-950 px-1 py-0.5 rounded border border-slate-800">
                        Sev: {item.severity_score ?? 0}
                      </span>
                      <span title={`Growth Contribution (10%): ${item.growth_score ?? 0} pts`} className="bg-slate-950 px-1 py-0.5 rounded border border-slate-800">
                        Gro: {item.growth_score ?? 0}
                      </span>
                      <span title={`Impact Contribution (10%): ${item.customer_impact_factor ?? 0} pts`} className="bg-slate-950 px-1 py-0.5 rounded border border-slate-800">
                        Imp: {item.customer_impact_factor ?? 0}
                      </span>
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


