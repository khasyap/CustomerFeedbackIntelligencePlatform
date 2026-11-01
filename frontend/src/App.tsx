import React, { useState, useEffect } from 'react';
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
      {/* Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        exceptionCount={exceptionCount}
        openActionCount={openActionCount}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Navbar */}
        <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950/90 px-6 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <span className="text-xs uppercase font-bold tracking-wider text-slate-400">
              Customer Feedback Intelligence
            </span>
            <span className="text-slate-400">/</span>
            <span className="text-xs font-semibold text-indigo-400 capitalize">
              {currentTab.replace('-', ' ')}
            </span>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div className="hidden sm:flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/80 px-3 py-1 text-[11px] text-slate-300">
              <span className="h-1.5 w-1.5 rounded-full bg-indigo-500"></span>
              <span>Model: v1.2.0-tfidf-linear</span>
            </div>
            <div className="flex items-center gap-2 text-slate-400 text-xs">
              <span>Environment:</span>
              <span className="font-mono text-emerald-400 font-semibold">Production</span>
            </div>
          </div>
        </header>

        {/* Dynamic Page Container */}
        <main className="flex-1 overflow-y-auto p-6 bg-radial from-slate-900/40 via-slate-950 to-slate-950">
          <div className="max-w-7xl mx-auto pb-12">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
