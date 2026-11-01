import React from 'react';
import {
  LayoutDashboard,
  Search,
  PieChart,
  Tag,
  TrendingUp,
  AlertTriangle,
  ListTodo,
  ShieldAlert,
  BrainCircuit,
  Database,
  Settings,
  Sparkles
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  exceptionCount?: number;
  openActionCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  exceptionCount = 0,
  openActionCount = 0
}) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'feedback', label: 'Feedback Explorer', icon: Search },
    { id: 'sentiment', label: 'Sentiment Analytics', icon: PieChart },
    { id: 'themes', label: 'Theme Intelligence', icon: Tag },
    { id: 'trends', label: 'Trend Detection', icon: TrendingUp },
    { id: 'priorities', label: 'Service Priorities', icon: Sparkles },
    { id: 'actions', label: 'Action Management', icon: ListTodo, badge: openActionCount },
    { id: 'quality', label: 'Data Quality', icon: ShieldAlert, badge: exceptionCount, badgeColor: 'bg-rose-500' },
    { id: 'evaluation', label: 'Model Evaluation', icon: BrainCircuit },
    { id: 'data', label: 'Data Management', icon: Database },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950/80 p-4 flex flex-col justify-between select-none">
      <div>
        <div className="flex items-center gap-3 px-2 py-4 mb-4 border-b border-slate-800">
          <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <BrainCircuit className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-sm tracking-wide text-white">YOTTA INTEL</h1>
            <p className="text-[10px] uppercase font-semibold text-indigo-400 tracking-wider">Feedback Platform</p>
          </div>
        </div>

        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 font-semibold shadow-sm'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`h-4 w-4 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge !== undefined && item.badge > 0 && (
                  <span
                    className={`px-1.5 py-0.5 text-[10px] font-bold rounded-full ${
                      item.badgeColor || 'bg-indigo-500'
                    } text-white`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      <div className="pt-4 border-t border-slate-800/80 px-2 text-[11px] text-slate-400">
        <div className="flex items-center justify-between mb-1">
          <span>Engine Status</span>
          <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span> Online
          </span>
        </div>
        <p className="text-[10px] text-slate-400">Seed: 20261022 | v2.0.0</p>
      </div>
    </aside>
  );
};
