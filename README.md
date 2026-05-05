# 🚨 Incident Management System (IMS)

> A production-inspired system for ingesting, processing, and resolving incidents at scale — built with **FastAPI** and **React**.

---

## 📌 Overview

This project is a simplified **Incident Management System** inspired by real-world **Site Reliability Engineering (SRE)** practices.

In large-scale distributed systems, thousands of signals (errors, latency spikes, crashes) are generated continuously. This system demonstrates how such signals can be:

- 🚀 Ingested efficiently at scale
- ⚡ Buffered and processed asynchronously
- 🔗 Grouped into meaningful incidents
- 🔄 Managed through a structured lifecycle
- 🧠 Resolved using Root Cause Analysis (RCA)

The goal is to simulate how production systems maintain **reliability, stability, and observability under load**.

---

## 🏗️ Architecture

![Architecture Diagram](architecture.svg)

### System Flow

| Step | Component | Role |
|------|-----------|------|
| 1 | **Frontend (React Dashboard)** | Displays incidents, allows lifecycle actions, captures RCA inputs |
| 2 | **FastAPI Backend** | Handles ingestion, async processing, and workflow transitions |
| 3 | **Signal Queue** | Buffers incoming signals to prevent system overload |
| 4 | **Processing Engine** | Applies debounce logic and groups signals into incidents |
| 5 | **In-Memory Storage** | Stores raw signals (audit log) and structured incidents (source of truth) |
| 6 | **Observability Layer** | Health endpoint and throughput logging |

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React.js |
| Backend | FastAPI (Python) |
| Storage | In-Memory |
| API Docs | Swagger UI |

---

## 🚀 Getting Started

### Option 1 — Run Locally

#### 1. Clone the Repository

```bash
git clone <your-repo-link>
cd incident-management-system
```

#### 2. Set Up the Backend

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Install dependencies and start the server:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

> Backend running at: `http://127.0.0.1:8000`

#### 3. Set Up the Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm start
```

> Frontend running at: `http://localhost:3000`

---

### Option 2 — Run with Docker

#### `docker-compose.yml`

```yaml
version: "3.9"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
```

#### Start the Application

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Backend API Docs | `http://127.0.0.1:8000/docs` |
| Frontend Dashboard | `http://localhost:3000` |

---

## 🎯 Features

### 🚀 Core Capabilities

- High-throughput signal ingestion
- Async queue-based processing
- Debounce-based incident creation
- Severity-based prioritization: **P0 → P1 → P2**

### 🔄 Workflow Engine

```
OPEN → INVESTIGATING → RESOLVED → CLOSED
```

- Mandatory RCA before closure
- MTTR (Mean Time To Repair) calculation

### 🖥️ Frontend Dashboard

- 📡 Live incident feed (real-time polling)
- 🔥 Severity-based sorting
- 🔍 Expandable incident details with raw signals
- 📝 Structured RCA form:
  - Category, Start / End time
  - Root cause & fix applied
  - Prevention steps
- 📊 RCA detail view toggle
- 🔔 Toast notifications
- 🔄 Active / Closed incident views

---

## ⚡ Backpressure Handling

### 1 — Rate Limiting
Limits ingestion to **100 requests/sec** to prevent overload.

### 2 — Queue Processing
Async signal handling keeps the API non-blocking.

### 3 — Debounce Logic
Groups repeated signals to reduce noise and create cleaner incidents.

**Why it matters:**
- Prevents cascading failures
- Handles burst traffic gracefully
- Ensures system stability under load

---

## 🧪 Simulation & Sample Data

#### `sample_events.json`

```json
[
  { "component_id": "DB_MAIN",       "message": "Database connection timeout" },
  { "component_id": "DB_MAIN",       "message": "Database crash" },
  { "component_id": "CACHE_CLUSTER", "message": "Cache latency spike" },
  { "component_id": "MCP_SERVICE",   "message": "Service unavailable" }
]
```

#### Simulation Script

```python
import requests

events = [
    ("DB_MAIN",       "Database crash"),
    ("DB_MAIN",       "Timeout"),
    ("CACHE_CLUSTER", "Cache spike"),
    ("MCP_SERVICE",   "Service down"),
]

for comp, msg in events:
    requests.post(
        f"http://127.0.0.1:8000/ingest?component_id={comp}&message={msg}"
    )
```

---

## 🩺 Health Check

```
GET http://127.0.0.1:8000/health
```

---

## 🚀 Future Improvements

- [ ] PostgreSQL integration for persistent storage
- [ ] Redis caching layer
- [ ] Kafka streaming ingestion
- [ ] Authentication & RBAC
- [ ] Analytics dashboard

---

## 👨‍💻 Author

**Santhosha Mohananda**