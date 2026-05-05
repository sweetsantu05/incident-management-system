🚨 Incident Management System (IMS)
📌 Overview

This project is a simplified Incident Management System inspired by real-world Site Reliability Engineering (SRE) practices.

In large-scale distributed systems, thousands of signals (errors, latency spikes, crashes) are generated continuously. This system demonstrates how such signals can be:

Ingested efficiently at scale
Buffered and processed asynchronously
Grouped into meaningful incidents
Managed through a lifecycle
Resolved using structured Root Cause Analysis (RCA)

The goal is to simulate how production systems maintain reliability, stability, and observability under load.

🏗️ Architecture Diagram

🧠 Architecture Explanation
🔄 System Flow
Frontend (React Dashboard)
Displays incidents, allows lifecycle actions, and captures RCA inputs.
FastAPI Backend
Handles ingestion, async processing, and workflow transitions.
Signal Queue (Backpressure Buffer)
Buffers incoming signals to prevent system overload.
Processing Engine
Applies debounce logic and groups signals into incidents.
In-Memory Storage
Raw signals (audit log)
Structured incidents (source of truth)
Observability Layer
Provides health checks and throughput logging.
⚙️ Tech Stack
Layer	Technology
Frontend	React.js
Backend	FastAPI
Storage	In-memory
API Docs	Swagger UI
🚀 Running the Project
🔧 Option 1: Run Locally (Recommended)
1. Clone Repository
git clone <your-repo-link>
cd incident-management-system
2. Backend Setup
cd backend
python -m venv venv

Activate environment:

Windows:

venv\Scripts\activate

Mac/Linux:

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Run backend:

uvicorn main:app --reload

👉 Backend:

http://127.0.0.1:8000
3. Frontend Setup

Open new terminal:

cd frontend
npm install
npm start

👉 Frontend:

http://localhost:3000
🐳 Option 2: Run with Docker
docker-compose.yml
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
Run Application
docker-compose up --build
Access

Backend:

http://127.0.0.1:8000/docs

Frontend:

http://localhost:3000
🎯 Features
🚀 Core Features
High-throughput signal ingestion
Async queue-based processing
Debounce-based incident creation
Severity-based prioritization (P0, P1, P2)
🔄 Workflow Engine

Incident lifecycle:

OPEN → INVESTIGATING → RESOLVED → CLOSED
Mandatory RCA enforcement before closure
MTTR (Mean Time To Repair) calculation
🖥️ Frontend (Dashboard)
Live incident feed (real-time polling)
Severity-based sorting
Expandable incident details (raw signals)
Structured RCA form:
Category
Start / End time
Root cause
Fix applied
Prevention steps
RCA detail view toggle
Toast notifications
Active / Closed incident views
⚡ Backpressure Handling
1. Rate Limiting
Limits ingestion to 100 requests/sec
Prevents API overload
2. Queue-Based Processing
Signals added to queue
Processed asynchronously
Prevents blocking
3. Debounce Logic
Groups repeated signals into one incident
Reduces noise
✅ Why It Matters
Prevents cascading failures
Handles burst traffic
Improves system stability
🧪 Sample Data (Simulation)
sample_events.json
[
  {"component_id": "DB_MAIN", "message": "Database connection timeout"},
  {"component_id": "DB_MAIN", "message": "Database crash"},
  {"component_id": "CACHE_CLUSTER", "message": "Cache latency spike"},
  {"component_id": "MCP_SERVICE", "message": "Service unavailable"}
]
Simulation Script
import requests

events = [
    ("DB_MAIN", "Database crash"),
    ("DB_MAIN", "Timeout"),
    ("CACHE_CLUSTER", "Cache spike"),
    ("MCP_SERVICE", "Service down")
]

for comp, msg in events:
    requests.post(
        f"http://127.0.0.1:8000/ingest?component_id={comp}&message={msg}"
    )
🩺 Health Check
http://127.0.0.1:8000/health
🧾 AI Prompts / Design Inputs
System Design

Design a scalable incident management system with async ingestion and RCA enforcement.

Backend

Implement FastAPI ingestion with queue processing and rate limiting.

Frontend

Build a React dashboard with real-time updates and RCA workflow.

🚀 Future Improvements
PostgreSQL integration
Redis caching
Kafka streaming ingestion
Authentication & RBAC
Advanced analytics dashboard
👨‍💻 Author

Santhosha Mohananda