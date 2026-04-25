interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  status?: 'normal' | 'warning' | 'danger';
}

export function StatCard({ title, value, subtitle, status = 'normal' }: StatCardProps) {
  const statusColors = {
    normal: 'text-accent',
    warning: 'text-warning',
    danger: 'text-fault',
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="text-muted text-sm font-mono mb-2">{title}</div>
      <div className={`text-4xl font-bold font-mono ${statusColors[status]}`}>
        {value}
      </div>
      {subtitle && (
        <div className="text-lightText text-xs font-mono mt-1">{subtitle}</div>
      )}
    </div>
  );
}
