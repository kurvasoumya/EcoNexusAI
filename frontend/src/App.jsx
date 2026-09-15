import { useState, useEffect } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const facilityDefaults = {
  food: "GreenCompost",
  plastic: "PlasticRecycle",
  paper: "PaperRecycle",
  metal: "MaterialRecovery",
  "e-waste": "EWasteFacility",
};

function App() {
  const [form, setForm] = useState({
    waste_type: "plastic",
    quantity_kg: 50,
    contamination: 10,
    source: "shopping_center",
    distance: 10,
    delivered_quantity: 50,
    actual_destination: "PlasticRecycle",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [facilities, setFacilities] = useState([]);
  const [facilityLoading, setFacilityLoading] = useState(true);

  const handleChange = (field, value) => {
    setForm((prev) => ({
      ...prev,
      [field]: value,
      ...(field === "waste_type"
        ? { actual_destination: facilityDefaults[value] || "" }
        : {}),
    }));
  };
 const loadFacilities = async () => {
  try {
    setFacilityLoading(true);

    const response = await fetch("http://127.0.0.1:8000/facilities");

    const data = await response.json();

    console.log("FACILITY DATA:", data);

    setFacilities(data.facilities);
  } catch (err) {
    console.error("FACILITY ERROR:", err);
  } finally {
    setFacilityLoading(false);
  }
};
const updateFacilityStatus = async (facilityName, newStatus) => {
  try {
    const response = await fetch(
      `${API_URL}/facility/update-status`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          facility_name: facilityName,
          new_status: newStatus,
        }),
      }
    );

    if (!response.ok) {
      throw new Error("Unable to update facility status.");
    }

    await loadFacilities();
  } catch (err) {
    console.error("Facility status update error:", err);
  }
};
const updateFacilityCapacity = async (facilityName, newCapacity) => {
  try {
    const response = await fetch(
      `${API_URL}/facility/update-capacity`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          facility_name: facilityName,
          new_capacity: newCapacity,
        }),
      }
    );

    if (!response.ok) {
      throw new Error("Unable to update facility capacity.");
    }

    await loadFacilities();
  } catch (err) {
    console.error("Facility capacity update error:", err);
  }
};

