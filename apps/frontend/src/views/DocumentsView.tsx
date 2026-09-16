import { useEffect, useState, type FormEvent } from 'react';
import { useAuth } from '../lib/store';
import { api, type Paginated } from '../lib/api';

interface DocumentSummary {
  id: string;
  title: string;
  filename: string;
  content_type: string | null;
  status: string;
  chunk_count: number;
  created_at: string;
}

const ACCEPTED = '.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.md,.csv,.json';

export default function DocumentsView() {
  const { user, token } = useAuth();
  const [docs, setDocs] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [available, setAvailable] = useState<boolean | null>(null);

  useEffect(() => {
    if (!token) return;
    api
      .get<Paginated<DocumentSummary>>('/documents?page=1&page_size=50', token)
      .then((page) => {
        setAvailable(true);
        setDocs(page.items);
      })
      .catch(() => setAvailable(false))
      .finally(() => setLoading(false));
  }, [token]);

  const upload = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const input = event.currentTarget.elements.namedItem('file') as HTMLInputElement;
    const file = input.files?.[0];
    if (!file || !token) return;
    setUploading(true);
    setError(null);
    const form = new FormData();
    form.append('file', file);
    try {
      const res = await fetch('/api/v1/documents', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      const payload = await res.json().catch(() => null);
      if (!res.ok) {
        throw new Error(payload?.error?.message ?? `Upload failed (${res.status})`);
      }
      const created = payload.data as DocumentSummary;
      setDocs((prev) => [created, ...prev]);
      input.value = '';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-sm text-mab-muted">Loading documents…</div>;
  }

  if (available === false) {
    return (
      <div className="grid h-full place-items-center p-8">
        <div className="max-w-md text-center">
          <div className="mb-3 text-5xl">📄</div>
          <h2 className="mab-heading mb-2 text-lg">Documents are coming online</h2>
          <p className="mab-subtle text-sm">
            The upload + indexing API (PDF, DOCX, PPTX, XLSX, scanned OCR, text) is the next backend
            increment. As soon as it's up this screen becomes your library — you'll drop files here
            and chat over them in the <strong>Document Q&amp;A</strong> assistant.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-8">
      <div className="mb-6 max-w-3xl">
        <h1 className="mab-heading mb-1 text-xl">Documents</h1>
        <p className="mab-subtle text-sm">
          Upload files to build your knowledge base. Extracted text is chunked and indexed for
          keyword + semantic retrieval.
        </p>
      </div>

      <div className="mb-8 max-w-3xl">
        <form onSubmit={upload} className="mab-panel rounded-xl border border-mab-border p-4">
          <div className="flex flex-wrap items-center gap-3">
            <input
              type="file"
              name="file"
              accept={ACCEPTED}
              className="block max-w-xs text-sm"
              required
            />
            <button
              type="submit"
              className="mab-btn mab-btn-primary mab-btn-md"
              disabled={uploading}
            >
              {uploading ? 'Uploading…' : 'Upload'}
            </button>
          </div>
          <p className="mab-hint mt-2">
            PDF (incl. scanned), Word, PowerPoint, Excel, TXT, Markdown, CSV, JSON. Max 50 MB.
          </p>
          {error && (
            <p className="mab-error mt-2" role="alert">
              {error}
            </p>
          )}
        </form>
      </div>

      <div className="max-w-3xl space-y-2">
        {docs.length === 0 ? (
          <p className="mab-subtle text-sm">No documents yet.</p>
        ) : (
          docs.map((doc) => (
            <div key={doc.id} className="mab-panel flex items-center justify-between rounded-lg border border-mab-border px-4 py-3">
              <div className="flex items-center gap-3">
                <span className="text-xl">📄</span>
                <div>
                  <div className="text-sm font-medium">{doc.title}</div>
                  <div className="text-xs text-mab-muted">
                    {doc.filename} · {doc.status} · {doc.chunk_count} chunks
                  </div>
                </div>
              </div>
              <span className="mab-badge mab-badge-neutral">{doc.status}</span>
            </div>
          ))
        )}
        <p className="mab-subtle pt-4 text-xs">
          Signed in as {user?.email}. Only admins can delete documents.
        </p>
      </div>
    </div>
  );
}