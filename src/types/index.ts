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
}

export interface NetworkSummary {
  total_villages: number;
  total_segments: number;
  active_faults: number;
  degraded: number;
  healthy: number;
  tanfinet_scale: string;
}

export interface NetworkOverview {
  overview: DistrictData[];
  summary: NetworkSummary;
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
  villages_scanned: number;
  faults_found: number;
  all_faults: FaultRecord[];
}

export interface FaultRecord {
  time: string;
  village: string;
  district?: string;
  segment: string;
  root_cause: string;
  confidence: string;
  action: string;
}

export interface FaultHistory {
  faults: FaultRecord[];
}

export interface SegmentHealth {
  name: string;
  status: 'HEALTHY' | 'DEGRADED' | 'FAULT';
  rtt: number;
  loss: number;
  updated: string;
}

export interface SegmentHealthResponse {
  segments: SegmentHealth[];
}

export interface DistrictMap {
  [district: string]: string[];
}

export interface DistrictsResponse {
  districts: DistrictMap;
}

export type TabType = 'overview' | 'villages' | 'history';
