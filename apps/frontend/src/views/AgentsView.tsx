import { useEffect, useState } from 'react';
import { api, type ProviderStatus } from '../lib/api';

const AGENTS = [
  {
    kind: 'all_rounder',
    name: 'All-rounder Agent',
    desc: 'Reads, writes, and updates code across the repo; also answers finance, news, and trip-planning questions.',
  },
  {
    kind: 'web_research',
    name: 'Research Agent',
    desc: 'Runs live web searches, gathers sources, and returns a cited synthesis.',
  },
  {
    kind: 'rag',
    name: 'Document Q&A',
    desc: 'Answers from your uploaded documents with source citations.',
  },
];

export default function AgentsView() {
  const [statuses, setStatuses] = useState<ProviderStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<ProviderStatus[]>('/providers')
      .then(setStatuses)
      .catch((err) => setError(err instanceof Error ? err.message : 'Could not load providers'))
      .finally(() => setLoading(false));
  }, []);

  const activeProviders = statuses.filter((s) => s.enabled).map((s) => s.display_name);
  const online = activeProviders.length > 0;
  const primary = statuses.find((s) => s.enabled && (s.capabilities ?? []).includes('chat') && !s.name.includes('mock'));

  return (
    <div className="h-full overflow-y-auto p-8">
      <div className="mb-6 max-w-3xl">
        <h1 className="mab-heading mb-1 text-xl">Agents</h1>
        <p className="mab-subtle text-sm">
          Purpose-built assistants that combine chat, tools, and retrieval. Select anything with tools
          enabled.
        </p>
      </div>

      <div className="mb-8 max-w-3xl">
        <div
          className={`mab-panel rounded-xl border p-4 ${
            online ? 'border-[var(--mab-primary)]' : 'border-mab-border'
          }`}
        >
          <div className="flex items-center gap-2">
            <span className={`text-sm font-medium ${online ? 'text-green-400' : 'text-mab-muted'}`}>
              ● {online ? 'Online' : 'Offline'}
            </span>
            <span className="mab-subtle text-sm">
              {activeProviders.length > 0
                ? activeProviders.join(', ')
                : 'No backend provider reachable — fallback to mock is automatic.'}
            </span>
          </div>
          {primary && (
            <p className="mab-hint mt-2">
              Primary chat model: <strong>{primary.model_chat ?? primary.default_model}</strong> on{' '}
              {primary.display_name}.
            </p>
          )}
          {error && <p className="mab-error mt-2">{error}</p>}
          {loading && <p className="mab-subtle mt-2 text-sm">Checking providers…</p>}
        </div>
      </div>

      <div className="max-w-3xl space-y-3">
        {AGENTS.map((agent) => (
          <div
            key={agent.kind}
            className="mab-panel rounded-xl border border-mab-border p-4 transition-colors hover:border-[var(--mab-primary)]"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-sm font-semibold">{agent.name}</div>
                <p className="mab-subtle mt-1 text-sm">{agent.desc}</p>
              </div>
              <span className="mab-badge mab-badge-neutral">{agent.kind}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}