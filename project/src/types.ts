// Core status types aligned with backend responses
export type SegmentStatus = 'HEALTHY' | 'DEGRADED' | 'FAILED';
export type VillageStatus = 'HEALTHY' | 'DEGRADED' | 'FAULT';

export type TabType = 'overview' | 'villages' | 'history';

// ── Network overview (/network-overview) ──────────────────────

export interface Village {
  village: string;
  status: VillageStatus;
  failed_segments: number;
  degraded_segments: number;
  total_segments: number;
}

export interface DistrictData {
  district: string;
  villages: Village[];
  healthy: number;
  degraded: number;
  faults: number;
  status: VillageStatus;
}

export interface NetworkOverview {
  overview: DistrictData[];
  summary: {
    total_villages: number;
    total_segments: number;
    total_subscribers: number;
    active_faults: number;
    degraded: number;
    healthy: number;
    subscribers_per_village: number;
    scale_note: string;
  };
}

// ── Diagnosis result (/run-diagnosis) ─────────────────────────

export interface DiagnosisResult {
  timestamp: string;
  detection_mode: string;
  fault_detected: string;
  district?: string;
  packet_loss: string;
  root_cause: string;
  confidence: string;
  isolation_time: string;
  affected_users: number;
  recommended_action: string;
  status: string;
  villages_scanned: number;
  faults_found: number;
}

// ── Segment health (/segment-health) ──────────────────────────

export interface SegmentHealth {
  name: string;
  status: SegmentStatus;
  rtt: number;
  loss: number;
  updated: string;
}

export interface SegmentHealthResponse {
  village: string;
  segments: SegmentHealth[];
}

// ── Fault history (/history) ──────────────────────────────────

export interface FaultHistoryItem {
  time: string;
  village: string;
  district: string;
  segment: string;
  root_cause: string;
  confidence: string;
  action: string;
  affected: number;
}

export interface FaultHistory {
  faults: FaultHistoryItem[];
}

// Legacy component support (History.tsx)
export interface HistoryRecord {
  timestamp: string;
  village: string;
  segment: string;
  root_cause: string;
  confidence: number;
  action: string;
}

// ── District list (/districts) ────────────────────────────────

export interface DistrictsResponse {
  districts: Record<string, string[]>;
}

