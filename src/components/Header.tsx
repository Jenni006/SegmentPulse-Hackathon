import { Activity } from 'lucide-react';

interface HeaderProps {
  isConnected: boolean;
  lastUpdated: string;
}

export function Header({ isConnected, lastUpdated }: HeaderProps) {
  return (
    <header className="bg-card border-b border-border px-8 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="text-accent" size={32} />
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-heading font-bold text-accent">
              SegmentPulse
            </h1>
            <span className="bg-orange text-background px-3 py-1 rounded text-sm font-bold">
              TANFINET
            </span>
          </div>
        </div>

        <div className="flex-1 flex justify-center">
          <h2 className="text-lightText text-sm font-mono">
            Automated Fault Localization — 12,525 Villages
          </h2>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div
              className={`w-3 h-3 rounded-full ${
                isConnected ? 'bg-success animate-pulse' : 'bg-fault'
              }`}
            />
            <span
              className={`font-mono text-sm font-bold ${
                isConnected ? 'text-success' : 'text-fault'
              }`}
            >
              {isConnected ? 'LIVE' : 'OFFLINE'}
            </span>
          </div>
          <div className="text-muted text-xs font-mono">
            Last: {lastUpdated}
          </div>
        </div>
      </div>
    </header>
  );
}
