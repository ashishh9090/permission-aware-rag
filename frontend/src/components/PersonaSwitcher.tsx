import React from 'react';
import { X, Shield, Check, Lock, Building2, UserCheck, AlertCircle } from 'lucide-react';
import { Persona } from '../types';

interface PersonaSwitcherProps {
  isOpen: boolean;
  onClose: () => void;
  personas: Persona[];
  activeUserId: string;
  onSelectPersona: (persona: Persona) => void;
}

export const PersonaSwitcher: React.FC<PersonaSwitcherProps> = ({
  isOpen,
  onClose,
  personas,
  activeUserId,
  onSelectPersona,
}) => {
  if (!isOpen) return null;

  const acmePersonas = personas.filter((p) => p.tenant_id === 'acme-corp');
  const cyberPersonas = personas.filter((p) => p.tenant_id === 'cyberdyne-sys');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Switch Authentication Persona</h2>
              <p className="text-xs text-slate-400">
                Test multi-tenant isolation, RBAC role boundaries, and ABAC clearance levels
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

        {/* Content */}
        <div className="p-6 max-h-[75vh] overflow-y-auto space-y-6">
          {/* Tenant 1: Acme Corp */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Building2 className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                Acme Corporation (Tenant: acme-corp)
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {acmePersonas.map((p) => {
                const isActive = p.id === activeUserId;
                return (
                  <button
                    key={p.id}
                    onClick={() => {
                      onSelectPersona(p);
                      onClose();
                    }}
                    className={`text-left p-3 rounded-xl border transition-all relative ${
                      isActive
                        ? 'bg-emerald-950/30 border-emerald-500/60 shadow-sm shadow-emerald-500/10'
                        : 'bg-slate-850/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800'
                    }`}
                  >
                    {isActive && (
                      <div className="absolute top-2.5 right-2.5 w-4 h-4 rounded-full bg-emerald-500 flex items-center justify-center text-slate-950">
                        <Check className="w-3 h-3 stroke-[3]" />
                      </div>
                    )}
                    <div className="font-semibold text-sm text-white flex items-center gap-2">
                      {p.username}
                    </div>
                    <div className="mt-1 flex flex-wrap gap-1 text-[11px]">
                      <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                        {p.roles.join(', ')}
                      </span>
                      <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-mono font-medium">
                        {p.clearance_level}
                      </span>
                    </div>
                    {p.groups.length > 0 && (
                      <p className="mt-1.5 text-[11px] text-slate-400">
                        Groups: {p.groups.join(', ')}
                      </p>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Tenant 2: CyberDyne Systems */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Building2 className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
                CyberDyne Systems (Tenant: cyberdyne-sys)
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {cyberPersonas.map((p) => {
                const isActive = p.id === activeUserId;
                return (
                  <button
                    key={p.id}
                    onClick={() => {
                      onSelectPersona(p);
                      onClose();
                    }}
                    className={`text-left p-3 rounded-xl border transition-all relative ${
                      isActive
                        ? 'bg-amber-950/30 border-amber-500/60 shadow-sm shadow-amber-500/10'
                        : 'bg-slate-850/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800'
                    }`}
                  >
                    {isActive && (
                      <div className="absolute top-2.5 right-2.5 w-4 h-4 rounded-full bg-amber-500 flex items-center justify-center text-slate-950">
                        <Check className="w-3 h-3 stroke-[3]" />
                      </div>
                    )}
                    <div className="font-semibold text-sm text-white flex items-center gap-2">
                      {p.username}
                    </div>
                    <div className="mt-1 flex flex-wrap gap-1 text-[11px]">
                      <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                        {p.roles.join(', ')}
                      </span>
                      <span className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 font-mono font-medium">
                        {p.clearance_level}
                      </span>
                    </div>
                    {p.groups.length > 0 && (
                      <p className="mt-1.5 text-[11px] text-slate-400">
                        Groups: {p.groups.join(', ')}
                      </p>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer info note */}
        <div className="px-6 py-3 bg-slate-950/60 border-t border-slate-800 flex items-center gap-2 text-xs text-slate-400">
          <AlertCircle className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Tokens are freshly minted via cryptographic JWT. Client-supplied tenant IDs are strictly rejected.</span>
        </div>
      </div>
    </div>
  );
};
