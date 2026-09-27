import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { ChatTab } from './components/ChatTab';
import { DocumentsTab } from './components/DocumentsTab';
import { AuditTab } from './components/AuditTab';
import { PersonaSwitcher } from './components/PersonaSwitcher';
import { ArchitectureModal } from './components/ArchitectureModal';
import { User, Persona, DocumentItem } from './types';
import { api } from './api';

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [activeTab, setActiveTab] = useState<'chat' | 'documents' | 'audit'>('chat');
  const [showPersonaModal, setShowPersonaModal] = useState(false);
  const [showArchModal, setShowArchModal] = useState(false);
  const [loading, setLoading] = useState(true);

  // Initialize Auth & Default Persona
  const initApp = async () => {
    try {
      const fetchedPersonas = await api.getPersonas();
      setPersonas(fetchedPersonas);

      // Default to Acme Manager to showcase confidential retrieval out of the box
      const defaultPersona =
        fetchedPersonas.find((p) => p.username === 'acme_manager') || fetchedPersonas[0];

      if (defaultPersona) {
        await switchPersona(defaultPersona);
      }
    } catch (err) {
      console.error('Failed to initialize platform', err);
    } finally {
      setLoading(false);
    }
  };

  const switchPersona = async (persona: Persona) => {
    try {
      await api.login(persona.username, 'password123');
      const me = await api.getMe();
      setCurrentUser(me);
      await fetchDocuments();
    } catch (err) {
      console.error('Failed to switch persona', err);
    }
  };

  const fetchDocuments = async () => {
    try {
      const docs = await api.listDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to load documents', err);
    }
  };

  useEffect(() => {
    initApp();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-400 gap-3">
        <div className="w-10 h-10 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-xs font-mono tracking-wider uppercase text-slate-300">
          Initializing Zero-Trust Security Pipeline...
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Header
        currentUser={currentUser}
        activeTab={activeTab}
        setActiveTab={(tab: any) => setActiveTab(tab)}
        onOpenPersonaModal={() => setShowPersonaModal(true)}
        onOpenArchModal={() => setShowArchModal(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'chat' && (
          <ChatTab
            currentUser={currentUser}
            documents={documents}
            onRefreshDocs={fetchDocuments}
          />
        )}
        {activeTab === 'documents' && (
          <DocumentsTab
            currentUser={currentUser}
            documents={documents}
            onRefreshDocs={fetchDocuments}
          />
        )}
        {activeTab === 'audit' && <AuditTab currentUser={currentUser} />}
      </main>

      <PersonaSwitcher
        isOpen={showPersonaModal}
        onClose={() => setShowPersonaModal(false)}
        personas={personas}
        activeUserId={currentUser?.id || ''}
        onSelectPersona={switchPersona}
      />

      <ArchitectureModal
        isOpen={showArchModal}
        onClose={() => setShowArchModal(false)}
      />
    </div>
  );
};

export default App;
