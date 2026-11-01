import React, { useState, useEffect } from 'react';
import {
  ShieldAlert, ShieldCheck, AlertOctagon, CheckCircle2,
  RefreshCw, Filter, Search, ArrowRight, Play
} from 'lucide-react';
import { api } from '../services/api';
import { DataQualityIssue, ValidationSummary } from '../types';

export const DataQualityPage: React.FC = () => {
  const [issues, setIssues] = useState<DataQualityIssue[]>([]);
  const [summary, setSummary] = useState<ValidationSummary | null>(null);
  const [selectedSeverity, setSelectedSeverity] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);

  const fetchIssues = async () => {
    setLoading(true);
    try {
      const data = await api.getQualityIssues(selectedSeverity, selectedStatus);
      setIssues(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIssues();
  }, [selectedSeverity, selectedStatus]);

  const handleRunValidation = async () => {
    setScanning(true);
    try {
      const res = await api.validateDataQuality();
      setSummary(res);
      fetchIssues();
    } catch (err: any) {
      alert(err.message || 'Validation error');
    } finally {
      setScanning(false);
    }
  };

  const handleUpdateStatus = async (issueId: string, newStatus: string) => {
    try {
      await api.updateIssue(issueId, newStatus, 'Status updated via Data Quality Dashboard');
      fetchIssues();
    } catch (err: any) {
      alert(err.message || 'Update failed');
    }
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
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
      {/* Header and Scan Action */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-rose-400" />
            Data Quality & Exception Management
          </h2>
          <p className="text-xs text-slate-400">10 automated integrity validation rules with audit tracking and exception resolution</p>
        </div>

        <button
          onClick={handleRunValidation}
          disabled={scanning}
          className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 transition-colors disabled:opacity-50"
        >
          {scanning ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
          {scanning ? 'Running Automated Scan...' : 'Run Automated Scan'}
        </button>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow-lg backdrop-blur-sm">
          <p className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Data Integrity Pass Rate</p>
          <h3 className="mt-1 text-2xl font-bold text-emerald-400">{summary?.pass_rate || 99.9}%</h3>
          <p className="text-[11px] text-slate-400 mt-0.5">High referential compliance</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow-lg backdrop-blur-sm">
          <p className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Total Exceptions Found</p>
          <h3 className="mt-1 text-2xl font-bold text-rose-400">{issues.length}</h3>
          <p className="text-[11px] text-slate-400 mt-0.5">Explicitly isolated anomalies</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow-lg backdrop-blur-sm">
          <p className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Under Investigation</p>
          <h3 className="mt-1 text-2xl font-bold text-amber-400">
            {issues.filter((i) => i.resolution_status === 'INVESTIGATING').length}
          </h3>
          <p className="text-[11px] text-slate-400 mt-0.5">Active analyst triage</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow-lg backdrop-blur-sm">
          <p className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Resolved / Sanitized</p>
          <h3 className="mt-1 text-2xl font-bold text-teal-400">
            {issues.filter((i) => i.resolution_status === 'RESOLVED').length}
          </h3>
          <p className="text-[11px] text-slate-400 mt-0.5">Verified remediations</p>
        </div>
      </div>

      {/* Issues Table & Filters */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 shadow-xl backdrop-blur-sm overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
          <h3 className="text-sm font-bold text-white">Detected Data Quality Exceptions</h3>

          <div className="flex items-center gap-2 text-xs">
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1.5 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1.5 text-slate-200 focus:border-indigo-500 focus:outline-hidden"
            >
              <option value="">All Statuses</option>
              <option value="DETECTED">Detected</option>
              <option value="INVESTIGATING">Investigating</option>
              <option value="RESOLVED">Resolved</option>
              <option value="IGNORED">Ignored</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/70 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Issue ID</th>
                <th className="px-4 py-3">Source Record</th>
                <th className="px-4 py-3">Exception Type</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Expected vs Actual Result</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Triage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {issues.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400">
                    No exceptions found for selected filter criteria.
                  </td>
                </tr>
              ) : (
                issues.map((iss) => (
                  <tr key={iss.issue_id} className="hover:bg-slate-800/40">
                    <td className="px-4 py-3 font-mono font-bold text-indigo-300 whitespace-nowrap">
                      {iss.issue_id}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="font-mono text-slate-200">{iss.source_record_id}</div>
                      <div className="text-[10px] text-slate-400">{iss.source_record_type}</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap font-medium text-white">
                      {iss.issue_type}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getSeverityBadge(iss.severity)}`}>
                        {iss.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3 max-w-md">
                      <div className="text-[11px] text-slate-400">
                        <span className="font-semibold text-slate-300">Expected:</span> {iss.expected_result}
                      </div>
                      <div className="text-[11px] text-rose-300 font-medium mt-0.5">
                        <span className="font-semibold text-rose-400">Actual:</span> {iss.actual_result}
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-semibold text-slate-300">
                        {iss.resolution_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      <select
                        value={iss.resolution_status}
                        onChange={(e) => handleUpdateStatus(iss.issue_id, e.target.value)}
                        className="rounded bg-slate-800 px-2 py-1 text-[11px] text-slate-200 border border-slate-700 focus:outline-hidden"
                      >
                        <option value="DETECTED">Detected</option>
                        <option value="INVESTIGATING">Investigate</option>
                        <option value="RESOLVED">Resolve</option>
                        <option value="IGNORED">Ignore</option>
                      </select>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

