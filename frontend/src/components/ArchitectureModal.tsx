import React from 'react';
import { X, Shield, Lock, Database, Cpu, CheckCircle2, ArrowRight, Layers } from 'lucide-react';

interface ArchitectureModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ArchitectureModal: React.FC<ArchitectureModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/60">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">System Architecture & Security Boundaries</h2>
              <p className="text-xs text-slate-400">
                Zero-Trust Multi-Tenant RAG Pipeline with Dual-Checkpoint Authorization
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-300">
          {/* Architecture Flowchart */}
          <div className="p-5 rounded-2xl bg-slate-950/70 border border-slate-800 font-mono text-[11px] leading-relaxed overflow-x-auto">
            <div className="text-slate-400 uppercase tracking-wider text-[10px] font-bold mb-3">
              End-to-End Zero-Trust Retrieval Sequence
            </div>
            <div className="flex flex-col md:flex-row items-center gap-2 text-center">
              <div className="p-2.5 rounded-lg bg-slate-850 border border-slate-700 w-full md:w-auto">
                <span className="text-emerald-400 font-bold block">1. User Identity</span>
                JWT Claim / Server Resolve
              </div>
              <ArrowRight className="w-4 h-4 text-slate-600 hidden md:block" />
              <div className="p-2.5 rounded-lg bg-slate-850 border border-slate-700 w-full md:w-auto">
                <span className="text-emerald-400 font-bold block">2. Policy Engine</span>
                Default-Deny RBAC + ABAC
              </div>
              <ArrowRight className="w-4 h-4 text-slate-600 hidden md:block" />
              <div className="p-2.5 rounded-lg bg-slate-850 border border-slate-700 w-full md:w-auto">
                <span className="text-emerald-400 font-bold block">3. DB Filter</span>
                Strict Tenant Row Isolation
              </div>
              <ArrowRight className="w-4 h-4 text-slate-600 hidden md:block" />
              <div className="p-2.5 rounded-lg bg-amber-950/40 border border-amber-600/50 w-full md:w-auto">
                <span className="text-amber-300 font-bold block">4. Security Checkpoint</span>
                Real-Time Revalidation
              </div>
              <ArrowRight className="w-4 h-4 text-slate-600 hidden md:block" />
              <div className="p-2.5 rounded-lg bg-slate-850 border border-slate-700 w-full md:w-auto">
                <span className="text-teal-400 font-bold block">5. Sandboxed LLM</span>
                Injection-Defused Context
              </div>
            </div>
          </div>

          {/* Three Standout Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-850/50 border border-slate-800 space-y-1.5">
              <div className="font-bold text-amber-400 flex items-center gap-1.5 text-xs">
                <Lock className="w-3.5 h-3.5" />
                Mid-Flight Revocation Check
              </div>
              <p className="text-[11px] text-slate-400 leading-normal">
                Permissions are rechecked at the final context-assembly boundary immediately before LLM generation. Even if access is revoked while a query executes, the document never reaches the prompt.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-850/50 border border-slate-800 space-y-1.5">
              <div className="font-bold text-emerald-400 flex items-center gap-1.5 text-xs">
                <Database className="w-3.5 h-3.5" />
                Tenant-Isolated Semantic Cache
              </div>
              <p className="text-[11px] text-slate-400 leading-normal">
                Cached embeddings and responses are cryptographically keyed by tenant_id, user clearance, roles, groups, and policy version. Zero cross-tenant or privilege-escalation cache hits.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-850/50 border border-slate-800 space-y-1.5">
              <div className="font-bold text-teal-400 flex items-center gap-1.5 text-xs">
                <Shield className="w-3.5 h-3.5" />
                Zero-Leakage Audit Trail
              </div>
              <p className="text-[11px] text-slate-400 leading-normal">
                Append-only audit records log exact retrieval decisions, authorized chunk IDs, and latency without ever persisting unauthorized document text or leaking confidential facts into logs.
              </p>
            </div>
          </div>

          {/* Security Boundary Table */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
              Security Boundary Enforcement Matrix
            </h3>
            <div className="rounded-xl border border-slate-800 overflow-hidden">
              <table className="w-full text-left text-[11px]">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="py-2.5 px-3">Boundary Layer</th>
                    <th className="py-2.5 px-3">Enforcement Mechanism</th>
                    <th className="py-2.5 px-3">Threat Neutralized</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-850">
                  <tr>
                    <td className="py-2.5 px-3 font-semibold text-white">Client / API Gateway</td>
                    <td className="py-2.5 px-3 font-mono text-emerald-400">Server-Side JWT Identity Validation</td>
                    <td className="py-2.5 px-3 text-slate-400">Header Spoofing, Forged Tenant IDs</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-semibold text-white">Vector DB / SQL Store</td>
                    <td className="py-2.5 px-3 font-mono text-emerald-400">Mandatory SQL Predicates & RLS</td>
                    <td className="py-2.5 px-3 text-slate-400">Cross-Tenant Bleed, SQL Injection</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-semibold text-white">Context Assembly</td>
                    <td className="py-2.5 px-3 font-mono text-emerald-400">Second Revalidation Checkpoint</td>
                    <td className="py-2.5 px-3 text-slate-400">Concurrent Revocation, Stale Index Desync</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-semibold text-white">LLM Prompt Boundary</td>
                    <td className="py-2.5 px-3 font-mono text-emerald-400">XML Tagging & Injection Defuser</td>
                    <td className="py-2.5 px-3 text-slate-400">Indirect Prompt Injection via Documents</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
