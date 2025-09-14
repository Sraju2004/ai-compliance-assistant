import React, { useState } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import { FaUpload, FaFileAlt, FaChartBar, FaCheckCircle, FaTimes } from "react-icons/fa";
import "./App.css";

const SAMPLE_KEYS = [
  { key: "compliant", label: "Synthetic_SOP_Compliant.DOCX" },
  { key: "missing_sections", label: "Synthetic_SOP_Missing_Sections.DOCX" },
  { key: "outdated_refs", label: "Synthetic_SOP_Outdated_References.DOCX" },
  { key: "placeholder", label: "Synthetic_SOP_Placeholder.DOCX" }
];

// Severity badge with modern colors
const SeverityBadge = ({ severity }) => {
  let colorClass = "badge-secondary";
  if (severity === "Critical") colorClass = "badge-critical";
  else if (severity === "Major") colorClass = "badge-major";
  else if (severity === "Minor") colorClass = "badge-minor";

  return <span className={`badge ${colorClass} me-2`}>{severity}</span>;
};

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [raw, setRaw] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [activeTab, setActiveTab] = useState("upload");

  const backendUrl = "http://127.0.0.1:8000";

  // Handle file selection
  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setMessage("");
    setAnalysis(null);
    setRaw(null);
  };

  // Upload file and analyze
  const uploadAndAnalyze = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setMessage("Please choose a DOCX or PDF file first.");
      return;
    }

    setLoading(true);
    const fd = new FormData();
    fd.append("file", selectedFile);

    try {
      const res = await axios.post(`${backendUrl}/analyze`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 120000
      });

      if (res.data.analysis) {
        setAnalysis(res.data.analysis);
        setRaw(null);
        setActiveTab("results");
      } else if (res.data.analysis_raw) {
        setRaw(res.data.analysis_raw);
        setAnalysis(null);
        setActiveTab("results");
      } else {
        setMessage("Unexpected backend response.");
      }
    } catch (err) {
      setMessage("Upload/analysis failed: " + (err.response?.data?.error || err.message));
    }

    setLoading(false);
  };

  // Analyze using sample files
  const analyzeSample = async (sampleKey) => {
    setLoading(true);
    setAnalysis(null);
    setRaw(null);
    setMessage("");

    try {
      const res = await axios.post(
        `${backendUrl}/analyze-sample`,
        { sample_key: sampleKey },
        { timeout: 120000 }
      );

      if (res.data.analysis) {
        setAnalysis(res.data.analysis);
        setActiveTab("results");
      } else if (res.data.analysis_raw) {
        setRaw(res.data.analysis_raw);
        setActiveTab("results");
      } else if (res.data.error) {
        setMessage("Backend error: " + res.data.error);
      } else {
        setMessage("Unexpected backend response.");
      }
    } catch (err) {
      setMessage("Sample analysis failed: " + (err.response?.data?.error || err.message));
    }

    setLoading(false);
  };

  return (
    <div className="compliance-app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-text">
            <h1>AI-Powered Compliance Assistant for Healthtech Documentation</h1>
            <p>Analyze SOP documents against FDA regulations</p>
          </div>
          <div className="header-logo">
            <img src="jade-logo.png" alt="Jade Logo" className="logo-img" />
          </div>
        </div>
      </header>

      <div className="app-container">
        <div className="tabs-container">
          <div className="tabs">
            <button 
              className={`tab ${activeTab === "upload" ? "active" : ""}`}
              onClick={() => setActiveTab("upload")}
            >
              <FaUpload className="tab-icon" />
              Upload Document
            </button>
            <button 
              className={`tab ${activeTab === "samples" ? "active" : ""}`}
              onClick={() => setActiveTab("samples")}
            >
              <FaFileAlt className="tab-icon" />
              Sample Files
            </button>
            <button 
              className={`tab ${activeTab === "results" ? "active" : ""}`}
              onClick={() => setActiveTab("results")}
            >
              <FaChartBar className="tab-icon" />
              Analysis Results
            </button>
          </div>
        </div>

        <div className="tab-content">
          {activeTab === "upload" && (
            <div className="upload-section fade-in">
              <div className="card shadow-lg border-0 p-4 modern-card">
                <h5 className="mb-3 card-title">
                  <FaUpload className="title-icon" />
                  Upload SOP (DOCX / PDF)
                </h5>
                
                <form onSubmit={uploadAndAnalyze} className="upload-form">
                  <div className="file-upload-area">
                    <input 
                      type="file"
                      accept=".docx,.pdf"
                      className="file-input"
                      onChange={handleFileChange}
                      id="file-upload"
                    />
                    <label htmlFor="file-upload" className="file-upload-label">
                      <div className="upload-placeholder">
                        <FaUpload className="upload-icon" />
                        <p className="upload-text">Drag & drop your file here or click to browse</p>
                        <span className="upload-subtext">Supports DOCX and PDF files</span>
                      </div>
                    </label>
                  </div>
                  
                  {selectedFile && (
                    <div className="selected-file slide-up">
                      <div className="file-info">
                        <FaFileAlt className="file-icon" />
                        <span className="file-name">{selectedFile.name}</span>
                      </div>
                      <button 
                        type="button" 
                        className="remove-file-btn"
                        onClick={() => setSelectedFile(null)}
                      >
                        <FaTimes />
                      </button>
                    </div>
                  )}
                  
                  <button
                    type="submit"
                    className={`analyze-btn ${selectedFile ? "active" : ""} ${loading ? "analyzing" : ""}`}
                    disabled={!selectedFile || loading}
                  >
                    {loading ? (
                      <>
                        <div className="spinner"></div>
                        Analyzing...
                      </>
                    ) : (
                      "Upload & Analyze"
                    )}
                  </button>
                </form>

                {message && (
                  <div className={`alert mt-3 ${message.includes("failed") ? "alert-error" : "alert-warning"}`}>
                    {message}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "samples" && (
            <div className="samples-section fade-in">
              <div className="card shadow-lg border-0 p-4 modern-card">
                <h5 className="mb-3 card-title">
                  <FaFileAlt className="title-icon" />
                  Analyze a sample SOP
                </h5>
                
                <div className="sample-list">
                  {SAMPLE_KEYS.map((s) => (
                    <div key={s.key} className="sample-item">
                      <div className="sample-icon-container">
                        <FaFileAlt className="sample-icon" />
                      </div>
                      <div className="sample-info">
                        <h6>{s.label}</h6>
                      </div>
                      <button 
                        className="use-sample-btn"
                        onClick={() => analyzeSample(s.key)}
                        disabled={loading}
                      >
                        {loading ? "Processing..." : "Use This Sample"}
                      </button>
                    </div>
                  ))}
                </div>
                
                {message && (
                  <div className={`alert mt-3 ${message.includes("failed") ? "alert-error" : "alert-warning"}`}>
                    {message}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "results" && (
            <div className="results-section fade-in">
              <div className="card shadow-lg border-0 p-4 modern-card">
                <h5 className="mb-3 card-title">
                  <FaChartBar className="title-icon" />
                  Analysis Result
                </h5>

                {loading && (
                  <div className="loading-indicator">
                    <div className="spinner"></div>
                    <p>Processing... this may take up to ~30s</p>
                  </div>
                )}

                {analysis && (
                  <div className="analysis-results">
                    <div className="result-header">
                      <h6><strong>Filename:</strong> {analysis.filename}</h6>
                    </div>

                    {/* Compliance Score with modern circular design */}
                    <div className="score-container">
                      <div 
                        className="score-circle"
                        style={{ '--score-percent': `${analysis.score}%` }}
                      >
                        <div className="score-value">{analysis.score}%</div>
                      </div>
                      <div className="score-label">Compliance Score</div>
                      <div className="score-description">
                        Overall compliance with FDA regulations
                      </div>
                    </div>

                    {/* Issues */}
                    <div className="result-card">
                      <h6 className="result-card-title">Issues</h6>
                      {analysis.issues && analysis.issues.length > 0 ? (
                        <ul className="issues-list">
                          {analysis.issues.map((it, idx) => (
                            <li key={idx} className="issue-item">
                              <SeverityBadge severity={it.severity} />
                              <span>{it.message}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="no-issues">
                          <FaCheckCircle className="success-icon" />
                          No issues found
                        </p>
                      )}
                    </div>

                    {/* Suggestions */}
                    <div className="result-card">
                      <h6 className="result-card-title">Suggestions</h6>
                      {analysis.suggestions && analysis.suggestions.length > 0 ? (
                        <ul className="suggestions-list">
                          {analysis.suggestions.map((sug, i) => (
                            <li key={i} className="suggestion-item">{sug}</li>
                          ))}
                        </ul>
                      ) : (
                        <p>No suggestions returned</p>
                      )}
                    </div>

                    {/* Notes */}
                    {analysis.notes && (
                      <div className="result-card notes-card">
                        <h6 className="result-card-title">Notes</h6>
                        <p>{analysis.notes}</p>
                      </div>
                    )}
                  </div>
                )}

                {raw && (
                  <div className="result-card raw-output">
                    <h6 className="result-card-title">Raw AI Output</h6>
                    <pre>{raw}</pre>
                  </div>
                )}

                {!analysis && !raw && !loading && (
                  <div className="no-analysis">
                    <p>No analysis yet. Upload a document or select a sample to begin.</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;