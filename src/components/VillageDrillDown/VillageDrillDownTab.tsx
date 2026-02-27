import { useState, useEffect } from 'react';
import { VillageCard } from './VillageCard';
import { SegmentTopology } from './SegmentTopology';
import { FaultInjector } from './FaultInjector';
import { apiService } from '../../services/api';
import { usePolling } from '../../hooks/usePolling';
import type { NetworkOverview, SegmentHealth } from '../../types';

interface VillageDrillDownTabProps {
  overview: NetworkOverview | null;
  selectedDistrict?: string;
}

export function VillageDrillDownTab({ overview, selectedDistrict }: VillageDrillDownTabProps) {
  const [district, setDistrict] = useState<string>('');
  const [selectedVillage, setSelectedVillage] = useState<string | null>(null);
  const [segments, setSegments] = useState<SegmentHealth[]>([]);

  const districts = overview?.overview.map((d) => d.district) || [];

  useEffect(() => {
    if (selectedDistrict && districts.includes(selectedDistrict)) {
      setDistrict(selectedDistrict);
    } else if (districts.length > 0 && !district) {
      setDistrict(districts[0]);
    }
  }, [selectedDistrict, districts, district]);

  const { data: segmentData } = usePolling(
    async () => {
      if (selectedVillage) {
        return await apiService.getSegmentHealth(selectedVillage);
      }
      return null;
    },
    10000,
    !!selectedVillage
  );

  useEffect(() => {
    if (segmentData) {
      setSegments(segmentData.segments);
    }
  }, [segmentData]);

  const villages = overview?.overview.find((d) => d.district === district)?.villages || [];

  const handleInjectFault = async (segment: string, faultType: string) => {
    if (selectedVillage) {
      await apiService.simulateFault(selectedVillage, segment, faultType);
    }
  };

  const handleClearFaults = async () => {
    if (selectedVillage) {
      await apiService.clearFaults(selectedVillage);
    }
  };

  const handleViewDetails = async (villageName: string) => {
    setSelectedVillage(villageName);
    const data = await apiService.getSegmentHealth(villageName);
    setSegments(data.segments);
  };

  if (!overview) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-accent font-mono text-xl">Loading villages...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <label className="text-lightText font-mono">Select District:</label>
        <select
          value={district}
          onChange={(e) => {
            setDistrict(e.target.value);
            setSelectedVillage(null);
          }}
          className="bg-card border border-border text-lightText rounded px-4 py-2 font-mono"
        >
          {districts.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {villages.map((village) => (
          <VillageCard
            key={village.village}
            village={village}
            district={district}
            onViewDetails={() => handleViewDetails(village.village)}
          />
        ))}
      </div>

      {selectedVillage && segments.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-2xl font-heading font-bold text-accent">
            {selectedVillage} — Segment Analysis
          </h3>
          <SegmentTopology segments={segments} />
          <FaultInjector
            village={selectedVillage}
            onInjectFault={handleInjectFault}
            onClearFaults={handleClearFaults}
          />
        </div>
      )}
    </div>
  );
}
