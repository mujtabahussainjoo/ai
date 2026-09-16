import type { ReactNode } from 'react';

export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="mab-state" role="status">
      <span className="mab-progress-bar" aria-hidden="true" />
      <p>{label}</p>
    </div>
  );
}

export function EmptyState({
  icon = '🗂',
  title,
  description,
  action,
}: {
  icon?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="mab-state mab-state-empty">
      <div className="mab-empty-icon" aria-hidden="true">
        {icon}
      </div>
      <h3>{title}</h3>
      {description ? <p>{description}</p> : null}
      {action ? <div className="mab-state-action">{action}</div> : null}
    </div>
  );
}

export function ErrorState({
  title = 'Something went wrong',
  description,
  retry,
}: {
  title?: string;
  description?: string;
  retry?: () => void;
}) {
  return (
    <div className="mab-state mab-state-error" role="alert">
      <div className="mab-empty-icon" aria-hidden="true">
        ⚠️
      </div>
      <h3>{title}</h3>
      {description ? <p>{description}</p> : null}
      {retry ? (
        <button type="button" className="mab-btn mab-btn-secondary mab-btn-sm" onClick={retry}>
          Retry
        </button>
      ) : null}
    </div>
  );
}