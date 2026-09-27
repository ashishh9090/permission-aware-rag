import React from 'react';
import { Shield, Building2, User, Key, Lock, Sparkles, Layers } from 'lucide-react';
import { User as UserType } from '../types';

interface HeaderProps {
  currentUser: UserType | null;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenPersonaModal: () => void;
  onOpenArchModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentUser,
  activeTab,
  setActiveTab,
  onOpenPersonaModal,
  onOpenArchModal,
}) => {
  const isAcme = currentUser?.tenant_id === 'acme-corp';
  
  const getClearanceBadgeClass = (level?: string) => {
    switch (level) {
      case 'Restricted':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      case 'Confidential':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'Internal':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      default:
        return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
    }
  };

  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Platform Name */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Shield className="w-5 h-5 text-slate-950 font-bold" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                  AegisRAG
                </span>
                <span className="px-1.5 py-0.5 text-[10px] font-mono font-semibold uppercase tracking-wider rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Zero-Trust
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Permission-Aware Multi-Tenant Enterprise Retrieval
              </p>
            </div>
          </div>

          {/* Nav Tabs */}
          <nav className="hidden md:flex items-center gap-1">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'chat'
                  ? 'bg-slate-800 text-white border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              RAG Chat & Search
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'documents'
                  ? 'bg-slate-800 text-white border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              Document Vault
            </button>
            <button
              onClick={() => setActiveTab('audit')}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'audit'
                  ? 'bg-slate-800 text-white border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              Audit Trail
            </button>
          </nav>

          {/* Right: Tenant, Persona Switcher & Architecture button */}
          <div className="flex items-center gap-3">
            <button
              onClick={onOpenArchModal}
              className="hidden lg:flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-lg text-slate-400 hover:text-white bg-slate-800/60 border border-slate-700/60 transition"
              title="View Architecture & Security Boundaries"
            >
              <Layers className="w-3.5 h-3.5 text-teal-400" />
              Architecture
            </button>

            {/* Tenant Badge */}
            <div
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border ${
                isAcme
                  ? 'bg-emerald-950/60 text-emerald-300 border-emerald-700/50'
                  : 'bg-amber-950/60 text-amber-300 border-amber-700/50'
              }`}
            >
              <Building2 className="w-3.5 h-3.5" />
              <span>{isAcme ? 'Acme Corp' : 'CyberDyne Systems'}</span>
            </div>

            {/* Persona Switcher Trigger */}
            <button
              onClick={onOpenPersonaModal}
              className="flex items-center gap-2 pl-2 pr-3 py-1 bg-slate-800 hover:bg-slate-750 text-slate-200 rounded-lg border border-slate-700 text-xs font-medium transition shadow-sm hover:border-slate-600"
            >
              <div className="w-6 h-6 rounded-full bg-slate-700 flex items-center justify-center text-slate-300">
                <User className="w-3.5 h-3.5" />
              </div>
              <div className="text-left">
                <div className="font-semibold text-slate-100 flex items-center gap-1.5">
                  {currentUser?.username || 'Switch User'}
                  <span
                    className={`text-[9px] px-1 py-0.2 rounded border font-mono ${getClearanceBadgeClass(
                      currentUser?.clearance_level
                    )}`}
                  >
                    {currentUser?.clearance_level}
                  </span>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
