from fastapi import FastAPI, HTTPException
from datetime import datetime
from time import time
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from collections import deque
import random

app = FastAPI()

# ----------------------------
# In-Memory Storage
# ----------------------------
signal_queue = deque()
signals = []       # Raw signal log (for observability)
incidents = []     # Processed incidents

# ----------------------------
# Rate Limiting
# ----------------------------
request_count = 0
start_time_window = time()

# ----------------------------
# Metrics
# ----------------------------
async def print_metrics():
    while True:
        print(f"Signals processed: {len(signals)}")
        await asyncio.sleep(5)

# ----------------------------
# ID Generator
# ----------------------------
def get_id():
    return len(incidents) + 1

# ----------------------------
# Retry Logic (Simulated DB Save)
# ----------------------------
def save_with_retry(incident):
    for _ in range(3):
        try:
            # Simulate random failure
            if random.random() < 0.2:
                raise Exception("Simulated DB failure")

            incidents.append(incident)
            return
        except:
            continue

    raise Exception("Failed to save incident after retries")

# ----------------------------
# 1. Ingest Signals (Producer)
# ----------------------------
@app.post("/ingest")
async def ingest_signal(component_id: str, message: str):

    global request_count, start_time_window

    current_time = time()

    if current_time - start_time_window > 1:
        request_count = 0
        start_time_window = current_time

    request_count += 1

    if request_count > 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    signal = {
        "component_id": component_id,
        "message": message,
        "timestamp": datetime.now()
    }

    # Push to queue (async processing)
    signal_queue.append(signal)

    return {"message": "Signal queued"}

# ----------------------------
# Queue Worker (Consumer)
# ----------------------------
async def process_queue():
    while True:
        if signal_queue:
            signal = signal_queue.popleft()

            # Store raw signal (observability)
            signals.append(signal)

            component_id = signal["component_id"]

            # Debounce logic
            existing = next(
                (i for i in incidents if i["component_id"] == component_id and i["status"] != "CLOSED"),
                None
            )

            if existing:
                existing["signals"].append(signal)

            else:
                # Severity assignment
                severity = "P2"
                if "DB" in component_id:
                    severity = "P0"
                elif "CACHE" in component_id:
                    severity = "P1"

                incident = {
                    "id": get_id(),
                    "component_id": component_id,
                    "severity": severity,
                    "status": "OPEN",
                    "signals": [signal],
                    "start_time": datetime.now(),
                    "end_time": None,
                    "rca": None
                }

                # Save with retry
                save_with_retry(incident)

        await asyncio.sleep(0.01)

# ----------------------------
# Startup Tasks
# ----------------------------
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_queue())
    asyncio.create_task(print_metrics())

# ----------------------------
# 2. Get Incidents
# ----------------------------
@app.get("/incidents")
async def get_incidents():
    return incidents

# ----------------------------
# 3. Update Status (State Machine)
# ----------------------------
valid_transitions = {
    "OPEN": ["INVESTIGATING"],
    "INVESTIGATING": ["RESOLVED"],
    "RESOLVED": ["CLOSED"]
}

@app.put("/incident/{incident_id}/status")
async def update_status(incident_id: int, status: str):

    incident = next((i for i in incidents if i["id"] == incident_id), None)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    current = incident["status"]

    if status not in valid_transitions.get(current, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {current} → {status}"
        )

    if status == "CLOSED" and not incident["rca"]:
        raise HTTPException(status_code=400, detail="RCA required")

    incident["status"] = status

    return {"message": f"Moved to {status}"}

# ----------------------------
# 4. Add RCA + MTTR
# ----------------------------
@app.post("/incident/{incident_id}/rca")
async def add_rca(incident_id: int, root_cause: str, fix: str):

    incident = next((i for i in incidents if i["id"] == incident_id), None)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    end_time = datetime.now()

    mttr = (end_time - incident["start_time"]).total_seconds()

    incident["rca"] = {
        "root_cause": root_cause,
        "fix": fix,
        "time": end_time,
        "mttr_seconds": mttr
    }

    incident["end_time"] = end_time

    return {"message": "RCA added", "mttr_seconds": mttr}

# ----------------------------
# Health & Root
# ----------------------------
@app.get("/")
def home():
    return {"message": "IMS Backend Running"}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "total_signals": len(signals),
        "total_incidents": len(incidents)
    }

# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)