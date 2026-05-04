# 🚨 Incident Management System (IMS)

## 📌 Overview

This project is a simplified **Incident Management System** designed to simulate how large-scale distributed systems handle failures.

It ingests high-volume signals, groups them into incidents, tracks lifecycle, and enforces Root Cause Analysis (RCA) before closure.

---

## 🏗️ Architecture

```
[Frontend (React)]
        ↓
[FastAPI Backend]
        ↓
-------------------------
| In-Memory Storage     |
| (Incidents, Signals)  |
-------------------------
        ↓
[Simulated DB / Logs]
```

---

## ⚙️ Tech Stack

* Backend: Python, FastAPI
* Frontend: React.js
* Storage: In-memory (for simulation)
* API Testing: Swagger UI

---

## 🔥 Features Implemented

### ✅ Signal Ingestion

* High-frequency signal ingestion via `/ingest`
* Debouncing logic to group signals into incidents

### ✅ Incident Lifecycle

* OPEN → INVESTIGATING → RESOLVED → CLOSED
* RCA mandatory before closing

### ✅ RCA & MTTR

* Root Cause Analysis required
* MTTR (Mean Time To Repair) automatically calculated

### ✅ Severity Handling

* P0 → Database failures
* P1 → Cache failures
* P2 → Other components

### ✅ Dashboard

* Live incident feed
* Sorted by severity
* RCA details visible

### ✅ Observability

* `/health` endpoint
* Console metrics (signals count every 5 sec)

### ✅ Rate Limiting

* Prevents overload using request throttling

---

## 🚀 Setup Instructions

### 1. Clone Repository

```
git clone <your-repo-link>
cd incident-management-system
```

---

### 2. Backend Setup

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn
uvicorn main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000/docs
```

---

### 3. Frontend Setup

```
cd frontend
npm install
npm start
```

Frontend runs at:

```
http://localhost:3000
```

---

## 🧪 Sample Test Flow

1. Create Signal:

   * Component: `DB_MAIN`
   * Message: `Database crash`

2. View Incident in dashboard

3. Add RCA:

   * Root Cause: DB failure
   * Fix: Restart service

4. Close Incident

---

## ⚡ Backpressure Handling (Important)

* Implemented basic rate limiting (100 req/sec)
* Prevents system overload
* Ensures stability during bursts

---

## 📊 Metrics

* Signals count logged every 5 seconds
* Health endpoint available

---

## 🎯 Future Improvements

* Replace in-memory DB with PostgreSQL
* Add Redis for caching
* Use Kafka for real-time ingestion
* Implement authentication
* Improve UI/UX

---

## 👨‍💻 Author

Santhosha Mohananda
