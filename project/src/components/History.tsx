import type { HistoryRecord } from '../types';

interface HistoryProps {
  records: HistoryRecord[];
}

export default function History({ records }: HistoryProps) {
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-healthy';
    if (confidence >= 0.5) return 'text-warning';
    return 'text-fault';
  };

  return (
    <div className="bg-card-bg border border-accent-cyan/20 rounded-lg overflow-hidden">
      <div className="p-6">
        <h2 className="text-xl font-bold text-text-main mb-4">Fault History</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-accent-cyan/20">
                <th className="text-left text-text-main/60 font-medium py-3 px-3">Time</th>
                <th className="text-left text-text-main/60 font-medium py-3 px-3">Village</th>
                <th className="text-left text-text-main/60 font-medium py-3 px-3">Segment</th>
                <th className="text-left text-text-main/60 font-medium py-3 px-3">Root Cause</th>
                <th className="text-center text-text-main/60 font-medium py-3 px-3">Confidence</th>
                <th className="text-left text-text-main/60 font-medium py-3 px-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {records.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center text-text-main/40 py-12">
                    No history records available
                  </td>
                </tr>
              ) : (
                records.slice(0, 50).map((record, index) => (
                  <tr
                    key={index}
                    className="border-b border-accent-cyan/10 hover:bg-accent-cyan/5 transition-colors"
                  >
                    <td className="text-text-main/80 py-3 px-3 text-sm font-mono">
                      {formatTimestamp(record.timestamp)}
                    </td>
                    <td className="text-text-main py-3 px-3 font-medium">{record.village}</td>
                    <td className="text-accent-cyan py-3 px-3">{record.segment}</td>
                    <td className="text-text-main/80 py-3 px-3">{record.root_cause}</td>
                    <td className="text-center py-3 px-3">
                      <span className={`font-bold ${getConfidenceColor(record.confidence)}`}>
                        {(record.confidence * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="text-text-main/80 py-3 px-3 text-sm">{record.action}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

