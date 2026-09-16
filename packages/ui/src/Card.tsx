import type { HTMLAttributes, ReactNode } from 'react';

export function Card({ className = '', ...rest }: HTMLAttributes<HTMLDivElement>) {
  return <div className={`mab-card ${className}`} {...rest} />;
}

export function CardHeader({
  title,
  actions,
  subtitle,
}: {
  title: string;
  actions?: ReactNode;
  subtitle?: string;
}) {
  return (
    <div className="mab-card-header">
      <div>
        <h3 className="mab-card-title">{title}</h3>
        {subtitle ? <p className="mab-card-subtitle">{subtitle}</p> : null}
      </div>
      {actions ? <div className="mab-card-actions">{actions}</div> : null}
    </div>
  );
}

export function CardBody({ className = '', ...rest }: HTMLAttributes<HTMLDivElement>) {
  return <div className={`mab-card-body ${className}`} {...rest} />;
}