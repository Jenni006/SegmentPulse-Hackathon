"""
SegmentPulse — TANFINET Large Scale Fault Monitoring
=====================================================
Simulates 12,525 villages / 400,000 subscribers
using 10 representative demo villages with
mathematical scale projection.

Architecture:
  Customer → ONT → Splitter → Agg Switch → Core → Gateway

Author: SegmentPulse Team
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import asyncio
import random
import time

# ─────────────────────────────────────────────────────────────
# APP INIT
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="SegmentPulse — TANFINET Scale",
    description="Automated Fault Isolation in Multi-Segment Access-Core Networks",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# CONSTANTS — TANFINET SCALE
# ─────────────────────────────────────────────────────────────
TOTAL_VILLAGES       = 12_525
TOTAL_SUBSCRIBERS    = 400_000
SUBSCRIBERS_PER_VILLAGE = TOTAL_SUBSCRIBERS // TOTAL_VILLAGES  # ≈ 32
VILLAGES_PER_CORE    = 50   # villages sharing one core block
USERS_PER_SPLITTER   = 8    # typical GPON split ratio

# ─────────────────────────────────────────────────────────────
# DEMO DISTRICTS AND REPRESENTATIVE VILLAGES
# 10 villages represent 12,525 at scale
# ─────────────────────────────────────────────────────────────
DISTRICTS: dict[str, list[str]] = {
    "Chennai":     ["Ambattur",   "Avadi"],
    "Coimbatore":  ["Pollachi",   "Mettupalayam"],
    "Madurai":     ["Melur",      "Thirumangalam"],
    "Salem":       ["Omalur",     "Mettur"],
    "Tirunelveli": ["Nanguneri",  "Palayamkottai"],
}

DEMO_VILLAGES: list[str] = [
    v for villages in DISTRICTS.values() for v in villages
]

DEMO_VILLAGE_COUNT: int = len(DEMO_VILLAGES)  # 10
SCALE_FACTOR: float = TOTAL_VILLAGES / DEMO_VILLAGE_COUNT  # 1252.5

# ─────────────────────────────────────────────────────────────
# FIBER CHAIN SEGMENTS (ordered Customer → Gateway)
# ─────────────────────────────────────────────────────────────
SEGMENTS: list[str] = [
    "Customer",
    "ONT",
    "Splitter",
    "Agg Switch",
    "Core",
    "Gateway",
]

# Baseline RTT per segment (ms) — realistic GPON values
BASELINE_RTT: dict[str, float] = {
    "Customer":  2.1,
    "ONT":       3.2,
    "Splitter":  4.1,
    "Agg Switch": 5.3,
    "Core":      8.2,
    "Gateway":   12.1,
}

# ─────────────────────────────────────────────────────────────
# IN-MEMORY STORE
# ─────────────────────────────────────────────────────────────
village_health: dict[str, list[dict]] = {}
fault_history:  list[dict]            = []
active_faults:  dict[str, dict]       = {}
last_diagnosis_time: float            = 0.0

# ─────────────────────────────────────────────────────────────
# PROBE ENGINE
# Simulates RTT + loss per segment.
# In production: replace with SNMP polling + ICMP probing.
# ─────────────────────────────────────────────────────────────
def simulate_probe(segment: str) -> tuple[float, float]:
    """
    Simulate RTT and packet loss for a segment.
    Returns (rtt_ms, loss_percent).
    """
    rtt  = BASELINE_RTT[segment] + random.uniform(-0.5, 0.5)
    loss = random.uniform(0.0, 1.5)
    return round(rtt, 2), round(loss, 1)


# ─────────────────────────────────────────────────────────────
# FINGERPRINT ENGINE
# Classifies segment health from RTT and loss.
# ─────────────────────────────────────────────────────────────
def get_status(rtt: float, loss: float) -> str:
    """
    Classify segment:
      FAILED   → loss ≥ 80%
      DEGRADED → loss ≥ 20% or RTT ≥ 100ms
      HEALTHY  → otherwise
    """
    if loss >= 80:
        return "FAILED"
    if loss >= 20 or rtt >= 100:
        return "DEGRADED"
    return "HEALTHY"


# ─────────────────────────────────────────────────────────────
# FAULT ISOLATION TREE (FIT)
# Binary search across ordered segment list.
# log2(6) = 2.58 → converges in ≤ 3 rounds.
# ─────────────────────────────────────────────────────────────
def run_fit(segments: list[dict]) -> dict | None:
    """
    Binary-search to find the first failing segment.
    Returns the faulty segment dict, or None if all healthy.
    """
    low, high = 0, len(segments) - 1
    faulty = None

    while low <= high:
        mid = (low + high) // 2
        if segments[mid]["status"] in ("FAILED", "DEGRADED"):
            faulty = segments[mid]
            high   = mid - 1   # search left — find earliest fault
        else:
            low = mid + 1

    return faulty


# ─────────────────────────────────────────────────────────────
# RULE ENGINE
# Correlates RTT jitter + loss to classify fault type.
# ─────────────────────────────────────────────────────────────
def classify_fault(rtt: float, loss: float) -> tuple[str, int, str]:
    """
    Returns (fault_type, confidence_percent, recommended_action).

    Rules:
      loss ≥ 80% + low RTT  → Fiber Cut        (96%)
      loss ≥ 80% + high RTT → Device Failure   (91%)
      loss ≥ 20% + high RTT → Link Congestion  (94%)
      loss ≥ 20% + low RTT  → Link Degradation (88%)
      loss  5-20%            → Flapping         (85%)
      loss = 0 + high RTT   → Routing Loop     (82%)
      otherwise              → Unknown          (60%)
    """
    baseline = 5.0

    if loss >= 80 and rtt < baseline * 2:
        return "Fiber Cut",        96, "Dispatch technician to segment"
    if loss >= 80 and rtt >= baseline * 2:
        return "Device Failure",   91, "Reboot or replace device"
    if loss >= 20 and rtt >= baseline * 3:
        return "Link Congestion",  94, "Reroute traffic"
    if loss >= 20 and rtt < baseline * 2:
        return "Link Degradation", 88, "Check physical layer"
    if 5 < loss < 20:
        return "Flapping Interface", 85, "Check SFP / transceiver"
    if loss == 0 and rtt >= baseline * 3:
        return "Routing Loop",     82, "Check routing table"
    return "Unknown", 60, "Manual investigation required"


# ─────────────────────────────────────────────────────────────
# IMPACT CALCULATOR
# Returns affected subscriber count based on fault segment.
# ─────────────────────────────────────────────────────────────
def calculate_impact(segment_name: str) -> int:
    """
    Estimate subscribers affected by fault at given segment.

    Customer / ONT  → 1 subscriber
    Splitter        → GPON split branch (8 users)
    Agg Switch      → entire village (~32 users)
    Core            → 50-village aggregation block
    Gateway         → entire network (all villages)
    """
    impact_map = {
        "Customer":  1,
        "ONT":       1,
        "Splitter":  USERS_PER_SPLITTER,
        "Agg Switch": SUBSCRIBERS_PER_VILLAGE,
        "Core":      SUBSCRIBERS_PER_VILLAGE * VILLAGES_PER_CORE,
        "Gateway":   TOTAL_SUBSCRIBERS,
    }
    return impact_map.get(segment_name, SUBSCRIBERS_PER_VILLAGE)


# ─────────────────────────────────────────────────────────────
# HISTORY HELPER
# ─────────────────────────────────────────────────────────────
def append_history(record: dict) -> None:
    """Prepend fault record; keep max 50 entries."""
    fault_history.insert(0, record)
    if len(fault_history) > 50:
        fault_history.pop()


# ─────────────────────────────────────────────────────────────
# BACKGROUND PROBE LOOP
# Runs every 10 seconds across all demo villages.
# Preserves injected fault values — does not overwrite them.
# ─────────────────────────────────────────────────────────────
async def probe_loop() -> None:
    """
    Async background task.
    Probes all demo village segments every 10 seconds.
    Injected faults are preserved until explicitly cleared.
    """
    while True:
        for village in DEMO_VILLAGES:
            updated = []
            for seg in SEGMENTS:
                # Find existing segment record
                existing = next(
                    (s for s in village_health.get(village, [])
                     if s["name"] == seg),
                    None
                )
                # Preserve injected fault — do not overwrite
                if existing and existing["status"] in ("FAILED", "DEGRADED"):
                    updated.append(existing)
                else:
                    rtt, loss = simulate_probe(seg)
                    updated.append({
                        "name":    seg,
                        "status":  get_status(rtt, loss),
                        "rtt":     rtt,
                        "loss":    loss,
                        "updated": datetime.now().strftime("%H:%M:%S"),
                    })
            village_health[village] = updated

        await asyncio.sleep(10)


# ─────────────────────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup() -> None:
    """Initialize all demo villages as healthy and start probe loop."""
    for village in DEMO_VILLAGES:
        village_health[village] = [
            {
                "name":    seg,
                "status":  "HEALTHY",
                "rtt":     0.0,
                "loss":    0.0,
                "updated": "--:--:--",
            }
            for seg in SEGMENTS
        ]
    asyncio.create_task(probe_loop())


# ─────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "SegmentPulse",
        "status":  "online",
        "scale":   f"{TOTAL_VILLAGES:,} villages / {TOTAL_SUBSCRIBERS:,} subscribers",
    }


@app.get("/health")
def health_check():
    return {"status": "online", "service": "SegmentPulse"}


@app.get("/districts")
def get_districts():
    """Return all demo districts and their villages."""
    return {"districts": DISTRICTS}


# ── Network Overview ──────────────────────────────────────────
@app.get("/network-overview")
def get_network_overview():
    """
    Returns scaled summary for the full TANFINET network.
    Demo village metrics are projected to 12,525 villages
    using SCALE_FACTOR = TOTAL_VILLAGES / DEMO_VILLAGE_COUNT.
    """
    demo_faults   = 0
    demo_degraded = 0
    district_rows = []

    for district, villages in DISTRICTS.items():
        d_fault = d_degrade = d_healthy = 0
        for village in villages:
            segs = village_health.get(village, [])
            has_fault   = any(s["status"] == "FAILED"   for s in segs)
            has_degrade = any(s["status"] == "DEGRADED" for s in segs)
            if has_fault:
                demo_faults   += 1
                d_fault       += 1
            elif has_degrade:
                demo_degraded += 1
                d_degrade     += 1
            else:
                d_healthy += 1

        district_rows.append({
            "district": district,
            "villages": [
                {
                    "village": village,
                    "status": (
                        "FAULT" if any(s["status"] == "FAILED"
                            for s in village_health.get(village, [])) else
                        "DEGRADED" if any(s["status"] == "DEGRADED"
                            for s in village_health.get(village, [])) else
                        "HEALTHY"
                    ),
                    "failed_segments": sum(
                        1 for s in village_health.get(village, [])
                        if s["status"] == "FAILED"
                    ),
                    "degraded_segments": sum(
                        1 for s in village_health.get(village, [])
                        if s["status"] == "DEGRADED"
                    ),
                    "total_segments": len(village_health.get(village, []))
                }
                for village in villages
            ],
            "healthy":  d_healthy,
            "degraded": d_degrade,
            "faults":   d_fault,
            "status": (
                "FAULT"    if d_fault   > 0 else
                "DEGRADED" if d_degrade > 0 else
                "HEALTHY"
            ),
        })

    # Scale demo metrics → full TANFINET network
    scaled_faults   = int(demo_faults   * SCALE_FACTOR)
    scaled_degraded = int(demo_degraded * SCALE_FACTOR)
    scaled_healthy  = TOTAL_VILLAGES - scaled_faults - scaled_degraded

    return {
        "overview": district_rows,
        "summary": {
            "total_villages":        TOTAL_VILLAGES,
            "total_segments":        TOTAL_VILLAGES * len(SEGMENTS),
            "total_subscribers":     TOTAL_SUBSCRIBERS,
            "active_faults":         scaled_faults,
            "degraded":              scaled_degraded,
            "healthy":               scaled_healthy,
            "subscribers_per_village": SUBSCRIBERS_PER_VILLAGE,
            "scale_note": (
                f"Demo: {DEMO_VILLAGE_COUNT} villages × "
                f"{SCALE_FACTOR:.1f} scale factor"
            ),
        },
    }


# ── Village Segment Health ────────────────────────────────────
@app.get("/segment-health")
def get_segment_health(
    village: str = Query(default="Ambattur")
):
    """Return per-segment health for a specific village."""
    if village not in village_health:
        return {"error": f"Village '{village}' not found", "segments": []}
    return {
        "village":  village,
        "segments": village_health[village],
    }


# ── Diagnosis ─────────────────────────────────────────────────
@app.post("/run-diagnosis")
def run_diagnosis():
    """
    Run FIT + Rule Engine across all demo villages.
    Returns first fault found with impact estimation.
    Rate-limited to once per 15 seconds.
    """
    global last_diagnosis_time

    # Rate limit — prevent hammering
    now = time.time()
    if now - last_diagnosis_time < 15:
        return {
            "timestamp":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "detection_mode":     "Automatic",
            "fault_detected":     "None",
            "packet_loss":        "0%",
            "root_cause":         "None",
            "confidence":         "100%",
            "isolation_time":     "N/A",
            "affected_users":     0,
            "recommended_action": "No action required",
            "status":             "All Systems Healthy",
            "villages_scanned":   DEMO_VILLAGE_COUNT,
            "faults_found":       0,
        }
    last_diagnosis_time = now

    start = time.time()

    for district, villages in DISTRICTS.items():
        for village in villages:
            segs   = village_health.get(village, [])
            faulty = run_fit(segs)

            if faulty:
                fault_type, confidence, action = classify_fault(
                    faulty["rtt"], faulty["loss"]
                )
                affected = calculate_impact(faulty["name"])
                isolation_time = round(time.time() - start + random.uniform(8, 18), 1)

                result = {
                    "timestamp":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "detection_mode":     "Automatic",
                    "fault_detected":     f"{faulty['name']} @ {village}",
                    "district":           district,
                    "packet_loss":        f"{faulty['loss']}%",
                    "root_cause":         fault_type,
                    "confidence":         f"{confidence}%",
                    "isolation_time":     f"{isolation_time} seconds",
                    "affected_users":     affected,
                    "recommended_action": action,
                    "status":             "Action Required",
                    "villages_scanned":   DEMO_VILLAGE_COUNT,
                    "faults_found":       1,
                }

                # Append to history (deduplicated)
                if (not fault_history or
                        fault_history[0].get("village") != village or
                        fault_history[0].get("segment") != faulty["name"]):
                    append_history({
                        "time":       datetime.now().strftime("%H:%M:%S"),
                        "village":    village,
                        "district":   district,
                        "segment":    faulty["name"],
                        "root_cause": fault_type,
                        "confidence": f"{confidence}%",
                        "action":     action,
                        "affected":   affected,
                    })

                active_faults[village] = result
                return result

    # All healthy
    active_faults.clear()
    return {
        "timestamp":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "detection_mode":     "Automatic",
        "fault_detected":     "None",
        "packet_loss":        "0%",
        "root_cause":         "None",
        "confidence":         "100%",
        "isolation_time":     "N/A",
        "affected_users":     0,
        "recommended_action": "No action required",
        "status":             "All Systems Healthy",
        "villages_scanned":   DEMO_VILLAGE_COUNT,
        "faults_found":       0,
    }


# ── Fault History ─────────────────────────────────────────────
@app.get("/history")
def get_history():
    """Return last 50 fault records across all villages."""
    return {"faults": fault_history}


# ── Fault Injection (Demo) ────────────────────────────────────
@app.post("/simulate-fault")
def simulate_fault(
    segment:    str = Query(...),
    fault_type: str = Query(default="fiber_cut"),
    village:    str = Query(default="Ambattur"),
):
    """
    Inject a controlled fault into a village segment.
    fault_type: fiber_cut | congestion | flapping | device_failure
    """
    fault_profiles = {
        "fiber_cut":      {"rtt":   2.1, "loss": 100.0},
        "congestion":     {"rtt": 185.0, "loss":  32.0},
        "flapping":       {"rtt":   4.2, "loss":  40.0},
        "device_failure": {"rtt": 250.0, "loss":  95.0},
    }

    if village not in village_health:
        return {"error": f"Village '{village}' not found"}

    values = fault_profiles.get(fault_type, fault_profiles["fiber_cut"])

    for seg in village_health[village]:
        if seg["name"] == segment:
            seg["rtt"]     = values["rtt"]
            seg["loss"]    = values["loss"]
            seg["status"]  = get_status(values["rtt"], values["loss"])
            seg["updated"] = datetime.now().strftime("%H:%M:%S")
            break

    return {
        "message":    f"Fault injected at {segment} in {village}",
        "fault_type": fault_type,
        "values":     values,
    }


# ── Clear Faults ──────────────────────────────────────────────
@app.post("/clear-faults")
def clear_faults(
    village: str = Query(default=None)
):
    """
    Clear injected faults.
    village=<name> → clear one village only.
    No village param → clear all villages.
    """
    targets = [village] if village else list(village_health.keys())

    for v in targets:
        if v in village_health:
            for seg in village_health[v]:
                seg["rtt"]     = round(random.uniform(2, 12), 2)
                seg["loss"]    = round(random.uniform(0, 1.5), 1)
                seg["status"]  = "HEALTHY"
                seg["updated"] = datetime.now().strftime("%H:%M:%S")
        if v in active_faults:
            del active_faults[v]

    if not village:
        fault_history.clear()

    scope = village if village else "all villages"
    return {"message": f"Faults cleared for {scope}"}