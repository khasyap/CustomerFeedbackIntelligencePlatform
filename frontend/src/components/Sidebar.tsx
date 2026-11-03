import React, { useEffect } from 'react';
import {
  LayoutDashboard,
  Search,
  PieChart,
  Tag,
  TrendingUp,
  ListTodo,
  ShieldAlert,
  BrainCircuit,
  Database,
  Settings,
  Sparkles,
  PanelLeftClose,
  PanelLeftOpen,
  X
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  exceptionCount?: number;
  openActionCount?: number;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  isMobileOpen: boolean;
  onMobileClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  exceptionCount = 0,
  openActionCount = 0,
  isCollapsed,
  onToggleCollapse,
  isMobileOpen,
  onMobileClose
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

  // Close mobile drawer on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isMobileOpen) {
        onMobileClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isMobileOpen, onMobileClose]);

  return (
    <>
      {/* ========================================================================= */}
      {/* 1. DESKTOP SIDEBAR (Visible on lg and larger screens)                     */}
      {/* ========================================================================= */}
      <aside
        className={`hidden lg:flex flex-col justify-between border-r border-slate-800 bg-slate-950/95 transition-all duration-300 ease-in-out select-none shrink-0 z-30 ${
          isCollapsed ? 'w-20 p-3' : 'w-64 p-4'
        }`}
      >
        <div>
          {/* Header */}
          {isCollapsed ? (
            <div className="flex flex-col items-center py-2.5 mb-3 border-b border-slate-800/80 gap-2">
              <div
                className="h-9 w-9 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20"
                title="YOTTA INTEL"
              >
                <BrainCircuit className="h-5 w-5 text-white" />
              </div>
              <button
                onClick={onToggleCollapse}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition-colors"
                title="Expand sidebar"
                aria-label="Expand sidebar"
              >
                <PanelLeftOpen className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center justify-between px-2 py-3 mb-3 border-b border-slate-800/80">
              <div className="flex items-center gap-3 min-w-0">
                <div className="h-9 w-9 shrink-0 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                  <BrainCircuit className="h-5 w-5 text-white" />
                </div>
                <div className="truncate">
                  <h1 className="font-bold text-sm tracking-wide text-white truncate">YOTTA INTEL</h1>
                  <p className="text-[10px] uppercase font-semibold text-indigo-400 tracking-wider">Feedback Platform</p>
                </div>
              </div>
              <button
                onClick={onToggleCollapse}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition-colors"
                title="Collapse sidebar"
                aria-label="Collapse sidebar"
              >
                <PanelLeftClose className="h-4 w-4" />
              </button>
            </div>
          )}

          {/* Navigation Items */}
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  title={isCollapsed ? item.label : undefined}
                  className={`relative w-full flex items-center ${
                    isCollapsed ? 'justify-center py-2.5 px-0' : 'justify-between px-3 py-2.5'
                  } rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 font-semibold shadow-sm'
                      : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className={`h-4 w-4 shrink-0 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                    {!isCollapsed && <span className="truncate">{item.label}</span>}
                  </div>
                  {item.badge !== undefined && item.badge > 0 && (
                    !isCollapsed ? (
                      <span
                        className={`px-1.5 py-0.5 text-[10px] font-bold rounded-full ${
                          item.badgeColor || 'bg-indigo-500'
                        } text-white`}
                      >
                        {item.badge}
                      </span>
                    ) : (
                      <span
                        className={`absolute top-1.5 right-1.5 h-2 w-2 rounded-full ${
                          item.badgeColor || 'bg-indigo-500'
                        } ring-2 ring-slate-950`}
                      />
                    )
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Desktop Footer Status */}
        <div className={`pt-3 border-t border-slate-800/80 ${isCollapsed ? 'text-center' : 'px-2'} text-[11px] text-slate-400`}>
          {!isCollapsed ? (
            <>
              <div className="flex items-center justify-between mb-1">
                <span>Engine Status</span>
                <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
                  <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span> Online
                </span>
              </div>
              <p className="text-[10px] text-slate-400">Seed: 20261022 | v2.0.0</p>
            </>
          ) : (
            <div className="flex justify-center" title="Engine Status: Online (Seed: 20261022)">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
            </div>
          )}
        </div>
      </aside>

      {/* ========================================================================= */}
      {/* 2. MOBILE DRAWER OVERLAY & SLIDE-OUT MENU (Visible below lg)              */}
      {/* ========================================================================= */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-black/75 backdrop-blur-xs z-40 lg:hidden transition-opacity duration-300"
          onClick={onMobileClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] bg-slate-950 border-r border-slate-800 p-4 flex flex-col justify-between shadow-2xl transition-transform duration-300 ease-in-out lg:hidden ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div>
          {/* Mobile Drawer Header with Close Button */}
          <div className="flex items-center justify-between pb-3.5 mb-3 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <BrainCircuit className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-sm tracking-wide text-white">YOTTA INTEL</h1>
                <p className="text-[10px] uppercase font-semibold text-indigo-400 tracking-wider">Feedback Platform</p>
              </div>
            </div>
            <button
              onClick={onMobileClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition-colors"
              aria-label="Close navigation"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Mobile Navigation List */}
          <nav className="space-y-1 overflow-y-auto max-h-[calc(100vh-180px)] pr-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onSelectTab(item.id);
                    onMobileClose();
                  }}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 font-semibold shadow-sm'
                      : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`h-4 w-4 shrink-0 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                    <span className="text-left">{item.label}</span>
                  </div>
                  {item.badge !== undefined && item.badge > 0 && (
                    <span
                      className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${
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

        {/* Mobile Drawer Footer */}
        <div className="pt-3 border-t border-slate-800/80 px-2 text-[11px] text-slate-400">
          <div className="flex items-center justify-between mb-1">
            <span>Engine Status</span>
            <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span> Online
            </span>
          </div>
          <p className="text-[10px] text-slate-400">Seed: 20261022 | v2.0.0</p>
        </div>
      </aside>
    </>
  );
};
