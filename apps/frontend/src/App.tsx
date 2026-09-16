import { useState } from 'react';
import { AuthProvider, useAuth } from './lib/store';
import LoginView from './views/LoginView';
import ChatView from './views/ChatView';
import DocumentsView from './views/DocumentsView';
import AgentsView from './views/AgentsView';
import SettingsView from './views/SettingsView';

type Tab = 'chat' | 'documents' | 'agents' | 'settings';

const NAV: { id: Tab; label: string; icon: string }[] = [
  { id: 'chat', label: 'Chat', icon: '💬' },
  { id: 'documents', label: 'Documents', icon: '📄' },
  { id: 'agents', label: 'Agents', icon: '🤖' },
  { id: 'settings', label: 'Settings', icon: '⚙️' },
];

function Shell() {
  const { user, logout } = useAuth();
  const [tab, setTab] = useState<Tab>('chat');

  if (!user) return <LoginView />;

  return (
    <div className="flex h-full">
      <aside className="flex w-60 shrink-0 flex-col border-r border-mab-border bg-mab-panel">
        <div className="flex items-center gap-2 px-5 py-4">
          <span className="text-xl">🤖</span>
          <div>
            <div className="text-sm font-semibold">MyAIBuddy</div>
            <div className="text-xs text-mab-muted">v0.1.0</div>
          </div>
        </div>
        <nav className="flex flex-1 flex-col gap-1 px-3">
          {NAV.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setTab(item.id)}
              className={`flex items-center gap-3 rounded-md px-3 py-2 text-left text-sm transition-colors ${
                tab === item.id
                  ? 'bg-[var(--mab-primary)] text-white'
                  : 'text-mab-muted hover:bg-[var(--mab-primary-soft)] hover:text-mab-text'
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
        <div className="border-t border-mab-border px-5 py-4">
          <div className="truncate text-xs font-medium">{user.email}</div>
          <div className="mb-2 text-[11px] text-mab-muted">
            {user.roles.map((r) => r.toLowerCase()).join(', ')}
          </div>
          <button
            type="button"
            onClick={logout}
            className="text-xs text-[var(--mab-danger)] hover:underline"
          >
            Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-hidden">
        {tab === 'chat' && <ChatView />}
        {tab === 'documents' && <DocumentsView />}
        {tab === 'agents' && <AgentsView />}
        {tab === 'settings' && <SettingsView />}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Shell />
    </AuthProvider>
  );
}