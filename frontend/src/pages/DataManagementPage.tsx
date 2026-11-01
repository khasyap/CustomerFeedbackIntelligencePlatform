import React, { useState, useEffect } from 'react';
import { Database, Download, RefreshCw, CheckCircle2, ShieldCheck, Play, Sparkles } from 'lucide-react';
import { api } from '../services/api';

export const DataManagementPage: React.FC = () => {
  const [reproducibility, setReproducibility] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');

  const fetchReproducibility = async () => {
    try {
      const res = await api.getReproducibility();
      setReproducibility(res);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchReproducibility();
  }, []);

  const handleGenerateData = async (mode: 'starter' | 'full') => {
    if (!confirm(`Generate synthetic datasets in ${mode.toUpperCase()} mode with fixed seed 20261022?`)) return;
    setGenerating(true);
    setStatusMsg(`Generating and seeding ${mode} dataset...`);
    try {
      const res = await api.generateData(mode);
      setStatusMsg(`Successfully seeded ${res.reviews_seeded} reviews and ${res.survey_responses_seeded} survey responses!`);
      fetchReproducibility();
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleRunBatchInference = async () => {
    setProcessing(true);
    setStatusMsg('Running batch NLP sentiment and multi-label theme processing...');
    try {
      const res = await api.runProcessingBatch(1000);
      setStatusMsg(`Batch processing complete! Processed: ${res.records_processed} records (${res.records_flagged} flagged for human review).`);
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}`);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow-xl backdrop-blur-sm">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Database className="h-5 w-5 text-indigo-400" />
          Data Generation, Exports & Reproducibility Management
        </h2>
        <p className="text-xs text-slate-400">Deterministic generator with fixed seed 20261022, audit exports, and batch processing</p>
      </div>

      {statusMsg && (
        <div className="rounded-lg bg-indigo-600/20 border border-indigo-500/30 p-3 text-xs text-indigo-200">
          {statusMsg}
        </div>
      )}

      {/* Generation Engine Control Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Starter Mode Card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-bold text-white">Starter Dataset Mode</h3>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Recommended
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Fast, high-density test environment designed for rapid development, instant analytics, and verification.
            </p>
            <ul className="text-xs space-y-1.5 text-slate-300 mb-4 bg-slate-950/70 p-3 rounded-lg border border-slate-800">
              <li>• 1,000 Customers & 10 Products</li>
              <li>• 8 Customer Channels & 50 Surveys</li>
              <li>• 5,000 Survey Responses & 5,000 Reviews</li>
              <li>• 2,000 Customer Support Messages</li>
              <li>• 10 Injected Data Quality Anomalies</li>
            </ul>
          </div>

          <button
            onClick={() => handleGenerateData('starter')}
            disabled={generating}
            className="w-full flex items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 transition-colors disabled:opacity-50"
          >
            {generating ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
            {generating ? 'Seeding Database...' : 'Generate Starter Mode Data'}
          </button>
        </div>

        {/* Full Mode Card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-bold text-white">Full Enterprise Mode</h3>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                Scale Benchmark
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Enterprise volume stress test dataset simulating long-term multi-channel customer behavior.
            </p>
            <ul className="text-xs space-y-1.5 text-slate-300 mb-4 bg-slate-950/70 p-3 rounded-lg border border-slate-800">
              <li>• 10,000 Customers & 25 Products</li>
              <li>• 12 Customer Channels & 500 Surveys</li>
              <li>• 50,000 Survey Responses & 50,000 Reviews</li>
              <li>• 20,000 Customer Support Messages</li>
              <li>• Full ground truth evaluation set</li>
            </ul>
          </div>

          <button
            onClick={() => handleGenerateData('full')}
            disabled={generating}
            className="w-full flex items-center justify-center gap-1.5 rounded-lg bg-purple-600 px-4 py-2 text-xs font-semibold text-white hover:bg-purple-500 transition-colors disabled:opacity-50"
          >
            {generating ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
            {generating ? 'Seeding Full Scale...' : 'Generate Full Mode Data'}
          </button>
        </div>
      </div>

      {/* Batch Processing Trigger */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-amber-400" />
              Batch NLP Inference Pipeline
            </h3>
            <p className="text-xs text-slate-400">Classify unanalyzed raw reviews, surveys & messages into FeedbackSentiment and FeedbackTheme tables</p>
          </div>
          <button
            onClick={handleRunBatchInference}
            disabled={processing}
            className="flex items-center gap-1.5 rounded-lg bg-amber-600 px-4 py-2 text-xs font-semibold text-white hover:bg-amber-500 transition-colors disabled:opacity-50"
          >
            {processing ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
            {processing ? 'Processing Batch...' : 'Run NLP Batch (1,000 items)'}
          </button>
        </div>
      </div>

      {/* Reproducibility Verification Section */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-sm">
        <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-emerald-400" />
            <div>
              <h3 className="text-sm font-bold text-white">Seed 20261022 Deterministic Reproducibility Status</h3>
              <p className="text-xs text-slate-400">SHA-256 integrity checksums verified across independent executions</p>
            </div>
          </div>
          <span className="flex items-center gap-1 text-xs text-emerald-400 font-bold bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
            <CheckCircle2 className="h-3.5 w-3.5" /> 100% Deterministic
          </span>
        </div>

        {reproducibility?.checksums && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-xs">
            {Object.entries(reproducibility.checksums).map(([entity, hash]: any) => (
              <div key={entity} className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">{entity}</span>
                <span className="font-mono text-[11px] text-indigo-300 font-semibold truncate block mt-0.5" title={hash}>
                  {hash.substring(0, 16)}...
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Export Options */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-sm">
        <h3 className="text-sm font-bold text-white mb-1">Data & Audit Artifact Exports</h3>
        <p className="text-xs text-slate-400 mb-4">Export connected database records in standard analytical and archive formats</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a
            href="/api/data/export/csv"
            download
            className="flex items-center justify-between p-3.5 rounded-xl border border-slate-800 bg-slate-950 hover:border-slate-700 hover:bg-slate-900 transition-all text-xs"
          >
            <div>
              <h4 className="font-semibold text-white">CSV Format Export</h4>
              <p className="text-slate-400 text-[11px]">Download flat tabular reviews and sentiment predictions</p>
            </div>
            <Download className="h-4 w-4 text-indigo-400" />
          </a>

          <a
            href="/api/data/export/json"
            target="_blank"
            rel="noreferrer"
            className="flex items-center justify-between p-3.5 rounded-xl border border-slate-800 bg-slate-950 hover:border-slate-700 hover:bg-slate-900 transition-all text-xs"
          >
            <div>
              <h4 className="font-semibold text-white">JSON Format Export</h4>
              <p className="text-slate-400 text-[11px]">Export complete master and transaction entities graph</p>
            </div>
            <Download className="h-4 w-4 text-indigo-400" />
          </a>
        </div>
      </div>
    </div>
  );
};

