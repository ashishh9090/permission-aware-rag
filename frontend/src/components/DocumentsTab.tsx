import React, { useState } from 'react';
import {
  FileText,
  Upload,
  Plus,
  Shield,
  Trash2,
  Edit2,
  CheckCircle2,
  Lock,
  Layers,
  X,
  FileCode,
  Tag
} from 'lucide-react';
import { DocumentItem, User } from '../types';
import { api } from '../api';

interface DocumentsTabProps {
  currentUser: User | null;
  documents: DocumentItem[];
  onRefreshDocs: () => void;
}

export const DocumentsTab: React.FC<DocumentsTabProps> = ({
  currentUser,
  documents,
  onRefreshDocs,
}) => {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);

  // Upload Form State
  const [docName, setDocName] = useState('');
  const [docType, setDocType] = useState('txt');
  const [classification, setClassification] = useState('Internal');
  const [roles, setRoles] = useState('Employee, Manager');
  const [groups, setGroups] = useState('engineering');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  // Edit Permissions State
  const [editClassification, setEditClassification] = useState('Internal');
  const [editRoles, setEditRoles] = useState('');
  const [editGroups, setEditGroups] = useState('');

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docName.trim() || !content.trim()) return;

    setLoading(true);
    try {
      await api.createRawDocument({
        document_name: docName,
        document_type: docType,
        classification,
        allowed_roles: roles.split(',').map((r) => r.trim()).filter(Boolean),
        allowed_groups: groups.split(',').map((g) => g.trim()).filter(Boolean),
        content,
      });
      setShowUploadModal(false);
      setDocName('');
      setContent('');
      onRefreshDocs();
    } catch (err: any) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const openEditModal = (doc: DocumentItem) => {
    setSelectedDoc(doc);
    setEditClassification(doc.classification);
    setEditRoles(doc.allowed_roles.join(', '));
    setEditGroups(doc.allowed_groups.join(', '));
    setShowEditModal(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDoc) return;

    setLoading(true);
    try {
      await api.updatePermissions(selectedDoc.document_id, {
        classification: editClassification,
        allowed_roles: editRoles.split(',').map((r) => r.trim()).filter(Boolean),
        allowed_groups: editGroups.split(',').map((g) => g.trim()).filter(Boolean),
      });
      setShowEditModal(false);
      onRefreshDocs();
    } catch (err: any) {
      alert(`Update failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document and its chunk vectors?')) return;
    try {
      await api.deleteDocument(docId);
      onRefreshDocs();
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const getClassificationBadge = (lvl: string) => {
    switch (lvl) {
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
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Top Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel p-5 rounded-2xl">
        <div>
          <h1 className="text-lg font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-emerald-400" />
            Authorized Document Vault
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Displaying only documents authorized for {currentUser?.username} ({currentUser?.clearance_level} clearance) in tenant <span className="font-mono text-emerald-400 font-semibold">{currentUser?.tenant_id}</span>.
          </p>
        </div>

        <button
          onClick={() => setShowUploadModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-semibold rounded-xl text-xs transition shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Ingest New Document
        </button>
      </div>

      {/* Document Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {documents.map((doc) => (
          <div
            key={doc.document_id}
            className="glass-card p-5 rounded-2xl border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition"
          >
            <div>
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-lg bg-slate-800 text-slate-300">
                    <FileCode className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm text-white truncate max-w-[180px]">
                      {doc.document_name}
                    </h3>
                    <span className="text-[10px] text-slate-400 font-mono">
                      Policy v{doc.access_policy_version}
                    </span>
                  </div>
                </div>

                <span
                  className={`text-[10px] px-2 py-0.5 rounded font-mono font-medium border ${getClassificationBadge(
                    doc.classification
                  )}`}
                >
                  {doc.classification}
                </span>
              </div>

              {doc.summary && (
                <p className="mt-3 text-xs text-slate-300 line-clamp-2">
                  {doc.summary}
                </p>
              )}

              {/* Roles & Groups Badges */}
              <div className="mt-4 pt-3 border-t border-slate-850 space-y-1.5 text-[11px]">
                <div className="flex items-center gap-1.5 text-slate-400">
                  <span className="font-medium text-slate-500 text-[10px] uppercase">Roles:</span>
                  <span className="text-slate-300 font-mono truncate">
                    {doc.allowed_roles.join(', ') || 'None'}
                  </span>
                </div>
                {doc.allowed_groups.length > 0 && (
                  <div className="flex items-center gap-1.5 text-slate-400">
                    <span className="font-medium text-slate-500 text-[10px] uppercase">Groups:</span>
                    <span className="text-slate-300 font-mono truncate">
                      {doc.allowed_groups.join(', ')}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Action Bar */}
            <div className="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-[10px] text-slate-400 font-mono">
                {new Date(doc.created_at).toLocaleDateString()}
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => openEditModal(doc)}
                  className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
                  title="Edit Permissions & Classification"
                >
                  <Edit2 className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => handleDelete(doc.document_id)}
                  className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-950/40 rounded-lg transition"
                  title="Delete Document"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {documents.length === 0 && (
        <div className="glass-panel p-12 text-center rounded-2xl">
          <Shield className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <h3 className="text-sm font-semibold text-slate-300">No Authorized Documents Available</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
            Current user does not have permission clearance or role privileges to view documents in this tenant.
          </p>
        </div>
      )}

      {/* Ingest Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Upload className="w-4 h-4 text-emerald-400" />
                Ingest Document with Permissions
              </h2>
              <button onClick={() => setShowUploadModal(false)}>
                <X className="w-5 h-5 text-slate-400 hover:text-white" />
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Document Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. strategic_roadmap_2027.md"
                  value={docName}
                  onChange={(e) => setDocName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Classification (ABAC)</label>
                  <select
                    value={classification}
                    onChange={(e) => setClassification(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                  >
                    <option value="Public">Public (Unclassified)</option>
                    <option value="Internal">Internal</option>
                    <option value="Confidential">Confidential</option>
                    <option value="Restricted">Restricted</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Document Type</label>
                  <select
                    value={docType}
                    onChange={(e) => setDocType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                  >
                    <option value="txt">Plain Text (.txt)</option>
                    <option value="md">Markdown (.md)</option>
                    <option value="pdf">PDF Document (.pdf)</option>
                    <option value="docx">Word (.docx)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Allowed Roles (comma-separated)</label>
                <input
                  type="text"
                  value={roles}
                  onChange={(e) => setRoles(e.target.value)}
                  placeholder="e.g. Employee, Manager, Tenant Admin"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Allowed Groups (comma-separated)</label>
                <input
                  type="text"
                  value={groups}
                  onChange={(e) => setGroups(e.target.value)}
                  placeholder="e.g. engineering, finance"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Document Content</label>
                <textarea
                  required
                  rows={5}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Enter or paste text content to be chunked, embedded, and indexed..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-white font-mono text-xs"
                />
              </div>

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-semibold rounded-xl"
                >
                  {loading ? 'Indexing Chunks...' : 'Ingest & Index'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Permissions Modal */}
      {showEditModal && selectedDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Lock className="w-4 h-4 text-amber-400" />
                Update Permissions: {selectedDoc.document_name}
              </h2>
              <button onClick={() => setShowEditModal(false)}>
                <X className="w-5 h-5 text-slate-400 hover:text-white" />
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Classification (ABAC)</label>
                <select
                  value={editClassification}
                  onChange={(e) => setEditClassification(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                >
                  <option value="Public">Public</option>
                  <option value="Internal">Internal</option>
                  <option value="Confidential">Confidential</option>
                  <option value="Restricted">Restricted</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Allowed Roles (comma-separated)</label>
                <input
                  type="text"
                  value={editRoles}
                  onChange={(e) => setEditRoles(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Allowed Groups (comma-separated)</label>
                <input
                  type="text"
                  value={editGroups}
                  onChange={(e) => setEditGroups(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white font-mono"
                />
              </div>

              <div className="p-3 bg-amber-950/20 border border-amber-900/40 rounded-xl text-amber-300/80 text-[11px]">
                Note: Updating permissions automatically increments the policy version and cascades to all child chunk vectors.
              </div>

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-slate-950 font-semibold rounded-xl"
                >
                  {loading ? 'Applying...' : 'Apply Permission Update'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
