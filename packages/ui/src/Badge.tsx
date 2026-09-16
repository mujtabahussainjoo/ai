import type { ReactNode } from 'react';

type Tone = 'neutral' | 'success' | 'warning' | 'danger' | 'info';

const toneClass: Record<Tone, string> = {
  neutral: 'mab-badge-neutral',
  success: 'mab-badge-success',
  warning: 'mab-badge-warning',
  danger: 'mab-badge-danger',
  info: 'mab-badge-info',
};

export function Badge({ tone = 'neutral', children }: { tone?: Tone; children: ReactNode }) {
  return <span className={`mab-badge ${toneClass[tone]}`}>{children}</span>;
}