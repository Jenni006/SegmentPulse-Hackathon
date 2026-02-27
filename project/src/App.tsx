import { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { NetworkOverviewTab } from './components/NetworkOverview/NetworkOverviewTab';
import { VillageDrillDownTab } from './components/VillageDrillDown/VillageDrillDownTab';
import { FaultHistoryTab } from './components/FaultHistory/FaultHistoryTab';
import { usePolling } from './hooks/usePolling';
import { apiService } from './services/api';
import type { DiagnosisResult, TabType } from './types';

// Build a diagnosis result for the alert box when user injects a fault (instant feedback)
function syntheticDiagnosisFromInjection(
  village: string,
  segment: string,
  faultType: string,
  district?: string
): DiagnosisResult {
  const now = new Date().toISOString().slice(0, 19).replace('T', ' ');
  const map: Record<string, { root_cause: string; confidence: string; action: string; packet_loss: string }> = {
    fiber_cut:      { root_cause: 'Fiber Cut',           confidence: '96%', packet_loss: '100%', action: 'Dispatch technician to segment' },
    congestion:      { root_cause: 'Link Congestion',    confidence: '94%', packet_loss: '32%',  action: 'Reroute traffic' },
    flapping:       { root_cause: 'Flapping Interface', confidence: '85%', packet_loss: '40%',  action: 'Check SFP / transceiver' },
    device_failure: { root_cause: 'Device Failure',      confidence: '91%', packet_loss: '95%',  action: 'Reboot or replace device' },
  };
  const m = map[faultType] ?? map.fiber_cut;
  const affectedMap: Record<string, number> = {
    'Customer': 1, 'ONT': 1, 'Splitter': 8, 'Agg Switch': 32, 'Core': 1600, 'Gateway': 400000,
  };
  const affected_users = affectedMap[segment] ?? 32;
  const isolationSeconds = (8 + Math.random() * 10).toFixed(1);
  return {
    timestamp: now,
    detection_mode: 'Manual (Injected)',
    fault_detected: `${segment} @ ${village}`,
    district,
    packet_loss: m.packet_loss,
    root_cause: m.root_cause,
    confidence: m.confidence,
    isolation_time: `${isolationSeconds} seconds`,
    affected_users,
    recommended_action: m.action,
    status: 'Action Required',
    villages_scanned: 1000,
    faults_found: 1,
  };
}

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [selectedDistrict, setSelectedDistrict] = useState<string | undefined>();
  const [failCount, setFailCount] = useState(0);
  const [diagnosis, setDiagnosis] = useState<DiagnosisResult | null>(null);

  const { data: overview } = usePolling(
    async () => {
      try {
        const result = await apiService.getNetworkOverview();
        setFailCount(0);
        return result;
      } catch {
        setFailCount((f) => f + 1);
        return null;
      }
    },
    30000
  );

  // Background diagnosis polling — don't overwrite a displayed fault with rate-limited "healthy"
  usePolling(
    async () => {
      try {
        const result = await apiService.runDiagnosis();
        setDiagnosis((prev) => {
          if (result.faults_found > 0) return result;
          if (prev && prev.faults_found > 0) return prev;
          return result;
        });
        return result;
      } catch {
        return null;
      }
    },
    30000
  );

  const { data: history, refetch: refetchHistory } = usePolling(
    () => apiService.getFaultHistory(),
    30000
  );

  const isConnected = failCount < 3;

  const lastUpdated = new Date().toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  // Called after fault injection (show fault in alert) or after clear (show healthy)
  const handleFaultInjected = useCallback(
    (village: string, segment: string, faultType: string, district?: string) => {
      if (!village && !segment) {
        const now = new Date().toISOString().slice(0, 19).replace('T', ' ');
        setDiagnosis({
          timestamp: now,
          detection_mode: 'Automatic',
          fault_detected: 'None',
          packet_loss: '0%',
          root_cause: 'None',
          confidence: '100%',
          isolation_time: 'N/A',
          affected_users: 0,
          recommended_action: 'No action required',
          status: 'All Systems Healthy',
          villages_scanned: 1000,
          faults_found: 0,
        });
      } else {
        const synthetic = syntheticDiagnosisFromInjection(village, segment, faultType, district);
        setDiagnosis(synthetic);
      }
      refetchHistory?.();
    },
    [refetchHistory]
  );

  const handleDistrictClick = useCallback((district: string) => {
    setSelectedDistrict(district);
    setActiveTab('villages');
  }, []);

  const tabs: { id: TabType; label: string }[] = [
    { id: 'overview', label: 'NETWORK OVERVIEW' },
    { id: 'villages', label: 'VILLAGE DRILL-DOWN' },
    { id: 'history', label: 'FAULT HISTORY' },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header isConnected={isConnected} lastUpdated={lastUpdated} />

      <div className="border-b border-border">
        <div className="flex gap-1 px-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 font-mono font-bold text-sm transition-colors ${
                activeTab === tab.id
                  ? 'bg-card text-accent border-t-2 border-accent'
                  : 'text-muted hover:text-lightText hover:bg-card hover:bg-opacity-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <main className="p-8">
        {activeTab === 'overview' && (
          <NetworkOverviewTab
            overview={overview}
            diagnosis={diagnosis}
            onDistrictClick={handleDistrictClick}
          />
        )}
        {activeTab === 'villages' && (
          <VillageDrillDownTab
            overview={overview}
            selectedDistrict={selectedDistrict}
            onFaultInjected={handleFaultInjected}
          />
        )}
        {activeTab === 'history' && <FaultHistoryTab history={history} />}
      </main>

      {failCount >= 3 && (
        <div className="fixed bottom-4 right-4 bg-fault text-white px-6 py-3 rounded-lg shadow-lg font-mono text-sm">
          Connection error: Unable to reach API at http://127.0.0.1:8000
        </div>
      )}
    </div>
  );
}

export default App;
