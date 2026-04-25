import { ArrowRight } from 'lucide-react';
import type { SegmentHealth, SegmentStatus } from '../../types';

interface SegmentTopologyProps {
  segments: SegmentHealth[];
}

export function SegmentTopology({ segments }: SegmentTopologyProps) {
  const getStatusColor = (status: SegmentStatus) => {
    switch (status) {
      case 'FAILED':
        return 'border-fault bg-fault text-white';
      case 'DEGRADED':
        return 'border-warning bg-warning text-black';
      case 'HEALTHY':
        return 'border-success bg-success text-black';
      default:
        return 'border-border bg-cardInner text-lightText';
    }
  };

  return (
    <div className="bg-cardInner rounded-lg p-6 border border-border">
      <h4 className="text-lg font-heading font-bold text-accent mb-4">
        Network Topology — 6-Segment Path
      </h4>

      <div className="flex items-center justify-between gap-2">
        {segments.map((segment, index) => (
          <div key={segment.name} className="flex items-center gap-2">
            <div
              className={`flex-1 border-2 rounded-lg p-4 ${getStatusColor(
                segment.status
              )}`}
            >
              <div className="font-bold font-mono text-sm mb-2">
                {segment.name}
              </div>
              <div className="space-y-1 text-xs font-mono">
                <div>RTT: {segment.rtt.toFixed(1)}ms</div>
                <div>Loss: {segment.loss.toFixed(1)}%</div>
                <div className="font-bold">{segment.status}</div>
              </div>
            </div>
            {index < segments.length - 1 && (
              <ArrowRight className="text-accent" size={24} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

