export interface Village {
  village: string;
  status: 'HEALTHY' | 'DEGRADED' | 'FAULT';
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
  status: string;
}

export interface NetworkOverview {
  overview: DistrictData[];
  summary: {
    total_villages: number;
    total_segments: number;
    total_subscribers: number;
    subscribers_per_village: number;
    active_faults: number;
    degraded: number;
    healthy: number;
    demo_villages: number;
    scale_note: string;
  };
}

export interface DiagnosisResult {
  timestamp: string;
  detection_mode: string;
  fault_detected: string;
  packet_loss: string;
  root_cause: string;
  confidence: string;
  isolation_time: string;
  recommended_action: string;
  status: string;
  affected_users?: number;
  villages_scanned?: number;
  faults_found?: number;
  district?: string;
}

export interface FaultRecord {
  time: string;
  village: string;
  district?: string;
  segment: string;
  root_cause: string;
  confidence: string;
  action: string;
  affected?: number;
}

export interface FaultHistory {
  faults: FaultRecord[];
}

export interface SegmentHealth {
  name: string;
  status: 'HEALTHY' | 'DEGRADED' | 'FAILED';
  rtt: number;
  loss: number;
  updated: string;
}

export interface SegmentHealthResponse {
  village: string;
  segments: SegmentHealth[];
}

export interface DistrictMap {
  [district: string]: string[];
}

export interface DistrictsResponse {
  districts: DistrictMap;
}

export type TabType = 'overview' | 'villages' | 'history';