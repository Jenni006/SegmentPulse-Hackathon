import type { Village } from '../../types';

interface VillageCardProps {
  village: Village;
  district: string;
  onViewDetails: () => void;
}

export function VillageCard({ village, district, onViewDetails }: VillageCardProps) {
  const getStatusColor = () => {
    switch (village.status) {
      case 'FAULT':
        return 'border-fault bg-fault bg-opacity-5';
      case 'DEGRADED':
        return 'border-warning bg-warning bg-opacity-5';
      case 'HEALTHY':
        return 'border-success bg-success bg-opacity-5';
    }
  };

  const getStatusBadge = () => {
    switch (village.status) {
      case 'FAULT':
        return 'bg-fault text-white';
      case 'DEGRADED':
        return 'bg-warning text-black';
      case 'HEALTHY':
        return 'bg-success text-black';
    }
  };

  const healthySegments = village.total_segments - village.failed_segments - village.degraded_segments;

  return (
    <div
      className={`bg-card border-2 rounded-lg p-6 ${getStatusColor()} ${
        village.status === 'FAULT' ? 'animate-pulse' : ''
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xl font-heading font-bold text-lightText">
          {village.village}
        </h3>
        <span
          className={`px-3 py-1 rounded text-sm font-bold font-mono ${getStatusBadge()}`}
        >
          {village.status}
        </span>
      </div>
      <div className="space-y-2 mb-4 font-mono text-sm">
        <div className="text-muted">
          District: <span className="text-lightText">{district}</span>
        </div>
        <div className="text-muted">
          Segments:{' '}
          <span className="text-success">{healthySegments}/{village.total_segments} healthy</span>
          {village.degraded_segments > 0 && (
            <span className="text-warning ml-2">{village.degraded_segments} degraded</span>
          )}
          {village.failed_segments > 0 && (
            <span className="text-fault ml-2">{village.failed_segments} failed</span>
          )}
        </div>
      </div>
      <button
        onClick={onViewDetails}
        className="w-full bg-accent text-background font-bold py-2 rounded hover:bg-opacity-80 transition-all font-mono"
      >
        View Details
      </button>
    </div>
  );
}