useEffect(() => {
  console.log("LOAD FACILITIES STARTED");
  loadFacilities();
}, []);
const processWaste = async () => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/process-waste`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...form,
          quantity_kg: Number(form.quantity_kg),
          contamination: Number(form.contamination),
          distance: Number(form.distance),
          delivered_quantity: Number(form.delivered_quantity),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        const validationMessage =
          Array.isArray(data.detail) && data.detail.length
            ? data.detail[0].msg
            : "Unable to process the waste.";

        throw new Error(validationMessage);
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message ||
          "Could not connect to EcoNexus AI. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-logo">🌱</div>
          <div>
            <h1>EcoNexus AI</h1>
            <p>Autonomous Waste-to-Resource Network</p>
          </div>
        </div>

        <div className="live-status">
          <span className="status-dot"></span>
          AI Network Online
        </div>
      </header>

      <main className="page">
        <section className="welcome">
          <div>
            <span className="eyebrow">SMART WASTE MANAGEMENT</span>
            <h2>Turn waste into a smarter resource journey.</h2>
            <p>
              Give EcoNexus the waste details and let the agent network
              analyze, decide, transport and verify the best recovery path.
            </p>
          </div>
          <div className="welcome-emoji">♻️</div>
        </section>
                <section className="dashboard-section">
          <div className="section-heading">
            <div className="heading-icon">📊</div>
            <div>
              <h3>EcoNexus Live Dashboard</h3>
              <p>Real-time overview of your waste management network.</p>
            </div>
          </div>

          <div className="dashboard-grid">
            <div className="dashboard-card">
              <span className="dashboard-icon">♻️</span>
              <div>
                <span className="dashboard-label">Waste Processed</span>
                <strong>{result ? `${result.quantity_kg} kg` : "0 kg"}</strong>
              </div>
            </div>

            <div className="dashboard-card">
              <span className="dashboard-icon">🏭</span>
              <div>
                <span className="dashboard-label">Active Facilities</span>
                <strong>
                  {facilities.filter(
                    (facility) => facility.status === "available"
                  ).length}
                  /{facilities.length}
                </strong>
              </div>
            </div>

            <div className="dashboard-card">
              <span className="dashboard-icon">🔄</span>
              <div>
                <span className="dashboard-label">Current Route</span>
                <strong>{result?.replan_required ? "Replanned" : "Direct"}</strong>
              </div>
            </div>

            <div className="dashboard-card">
              <span className="dashboard-icon">🌍</span>
              <div>
                <span className="dashboard-label">Environmental Impact</span>
                <strong>
                  {result?.environmental_impact || "Waiting"}
                </strong>
              </div>
            </div>

            <div className="dashboard-card">
              <span className="dashboard-icon">✅</span>
              <div>
                <span className="dashboard-label">Verification</span>
                <strong>
                  {result?.verification || "Waiting"}
                </strong>
              </div>
            </div>
          </div>
        </section>

        <section className="input-card">
          <div className="section-heading">
            <div className="heading-icon">📦</div>
            <div>
              <h3>Process Your Waste</h3>
              <p>Enter the information for the waste batch.</p>
            </div>
          </div>

          <div className="form-grid">
            <label>
              <span>Waste Type</span>
              <select
                value={form.waste_type}
                onChange={(e) =>
                  handleChange("waste_type", e.target.value)
                }
              >
                <option value="plastic">♻️ Plastic</option>
                <option value="food">🥬 Food</option>
                <option value="paper">📄 Paper</option>
                <option value="metal">🔩 Metal</option>
                <option value="e-waste">💻 E-Waste</option>
              </select>
            </label>

            <label>
              <span>Quantity (kg)</span>
              <input
                type="number"
                min="0"
                value={form.quantity_kg}
                onChange={(e) =>
                  handleChange("quantity_kg", e.target.value)
                }
              />
            </label>

            <label>
              <span>Contamination (%)</span>
              <input
                type="number"
                min="0"
                max="100"
                value={form.contamination}
                onChange={(e) =>
                  handleChange("contamination", e.target.value)
                }
              />
            </label>

            <label>
              <span>Source</span>
              <input
                type="text"
                value={form.source}
                onChange={(e) => handleChange("source", e.target.value)}
              />
            </label>

            <label>
              <span>Distance (km)</span>
              <input
                type="number"
                min="0"
                value={form.distance}
                onChange={(e) =>
                  handleChange("distance", e.target.value)
                }
              />
            </label>

            <label>
              <span>Delivered Quantity (kg)</span>
              <input
                type="number"
                min="0"
                value={form.delivered_quantity}
                onChange={(e) =>
                  handleChange("delivered_quantity", e.target.value)
                }
              />
            </label>

            <label className="wide-field">
              <span>Actual Destination</span>
              <input
                type="text"
                value={form.actual_destination}
                onChange={(e) =>
                  handleChange("actual_destination", e.target.value)
                }
              />
            </label>
          </div>

          <button
            className="process-btn"
            onClick={processWaste}
            disabled={loading}
          >
            {loading ? "🤖 EcoNexus is thinking..." : "🌿 Process Waste"}
          </button>

          {error && <div className="error-message">⚠️ {error}</div>}
        </section>
        <section className="facility-section">
  <div className="facility-header">
    <div>
      <span className="eyebrow">LIVE FACILITY NETWORK</span>
      <h2>🏭 Facility Network</h2>
      <p>Current facility availability and processing capacity.</p>
    </div>

    <button
      className="refresh-btn"
      onClick={loadFacilities}
      disabled={facilityLoading}
    >
      🔄 Refresh
    </button>
  </div>

  {facilityLoading ? (
    <div className="facility-loading">
      🤖 Loading facility network...
    </div>
  ) : facilities.length === 0 ? (
    <div className="facility-loading">
      ⚠️ No facility data available.
    </div>
  ) : (
    <div className="facility-grid">
      {facilities.map((facility) => (
        <div
          className={`facility-card ${
            facility.status !== "available" ? "facility-warning" : ""
          }`}
          key={facility.name}
        >
          <div className="facility-top">
            <span className="facility-icon">🏭</span>

            <span
              className={`facility-status ${
                facility.status === "available"
                  ? "available"
                  : "unavailable"
              }`}
            >
              {facility.status === "available" ? "🟢" : "🟠"}{" "}
              {facility.status}
            </span>
          </div>

          <h3>{facility.name}</h3>

          <p className="facility-type">
            ♻️ {facility.waste_type}
          </p>

          <div className="capacity-row">
            <span>Available Capacity</span>
            <strong>{facility.capacity} kg</strong>
          </div>

          <div className="capacity-bar">
            <div
              className="capacity-fill"
              style={{
                width: `${Math.min(
                  (facility.capacity / 1000) * 100,
                  100
                )}%`,
              }}
            ></div>
          </div>

         <div className="facility-process"> 
  ⚙️ {facility.accepted_processes.join(" • ")} 
</div>
<div className="facility-capacity-control">
 <input
  type="range"
  min="0"
  max="1000"
  step="50"
  value={Number(facility.capacity)}
  onChange={(e) => {
    const newCapacity = Number(e.target.value);

    setFacilities((prev) =>
      prev.map((item) =>
        item.name === facility.name
          ? { ...item, capacity: newCapacity }
          : item
      )
    );
  }}
  onMouseUp={(e) => {
    updateFacilityCapacity(
      facility.name,
      Number(e.target.value)
    );
  }}
  onTouchEnd={(e) => {
    updateFacilityCapacity(
      facility.name,
      Number(e.target.value)
    );
  }}
/>
  <div className="capacity-slider-label">
    <span>0 kg</span>
    <strong>{facility.capacity} kg</strong>
    <span>1000 kg</span>
  </div>
</div>

<div className="facility-controls">
  {facility.status === "available" ? (
    <button
      className="maintenance-btn"
      onClick={() =>
        updateFacilityStatus(facility.name, "maintenance")
      }
    >
      🔧 Set Maintenance
    </button>
  ) : (
    <button
      className="available-btn"
      onClick={() =>
        updateFacilityStatus(facility.name, "available")
      }
    >
      🟢 Set Available
    </button>
  )}
</div>

</div> 
))} 
    </div>
  )}
</section>
        {result && (
          <section className="results-area">
            <div className="results-title">
              <div>
                <span className="eyebrow">AI WORKFLOW RESULT</span>
                <h2>✨ Your EcoNexus Decision</h2>
              </div>

              <div
                className={`result-badge ${
                  result.replan_required ? "warning" : "success"
                }`}
              >
                {result.replan_required
                  ? "🔄 Replanned"
                  : "✅ Completed"}
              </div>
            </div>

            <section className="cards-grid">
              <InfoCard
                icon="🧠"
                title="Waste Intelligence"
                value={capitalize(result.waste_type)}
                text={`${result.quantity_kg} kg analyzed`}
              />

              <InfoCard
                icon="♻️"
                title="Recovery Decision"
                value={result.recovery_action || "Not available"}
                text="Recommended recovery pathway"
              />

              <InfoCard
                icon="🏭"
                title="Facility"
                value={result.facility || "No facility"}
                text={
                  result.replan_required
                    ? "Alternative facility selected"
                    : "Best available facility"
                }
              />

              <InfoCard
                icon="🚚"
                title="Transport"
                value={result.transport || "Not assigned"}
                text="Logistics plan generated"
              />

              <InfoCard
                icon="🌍"
                title="Environmental Impact"
                value={result.environmental_impact || "Not available"}
                text="Estimated environmental impact"
              />

              <InfoCard
                icon="✅"
                title="Verification"
                value={result.verification || "Pending"}
                text={
                  result.replan_required
                    ? "Replanned route verification"
                    : "Original route verified"
                }
              />
            </section>
          <section className="rag-section">
            <div className="rag-header">
              <div>
                <span className="eyebrow">AI KNOWLEDGE RETRIEVAL</span>
                <h3>📚 Knowledge Used by EcoNexus</h3>
                <p>
                  Information retrieved by the RAG Knowledge Agent for this decision.
                </p>
              </div>
            </div>

  <div className="rag-grid">
    {(result.rag_knowledge || []).map((item, index) => (
      <div className="rag-card" key={`${item.source}-${index}`}>
        <div className="rag-source">
          📄 {item.source}
        </div>

        <p>{item.content}</p>

        <span className="rag-badge">
          🤖 Retrieved by RAG Agent
        </span>
      </div>
    ))}
  </div>
</section>

            <section className="journey-card">
              <div className="journey-header">
                <div>
                  <span className="eyebrow">AGENTIC WORKFLOW</span>
                  <h3>🤖 AI Agent Journey</h3>
                </div>
                <span className="journey-pill">7 Agents</span>
              </div>

              <div className="agent-grid">
                <Agent icon="🧠" name="Waste Intelligence" />
                <Agent icon="📚" name="RAG Knowledge" />
                <Agent icon="♻️" name="Resource Recovery" />
                <Agent icon="🏭" name="Facility" />
                <Agent icon="🌍" name="Environment" />
                <Agent icon="🚚" name="Logistics" />
                <Agent icon="🔍" name="Verification" />
              </div>
            </section>
            <section className="alerts-section">
  <div className="section-heading">
    <div className="heading-icon">🚨</div>
    <div>
      <h3>Smart Alerts</h3>
      <p>EcoNexus recommendations and system alerts.</p>
    </div>
  </div>

  <div className="alerts-grid">
    {Number(form.contamination) > 40 && (
      <div className="alert-card warning-alert">
        <span className="alert-icon">⚠️</span>
        <div>
          <strong>High Contamination</strong>
          <p>
            This waste batch has {form.contamination}% contamination.
            Pre-treatment may be required before recovery.
          </p>
        </div>
      </div>
    )}

    {result.replan_required && (
      <div className="alert-card danger-alert">
        <span className="alert-icon">🚨</span>
        <div>
          <strong>Facility Alert</strong>
          <p>
            The original route could not be completed.
            EcoNexus activated autonomous replanning.
          </p>
        </div>
      </div>
    )}

    {result.environmental_impact === "High Impact" && (
      <div className="alert-card danger-alert">
        <span className="alert-icon">🌍</span>
        <div>
          <strong>Environmental Alert</strong>
          <p>
            The selected pathway has a high estimated environmental impact.
          </p>
        </div>
      </div>
    )}

    {Number(form.contamination) <= 40 &&
      !result.replan_required &&
      result.environmental_impact !== "High Impact" && (
        <div className="alert-card success-alert">
          <span className="alert-icon">🌱</span>
          <div>
            <strong>System Recommendation</strong>
            <p>
              Current waste conditions are suitable for the selected
              recovery pathway.
            </p>
          </div>
        </div>
      )}
  </div>
</section>

{result.replan_required && (
  <section className="replan-card">
    <div className="replan-title">
      <span className="replan-main-icon">🔄</span>
      <div>
        <span className="eyebrow">AUTONOMOUS FALLBACK</span>
        <h3>EcoNexus Replanned the Journey</h3>
        <p>The Manager Agent detected a problem and selected an alternative pathway.</p>
      </div>
    </div>

    <div className="replan-flow">
      <div className="flow-step failed">
        <span>❌</span>
        <strong>Original Plan</strong>
        <small>
          {result.facility || "Original facility"} unavailable
        </small>
      </div>

      <div className="flow-arrow">→</div>

      <div className="flow-step thinking">
        <span>🤖</span>
        <strong>Manager Agent</strong>
        <small>Re-evaluating options</small>
      </div>

      <div className="flow-arrow">→</div>

      <div className="flow-step thinking">
        <span>🔄</span>
        <strong>Replanning</strong>
        <small>Alternative pathway selected</small>
      </div>

      <div className="flow-arrow">→</div>

      <div className="flow-step complete">
        <span>✅</span>
        <strong>New Plan</strong>
        <small>{result.facility || "Alternative facility"}</small>
      </div>
    </div>
  </section>
)}
            <section className="final-card">
              <div className="final-badge">🎯 FINAL DECISION</div>

              <h2>{result.recovery_action || "Processing completed"}</h2>

              <div className="final-details">
                <div>
                  <span>🏭</span>
                  <strong>{result.facility || "N/A"}</strong>
                </div>

                <div>
                  <span>🚚</span>
                  <strong>{result.transport || "N/A"}</strong>
                </div>

                <div>
                  <span>
                    {result.verification === "verified" ? "✅" : "⚠️"}
                  </span>
                  <strong>
                    {result.verification || "Not verified"}
                  </strong>
                </div>
              </div>

              <p>{result.message}</p>
            </section>
          </section>
        )}
      </main>
    </div>
  );
}

function InfoCard({ icon, title, value, text }) {
  return (
    <article className="info-card">
      <div className="info-icon">{icon}</div>
      <div className="info-title">{title}</div>
      <div className="info-value">{value}</div>
      <div className="info-text">{text}</div>
    </article>
  );
}

function Agent({ icon, name }) {
  return (
    <div className="agent-item">
      <span className="agent-icon">{icon}</span>
      <span>{name}</span>
      <span className="agent-check">✓</span>
    </div>
  );
}

function capitalize(value) {
  if (!value) return "";
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export default App;