#!/bin/bash
# SegmentPulse Fault Injection Script
# Uses the /simulate-fault API endpoint for demo

API="http://localhost:8000"

echo "SegmentPulse Fault Simulator"
echo "=============================="
echo "1. Fiber Cut @ Splitter"
echo "2. Congestion @ Agg Switch"
echo "3. Flapping @ ONT"
echo "4. Device Failure @ Core"
echo "5. Clear All Faults"
echo ""
read -p "Choose (1-5): " choice

case $choice in
  1)
    curl -X POST "$API/simulate-fault?segment=Splitter&fault_type=fiber_cut"
    echo ""
    echo "Fiber Cut injected at Splitter"
    ;;
  2)
    curl -X POST "$API/simulate-fault?segment=Agg Switch&fault_type=congestion"
    echo ""
    echo "Congestion injected at Agg Switch"
    ;;
  3)
    curl -X POST "$API/simulate-fault?segment=ONT&fault_type=flapping"
    echo ""
    echo "Flapping injected at ONT"
    ;;
  4)
    curl -X POST "$API/simulate-fault?segment=Core&fault_type=device_failure"
    echo ""
    echo "Device Failure injected at Core"
    ;;
  5)
    curl -X POST "$API/clear-faults"
    echo ""
    echo "All faults cleared"
    ;;
  *)
    echo "Invalid choice"
    ;;
esac

echo ""
echo "Run diagnosis:"
echo "curl -X POST http://localhost:8000/run-diagnosis"
