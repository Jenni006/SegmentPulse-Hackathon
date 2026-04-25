# SegmentPulse-Hackathon

**SegmentPulse** is an intelligent **Fiber Network Fault Diagnosis & Management System** designed for telecommunications infrastructure. It provides real-time network monitoring, automated fault detection, root cause analysis, and an intuitive dashboard for managing large-scale fiber optic networks across multiple districts and villages.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Fault Injection & Testing](#fault-injection--testing)
- [Components](#components)
- [Key Technologies](#key-technologies)
- [Contributing](#contributing)

---

## Overview

**SegmentPulse** addresses critical challenges in fiber network management by providing:

- **Real-time Network Status**: Monitor thousands of villages and network segments simultaneously
- **Intelligent Fault Detection**: Automated diagnosis of network failures with root cause analysis
- **Village-Level Diagnostics**: Drill down to segment-level health metrics (RTT, packet loss, status)
- **Historical Fault Tracking**: Track faults, resolutions, and system performance over time
- **Fault Simulation**: Test and demo fault scenarios to validate network response
- **Scalable Architecture**: Handle networks with 1000+ villages and 400,000+ subscribers

---

## Features

### Dashboard Features
1. **Network Overview Tab**
   - System-wide health summary (healthy/degraded/faulty villages)
   - District-level aggregation with color-coded status indicators
   - Click-to-drill functionality for village-level analysis
   - Real-time statistics: total villages, segments, subscribers, active faults

2. **Village Drill-Down Tab**
   - Per-village segment health monitoring
   - Fault injection simulation tool (CLI & UI)
   - Individual segment metrics (RTT, packet loss)
   - Test different fault types: fiber cuts, congestion, flapping, device failures

3. **Fault History Tab**
   - Complete audit trail of detected faults
   - Root cause analysis and confidence scores
   - Recommended actions and affected user counts
   - Timestamp-based historical analysis

### Backend Capabilities
- **Ping-Based Health Monitoring**: Continuous RTT and packet loss measurement
- **Fault Diagnosis Engine**: Analyzes network patterns to identify root causes
- **Multi-level Segmentation**:
  - Customer level (1 affected user)
  - ONT - Optical Network Terminal (1 affected user)
  - Splitter (8 affected users)
  - Aggregation Switch (32 affected users)
  - Core (1600 affected users)
  - Gateway (400,000 affected users)
- **SQLite Database**: Persistent fault history and network state tracking
- **RESTful API**: Full HTTP API for frontend communication

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React + TypeScript)          │
│         - Network Overview Dashboard                    │
│         - Village Drill-Down UI                         │
│         - Fault History Timeline                        │
└───────────────────┬─────────────────────────────────────┘
                    │ HTTP/REST
                    │
┌───────────────────▼─────────────────────────────────────┐
│              Backend (FastAPI + Python)                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Endpoints:                                     │   │
│  │  - /network-overview  (system health)          │   │
│  │  - /segment-health    (village details)        │   │
│  │  - /run-diagnosis     (fault detection)        │   │
│  │  - /history           (fault records)          │   │
│  │  - /simulate-fault    (testing/demo)          │   │
│  │  - /clear-faults      (reset state)            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Core Services:                                 │   │
│  │  - Ping3 Health Monitor                         │   │
│  │  - Diagnosis Engine (root cause analysis)      │   │
│  │  - SQLite Data Persistence                      │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              SQLite Database (segmentpulse.db)          │
│  - Network topology and segment hierarchy               │
│  - Historical fault records                             │
│  - Diagnosis results and metadata                       │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Frontend
- **React 18.3** - UI framework
- **TypeScript 5.5** - Type-safe JavaScript
- **Tailwind CSS 3.4** - Utility-first styling
- **Vite 5.4** - Build tool & dev server
- **Axios 1.13** - HTTP client
- **Lucide React 0.344** - Icon library
- **Supabase JS 2.57** - Optional backend support

### Backend
- **FastAPI 0.109** - High-performance Python web framework
- **Uvicorn 0.27** - ASGI server
- **Ping3 4.0** - Network diagnostics (ICMP ping)
- **Python-dotenv 1.0** - Environment variable management
- **SQLite** - Embedded database

### DevOps & Containerization
- **Docker** - Application containerization
- **Docker Compose** - Multi-container orchestration
- **Python 3.10** - Backend runtime

---

## Project Structure

```
SegmentPulse-Hackathon/
├── backend/
│   ├── main.py                    # FastAPI application (core logic)
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                 # Docker configuration
│   └── segmentpulse.db           # SQLite database
│
├── project/
│   ├── src/
│   │   ├── App.tsx                # Main application component
│   │   ├── types.ts               # TypeScript type definitions
│   │   ├── main.tsx               # React entry point
│   ��   ├── index.css              # Global styles
│   │   │
│   │   ├── components/
│   │   │   ├── Header.tsx          # Navigation & status header
│   │   │   ├── History.tsx         # Fault history display
│   │   │   ├── NetworkOverview/    # Overview tab components
│   │   │   ├── VillageDrillDown/   # Village detail components
│   │   │   └── FaultHistory/       # Historical data components
│   │   │
│   │   ├── hooks/
│   │   │   └── usePolling.ts       # Polling hook for API updates
│   │   │
│   │   ├── services/
│   │   │   └── api.ts              # API client & endpoints
│   │   │
│   │   └── types/
│   │       └── (TypeScript type definitions)
│   │
│   ├── index.html                 # HTML entry point
│   ├── package.json               # NPM dependencies
│   ├── vite.config.ts             # Vite configuration
│   ├── tailwind.config.js         # Tailwind CSS configuration
│   └── tsconfig.json              # TypeScript configuration
│
├── docker-compose.yml             # Docker Compose configuration
├── simulate.sh                    # Fault injection CLI tool
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

---

## Installation & Setup

### Prerequisites
- Docker & Docker Compose (recommended)
- **OR** Node.js 16+ & Python 3.10+
- Git

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/Jenni006/SegmentPulse-Hackathon.git
cd SegmentPulse-Hackathon

# Build and start all services
docker-compose up --build

# Services will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd project

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

---

## Usage

### Access the Dashboard
1. Open browser to **http://localhost:3000**
2. View real-time network status across districts and villages
3. Click on districts to drill down into village-level details
4. Inject faults to test system response

### Run Diagnosis
The frontend automatically polls for diagnosis results every 60 seconds. Manual API call:

```bash
curl -X POST http://localhost:8000/run-diagnosis
```

### Health Check
```bash
curl http://localhost:8000/health
```

---

## API Endpoints

### Network Status
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/network-overview` | GET | System-wide health overview with district/village status |
| `/segment-health?village={name}` | GET | Detailed health metrics for all segments in a village |
| `/districts` | GET | List all districts and their villages |

### Diagnostics
| Endpoint | Method | Description |
| `/run-diagnosis` | POST | Execute fault detection and root cause analysis |
| `/history` | GET | Retrieve historical fault records |
| `/health` | GET | API health check |

### Fault Testing (Demo/Development)
| Endpoint | Method | Parameters | Description |
|----------|--------|-----------|-------------|
| `/simulate-fault` | POST | `segment`, `fault_type` | Inject a fault for testing |
| `/clear-faults` | POST | - | Clear all injected faults |

#### Fault Types
- `fiber_cut` - Complete fiber break
- `congestion` - Link saturation
- `flapping` - Intermittent interface issues
- `device_failure` - Hardware failure

#### Example
```bash
# Inject fiber cut at Splitter
curl -X POST "http://localhost:8000/simulate-fault?segment=Splitter&fault_type=fiber_cut"

# Clear all faults
curl -X POST http://localhost:8000/clear-faults
```

---

## Fault Injection & Testing

### Using the CLI Tool

```bash
chmod +x simulate.sh
./simulate.sh
```

**Menu Options:**
```
SegmentPulse Fault Simulator
==============================
1. Fiber Cut @ Splitter
2. Congestion @ Agg Switch
3. Flapping @ ONT
4. Device Failure @ Core
5. Clear All Faults
```

### Programmatic Usage

```bash
# Inject fault via curl
curl -X POST "http://localhost:8000/simulate-fault?segment=Splitter&fault_type=fiber_cut"

# Run diagnosis to see results
curl -X POST http://localhost:8000/run-diagnosis

# Clear faults
curl -X POST http://localhost:8000/clear-faults
```

---

## Components Overview

### Frontend React Components

#### **App.tsx** (Main Application)
- Manages tab navigation (Overview, Villages, History)
- Handles polling for network data and diagnoses
- Manages fault injection callbacks
- Displays connection status indicators

#### **Header.tsx**
- Shows system name and logo
- Displays connection status (green = connected, red = error)
- Shows last update timestamp

#### **NetworkOverviewTab**
- Displays all districts with color-coded health status
- Summary statistics panel
- Interactive district selection

#### **VillageDrillDownTab**
- Shows segment-level health for selected village
- Fault injection UI
- Real-time RTT and packet loss metrics

#### **FaultHistoryTab**
- Timeline view of historical faults
- Root cause analysis display
- Recommended actions and affected user counts

### Type Definitions (types.ts)
```typescript
- SegmentStatus: 'HEALTHY' | 'DEGRADED' | 'FAILED'
- VillageStatus: 'HEALTHY' | 'DEGRADED' | 'FAULT'
- DiagnosisResult: Complete fault analysis with recommendations
- SegmentHealth: Individual segment metrics (RTT, packet loss)
- FaultHistoryItem: Historical fault record
```

---

## Key Technologies Deep Dive

### FastAPI Backend Architecture
- **Asynchronous Request Handling**: Non-blocking I/O for high concurrency
- **Automatic API Documentation**: Swagger UI at `/docs`, ReDoc at `/redoc`
- **Type Safety**: Pydantic models for request/response validation
- **CORS Support**: Cross-origin requests for frontend communication

### React Frontend Architecture
- **Component Composition**: Modular, reusable UI components
- **State Management**: React hooks (useState, useCallback, useEffect)
- **Polling Mechanism**: Custom `usePolling` hook for periodic API updates
- **Type Safety**: Full TypeScript implementation

### Network Diagnostics
- **ICMP Ping Monitoring**: Measures RTT and packet loss
- **Fault Simulation**: Injects synthetic network conditions for testing
- **Root Cause Analysis**: Maps observed metrics to specific fault types
- **Confidence Scoring**: Provides certainty levels for diagnosis

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is part of a hackathon submission. See LICENSE file for details.

---

## Contact

**Project Owner**: Jenni006  
**GitHub**: [Jenni006/SegmentPulse-Hackathon](https://github.com/Jenni006/SegmentPulse-Hackathon)

---

## Future Enhancements

- [ ] Multi-user authentication & role-based access control
- [ ] Advanced analytics and ML-based fault prediction
- [ ] Real-time alerting & notification system
- [ ] Integration with Network Management Systems (NMS)
- [ ] Multi-language support
- [ ] Mobile app for on-field diagnosis
- [ ] Automated remediation workflows
- [ ] Performance optimization for 10,000+ villages

---

**Last Updated**: April 2026  
**Version**: 1.0.0 (Hackathon Release)
