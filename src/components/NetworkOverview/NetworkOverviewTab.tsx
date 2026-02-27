import { StatCard } from './StatCard';
import { DistrictTable } from './DistrictTable';
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
  onDistrictClick,
}: NetworkOverviewTabProps) {
  if (!overview) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-accent font-mono text-xl">Loading network data...</div>
      </div>
    );
  }

  const { summary } = overview;
  const avgIsolationTime = diagnosis?.isolation_time || 'N/A';
  const systemStatus =
    summary.active_faults > 0 ? 'FAULT DETECTED' : 'MONITORING';

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-5 gap-4">
        <StatCard
          title="Villages Monitored"
          value="12,525"
          subtitle={`Active: ${summary.total_villages}`}
        />
        <StatCard
          title="Segments Monitored"
          value="75,150"
          subtitle={`Active: ${summary.total_segments}`}
        />
        <StatCard
          title="Active Faults"
          value={summary.active_faults}
          status={summary.active_faults > 0 ? 'danger' : 'normal'}
        />
        <StatCard
          title="Avg Isolation Time"
          value={avgIsolationTime}
          subtitle="Auto Detection"
        />
        <StatCard
          title="System Status"
          value={systemStatus}
          status={summary.active_faults > 0 ? 'danger' : 'normal'}
        />
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <DistrictTable
            districts={overview.overview}
            onDistrictClick={onDistrictClick}
          />
        </div>
        <div>
          <AlertTerminal diagnosis={diagnosis} />
        </div>
      </div>
    </div>
  );
}
