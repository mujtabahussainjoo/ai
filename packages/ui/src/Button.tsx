import type { ButtonHTMLAttributes, ReactNode } from 'react';

type Variant = 'primary' | 'secondary' | 'danger' | 'ghost';
type Size = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  children: ReactNode;
}

const variantClass: Record<Variant, string> = {
  primary: 'mab-btn-primary',
  secondary: 'mab-btn-secondary',
  danger: 'mab-btn-danger',
  ghost: 'mab-btn-ghost',
};

const sizeClass: Record<Size, string> = {
  sm: 'mab-btn-sm',
  md: 'mab-btn-md',
  lg: 'mab-btn-lg',
};

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  children,
  className = '',
  type = 'button',
  ...rest
}: ButtonProps) {
  return (
    <button
      type={type}
      className={`mab-btn ${variantClass[variant]} ${sizeClass[size]} ${className}`}
      disabled={disabled || loading}
      aria-busy={loading}
      {...rest}
    >
      {loading ? <span className="mab-btn-spinner" aria-hidden="true" /> : null}
      {children}
    </button>
  );
}