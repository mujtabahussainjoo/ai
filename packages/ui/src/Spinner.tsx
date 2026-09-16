export function Spinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <span className="mab-spinner-wrap" role="status">
      <span className="mab-spinner" aria-hidden="true" />
      <span className="visually-hidden">{label}</span>
    </span>
  );
}