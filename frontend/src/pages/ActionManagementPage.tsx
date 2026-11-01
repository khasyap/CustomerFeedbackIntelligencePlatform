import React, { useState, useEffect } from 'react';
import {
  ListTodo, Plus, CheckCircle, Clock, AlertTriangle, XCircle,
  History, ArrowRight, ShieldCheck, ChevronRight
} from 'lucide-react';
import { api } from '../services/api';
import { ActionItem, ActionStatus, ActionHistoryItem, ThemeItem, ProductItem } from '../types';
import { CreateActionModal } from '../components/CreateActionModal';

export const ActionManagementPage: React.FC = () => {
  const [actions, setActions] = useState<ActionItem[]>([]);
  const [themes, setThemes] = useState<ThemeItem[]>([]);
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [loading, setLoading] = useState(true);

  // Modals
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [historyActionId, setHistoryActionId] = useState<string | null>(null);
  const [historyItems, setHistoryItems] = useState<ActionHistoryItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const fetchActions = async () => {
    setLoading(true);
    try {
      const [acts, th, prods] = await Promise.all([
        api.getActions(statusFilter),
        api.getThemes(),
        api.getProducts(),
      ]);
      setActions(acts);
      setThemes(th);
      setProducts(prods);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActions();
  }, [statusFilter]);

  const handleStatusTransition = async (actionId: string, nextStatus: ActionStatus) => {
    try {
      await api.updateAction(actionId, {
        status: nextStatus,
        change_reason: `Workflow transition to ${nextStatus}`
      });
      fetchActions();
    } catch (err: any) {
      alert(err.message || 'Transition error');
    }
  };

  const openHistory = async (actionId: string) => {
    setHistoryActionId(actionId);
    setLoadingHistory(true);
    try {
      const hist = await api.getActionHistory(actionId);
      setHistoryItems(hist);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const getStatusBadge = (status: ActionStatus) => {
    switch (status) {
      case 'OPEN':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'IN_PROGRESS':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'RESOLVED':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'CLOSED':
        return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
      case 'BLOCKED':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ListTodo className="h-5 w-5 text-indigo-400" />
            Service Action Item Management & Traceability
          </h2>
          <p className="text-xs text-slate-400">Strictly validated lifecycle states with immutable audit events</p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-slate-200 focus:border-indigo-500 focus:outline-hidden"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="RESOLVED">Resolved</option>
            <option value="CLOSED">Closed</option>
            <option value="BLOCKED">Blocked</option>
          </select>

          <button
            onClick={() => setIsCreateOpen(true)}
            className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Create Action
          </button>
        </div>
      </div>

      {/* Action Items List */}
      <div className="space-y-3">
        {actions.length === 0 ? (
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-12 text-center text-xs text-slate-400">
            No action items match the selected filter.
          </div>
        ) : (
          actions.map((act) => (
            <div
              key={act.action_id}
              className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm transition-all hover:border-slate-700"
            >
              <div className="flex flex-wrap items-start justify-between gap-3 border-b border-slate-800 pb-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs font-bold text-indigo-300 px-2 py-0.5 rounded bg-slate-950 border border-slate-800">
                    {act.action_id}
                  </span>
                  <div>
                    <h3 className="text-sm font-bold text-white">{act.theme_name} — {act.product_name}</h3>
                    <p className="text-[11px] text-slate-400">Owner: {act.owner} | Team: {act.assigned_team} | Due: {new Date(act.due_date).toLocaleDateString()}</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`px-2.5 py-0.5 rounded text-xs font-bold border ${getStatusBadge(act.status)}`}>
                    {act.status}
                  </span>
                  <button
                    onClick={() => openHistory(act.action_id)}
                    className="flex items-center gap-1 text-[11px] rounded bg-slate-800 px-2 py-1 text-slate-300 hover:bg-slate-700"
                  >
                    <History className="h-3.5 w-3.5" />
                    Audit Trail
                  </button>
                </div>
              </div>

              {/* Action Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-3 text-xs">
                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Identified Problem</span>
                  <p className="text-slate-200 leading-relaxed">{act.problem_description}</p>
                </div>
                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-indigo-400 block mb-1">Recommended Intervention</span>
                  <p className="text-slate-200 leading-relaxed">{act.recommended_action}</p>
                </div>
              </div>

              {/* Expected Impact and Valid Transition Controls */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs border-t border-slate-800/80">
                <div className="text-slate-400 text-[11px]">
                  <span className="font-semibold text-slate-300">Expected Outcome:</span> {act.expected_impact}
                </div>

                {/* Valid transition buttons */}
                <div className="flex items-center gap-1.5">
                  <span className="text-[11px] text-slate-400 mr-1">Move State:</span>
                  {act.status === 'OPEN' && (
                    <>
                      <button
                        onClick={() => handleStatusTransition(act.action_id, 'IN_PROGRESS')}
                        className="px-2.5 py-1 rounded bg-amber-600/20 text-amber-300 border border-amber-500/30 hover:bg-amber-600 hover:text-white transition-colors"
                      >
                        Start Work →
                      </button>
                      <button
                        onClick={() => handleStatusTransition(act.action_id, 'BLOCKED')}
                        className="px-2 py-1 rounded bg-rose-600/20 text-rose-300 border border-rose-500/30 hover:bg-rose-600 hover:text-white transition-colors"
                      >
                        Block
                      </button>
                    </>
                  )}
                  {act.status === 'IN_PROGRESS' && (
                    <>
                      <button
                        onClick={() => handleStatusTransition(act.action_id, 'RESOLVED')}
                        className="px-2.5 py-1 rounded bg-emerald-600/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-600 hover:text-white transition-colors"
                      >
                        Resolve ✓
                      </button>
                      <button
                        onClick={() => handleStatusTransition(act.action_id, 'BLOCKED')}
                        className="px-2 py-1 rounded bg-rose-600/20 text-rose-300 border border-rose-500/30 hover:bg-rose-600 hover:text-white transition-colors"
                      >
                        Block
                      </button>
                    </>
                  )}
                  {act.status === 'BLOCKED' && (
                    <button
                      onClick={() => handleStatusTransition(act.action_id, 'IN_PROGRESS')}
                      className="px-2.5 py-1 rounded bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-600 hover:text-white transition-colors"
                    >
                      Unblock to In-Progress
                    </button>
                  )}
                  {act.status === 'RESOLVED' && (
                    <>
                      <button
                        onClick={() => handleStatusTransition(act.action_id, 'CLOSED')}
                        className="px-2.5 py-1 rounded bg-slate-700 text-slate-200 border border-slate-600 hover:bg-slate-600 transition-colors"
                      >
                        Close Action
                      </button>
                      <button
                        onClick={() => handleStatusTransition(act.action_id, 'IN_PROGRESS')}
                        className="px-2 py-1 rounded bg-amber-600/20 text-amber-300 border border-amber-500/30 hover:bg-amber-600 hover:text-white transition-colors"
                      >
                        Reopen
                      </button>
                    </>
                  )}
                  {act.status === 'CLOSED' && (
                    <button
                      onClick={() => handleStatusTransition(act.action_id, 'IN_PROGRESS')}
                      className="px-2 py-1 rounded bg-amber-600/20 text-amber-300 border border-amber-500/30 hover:bg-amber-600 hover:text-white transition-colors"
                    >
                      Reopen
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Modal */}
      {isCreateOpen && (
        <CreateActionModal
          themes={themes}
          products={products}
          onClose={() => setIsCreateOpen(false)}
          onSuccess={() => fetchActions()}
        />
      )}

      {/* Audit History Modal */}
      {historyActionId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <History className="h-4 w-4 text-indigo-400" />
                Immutable State Audit Trail: {historyActionId}
              </h3>
              <button onClick={() => setHistoryActionId(null)} className="text-slate-400 hover:text-white">
                ✕
              </button>
            </div>

            <div className="mt-4 space-y-3 max-h-80 overflow-y-auto">
              {loadingHistory ? (
                <p className="text-xs text-slate-400 py-4 text-center">Loading audit log...</p>
              ) : historyItems.length === 0 ? (
                <p className="text-xs text-slate-400 py-4 text-center">No state changes recorded yet.</p>
              ) : (
                historyItems.map((h) => (
                  <div key={h.id} className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                    <div className="flex items-center justify-between text-[11px] mb-1">
                      <span className="font-semibold text-slate-300">{h.changed_by}</span>
                      <span className="text-slate-400">{new Date(h.change_timestamp).toLocaleString()}</span>
                    </div>
                    <div className="flex items-center gap-2 text-indigo-400 font-bold">
                      <span>{h.previous_state || 'CREATION'}</span>
                      <ArrowRight className="h-3 w-3" />
                      <span className="text-emerald-400">{h.new_state}</span>
                    </div>
                    {h.change_reason && <p className="text-[11px] text-slate-400 mt-1">{h.change_reason}</p>}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

