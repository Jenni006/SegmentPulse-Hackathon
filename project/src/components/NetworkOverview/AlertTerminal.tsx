import { AlertTriangle, CheckCircle } from 'lucide-react';
import type { DiagnosisResult } from '../../types';

interface AlertTerminalProps {
  diagnosis: DiagnosisResult | null;
}

export function AlertTerminal({ diagnosis }: AlertTerminalProps) {
  const hasFault = diagnosis && diagnosis.faults_found > 0;

  return (
    <div
      className={`bg-black rounded-lg p-6 border-2 ${
        hasFault ? 'border-fault animate-pulse' : 'border-success'
      }`}
    >
      <div className="flex items-center gap-2 mb-4">
        {hasFault ? (
          <AlertTriangle className="text-fault" size={24} />
        ) : (
          <CheckCircle className="text-success" size={24} />
        )}
        <h3 className="text-success font-mono text-lg font-bold">
          SEGMENTPULSE ALERT — LIVE DETECTION
        </h3>
      </div>

      <div className="font-mono text-sm text-success space-y-1">
        <div className="border-b border-success pb-2 mb-3">
          ─────────────────────────────────────────────
        </div>

        {diagnosis ? (
          <>
            <div className="flex justify-between">
              <span>Timestamp</span>
              <span className="text-lightText">{diagnosis.timestamp}</span>
            </div>
            <div className="flex justify-between">
              <span>Detection Mode</span>
              <span className="text-lightText">{diagnosis.detection_mode}</span>
            </div>
            <div className="flex justify-between">
              <span>Villages Scanned</span>
              <span className="text-lightText">{diagnosis.villages_scanned}</span>
            </div>
            <div className="flex justify-between">
              <span>Faults Found</span>
              <span
                className={hasFault ? 'text-fault font-bold' : 'text-success'}
              >
                {diagnosis.faults_found}
              </span>
            </div>

            {hasFault ? (
              <>
                <div className="border-t border-success pt-2 mt-2" />
                <div className="flex justify-between">
                  <span>Fault Detected</span>
                  <span className="text-fault font-bold">
                    {diagnosis.fault_detected}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Packet Loss</span>
                  <span className="text-fault">{diagnosis.packet_loss}</span>
                </div>
                <div className="flex justify-between">
                  <span>Root Cause</span>
                  <span className="text-warning">{diagnosis.root_cause}</span>
                </div>
                <div className="flex justify-between">
                  <span>Confidence</span>
                  <span className="text-accent">{diagnosis.confidence}</span>
                </div>
                <div className="flex justify-between">
                  <span>Isolation Time</span>
                  <span className="text-lightText">{diagnosis.isolation_time}</span>
                </div>
                <div className="flex justify-between">
                  <span>Recommended Action</span>
                  <span className="text-orange">{diagnosis.recommended_action}</span>
                </div>
                <div className="flex justify-between">
                  <span>Status</span>
                  <span className="text-fault font-bold">⚠ {diagnosis.status}</span>
                </div>
              </>
            ) : (
              <div className="text-center mt-4 text-success font-bold text-lg">
                ✓ ALL VILLAGES HEALTHY
              </div>
            )}
          </>
        ) : (
          <div className="text-center text-muted">
            Initializing diagnostic system...
          </div>
        )}

        <div className="border-t border-success pt-2 mt-3">
          ─────────────────────────────────────────────
        </div>
      </div>
    </div>
  );
}
