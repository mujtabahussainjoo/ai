import type { Citation as CitationType } from '@myaibuddy/shared-types';

export function Citation({ citation, index }: { citation: CitationType; index: number }) {
  return (
    <a
      className="mab-citation"
      href={`/documents/${citation.document_id}`}
      title={citation.filename}
    >
      <sup>[{index + 1}]</sup> {citation.filename}
      {citation.page_number !== null && citation.page_number !== undefined
        ? ` · p.${citation.page_number + 1}`
        : ''}
    </a>
  );
}