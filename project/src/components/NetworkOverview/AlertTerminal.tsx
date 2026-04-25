import type { DiagnosisResult } from '../../types';

interface AlertTerminalProps {
  diagnosis: DiagnosisResult | null;
}

export function AlertTerminal({ diagnosis }: AlertTerminalProps) {
  const isAlert = diagnosis?.status === 'Action Required';

  return (
    <div className={`rounded-lg border font-mono text-sm h-full ${
      isAlert
        ? 'border-fault shadow-[0_0_12px_rgba(255,59,92,0.4)]'
        : 'border-success shadow-[0_0_8px_rgba(0,255,156,0.2)]'
    } bg-[#020810]`}>

      {/* Header */}
      <div className={`px-4 py-2 border-b text-xs font-bold tracking-widest ${
        isAlert ? 'border-fault text-fault' : 'border-success text-success'
      }`}>
        {isAlert ? '⚠ SEGMENTPULSE ALERT — LIVE DETECTION' : '✓ SEGMENTPULSE — LIVE DETECTION'}
      </div>

      {/* Divider line */}
      <div className="px-4 py-1 text-xs text-muted">
        {'─'.repeat(45)}
      </div>

      {/* Content */}
      {!diagnosis ? (
        <div className="px-4 py-6 text-success text-xs">
          <div className="animate-pulse">Awaiting diagnosis...</div>
          <div className="mt-2 text-muted">System scanning 1,000 villages</div>
        </div>
      ) : (
        <div className="px-4 pb-4 space-y-1.5 text-xs">

          <Row label="Timestamp"         value={diagnosis.timestamp}           color="text-lightText" />
          <Row label="Detection Mode"    value={diagnosis.detection_mode}      color="text-lightText" />

          <div className="py-1">
            <div className="text-muted">{'─'.repeat(45)}</div>
          </div>

          <Row
            label="Fault Detected"
            value={diagnosis.fault_detected === 'None' ? 'None' : diagnosis.fault_detected}
            color={diagnosis.fault_detected === 'None' ? 'text-success' : 'text-fault'}
          />
          <Row label="Packet Loss"       value={diagnosis.packet_loss}         color={isAlert ? 'text-fault' : 'text-success'} />
          <Row label="Root Cause"        value={diagnosis.root_cause}          color={isAlert ? 'text-warning' : 'text-success'} />
          <Row label="Confidence"        value={diagnosis.confidence}          color="text-accent" />
          <Row label="Isolation Time"    value={diagnosis.isolation_time}      color="text-lightText" />

          {diagnosis.affected_users !== undefined && diagnosis.affected_users > 0 && (
            <Row label="Affected Users"  value={diagnosis.affected_users.toLocaleString()} color="text-fault" />
          )}

          <div className="py-1">
            <div className="text-muted">{'─'.repeat(45)}</div>
          </div>

          <Row label="Recommended Action" value={diagnosis.recommended_action} color="text-warning" />

          <div className="mt-2">
            <span className="text-muted">Status           : </span>
            <span className={`font-bold px-2 py-0.5 rounded text-xs ${
              isAlert
                ? 'bg-fault bg-opacity-20 text-fault border border-fault'
                : 'bg-success bg-opacity-10 text-success border border-success'
            }`}>
              {diagnosis.status}
            </span>
          </div>

          {diagnosis.villages_scanned !== undefined && (
            <div className="pt-2 text-muted text-xs border-t border-border mt-2">
              Villages scanned: {diagnosis.villages_scanned.toLocaleString()} · 
              Faults found: {diagnosis.faults_found ?? 0}
            </div>
          )}

        </div>
      )}
    </div>
  );
}

function Row({ label, value, color }: { label: string; value: string | number; color: string }) {
  const padded = label.padEnd(18, ' ');
  return (
    <div>
      <span className="text-muted">{padded}: </span>
      <span className={color}>{value}</span>
    </div>
  );
}