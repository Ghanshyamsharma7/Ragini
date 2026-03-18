// src/components/SessionSelector.jsx
import { useState, useEffect } from "react";
import API from "../api/api";

// Cache config in module scope — fetched once per app session
let cachedConfig = null;

function SessionSelector({ className, subject, onClassChange, onSubjectChange, locked }) {
  const [classes, setClasses] = useState({});
  const [subjects, setSubjects] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Use cache if available
    if (cachedConfig) {
      setClasses(cachedConfig.classes);
      setSubjects(cachedConfig.subjects);
      setLoading(false);
      return;
    }

    API.get("/config/subjects")
      .then((res) => {
        cachedConfig = res.data;
        setClasses(res.data.classes);
        setSubjects(res.data.subjects);
      })
      .catch((err) => {
        console.error("Failed to load config:", err);
        setError("Failed to load classes");
      })
      .finally(() => setLoading(false));
  }, []);

  const classEntries = Object.entries(classes);
  const subjectEntries = Object.entries(subjects[className] || {});

  if (loading) {
    return (
      <div className="session-selector">
        <p className="selector-hint">Loading classes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="session-selector">
        <p className="selector-hint" style={{ color: "red" }}>{error}</p>
      </div>
    );
  }

  return (
    <div className="session-selector">
      <div className="selector-group">
        <label className="selector-label">Class</label>
        <select
          value={className}
          onChange={(e) => {
            onClassChange(e.target.value);
            // Reset subject when class changes
            onSubjectChange("");
          }}
          disabled={locked}
          className="selector-select"
        >
          <option value="">Select</option>
          {classEntries.map(([key, display]) => (
            <option key={key} value={key}>{display}</option>
          ))}
        </select>
      </div>

      <div className="selector-group">
        <label className="selector-label">Subject</label>
        <select
          value={subject}
          onChange={(e) => onSubjectChange(e.target.value)}
          disabled={!className || locked}
          className="selector-select"
        >
          <option value="">Select</option>
          {subjectEntries.map(([key, display]) => (
            <option key={key} value={key}>{display}</option>
          ))}
        </select>
      </div>

      {locked && (
        <span className="selector-locked-badge">Locked</span>
      )}
    </div>
  );
}

export default SessionSelector;