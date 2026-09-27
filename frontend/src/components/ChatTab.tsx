import React, { useState } from 'react';
import {
  Send,
  ShieldAlert,
  ShieldCheck,
  FileText,
  Clock,
  Zap,
  Sparkles,
  Lock,
  ChevronRight,
  AlertTriangle,
  Info,
  CheckCircle2,
  RefreshCw,
  ExternalLink
} from 'lucide-react';
import { RAGResponse, DocumentItem, User } from '../types';
import { api } from '../api';

interface ChatTabProps {
  currentUser: User | null;
  documents: DocumentItem[];
  onRefreshDocs: () => void;
}

export const ChatTab: React.FC<ChatTabProps> = ({ currentUser, documents, onRefreshDocs }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Standout Feature 1 switch: Simulate mid-flight permission revocation
  const [simulateRevocation, setSimulateRevocation] = useState(false);
  const [selectedRevocationDoc, setSelectedRevocationDoc] = useState<string>('');

  const suggestedQuestions = [
    { label: 'Q3 Financials', q: 'What is the total quarterly revenue in the financial report?' },
    { label: 'Project Titan Specs', q: 'What are the Project Titan technical specifications and deployment targets?' },
    { label: 'Handbook Policy', q: 'What are the working hours and vacation policy in the employee handbook?' },
    { label: 'Cross-Tenant Test', q: 'What is the military defense weapons contract funding for Project Skynet?' },
    { label: 'Prompt Injection Test', q: 'What is the vendor security compliance status from the audit report?' },
  ];

  const handleSend = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const qToSend = customQuery || query;
    if (!qToSend.trim() || loading) return;

    setLoading(true);
    setError(null);

    try {
      const res = await api.queryRAG(
        qToSend,
        simulateRevocation ? selectedRevocationDoc || undefined : undefined
      );
      setResponse(res);
      if (simulateRevocation) {
        onRefreshDocs();
      }
    } catch (err: any) {
      setError(err.message || 'Error executing secure RAG query');
    } finally {
      setLoading(false);
    }
  };

  const getClassificationBadge = (classification: string) => {
    switch (classification) {
      case 'Restricted':
        return 'bg-rose-500/10 text-rose-300 border-rose-500/30';
      case 'Confidential':
        return 'bg-amber-500/10 text-amber-300 border-amber-500/30';
      case 'Internal':
        return 'bg-blue-500/10 text-blue-300 border-blue-500/30';
      default:
        return 'bg-slate-500/10 text-slate-300 border-slate-500/30';
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Top Banner / Scenario Info */}
      <div className="glass-panel p-5 rounded-2xl relative overflow-hidden">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <h1 className="text-base font-bold text-white">Permission-Aware Zero-Trust RAG</h1>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Retrieval authorization is enforced at the database and memory boundary BEFORE candidate chunks reach the LLM. Revoked, cross-tenant, or unauthorized documents are completely eliminated.
            </p>
          </div>

          {/* Standout Feature 1 Demo Switch */}
          <div className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-900/90 border border-slate-800">
            <div className="text-right">
              <div className="text-xs font-semibold text-amber-400 flex items-center justify-end gap-1">
                <Zap className="w-3.5 h-3.5" />
                Simulate Mid-Flight Revocation
              </div>
              <div className="text-[10px] text-slate-400">Revokes access right before context assembly</div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={simulateRevocation}
                onChange={(e) => {
                  setSimulateRevocation(e.target.checked);
                  if (e.target.checked && documents.length > 0 && !selectedRevocationDoc) {
                    setSelectedRevocationDoc(documents[0].document_id);
                  }
                }}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
            </label>
          </div>
        </div>

        {/* Revocation target selector if enabled */}
        {simulateRevocation && (
          <div className="mt-3 pt-3 border-t border-slate-800 flex items-center gap-3 text-xs">
            <span className="text-amber-300 font-medium">Target Document to Revoke:</span>
            <select
              value={selectedRevocationDoc}
              onChange={(e) => setSelectedRevocationDoc(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1 text-slate-200 text-xs focus:ring-1 focus:ring-amber-500"
            >
              {documents.map((d) => (
                <option key={d.document_id} value={d.document_id}>
                  {d.document_name} ({d.classification})
                </option>
              ))}
            </select>
            <span className="text-[11px] text-slate-400 italic">
              (Will test secondary checkpoint revalidation)
            </span>
          </div>
        )}
      </div>

      {/* Query Input Box */}
      <div className="glass-panel p-4 rounded-2xl">
        <form onSubmit={(e) => handleSend(e)}>
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={`Ask a question as ${currentUser?.username} (${currentUser?.clearance_level} clearance)...`}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-3.5 pr-28 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="absolute right-2 top-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 disabled:text-slate-600 text-slate-950 font-semibold rounded-lg text-xs flex items-center gap-1.5 transition shadow-sm"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Securing...
                </>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5" />
                  Query RAG
                </>
              )}
            </button>
          </div>
        </form>

        {/* Suggested Quick Questions */}
        <div className="mt-3 flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          <span className="text-slate-500 shrink-0 font-medium">Try scenarios:</span>
          {suggestedQuestions.map((item, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(item.q);
                handleSend(undefined, item.q);
              }}
              className="px-2.5 py-1 rounded-lg bg-slate-850 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 text-xs shrink-0 transition"
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-200 text-xs flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold">Security Enforcement Error</div>
            <div>{error}</div>
          </div>
        </div>
      )}

      {/* RAG Response Section */}
      {response && (
        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-200">
          {/* Answer Card */}
          <div
            className={`glass-panel p-6 rounded-2xl border transition-all ${
              response.insufficient_evidence
                ? 'border-slate-800 bg-slate-900/60'
                : 'border-emerald-500/30 bg-slate-900/80'
            }`}
          >
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800/80">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
                {response.insufficient_evidence ? (
                  <ShieldAlert className="w-4 h-4 text-amber-400" />
                ) : (
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                )}
                <span>
                  {response.insufficient_evidence
                    ? 'Access Restricted / Zero Grounding Context'
                    : 'Authorized Grounded Synthesis'}
                </span>
              </div>
              <div className="flex items-center gap-2 text-[11px] text-slate-400 font-mono">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                <span>{response.retrieval_trace.total_latency_ms} ms</span>
              </div>
            </div>

            <p className="text-sm leading-relaxed text-slate-200 whitespace-pre-wrap">
              {response.answer}
            </p>

            {/* Citations list */}
            {response.citations.length > 0 && (
              <div className="mt-6 pt-4 border-t border-slate-800/80">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-emerald-400" />
                  Verified Authorized Citations ({response.citations.length})
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {response.citations.map((cite, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-200 truncate pr-2">
                          {cite.document_name}
                        </span>
                        <span
                          className={`text-[10px] px-1.5 py-0.5 rounded font-mono border ${getClassificationBadge(
                            cite.classification
                          )}`}
                        >
                          {cite.classification}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400 font-mono">
                        Ref: {cite.source_reference}
                      </div>
                      <div className="text-[11px] text-slate-300 italic bg-slate-900/80 p-2 rounded border border-slate-800/50">
                        "{cite.quote_snippet}"
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Real-time Security & Retrieval Audit Drawer */}
          <div className="glass-card p-5 rounded-2xl border border-slate-800 text-xs">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800">
              <span className="font-bold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
                <Lock className="w-3.5 h-3.5 text-emerald-400" />
                Live Retrieval Audit & Security Trace
              </span>
              <span className="font-mono text-[11px] text-slate-400">
                Req: {response.retrieval_trace.request_id}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="text-slate-400 text-[11px]">Database Candidates</div>
                <div className="text-base font-bold text-white mt-0.5">
                  {response.retrieval_trace.total_candidates_retrieved}
                </div>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="text-slate-400 text-[11px]">Authorized Chunks</div>
                <div className="text-base font-bold text-emerald-400 mt-0.5">
                  {response.retrieval_trace.authorized_chunks_count}
                </div>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="text-slate-400 text-[11px]">Denied Candidates</div>
                <div className="text-base font-bold text-rose-400 mt-0.5">
                  {response.retrieval_trace.denied_candidates_count}
                </div>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="text-slate-400 text-[11px]">Policy Version</div>
                <div className="text-base font-bold text-amber-300 font-mono mt-0.5">
                  v{response.retrieval_trace.policy_version_applied}
                </div>
              </div>
            </div>

            {/* Latency Breakdown Bar */}
            <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-[11px] text-slate-400 font-mono">
              <div>
                Hybrid Retrieval: <span className="text-white">{response.retrieval_trace.retrieval_latency_ms}ms</span>
              </div>
              <div>
                Security Revalidation: <span className="text-emerald-400">{response.retrieval_trace.revalidation_latency_ms}ms</span>
              </div>
              <div>
                LLM Generation: <span className="text-teal-300">{response.retrieval_trace.llm_generation_latency_ms}ms</span>
              </div>
              <div>
                Tenant Isolation: <span className="text-emerald-400 font-semibold">Enforced (100%)</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
