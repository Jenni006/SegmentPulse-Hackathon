import { StatCard } from './StatCard';
import { AlertTerminal } from './AlertTerminal';
import type { NetworkOverview, DiagnosisResult } from '../../types';

interface NetworkOverviewTabProps {
  overview: NetworkOverview | null;
  diagnosis: DiagnosisResult | null;
  onDistrictClick: (district: string) => void;
}

export function NetworkOverviewTab({
  overview,
  diagnosis,
}: NetworkOverviewTabProps) {
  if (!overview) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-accent font-mono text-xl">
          Loading network data...
        </div>
      </div>
    );
  }

  const { summary } = overview;

  const systemStatus =
    summary.active_faults > 0 ? 'FAULT DETECTED' : 'MONITORING';

  const affectedUsers =
    summary.active_faults > 0
      ? diagnosis?.affected_users?.toLocaleString() || 'Calculating...'
      : '0';

  return (
    <div className="space-y-6">
      {/* TOP KPI CARDS */}
      <div className="grid grid-cols-5 gap-4">
        <StatCard
          title="Total Subscribers"
          value={summary.total_subscribers.toLocaleString()}
          subtitle={`Per Village: ${summary.subscribers_per_village}`}
        />

        <StatCard
          title="Villages Monitored"
          value={summary.total_villages.toLocaleString()}
        />

        <StatCard
          title="Active Faults"
          value={summary.active_faults}
          status={summary.active_faults > 0 ? 'danger' : 'normal'}
        />

        <StatCard
          title="Affected Users"
          value={affectedUsers}
          status={summary.active_faults > 0 ? 'danger' : 'normal'}
        />

        <StatCard
          title="System Status"
          value={systemStatus}
          status={summary.active_faults > 0 ? 'danger' : 'normal'}
        />
      </div>

      {/* ALERT TERMINAL ONLY (No heavy district rendering) */}
      <div>
        <AlertTerminal diagnosis={diagnosis} />
      </div>
    </div>
  );
}