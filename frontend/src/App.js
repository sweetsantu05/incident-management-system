import React, { useEffect, useState } from "react";

function App() {
  const [incidents, setIncidents] = useState([]);
  const [component, setComponent] = useState("");
  const [message, setMessage] = useState("");
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [showRCAForm, setShowRCAForm] = useState(null);
  const [showRCADetails, setShowRCADetails] = useState(null);
  const [rcaData, setRcaData] = useState({
  root: "",
  fix: "",
  category: "",
  start: "",
  end: "",
  prevention: ""
  });
  const [view, setView] = useState("ACTIVE");
  const [toast, setToast] = useState("");
  

  // Toast helper
  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(""), 3000);
  };

  // Fetch incidents
  const fetchIncidents = async () => {
    const res = await fetch("http://127.0.0.1:8000/incidents");
    const data = await res.json();

    const priority = { P0: 1, P1: 2, P2: 3 };

    const sorted = data.sort(
      (a, b) => priority[a.severity] - priority[b.severity]
    );

    setIncidents(sorted);
  };

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 3000);
    return () => clearInterval(interval);
  }, []);

  // Status steps
  const getStatusSteps = (current) => {
    const steps = ["OPEN", "INVESTIGATING", "RESOLVED", "CLOSED"];
    return steps.map((step) => ({
      name: step,
      active: step === current,
      completed: steps.indexOf(step) < steps.indexOf(current),
    }));
  };

  // Send signal
  const sendSignal = async () => {
    if (!component || !message) {
      showToast("⚠️ Enter Component & Message");
      return;
    }

    await fetch(
      `http://127.0.0.1:8000/ingest?component_id=${component}&message=${message}`,
      { method: "POST" }
    );

    showToast("✅ Incident Created");
    setComponent("");
    setMessage("");
    fetchIncidents();
  };

  const updateStatus = async (id, status) => {
    await fetch(
      `http://127.0.0.1:8000/incident/${id}/status?status=${status}`,
      { method: "PUT" }
    );
    showToast(`Moved to ${status}`);
    fetchIncidents();
  };

  const closeIncident = async (id) => {
    const res = await fetch(
      `http://127.0.0.1:8000/incident/${id}/status?status=CLOSED`,
      { method: "PUT" }
    );

    const data = await res.json();

    if (!res.ok) {
      showToast(data.detail);
    } else {
      showToast("Incident Closed");
    }

    fetchIncidents();
  };

  const submitRCA = async (id) => {
    if (!rcaData.root || !rcaData.fix) {
      showToast("Fill all RCA fields");
      return;
    }

    await fetch(
    `http://127.0.0.1:8000/incident/${id}/rca?root_cause=${rcaData.root}&fix=${rcaData.fix}&category=${rcaData.category}&start=${rcaData.start}&end=${rcaData.end}&prevention=${rcaData.prevention}`,
    { method: "POST" }
  );

    showToast("RCA Added");
    setShowRCAForm(null);
    setRcaData({ root: "", fix: "" });
    fetchIncidents();
  };

  const filteredIncidents =
    view === "ACTIVE"
      ? incidents.filter((i) => i.status !== "CLOSED")
      : incidents.filter((i) => i.status === "CLOSED");

  return (
    <div
      style={{
        padding: "20px",
        fontFamily: "Arial",
        background: "#f5f7fa",
        minHeight: "100vh",
      }}
    >
      {/* Toast */}
      {toast && (
        <div
          style={{
            position: "fixed",
            top: "20px",
            right: "20px",
            background: "#2ecc71",
            color: "#fff",
            padding: "10px 15px",
            borderRadius: "6px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
          }}
        >
          {toast}
        </div>
      )}

      <h1 style={{ color: "#222e39", fontSize: "40px", marginBottom: "1" }}>
        Incident Dashboard
      </h1>

      {/* Input Card */}
      <div
        style={{
          background: "#fff",
          padding: "20px",
          borderRadius: "10px",
          marginBottom: "20px",
          boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
          display: "flex",
          gap: "10px",
        }}
      >
        <input
          placeholder="Component"
          value={component}
          onChange={(e) => setComponent(e.target.value)}
          style={{ padding: "10px", flex: 1 }}
        />
        <input
          placeholder="Message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          style={{ padding: "10px", flex: 1 }}
        />
        <button
          onClick={sendSignal}
          style={{
            background: "#3498db",
            color: "#fff",
            border: "none",
            padding: "10px 15px",
            borderRadius: "6px",
          }}
        >
          Send
        </button>
      </div>

      {/* Toggle */}
      <div style={{ marginBottom: "15px" }}>
        <button
          onClick={() => setView("ACTIVE")}
          style={{
            padding: "8px 15px",
            background: view === "ACTIVE" ? "#3498db" : "#ddd",
            color: view === "ACTIVE" ? "#fff" : "#000",
            border: "none",
            borderRadius: "6px",
          }}
        >
          Active
        </button>

        <button
          onClick={() => setView("CLOSED")}
          style={{
            padding: "8px 15px",
            marginLeft: "10px",
            background: view === "CLOSED" ? "#2ecc71" : "#ddd",
            color: view === "CLOSED" ? "#fff" : "#000",
            border: "none",
            borderRadius: "6px",
          }}
        >
          Closed
        </button>
      </div>

      <h2>
        {view} Incidents ({filteredIncidents.length})
      </h2>

      {/* Cards */}
      {filteredIncidents.map((inc) => (
        <div
          key={inc.id}
          onClick={() =>
            setSelectedIncident(selectedIncident === inc.id ? null : inc.id)
          }
          style={{
            background: "#fff",
            margin: "12px 0",
            padding: "18px",
            borderRadius: "10px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
            cursor: "pointer",
          }}
        >
          <h3>Incident #{inc.id}</h3>

          <p><b>Component:</b> {inc.component_id}</p>

          <p>
            <b>Severity:</b>{" "}
            <span
              style={{
                background:
                  inc.severity === "P0"
                    ? "red"
                    : inc.severity === "P1"
                    ? "orange"
                    : "gray",
                color: "#fff",
                padding: "4px 8px",
                borderRadius: "5px",
              }}
            >
              {inc.severity}
            </span>
          </p>

          {/* Status bar */}
          <div style={{ display: "flex", marginBottom: "10px" }}>
            {getStatusSteps(inc.status).map((step, i) => (
              <div
                key={i}
                style={{
                  padding: "5px 10px",
                  marginRight: "5px",
                  borderRadius: "5px",
                  fontSize: "12px",
                  backgroundColor: step.active
                    ? "#3498db"
                    : step.completed
                    ? "#2ecc71"
                    : "#ddd",
                  color: "#fff",
                }}
              >
                {step.name}
              </div>
            ))}
          </div>

          <p><b>Signals:</b> {inc.signals.length}</p>

          {/* RCA */}
          {inc.rca && (
  <div style={{ marginTop: "10px" }}>
    
    {/* Toggle Button */}
    <button
      onClick={(e) => {
        e.stopPropagation();
        setShowRCADetails(
          showRCADetails === inc.id ? null : inc.id
        );
      }}
      style={{
        background: "#2ecc71",
        color: "#fff",
        border: "none",
        padding: "6px 10px",
        borderRadius: "5px",
        cursor: "pointer"
      }}
    >
      {showRCADetails === inc.id ? "Hide RCA" : "View RCA Details"}
    </button>

    {/* Expanded RCA Details */}
    {showRCADetails === inc.id && (
      <div
        style={{
          marginTop: "10px",
          padding: "10px",
          background: "#ecf9f1",
          borderRadius: "6px"
        }}
      >
        <p><b>Category:</b> {inc.rca.category || "N/A"}</p>
        <p><b>Start Time:</b> {inc.rca.start || "N/A"}</p>
        <p><b>End Time:</b> {inc.rca.end || "N/A"}</p>
        <p><b>Root Cause:</b> {inc.rca.root_cause}</p>
        <p><b>Fix:</b> {inc.rca.fix}</p>
        <p><b>Prevention:</b> {inc.rca.prevention || "N/A"}</p>
      </div>
    )}
  </div>
)}
          {/* Actions */}
          <div style={{ marginTop: "10px" }}>
            <button
              disabled={inc.status !== "OPEN"}
              onClick={(e) => {
                e.stopPropagation();
                updateStatus(inc.id, "INVESTIGATING");
              }}
            >
              Investigate
            </button>

            <button
              disabled={inc.status !== "INVESTIGATING"}
              onClick={(e) => {
                e.stopPropagation();
                updateStatus(inc.id, "RESOLVED");
              }}
            >
              Resolve
            </button>

            <button
              disabled={inc.status !== "RESOLVED" || inc.rca}
              onClick={(e) => {
                e.stopPropagation();
                setShowRCAForm(inc.id);
              }}
            >
              Add RCA
            </button>

            <button
              disabled={inc.status !== "RESOLVED" || !inc.rca}
              onClick={(e) => {
                e.stopPropagation();
                closeIncident(inc.id);
              }}
            >
              Close
            </button>
          </div>

          {/* RCA Form */}
          {showRCAForm === inc.id && (
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              marginTop: "12px",
              padding: "12px",
              border: "1px solid #ddd",
              borderRadius: "8px",
              backgroundColor: "#fafafa",
              display: "flex",
              flexDirection: "column",
              gap: "10px",
            }}
          >
            <h4 style={{ margin: 0 }}>RCA Form</h4>

            {/* Category */}
            <label style={{ fontSize: "13px" }}>Root Cause Category</label>
            <select
              value={rcaData.category || ""}
              onChange={(e) =>
                setRcaData({ ...rcaData, category: e.target.value })
              }
              style={{
                padding: "8px",
              borderRadius: "5px",
              border: "1px solid #ccc",
            }}
          >
            <option value="">Select Category</option>
            <option value="Infrastructure">Infrastructure</option>
            <option value="Application">Application</option>
            <option value="Network">Network</option>
          </select>

          {/* Start Time */}
          <label style={{ fontSize: "13px" }}>Incident Start Time</label>
          <input
            type="datetime-local"
            value={rcaData.start || ""}
            onChange={(e) =>
              setRcaData({ ...rcaData, start: e.target.value })
            }
            style={{
              padding: "8px",
              borderRadius: "5px",
              border: "1px solid #ccc",
            }}
          />

          {/* End Time */}
          <label style={{ fontSize: "13px" }}>Incident End Time</label>
          <input
            type="datetime-local"
            value={rcaData.end || ""}
            onChange={(e) =>
              setRcaData({ ...rcaData, end: e.target.value })
            }
            style={{
              padding: "8px",
              borderRadius: "5px",
              border: "1px solid #ccc",
            }}
          />

          {/* Root Cause */}
          <label style={{ fontSize: "13px" }}>Root Cause</label>
          <input
            placeholder="Describe root cause"
            value={rcaData.root}
            onChange={(e) =>
              setRcaData({ ...rcaData, root: e.target.value })
            }
            style={{
              padding: "8px",
              borderRadius: "5px",
              border: "1px solid #ccc",
            }}
          />

          {/* Fix */}
          <label style={{ fontSize: "13px" }}>Fix Applied</label>
          <textarea
            placeholder="Describe fix"
            value={rcaData.fix}
            onChange={(e) =>
              setRcaData({ ...rcaData, fix: e.target.value })
            }
            style={{
              padding: "8px",
              borderRadius: "5px",
              border: "1px solid #ccc",
              minHeight: "80px",
            }}
          />

          {/* Prevention */}
          <label style={{ fontSize: "13px" }}>Prevention Steps</label>
          <textarea
            placeholder="How will this be prevented?"
            onChange={(e) =>
              setRcaData({ ...rcaData, prevention: e.target.value })
            }
            style={{
              padding: "8px",
              borderRadius: "5px",
              border: "1px solid #ccc",
              minHeight: "60px",
            }}
          />

          {/* Submit */}
          <button
            onClick={() => submitRCA(inc.id)}
            style={{
              alignSelf: "flex-end",
              backgroundColor: "#2ecc71",
              color: "#fff",
              border: "none",
              padding: "6px 12px",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            Submit RCA
          </button>
        </div>
      )}
             
        </div>
      ))}
    </div>
  );
}

export default App;