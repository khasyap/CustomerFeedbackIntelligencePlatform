import React, { useState } from 'react';
import { X, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { ThemeItem, ProductItem, PriorityLevel } from '../types';

interface CreateActionModalProps {
  initialThemeId?: string;
  initialProductId?: string;
  initialPriority?: PriorityLevel;
  initialProblem?: string;
  initialAction?: string;
  initialTeam?: string;
  themes: ThemeItem[];
  products: ProductItem[];
  onClose: () => void;
  onSuccess: () => void;
}

export const CreateActionModal: React.FC<CreateActionModalProps> = ({
  initialThemeId = '',
  initialProductId = '',
  initialPriority = 'HIGH',
  initialProblem = '',
  initialAction = '',
  initialTeam = 'Operations',
  themes,
  products,
  onClose,
  onSuccess
}) => {
  const [themeId, setThemeId] = useState(initialThemeId || (themes[0]?.theme_id || ''));
  const [productId, setProductId] = useState(initialProductId || (products[0]?.product_id || ''));
  const [priorityLevel, setPriorityLevel] = useState<PriorityLevel>(initialPriority);
  const [priorityScore, setPriorityScore] = useState<number>(75);
  const [problemDescription, setProblemDescription] = useState(initialProblem);
  const [recommendedAction, setRecommendedAction] = useState(initialAction);
  const [assignedTeam, setAssignedTeam] = useState(initialTeam);
  const [owner, setOwner] = useState('Team Lead');
  const [expectedImpact, setExpectedImpact] = useState('Reduce customer dissatisfaction by 30%');
  const [daysToDue, setDaysToDue] = useState(21);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const dueDate = new Date();
      dueDate.setDate(dueDate.getDate() + daysToDue);

      await api.createAction({
        theme_id: themeId,
        product_id: productId,
        priority_score: priorityScore,
        priority_level: priorityLevel,
        problem_description: problemDescription,
        recommended_action: recommendedAction,
        assigned_team: assignedTeam,
        owner,
        expected_impact: expectedImpact,
        due_date: dueDate.toISOString(),
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to create action item');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
      <div className="w-full max-w-xl rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl overflow-y-auto max-h-[90vh]">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-indigo-600/20 p-2 text-indigo-400">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Create Service Improvement Action</h3>
              <p className="text-[11px] text-slate-400">Assign accountable team, problem resolution, and expected outcome</p>
            </div>
          </div>
          <button onClick={onClose} className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 space-y-3.5 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 mb-1">Related Theme</label>
              <select
                value={themeId}
                onChange={(e) => setThemeId(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
              >
                {themes.map((t) => (
                  <option key={t.theme_id} value={t.theme_id}>
                    {t.theme_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 mb-1">Related Product</label>
              <select
                value={productId}
                onChange={(e) => setProductId(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
              >
                {products.map((p) => (
                  <option key={p.product_id} value={p.product_id}>
                    {p.product_name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 mb-1">Priority Level</label>
              <select
                value={priorityLevel}
                onChange={(e) => setPriorityLevel(e.target.value as PriorityLevel)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
              >
                <option value="CRITICAL">CRITICAL</option>
                <option value="HIGH">HIGH</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="LOW">LOW</option>
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 mb-1">Assigned Team</label>
              <select
                value={assignedTeam}
                onChange={(e) => setAssignedTeam(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
              >
                <option value="Operations">Operations</option>
                <option value="Engineering">Engineering</option>
                <option value="Support">Support</option>
                <option value="Product">Product</option>
                <option value="Finance">Finance</option>
                <option value="Marketing">Marketing</option>
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 mb-1">Owner / Lead</label>
              <input
                type="text"
                value={owner}
                onChange={(e) => setOwner(e.target.value)}
                required
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-400 mb-1">Problem Description</label>
            <textarea
              rows={2}
              value={problemDescription}
              onChange={(e) => setProblemDescription(e.target.value)}
              required
              placeholder="Describe the root friction observed in feedback records..."
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-400 mb-1">Recommended Action</label>
            <textarea
              rows={2}
              value={recommendedAction}
              onChange={(e) => setRecommendedAction(e.target.value)}
              required
              placeholder="Actionable steps for operations or engineering team..."
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 mb-1">Expected Impact</label>
              <input
                type="text"
                value={expectedImpact}
                onChange={(e) => setExpectedImpact(e.target.value)}
                required
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 mb-1">Timeline (Days to Due)</label>
              <input
                type="number"
                min={1}
                max={90}
                value={daysToDue}
                onChange={(e) => setDaysToDue(parseInt(e.target.value) || 14)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
              />
            </div>
          </div>

          {error && <p className="text-xs text-rose-400">{error}</p>}

          <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-800 px-3 py-1.5 text-slate-400 hover:bg-slate-800 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-indigo-600 px-4 py-1.5 font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Action Item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
