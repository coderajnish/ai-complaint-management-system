import React, { useState } from "react";
import { Paperclip, Zap } from "lucide-react";
import "./index.css";

function App() {
  const [isAiResponding, setIsAiResponding] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("pending");
  const [formData, setFormData] = useState({});
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Ready to process new complaints. You can paste the complaint text or upload a document."
    }
  ]);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const isExpanded = formData && Object.keys(formData).length > 0;
  const hasConversation = messages.length > 1;

  const getValue = (key) =>
    formData[key] || "Awaiting AI evaluation...";

  const handleSend = async () => {
    if (!input.trim()) return;

    setMessages(prev => [...prev, { sender: "user", text: input }]);
    setIsAiResponding(true);

    const startTime = Date.now();

    try {
      let res;

      if (formData.product_name) {
        res = await fetch("http://127.0.0.1:8000/modify", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            current_data: formData,
            instruction: input
          })
        });
      } else {
        res = await fetch("http://127.0.0.1:8000/analyze-text", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: input })
        });
      }

      const data = await res.json();
      setFormData(data);
      setStatus("ready");

      const elapsed = Date.now() - startTime;
      const remaining = Math.max(700 - elapsed, 0);

      setTimeout(() => {
        setIsAiResponding(false);
        setMessages(prev => [
          ...prev,
          { sender: "ai", text: "Complaint processed successfully. Form updated." }
        ]);
      }, remaining);

    } catch {
      setIsAiResponding(false);
      setMessages(prev => [
        ...prev,
        { sender: "ai", text: "Error processing request." }
      ]);
    }

    setInput("");
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsLoading(true);
    setProgress(0);

    let progressValue = 0;

    const interval = setInterval(() => {
      progressValue += 5;
      if (progressValue >= 90) {
        progressValue = 90;
        clearInterval(interval);
      }
      setProgress(progressValue);
    }, 150);

    const formDataUpload = new FormData();
    formDataUpload.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/analyze-pdf", {
        method: "POST",
        body: formDataUpload
      });

      const data = await res.json();
      setFormData(data);
      setStatus("ready");

      setMessages(prev => [
        ...prev,
        { sender: "ai", text: "Document analysis complete. Complaint extracted and form populated." }
      ]);
    } catch {
      setMessages(prev => [
        ...prev,
        { sender: "ai", text: "Error uploading/analyzing file." }
      ]);
    } finally {
      clearInterval(interval);
      setProgress(0);
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({});
    setStatus("pending");
  };

  return (
    <div className="app-container">

      <div className="left-panel">

        <div className="header">
          <div>
            <h2>Log Customer Complaint</h2>
            <div className="subtitle">
              API & FDF Quality Assurance Module
            </div>
          </div>

          <div className={`badge ${status}`}>
            {status === "ready" ? "Ready to Commit" : "Pending Triage"}
          </div>
        </div>

        {!isExpanded && (
          <>
            <Section title="1. PRODUCT & BATCH IDENTIFICATION">
              <Field label="Product Name (API/FDF)" value="" />
              <Field label="Batch / Lot Number" value="" />
            </Section>

            <Section title="2. FACILITY & MATERIAL IMPACT">
              <Field label="Originating Site Block" value="" />
              <Field label="Impacted Non‑Product Materials (NPM)" value="" />
            </Section>

            <Section title="3. DEFECT ANALYSIS">
              <Field label="Structured Defect Summary" value="" textarea />
            </Section>
          </>
        )}

        {isExpanded && (
          <>
            <Section title="1. ORIGIN & CUSTOMER DETAILS">
              <Field label="Complaint Source" value={getValue("complaint_source")} />
              <Field label="Customer Name" value={getValue("customer_name")} />
            </Section>

            <Section title="2. PRODUCT & BATCH IDENTIFICATION">
              <Field label="Product Name (API/FDF)" value={getValue("product_name")} />
              <Field label="Product Strength / Grade" value={getValue("product_strength")} />
              <Field label="Batch / Lot Number" value={getValue("batch_number")} />
              <Field label="Affected Quantity" value={getValue("affected_quantity")} />
              <Field label="Manufacturing Date" value={getValue("manufacturing_date")} />
              <Field label="Expiry Date" value={getValue("expiry_date")} />
            </Section>

            <Section title="3. FACILITY & MATERIAL IMPACT">
              <Field label="Originating Site Block" value={getValue("originating_site")} />
              <Field label="Impacted Non‑Product Materials (NPM)" value={getValue("impacted_materials")} />
            </Section>

            <Section title="4. DEFECT ANALYSIS">
              <Field label="Complaint Category" value={getValue("complaint_category")} />
              <Field label="Complaint Description" value={getValue("description")} textarea />
            </Section>

            <div className="risk-card">
              <div className="risk-title">AI Copilot Risk Assessment</div>

              <Section title="AI Copilot Risk Assessment">
                <Field label="Severity (Suggested)" value={getValue("severity")} />
                <Field label="Suggested Next Action" value={getValue("suggested_action")} />
                <Field label="Initial Risk Assessment" value={getValue("initial_risk_assessment")} textarea />
              </Section>

              <button className="commit-btn">
                Commit to QMS Ledger
              </button>

        <div className="right-panel">

          {!hasConversation && !isLoading ? (
            <>
              <div className="copilot-header">
                <strong>AI Complaint Intake Assistant</strong>
                <span className="beta-badge">BETA</span>
              </div>

              <div className="copilot-scroll">

                <div className="upload-box">
                  <input
                    type="file"
                    id="fileUpload"
                    onChange={handleFileUpload}
                    accept=".pdf,.docx,.txt,.eml"
                    hidden
                  />
                  <label htmlFor="fileUpload" className="upload-label">
                    <div>Drag & drop complaint document here</div>
                    <div className="browse-text">or click to browse</div>
                  </label>
                </div>

                <div className="or-divider">OR</div>

                <button className="paste-btn">
                  Paste Complaint Text / Email
                </button>

                <div className="supported-box">
                  Supported formats: PDF, DOCX, TXT, EML
                  <br />
                  Max file size: 10MB
                </div>

                <div className="ai-info-box">
                  <strong>AI Assistant</strong>
                  <div>
                    Upload a complaint document or paste text above.
                    I will automatically extract the details and populate the form for you.
                  </div>
                </div>

              </div>
            </>
          ) : (
            <>
              <div className="copilot-header">
                <strong>AIVOA Copilot</strong>
                <div className="online-dot"></div>
              </div>

              <div className="copilot-scroll">
                {messages.map((msg, i) => (
                  <div key={i} className={`message ${msg.sender}`}>
                    {msg.text}
                  </div>
                ))}

                {isLoading && (
                  <div className="message ai">
                    <div className="progress-section" style={{ width: "100%", margin: 0 }}>
                      <div className="progress-header">
                        <span>Extraction Progress</span>
                        <span>{progress}%</span>
                      </div>
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                      <div className="progress-text" style={{ marginTop: 6 }}>
                        Analyzing document content...
                      </div>
                    </div>
                  </div>
                )}

                {isAiResponding && (
                  <div className="typing-wrapper">
                    <div className="typing-icon-circle">
                      <Zap size={14} />
                    </div>
                    <div className="typing-bubble-small">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}

          <div className="input-row">
            <input
              type="file"
              id="chatFileUpload"
              onChange={handleFileUpload}
              hidden
            />

            <label htmlFor="chatFileUpload" className="attach-icon">
              <Paperclip size={18} />
            </label>

            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Type a message or paste a complaint..."
            />

            <button onClick={handleSend}>✔</button>
          </div>

        </div>

      </div>
      );
}

      function Section({title, children}) {
  return (
      <>
        <div className="section-title">{title}</div>
        <div className="grid">{children}</div>
      </>
      );
}

      function Field({label, value, textarea}) {
  const isEmpty = !value || value === "Awaiting AI evaluation...";

      return (
      <div className="field">
        <label>{label}</label>
        {textarea ? (
          <textarea
            readOnly
            value={isEmpty ? "" : value}
            placeholder="Awaiting AI evaluation..."
            className={isEmpty ? "input-soft" : "input-strong"}
          />
        ) : (
          <input
            readOnly
            value={isEmpty ? "" : value}
            placeholder="Awaiting AI evaluation..."
            className={isEmpty ? "input-soft" : "input-strong"}
          />
        )}
      </div>
      );
}

      export default App;