import { useState } from 'react';
import { AlertTriangle, Trash2 } from 'lucide-react';

interface FaultInjectorProps {
  village: string;
  onInjectFault: (segment: string, faultType: string) => Promise<void>;
  onClearFaults: () => Promise<void>;
}

const SEGMENTS = ['Customer', 'ONT', 'Splitter', 'Agg Switch', 'Core', 'Gateway'];
const FAULT_TYPES = [
  { value: 'fiber_cut', label: 'Fiber Cut' },
  { value: 'congestion', label: 'Congestion' },
  { value: 'flapping', label: 'Flapping Interface' },
  { value: 'device_failure', label: 'Device Failure' },
];

export function FaultInjector({ village, onInjectFault, onClearFaults }: FaultInjectorProps) {
  const [selectedSegment, setSelectedSegment] = useState(SEGMENTS[0]);
  const [selectedFault, setSelectedFault] = useState(FAULT_TYPES[0].value);
  const [injecting, setInjecting] = useState(false);
  const [clearing, setClearing] = useState(false);

  const handleInject = async () => {
    setInjecting(true);
    try {
      await onInjectFault(selectedSegment, selectedFault);
    } finally {
      setInjecting(false);
    }
  };

  const handleClear = async () => {
    setClearing(true);
    try {
      await onClearFaults();
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="text-orange" size={20} />
        <h4 className="text-lg font-heading font-bold text-orange">
          Inject Fault (Demo)
        </h4>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-muted text-sm font-mono mb-2">
            Segment
          </label>
          <select
            value={selectedSegment}
            onChange={(e) => setSelectedSegment(e.target.value)}
            className="w-full bg-cardInner border border-border text-lightText rounded px-3 py-2 font-mono"
          >
            {SEGMENTS.map((segment) => (
              <option key={segment} value={segment}>
                {segment}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-muted text-sm font-mono mb-2">
            Fault Type
          </label>
          <select
            value={selectedFault}
            onChange={(e) => setSelectedFault(e.target.value)}
            className="w-full bg-cardInner border border-border text-lightText rounded px-3 py-2 font-mono"
          >
            {FAULT_TYPES.map((fault) => (
              <option key={fault.value} value={fault.value}>
                {fault.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex gap-3">
        <button
          onClick={handleInject}
          disabled={injecting}
          className="flex-1 bg-fault hover:bg-opacity-80 text-white font-bold py-2 rounded transition-all font-mono disabled:opacity-50"
        >
          {injecting ? 'Injecting...' : 'Inject Fault'}
        </button>
        <button
          onClick={handleClear}
          disabled={clearing}
          className="flex items-center gap-2 bg-success hover:bg-opacity-80 text-black font-bold px-4 py-2 rounded transition-all font-mono disabled:opacity-50"
        >
          <Trash2 size={16} />
          {clearing ? 'Clearing...' : 'Clear'}
        </button>
      </div>

      <div className="mt-3 text-muted text-xs font-mono">
        Village: {village}
      </div>
    </div>
  );
}
