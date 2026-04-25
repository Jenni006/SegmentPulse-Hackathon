import type { DistrictData, Village } from '../../types';

interface DistrictTableProps {
  districts?: DistrictData[]; // make optional for safety
  onDistrictClick: (district: string) => void;
}

export function DistrictTable({
  districts = [],
  onDistrictClick,
}: DistrictTableProps) {
  // 🔒 Safe stats calculator
  const getDistrictStats = (villages?: Village[]) => {
    if (!Array.isArray(villages)) {
      console.error('Villages is not an array:', villages);
      return {
        healthy: 0,
        degraded: 0,
        faults: 0,
        status: 'HEALTHY' as const,
      };
    }

    const healthy = villages.filter((v) => v.status === 'HEALTHY').length;
    const degraded = villages.filter((v) => v.status === 'DEGRADED').length;
    const faults = villages.filter((v) => v.status === 'FAULT').length;

    const status =
      faults > 0 ? 'FAULT' : degraded > 0 ? 'DEGRADED' : 'HEALTHY';

    return { healthy, degraded, faults, status };
  };

  const getRowColor = (status: string) => {
    if (status === 'FAULT')
      return 'bg-fault bg-opacity-10 border-fault';
    if (status === 'DEGRADED')
      return 'bg-warning bg-opacity-10 border-warning';
    return 'bg-success bg-opacity-10 border-success';
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <h3 className="text-xl font-heading font-bold text-accent mb-4">
        District Overview — Tamil Nadu FibreNet
      </h3>

      <div className="overflow-x-auto">
        <table className="w-full font-mono text-sm">
          <thead>
            <tr className="border-b border-border text-muted">
              <th className="text-left py-3 px-4">District</th>
              <th className="text-right py-3 px-4">Villages</th>
              <th className="text-right py-3 px-4">Healthy</th>
              <th className="text-right py-3 px-4">Degraded</th>
              <th className="text-right py-3 px-4">Faults</th>
              <th className="text-center py-3 px-4">Status</th>
            </tr>
          </thead>

          <tbody>
            {Array.isArray(districts) &&
              districts.map((district) => {
                const villages = Array.isArray(district.villages)
                  ? district.villages
                  : [];

                const stats = getDistrictStats(villages);

                return (
                  <tr
                    key={district.district}
                    onClick={() =>
                      onDistrictClick(district.district)
                    }
                    className={`border-b border-border cursor-pointer hover:bg-cardInner transition-colors ${
                      stats.status === 'FAULT'
                        ? 'animate-pulse'
                        : ''
                    }`}
                  >
                    <td className="py-3 px-4 text-lightText font-bold">
                      {district.district}
                    </td>

                    <td className="text-right py-3 px-4 text-lightText">
                      {villages.length}
                    </td>

                    <td className="text-right py-3 px-4 text-success">
                      {stats.healthy}
                    </td>

                    <td className="text-right py-3 px-4 text-warning">
                      {stats.degraded}
                    </td>

                    <td className="text-right py-3 px-4 text-fault">
                      {stats.faults}
                    </td>

                    <td className="text-center py-3 px-4">
                      <span
                        className={`inline-block px-3 py-1 rounded border ${getRowColor(
                          stats.status
                        )}`}
                      >
                        <span
                          className={
                            stats.status === 'FAULT'
                              ? 'text-fault'
                              : stats.status === 'DEGRADED'
                              ? 'text-warning'
                              : 'text-success'
                          }
                        >
                          {stats.status}
                        </span>
                      </span>
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
