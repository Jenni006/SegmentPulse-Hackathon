import { useState, useMemo } from 'react';
import { Filter, XCircle } from 'lucide-react';
import type { FaultHistory } from '../../types';

interface FaultHistoryTabProps {
  history: FaultHistory | null;
}

export function FaultHistoryTab({ history }: FaultHistoryTabProps) {
  const [districtFilter, setDistrictFilter] = useState<string>('all');
  const [faultTypeFilter, setFaultTypeFilter] = useState<string>('all');

  const faults = history?.faults || [];

  const districts = useMemo(() => {
    const uniqueDistricts = new Set(
      faults.map((f) => f.district).filter(Boolean)
    );
    return ['all', ...Array.from(uniqueDistricts)];
  }, [faults]);

  const faultTypes = useMemo(() => {
    const uniqueTypes = new Set(faults.map((f) => f.root_cause));
    return ['all', ...Array.from(uniqueTypes)];
  }, [faults]);

  const filteredFaults = useMemo(() => {
    return faults.filter((fault) => {
      const districtMatch =
        districtFilter === 'all' || fault.district === districtFilter;
      const typeMatch =
        faultTypeFilter === 'all' || fault.root_cause === faultTypeFilter;
      return districtMatch && typeMatch;
    });
  }, [faults, districtFilter, faultTypeFilter]);

  const getFaultColor = (rootCause: string) => {
    const lowerCause = rootCause.toLowerCase();
    if (lowerCause.includes('cut') || lowerCause.includes('failure')) {
      return 'text-fault';
    }
    if (lowerCause.includes('congestion') || lowerCause.includes('degradation')) {
      return 'text-warning';
    }
    if (lowerCause.includes('flapping')) {
      return 'text-orange';
    }
    return 'text-muted';
  };

  const handleClearFilters = () => {
    setDistrictFilter('all');
    setFaultTypeFilter('all');
  };

  if (!history) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-accent font-mono text-xl">Loading fault history...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-heading font-bold text-accent">
          Fault Detection Log — All Villages
        </h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="text-muted" size={18} />
            <select
              value={districtFilter}
              onChange={(e) => setDistrictFilter(e.target.value)}
              className="bg-card border border-border text-lightText rounded px-3 py-2 font-mono text-sm"
            >
              {districts.map((d) => (
                <option key={d} value={d}>
                  {d === 'all' ? 'All Districts' : d}
                </option>
              ))}
            </select>
          </div>
          <select
            value={faultTypeFilter}
            onChange={(e) => setFaultTypeFilter(e.target.value)}
            className="bg-card border border-border text-lightText rounded px-3 py-2 font-mono text-sm"
          >
            {faultTypes.map((type) => (
              <option key={type} value={type}>
                {type === 'all' ? 'All Fault Types' : type}
              </option>
            ))}
          </select>
          {(districtFilter !== 'all' || faultTypeFilter !== 'all') && (
            <button
              onClick={handleClearFilters}
              className="flex items-center gap-1 text-muted hover:text-lightText transition-colors font-mono text-sm"
            >
              <XCircle size={16} />
              Clear Filters
            </button>
          )}
        </div>
      </div>

      <div className="bg-card border border-border rounded-lg overflow-hidden">
        {filteredFaults.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full font-mono text-sm">
              <thead>
                <tr className="bg-cardInner border-b border-border text-muted">
                  <th className="text-left py-3 px-4">Time</th>
                  <th className="text-left py-3 px-4">Village</th>
                  <th className="text-left py-3 px-4">District</th>
                  <th className="text-left py-3 px-4">Segment</th>
                  <th className="text-left py-3 px-4">Root Cause</th>
                  <th className="text-left py-3 px-4">Confidence</th>
                  <th className="text-left py-3 px-4">Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredFaults.slice(0, 50).map((fault, index) => (
                  <tr
                    key={index}
                    className="border-b border-border hover:bg-cardInner transition-colors"
                  >
                    <td className="py-3 px-4 text-accent">{fault.time}</td>
                    <td className="py-3 px-4 text-lightText font-bold">
                      {fault.village}
                    </td>
                    <td className="py-3 px-4 text-lightText">
                      {fault.district || 'N/A'}
                    </td>
                    <td className="py-3 px-4 text-warning">{fault.segment}</td>
                    <td className={`py-3 px-4 font-bold ${getFaultColor(fault.root_cause)}`}>
                      {fault.root_cause}
                    </td>
                    <td className="py-3 px-4 text-accent">{fault.confidence}</td>
                    <td className="py-3 px-4 text-muted">{fault.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-success text-lg font-mono font-bold mb-2">
              ✓ No faults detected across TANFINET network
            </div>
            <div className="text-muted text-sm font-mono">
              All villages reporting healthy status
            </div>
          </div>
        )}
      </div>

      {filteredFaults.length > 0 && (
        <div className="text-muted text-sm font-mono text-center">
          Showing {Math.min(filteredFaults.length, 50)} of {filteredFaults.length} faults
        </div>
      )}
    </div>
  );
}
