import React, { useState, useEffect } from 'react';
import { Menu, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { Sidebar } from './components/Sidebar';
import { OverviewPage } from './pages/OverviewPage';
import { FeedbackExplorerPage } from './pages/FeedbackExplorerPage';
import { SentimentAnalyticsPage } from './pages/SentimentAnalyticsPage';
import { ThemeIntelligencePage } from './pages/ThemeIntelligencePage';
import { TrendDetectionPage } from './pages/TrendDetectionPage';
import { ServicePrioritiesPage } from './pages/ServicePrioritiesPage';
import { ActionManagementPage } from './pages/ActionManagementPage';
import { DataQualityPage } from './pages/DataQualityPage';
import { ModelEvaluationPage } from './pages/ModelEvaluationPage';
import { DataManagementPage } from './pages/DataManagementPage';
import { SettingsPage } from './pages/SettingsPage';
import { api } from './services/api';

export function App() {
  const [currentTab, setCurrentTab] = useState('overview');
  const [exceptionCount, setExceptionCount] = useState(0);
  const [openActionCount, setOpenActionCount] = useState(0);

  // Responsive Sidebar States
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(() => {
    try {
      return localStorage.getItem('yotta_sidebar_collapsed') === 'true';
    } catch {
      return false;
    }
  });

  const handleToggleCollapse = () => {
    setIsCollapsed((prev) => {
      const next = !prev;
      try {
        localStorage.setItem('yotta_sidebar_collapsed', String(next));
      } catch {}
      return next;
    });
  };

  useEffect(() => {
    // Load badges
    api.getOverview().then((ov) => {
      setExceptionCount(ov.data_quality_exceptions_count);
      setOpenActionCount(ov.open_actions_count);
    }).catch(() => {});
  }, [currentTab]);

  const renderContent = () => {
    switch (currentTab) {
      case 'overview':
        return <OverviewPage />;
      case 'feedback':
        return <FeedbackExplorerPage />;
      case 'sentiment':
        return <SentimentAnalyticsPage />;
      case 'themes':
        return <ThemeIntelligencePage />;
      case 'trends':
        return <TrendDetectionPage />;
      case 'priorities':
        return <ServicePrioritiesPage />;
      case 'actions':
        return <ActionManagementPage />;
      case 'quality':
        return <DataQualityPage />;
      case 'evaluation':
        return <ModelEvaluationPage />;
      case 'data':
        return <DataManagementPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <OverviewPage />;
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 font-sans">
      {/* Responsive Sidebar (handles both desktop collapsible and mobile slide-out drawer) */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        exceptionCount={exceptionCount}
        openActionCount={openActionCount}
        isCollapsed={isCollapsed}
        onToggleCollapse={handleToggleCollapse}
        isMobileOpen={isMobileOpen}
        onMobileClose={() => setIsMobileOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden min-w-0">
        {/* Top Navbar */}
        <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950/90 px-3 sm:px-6 backdrop-blur-md shrink-0 z-20">
          <div className="flex items-center gap-2 sm:gap-3 min-w-0">
            {/* Mobile Hamburger Button */}
            <button
              onClick={() => setIsMobileOpen(true)}
              className="lg:hidden p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition-colors shrink-0"
              aria-label="Open navigation menu"
            >
              <Menu className="h-5 w-5" />
            </button>

            {/* Desktop Collapse Toggle */}
            <button
              onClick={handleToggleCollapse}
              className="hidden lg:flex p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition-colors shrink-0"
              title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
              aria-label="Toggle sidebar"
            >
              {isCollapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
            </button>

            {/* Breadcrumb Navigation */}
            <div className="flex items-center gap-2 min-w-0 text-xs">
              <span className="uppercase font-bold tracking-wider text-slate-400 truncate hidden sm:inline">
                Customer Feedback Intelligence
              </span>
              <span className="uppercase font-bold tracking-wider text-indigo-400 sm:hidden">
                YOTTA
              </span>
              <span className="text-slate-600">/</span>
              <span className="font-semibold text-indigo-400 capitalize truncate">
                {currentTab.replace('-', ' ')}
              </span>
            </div>
          </div>

          {/* Right Header Status Badges */}
          <div className="flex items-center gap-2 sm:gap-3 text-xs shrink-0">
            <div className="hidden md:flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/80 px-3 py-1 text-[11px] text-slate-300">
              <span className="h-1.5 w-1.5 rounded-full bg-indigo-500"></span>
              <span>Model: v1.2.0-tfidf-linear</span>
            </div>
            <div className="flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[11px] text-emerald-300">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="font-semibold hidden xs:inline">Online</span>
              <span className="font-mono text-slate-400 text-[10px] hidden sm:inline">| Production</span>
            </div>
          </div>
        </header>

        {/* Dynamic Page Container */}
        <main className="flex-1 overflow-y-auto p-3 sm:p-5 lg:p-6 bg-radial from-slate-900/40 via-slate-950 to-slate-950 min-w-0">
          <div className="max-w-7xl mx-auto pb-12 w-full min-w-0">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
