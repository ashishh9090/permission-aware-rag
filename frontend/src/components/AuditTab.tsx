import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  Activity,
  Filter,
  RefreshCw,
  Clock,
  EyeOff,
  AlertTriangle,
  Lock,
  Layers
} from 'lucide-react';
import { AuditLog, AuditSummary, User } from '../types';
import { api } from '../api';

interface AuditTabProps {
  currentUser: User | null;
}

export const AuditTab: React.FC<AuditTabProps> = ({ currentUser }) => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [summary, setSummary] = useState<AuditSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [filterAction, setFilterAction] = useState<string>('');

  const fetchAuditData = async () => {
    setLoading(true);
    try {
      const [fetchedLogs, fetchedSummary] = await Promise.all([
        api.getAuditLogs(50, filterAction || undefined),
        api.getAuditSummary(),
      ]);
      setLogs(fetchedLogs);
      setSummary(fetchedSummary);
    } catch (err) {
      console.error('Failed to load audit logs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditData();
  }, [filterAction, currentUser?.tenant_id]);

  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case 'PERMIT':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'DENY':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      default:
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 glass-panel p-5 rounded-2xl">
        <div>
          <h1 className="text-lg font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" />
            Append-Only Security Audit Trail
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Cryptographic decision logs for tenant <span className="font-mono text-emerald-400">{currentUser?.tenant_id}</span>. Guarantees sensitive data minimization with zero unauthorized document text exposure.
          </p>
        </div>

        <button
          onClick={fetchAuditData}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs transition border border-slate-700"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Audit Trail
        </button>
      </div>

      {/* Metrics Cards */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="glass-card p-4 rounded-xl border border-slate-800">
            <span className="text-slate-400 text-[11px] uppercase tracking-wider">Total Audited Events</span>
            <div className="text-xl font-extrabold text-white mt-1">{summary.total_events}</div>
          </div>
          <div className="glass-card p-4 rounded-xl border border-slate-800">
            <span className="text-emerald-400 text-[11px] uppercase tracking-wider">Authorized Permits</span>
            <div className="text-xl font-extrabold text-emerald-400 mt-1">{summary.permit_count}</div>
          </div>
          <div className="glass-card p-4 rounded-xl border border-slate-800">
            <span className="text-rose-400 text-[11px] uppercase tracking-wider">Security Denials</span>
            <div className="text-xl font-extrabold text-rose-400 mt-1">{summary.deny_count}</div>
          </div>
          <div className="glass-card p-4 rounded-xl border border-slate-800">
            <span className="text-teal-400 text-[11px] uppercase tracking-wider">Average Latency</span>
            <div className="text-xl font-extrabold text-teal-300 font-mono mt-1">
              {summary.average_latency_ms} <span className="text-xs text-slate-500 font-normal">ms</span>
            </div>
          </div>
        </div>
      )}

      {/* Sensitive Data Minimization Badge */}
      <div className="p-3 bg-emerald-950/20 border border-emerald-800/40 rounded-xl flex items-center justify-between text-xs text-emerald-300">
        <div className="flex items-center gap-2">
          <EyeOff className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Sensitive Data Minimization active: Zero unauthorized document text is stored in audit records.</span>
        </div>
        <span className="font-mono text-[10px] uppercase bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
          SOC2 / HIPAA Compliant
        </span>
      </div>

      {/* Filter and Log Table */}
      <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800">
        <div className="p-4 border-b border-slate-800/80 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <span>Filter Action:</span>
            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-2 py-1 text-slate-200 text-xs focus:ring-1 focus:ring-emerald-500"
            >
              <option value="">All Actions</option>
              <option value="rag_query">RAG Queries</option>
              <option value="retrieval">Retrievals</option>
              <option value="document_ingestion">Document Ingestion</option>
              <option value="permission_update">Permission Updates</option>
            </select>
          </div>
          <span className="text-[11px] text-slate-500 font-mono">
            Showing latest {logs.length} events
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Decision</th>
                <th className="py-3 px-4">Outcome</th>
                <th className="py-3 px-4">Query / Subject</th>
                <th className="py-3 px-4">Denied Chunks</th>
                <th className="py-3 px-4">Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {logs.map((log) => (
                <tr key={log.event_id} className="hover:bg-slate-900/50 transition">
                  <td className="py-3 px-4 font-mono text-[11px] text-slate-400 whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-300">
                    {log.action}
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2 py-0.5 rounded font-mono font-semibold text-[10px] border ${getDecisionBadge(
                        log.access_decision
                      )}`}
                    >
                      {log.access_decision}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-[11px] text-slate-300">
                    {log.outcome}
                  </td>
                  <td className="py-3 px-4 text-slate-300 max-w-xs truncate">
                    {log.query_text || '-'}
                  </td>
                  <td className="py-3 px-4 font-mono">
                    {log.denied_candidate_count > 0 ? (
                      <span className="text-rose-400 font-semibold">
                        {log.denied_candidate_count}
                      </span>
                    ) : (
                      <span className="text-slate-500">0</span>
                    )}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400 text-[11px]">
                    {log.latency_ms}ms
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
