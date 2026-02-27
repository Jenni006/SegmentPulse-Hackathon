import { useState, useMemo } from 'react';
import { Filter, XCircle } from 'lucide-react';
import type { FaultHistory } from '../../types';

interface FaultHistoryTabProps {
  history: FaultHistory | null;
}

export function FaultHistoryTab({ history }: FaultHistoryTabProps) {
  const [districtFilter, setDistrictFilter] = useState<string>('all');
  const [faultTypeFilter, setFaultTypeFilter] = useState<string>('all');

  const faults = history?.faults ?? [];

  const districts = useMemo(() => {
    const unique = Array.from(
      new Set(faults.map((f) => f.district ?? 'Unknown').filter((d) => d !== 'Unknown'))
    ).sort();
    return ['all', ...unique];
  }, [faults]);

  const faultTypes = useMemo(() => {
    const unique = Array.from(
      new Set(faults.map((f) => f.root_cause).filter(Boolean))
    ).sort();
    return ['all', ...unique];
  }, [faults]);

  const filteredFaults = useMemo(() => {
    return faults.filter((fault) => {
      const districtMatch =
        districtFilter === 'all' || (fault.district ?? 'Unknown') === districtFilter;
      const typeMatch =
        faultTypeFilter === 'all' || fault.root_cause === faultTypeFilter;
      return districtMatch && typeMatch;
    });
  }, [faults, districtFilter, faultTypeFilter]);

  const getFaultRowStyle = (rootCause: string) => {
    const lc = rootCause.toLowerCase();
    if (lc.includes('cut') || lc.includes('failure'))
      return { row: 'border-l-2 border-l-fault', cause: 'text-fault' };
    if (lc.includes('congestion') || lc.includes('degradation'))
      return { row: 'border-l-2 border-l-warning', cause: 'text-warning' };
    if (lc.includes('flapping'))
      return { row: 'border-l-2 border-l-orange-400', cause: 'text-orange-400' };
    if (lc.includes('loop'))
      return { row: 'border-l-2 border-l-accent', cause: 'text-accent' };
    return { row: '', cause: 'text-muted' };
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

      {/* Header + Filters */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-2xl font-heading font-bold text-accent">
            Fault Detection Log
          </h2>
          <p className="text-muted font-mono text-xs mt-1">
            {faults.length} total records · last 50 shown
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="text-muted" size={16} />
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
              className="flex items-center gap-1 text-muted hover:text-fault transition-colors font-mono text-sm"
            >
              <XCircle size={16} />
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="bg-card border border-border rounded-lg overflow-hidden">
        {filteredFaults.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full font-mono text-sm">
              <thead>
                <tr className="bg-[#0a1628] border-b border-border text-muted text-xs uppercase tracking-wider">
                  <th className="text-left py-3 px-4">Time</th>
                  <th className="text-left py-3 px-4">Village</th>
                  <th className="text-left py-3 px-4">District</th>
                  <th className="text-left py-3 px-4">Segment</th>
                  <th className="text-left py-3 px-4">Root Cause</th>
                  <th className="text-left py-3 px-4">Confidence</th>
                  <th className="text-left py-3 px-4">Affected</th>
                  <th className="text-left py-3 px-4">Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredFaults.slice(0, 50).map((fault, index) => {
                  const style = getFaultRowStyle(fault.root_cause);
                  return (
                    <tr
                      key={`${fault.time}-${fault.village}-${index}`}
                      className={`border-b border-border hover:bg-[#0a1628] transition-colors ${style.row}`}
                    >
                      <td className="py-3 px-4 text-accent whitespace-nowrap">
                        {fault.time}
                      </td>
                      <td className="py-3 px-4 text-lightText font-bold whitespace-nowrap">
                        {fault.village}
                      </td>
                      <td className="py-3 px-4 text-lightText whitespace-nowrap">
                        {fault.district ?? '—'}
                      </td>
                      <td className="py-3 px-4 text-warning whitespace-nowrap">
                        {fault.segment}
                      </td>
                      <td className={`py-3 px-4 font-bold whitespace-nowrap ${style.cause}`}>
                        {fault.root_cause}
                      </td>
                      <td className="py-3 px-4 text-accent whitespace-nowrap">
                        {fault.confidence}
                      </td>
                      <td className="py-3 px-4 text-fault whitespace-nowrap">
                        {fault.affected != null ? fault.affected.toLocaleString() : '—'}
                      </td>
                      <td className="py-3 px-4 text-muted">
                        {fault.action}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="text-success text-lg font-mono font-bold mb-2">
              ✓ No faults detected
            </div>
            <div className="text-muted text-sm font-mono">
              {faults.length === 0
                ? 'Inject a fault to see it logged here'
                : `No results for current filters — ${faults.length} total records exist`}
            </div>
          </div>
        )}
      </div>

      {/* Footer count */}
      {filteredFaults.length > 0 && (
        <div className="text-muted text-xs font-mono text-center">
          Showing {Math.min(filteredFaults.length, 50)} of {filteredFaults.length} records
          {(districtFilter !== 'all' || faultTypeFilter !== 'all') && (
            <span className="ml-2 text-accent">(filtered)</span>
          )}
        </div>
      )}

    </div>
  );
}