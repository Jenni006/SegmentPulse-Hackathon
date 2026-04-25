import type { NetworkOverview, DiagnosisResult } from '../../types';
import { AlertTerminal } from './AlertTerminal';
import { DistrictTable } from './DistrictTable';

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
  if (!overview || typeof overview !== 'object') {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-accent font-mono text-xl">
          Loading TANFINET network overview...
        </div>
      </div>
    );
  }

  const districts = Array.isArray(overview.overview) ? overview.overview : [];

  // Real counts from demo villages (not scaled)
  const totalVillagesMonitored = districts.reduce(
    (acc, d) => acc + (Array.isArray(d.villages) ? d.villages.length : 0), 0
  );

  const activeFaults = districts.reduce((acc, d) => acc + (d.faults ?? 0), 0);
  const degraded     = districts.reduce((acc, d) => acc + (d.degraded ?? 0), 0);
  const healthy      = totalVillagesMonitored - activeFaults - degraded;
  const totalSegments = totalVillagesMonitored * 6;

  const systemStatus = activeFaults > 0 ? 'FAULT' : degraded > 0 ? 'DEGRADED' : 'HEALTHY';

  return (
    <div className="space-y-6">

      {/* Summary cards */}
      <div className="grid grid-cols-4 gap-4">

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-muted font-mono text-xs mb-2">VILLAGES MONITORED</div>
          <div className="text-3xl font-heading font-bold text-accent">
            {totalVillagesMonitored.toLocaleString()}
          </div>
          <div className="text-muted font-mono text-xs mt-1">
            {totalSegments.toLocaleString()} segments tracked
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-muted font-mono text-xs mb-2">ACTIVE FAULTS</div>
          <div className={`text-3xl font-heading font-bold ${activeFaults > 0 ? 'text-fault' : 'text-success'}`}>
            {activeFaults}
          </div>
          <div className="text-muted font-mono text-xs mt-1">
            Degraded: {degraded}
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-muted font-mono text-xs mb-2">HEALTHY VILLAGES</div>
          <div className="text-3xl font-heading font-bold text-success">
            {healthy.toLocaleString()}
          </div>
          <div className="text-muted font-mono text-xs mt-1">
            {totalVillagesMonitored} total − {activeFaults} faults − {degraded} degraded
          </div>
        </div>

        <div className={`bg-card border rounded-lg p-4 ${
          systemStatus === 'FAULT'    ? 'border-fault' :
          systemStatus === 'DEGRADED' ? 'border-warning' :
          'border-success'
        }`}>
          <div className="text-muted font-mono text-xs mb-2">SYSTEM STATUS</div>
          <div className={`text-3xl font-heading font-bold ${
            systemStatus === 'FAULT'    ? 'text-fault' :
            systemStatus === 'DEGRADED' ? 'text-warning' :
            'text-success'
          }`}>
            {systemStatus}
          </div>
          <div className="text-muted font-mono text-xs mt-1">
            20 districts · 50 villages each
          </div>
        </div>

      </div>

      {/* District table + Alert terminal */}
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <DistrictTable districts={districts} onDistrictClick={onDistrictClick} />
        </div>
        <div>
          <AlertTerminal diagnosis={diagnosis} />
        </div>
      </div>

    </div>
  );
}