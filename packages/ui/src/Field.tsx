import type {
  InputHTMLAttributes,
  ReactNode,
  SelectHTMLAttributes,
  TextareaHTMLAttributes,
} from 'react';

function FieldShell({
  label,
  error,
  hint,
  id,
  children,
}: {
  label: string;
  error?: string;
  hint?: string;
  id: string;
  children: ReactNode;
}) {
  return (
    <div className="mab-field">
      <label htmlFor={id} className="mab-label">
        {label}
      </label>
      {children}
      {hint && !error ? <p className="mab-hint">{hint}</p> : null}
      {error ? (
        <p className="mab-error" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
}

export function Input({ label, error, hint, id, className = '', ...rest }: InputProps) {
  const inputId = id ?? rest.name ?? 'field-input';
  return (
    <FieldShell label={label} error={error} hint={hint} id={inputId}>
      <input id={inputId} className={`mab-input ${error ? 'mab-input-error' : ''} ${className}`} {...rest} />
    </FieldShell>
  );
}

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  error?: string;
  hint?: string;
}

export function Textarea({ label, error, hint, id, className = '', ...rest }: TextareaProps) {
  const inputId = id ?? rest.name ?? 'field-textarea';
  return (
    <FieldShell label={label} error={error} hint={hint} id={inputId}>
      <textarea id={inputId} className={`mab-textarea ${error ? 'mab-input-error' : ''} ${className}`} {...rest} />
    </FieldShell>
  );
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  error?: string;
  hint?: string;
  options: ReadonlyArray<{ value: string; label: string }>;
}

export function Select({ label, error, hint, id, options, className = '', ...rest }: SelectProps) {
  const inputId = id ?? rest.name ?? 'field-select';
  return (
    <FieldShell label={label} error={error} hint={hint} id={inputId}>
      <select id={inputId} className={`mab-input ${error ? 'mab-input-error' : ''} ${className}`} {...rest}>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </FieldShell>
  );
}