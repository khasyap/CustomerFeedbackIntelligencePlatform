import React from 'react';
import { Settings, Shield, Sliders, Server, Lock, Cpu, Database } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow-xl backdrop-blur-sm">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Settings className="h-5 w-5 text-indigo-400" />
          System Settings & Platform Architecture Configuration
        </h2>
        <p className="text-xs text-slate-400">Environment parameters, NLP hyperparameters, and privacy policies</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
        {/* NLP & Scoring Configuration */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Sliders className="h-4 w-4 text-indigo-400" />
            Priority Engine & Threshold Weights
          </h3>

          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-slate-300">Negative Sentiment Rate Weight</span>
                <span className="font-mono text-indigo-300 font-bold">35%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: '35%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-slate-300">Feedback Volume Weight</span>
                <span className="font-mono text-indigo-300 font-bold">25%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: '25%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-slate-300">Issue Severity Weight</span>
                <span className="font-mono text-indigo-300 font-bold">20%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: '20%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-slate-300">Recent Growth Rate Weight</span>
                <span className="font-mono text-indigo-300 font-bold">10%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: '10%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-slate-300">Customer Impact Weight</span>
                <span className="font-mono text-indigo-300 font-bold">10%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: '10%' }}></div>
              </div>
            </div>
          </div>

          <div className="border-t border-slate-800 pt-3 space-y-2 text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-400">High Confidence Threshold:</span>
              <span className="font-mono text-emerald-400 font-bold">≥ 0.75 (Auto-Classify)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Low Confidence Review Threshold:</span>
              <span className="font-mono text-amber-400 font-bold">&lt; 0.45 (Human Review)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Anomaly Shift Spike Threshold:</span>
              <span className="font-mono text-rose-400 font-bold">≥ +20% Dissatisfaction</span>
            </div>
          </div>
        </div>

        {/* Security and Privacy Compliance */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Shield className="h-4 w-4 text-emerald-400" />
            Security, Privacy & Compliance Controls
          </h3>

          <div className="space-y-3">
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-white">Automated PII Masking</span>
                <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">
                  ACTIVE
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                SSNs, credit cards, telephone numbers, and email patterns are automatically scrubbed from inference features.
              </p>
            </div>

            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-white">Ground-Truth Isolation</span>
                <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">
                  ENFORCED
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Ground-truth evaluation labels are strictly partitioned in data/ground_truth/ and never used as model inputs.
              </p>
            </div>

            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-white">Immutable Lifecycle Audit Log</span>
                <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">
                  RECORDING
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                All action transitions and analyst corrections are preserved in StateChangeEvent without overwriting historical records.
              </p>
            </div>
          </div>
        </div>

        {/* Runtime Environment Info */}
        <div className="col-span-full rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <Server className="h-4 w-4 text-indigo-400" />
            Runtime Environment & Service Endpoints
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Random Seed</span>
              <p className="font-mono text-sm font-bold text-indigo-300 mt-0.5">20261022</p>
            </div>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Database Engine</span>
              <p className="font-mono text-sm font-bold text-emerald-300 mt-0.5">SQLAlchemy / SQLite</p>
            </div>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Backend Framework</span>
              <p className="font-mono text-sm font-bold text-teal-300 mt-0.5">FastAPI & Pydantic v2</p>
            </div>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Frontend Client</span>
              <p className="font-mono text-sm font-bold text-purple-300 mt-0.5">React 19 & Tailwind v4</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

