import { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { NetworkOverviewTab } from './components/NetworkOverview/NetworkOverviewTab';
import { VillageDrillDownTab } from './components/VillageDrillDown/VillageDrillDownTab';
import { FaultHistoryTab } from './components/FaultHistory/FaultHistoryTab';
import { usePolling } from './hooks/usePolling';
import { apiService, runDiagnosisSafe } from './services/api';
import type { TabType } from './types';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [selectedDistrict, setSelectedDistrict] = useState<string | undefined>();

  const { data: overview, error: overviewError } = usePolling(
    () => apiService.getNetworkOverview(),
    30000
  );

  const { data: diagnosis } = usePolling(
    () => runDiagnosisSafe(),
    30000
  );

  const { data: history, error: historyError } = usePolling(
    () => apiService.getFaultHistory(),
    30000
  );

  const isConnected = !overviewError ;

  const lastUpdated = new Date().toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

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
          />
        )}
        {activeTab === 'history' && <FaultHistoryTab history={history} />}
      </main>

      {(overviewError || historyError) && (
        <div className="fixed bottom-4 right-4 bg-fault text-white px-6 py-3 rounded-lg shadow-lg font-mono text-sm">
          Connection error: Unable to reach API at http://127.0.0.1:8000
        </div>
      )}
    </div>
  );
}

export default App;
