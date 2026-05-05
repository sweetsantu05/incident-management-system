from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from time import time
from collections import deque
import asyncio
import random

app = FastAPI()

# In-memory structures
signal_queue = deque()     # Incoming signals (acts as buffer)
signals = []               # Raw signal log (for observability)
incidents = []             # Processed incidents (source of truth)

# Rate limiting variables
request_count = 0
start_time_window = time()

# Generate simple incremental IDs
def get_id():
    return len(incidents) + 1

def get_severity(component_id: str):
    if "DB" in component_id:
        return "P0"
    elif "CACHE" in component_id:
        return "P1"
    return "P2"


# Simulated database write with retry
def save_with_retry(incident):
    for _ in range(3):
        try:
            # Simulate occasional failure
            if random.random() < 0.2:
                raise Exception("Temporary DB failure")

            incidents.append(incident)
            return
        except:
            continue

    raise Exception("Failed to save incident after retries")
# def get_severity(component_id):
#     if "DB" in component_id:
#         return "P0"
#     elif "CACHE" in component_id:
#         return "P1"
#     return "P2"

# # severity = get_severity(component_id)

# API to ingest signals
@app.post("/ingest")
async def ingest_signal(component_id: str, message: str):
    global request_count, start_time_window

    current_time = time()

    # Reset rate counter every second
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

    # Add signal to queue for async processing
    signal_queue.append(signal)

    return {"message": "Signal queued"}


# Background worker to process signals
async def process_queue():
    while True:
        if signal_queue:
            signal = signal_queue.popleft()

            # Store raw signal for monitoring
            signals.append(signal)

            component_id = signal["component_id"]

            # Check if an active incident already exists
            existing = next(
                (i for i in incidents
                 if i["component_id"] == component_id and i["status"] != "CLOSED"),
                None
            )

            # if existing:
            #     last_signal_time = existing["signals"][-1]["timestamp"]

                # Debounce: group signals within 10 seconds
            if existing:
                if datetime.now() - existing["start_time"] < timedelta(seconds=10):
                    existing["signals"].append(signal)
                    continue

            # Create a new incident
            severity = get_severity(component_id)

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

            save_with_retry(incident)

        await asyncio.sleep(0.01)



# Periodically print throughput metrics
async def print_metrics():
    previous_count = 0

    while True:
        current_count = len(signals)
        rate = current_count - previous_count

        print(f"Signals processed per 5 seconds: {rate}")
        previous_count = current_count

        await asyncio.sleep(5)


# Start background workers
@app.on_event("startup")
async def startup_event():
    for _ in range(3):  # multiple workers for better throughput
        asyncio.create_task(process_queue())

    asyncio.create_task(print_metrics())


# Fetch all incidents
@app.get("/incidents")
async def get_incidents():
    return incidents


# Valid state transitions
valid_transitions = {
    "OPEN": ["INVESTIGATING"],
    "INVESTIGATING": ["RESOLVED"],
    "RESOLVED": ["CLOSED"]
}


# Update incident status
@app.put("/incident/{incident_id}/status")
async def update_status(incident_id: int, status: str):
    incident = next((i for i in incidents if i["id"] == incident_id), None)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    current_status = incident["status"]

    # Enforce valid transitions
    if status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {current_status} → {status}"
        )

    # Ensure RCA exists before closing
    if status == "CLOSED" and not incident["rca"]:
        raise HTTPException(status_code=400, detail="RCA required before closing")

    incident["status"] = status

    return {"message": f"Moved to {status}"}


# Add RCA and calculate MTTR
@app.post("/incident/{incident_id}/rca")
async def add_rca(
    incident_id: int,
    root_cause: str,
    fix: str,
    category: str = None,
    start: str = None,
    end: str = None,
    prevention: str = None
):
    # Find incident
    incident = next((i for i in incidents if i["id"] == incident_id), None)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Use current time as end_time (system recorded)
    end_time = datetime.now()

    # MTTR calculation
    mttr = (end_time - incident["start_time"]).total_seconds()

    # Store RCA with all fields
    incident["rca"] = {
        "root_cause": root_cause,
        "fix": fix,
        "category": category,
        "start": start,
        "end": end,
        "prevention": prevention,
        "time": end_time,
        "mttr_seconds": mttr
    }

    incident["end_time"] = end_time

    return {
        "message": "RCA added",
        "mttr_seconds": mttr
    }

# Basic health check
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "total_signals": len(signals),
        "total_incidents": len(incidents)
    }


# Root endpoint
@app.get("/")
def home():
    return {"message": "IMS Backend Running"}

@app.get("/metrics")
async def metrics():
    return {
        "total_signals": len(signals),
        "total_incidents": len(incidents),
    }


# Enable frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)