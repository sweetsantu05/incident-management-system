from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import List
from time import time
import asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#for time line 

request_count = 0
start_time_window = time()

# In-memory storage (for simplicity)
signals = []
incidents = []


async def print_metrics():
    while True:
        print(f"Signals received: {len(signals)}")
        await asyncio.sleep(5)



# Simple ID generator
def get_id():
    return len(incidents) + 1

# ----------------------------
# 1. Ingest Signals
# ----------------------------
@app.post("/ingest")
async def ingest_signal(component_id: str, message: str):

    global request_count, start_time_window

    current_time = time()

    # reset every 1 second
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

    signals.append(signal)

    # Debounce logic (simplified)
    existing = next((i for i in incidents if i["component_id"] == component_id and i["status"] != "CLOSED"), None)

    if existing:
        existing["signals"].append(signal)
    else:
        incident = {
            "id": get_id(),
            "component_id": component_id,
            "status": "OPEN",
            "signals": [signal],
            "start_time": datetime.now(),
            "end_time": None,
            "rca": None
        }
        incidents.append(incident)

    return {"message": "Signal processed"}

# ----------------------------
# 2. Get Incidents
# ----------------------------
@app.get("/incidents")
async def get_incidents():
    return incidents

# ----------------------------
# 3. Update Status
# ----------------------------
@app.put("/incident/{incident_id}/status")
async def update_status(incident_id: int, status: str):

    incident = next((i for i in incidents if i["id"] == incident_id), None)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if status == "CLOSED":
        if not incident["rca"] or not incident["rca"].get("root_cause") or not incident["rca"].get("fix"):
            raise HTTPException(status_code=400, detail="Complete RCA required before closing")

    incident["status"] = status

    return {"message": "Status updated"}

# ----------------------------
# 4. Add RCA
# ----------------------------
@app.post("/incident/{incident_id}/rca")
async def add_rca(incident_id: int, root_cause: str, fix: str):

    incident = next((i for i in incidents if i["id"] == incident_id), None)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    end_time = datetime.now()

    # MTTR calculation
    mttr = (end_time - incident["start_time"]).total_seconds()

    incident["rca"] = {
        "root_cause": root_cause,
        "fix": fix,
        "time": end_time,
        "mttr_seconds": mttr
    }

    incident["end_time"] = end_time

    return {"message": "RCA added", "mttr_seconds": mttr}

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

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(print_metrics())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)