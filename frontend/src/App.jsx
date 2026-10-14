import { useState } from "react";

import "./App.css";

import ReactMarkdown from "react-markdown";

const API_BASE_URL = "http://127.0.0.1:8000";

const initialMessages = [

  {

    role: "assistant",

    text: "Hi! I'm CareerPilot, your AI career agent. Upload your resume to get personalized role suggestions, skill-gap analysis, and a learning roadmap.",

  },

];

const activities = [

  "Understanding your career goal",

  "Searching resume evidence",

  "Evaluating your skills",

  "Preparing recommendations",

];

function formatValue(value) {

  if (value === null || value === undefined || value === "") {

    return "Not available";

  }

  if (typeof value === "string" || typeof value === "number") {

    return String(value);

  }

  if (Array.isArray(value)) {

    return value.map((item) => formatValue(item)).join(", ");

  }

  return JSON.stringify(value, null, 2);

}

function getSkills(value) {

  if (Array.isArray(value)) {

    return value.map((item) => {

      if (typeof item === "string") return item;

      return (

        item.skill ||

        item.name ||

        item.technology ||

        JSON.stringify(item)

      );

    });

  }

  if (typeof value === "string") {

    return value ? [value] : [];

  }

  return [];

}

function getLearningItems(plan) {

  if (Array.isArray(plan)) {

    return plan;

  }

  if (Array.isArray(plan?.learning_plan)) {

    return plan.learning_plan;

  }

  if (Array.isArray(plan?.steps)) {

    return plan.steps;

  }

  if (Array.isArray(plan?.recommendations)) {

    return plan.recommendations;

  }

  return [];

}

function formatLearningItem(item) {

  if (typeof item === "string") {

    return item;

  }

  if (!item || typeof item !== "object") {

    return String(item);

  }

  const title =

    item.skill ||

    item.title ||

    item.topic ||

    item.task ||

    item.name ||

    "Learning step";

  const description =

    item.description ||

    item.details ||

    item.reason ||

    "";

  const resource = item.resource || item.url || "";

  return [

    title,

    description,

    resource ? `Resource: ${resource}` : "",

  ]

    .filter(Boolean)

    .join(" — ");

}

function App() {

  const [messages, setMessages] = useState(initialMessages);

  const [input, setInput] = useState("");

  const [activeTab, setActiveTab] = useState("Overview");

  const [selectedFile, setSelectedFile] = useState(null);

  const [sessionId, setSessionId] = useState("");

  const [suggestedRoles, setSuggestedRoles] = useState([]);

  const [uploadStatus, setUploadStatus] = useState("idle");

  const [analysisStatus, setAnalysisStatus] = useState("idle");

  const [uploadError, setUploadError] = useState("");

  const [isDragging, setIsDragging] = useState(false);

  const [analysis, setAnalysis] = useState(null);

  const [selectedRole, setSelectedRole] = useState("");

  function addAssistantMessage(text) {

    setMessages((previous) => [

      ...previous,

      { role: "assistant", text },

    ]);

  }

  function handleNewConversation() {

    setMessages(initialMessages);

    setInput("");

  }

  function handleFileSelection(file) {

    setUploadError("");

    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {

      setSelectedFile(null);

      setUploadError("Please select a PDF resume.");

      return;

    }

    if (file.size > 5 * 1024 * 1024) {

      setSelectedFile(null);

      setUploadError("Your resume must be 5 MB or smaller.");

      return;

    }

    setSelectedFile(file);

    setUploadStatus("idle");

  }

  async function handleUpload(event) {

    event.preventDefault();

    if (!selectedFile || uploadStatus === "uploading") {

      return;

    }

    setUploadStatus("uploading");

    setUploadError("");

    setSuggestedRoles([]);

    setSessionId("");

    setAnalysis(null);

    setSelectedRole("");

    setAnalysisStatus("idle");

    setMessages((previous) => [

      ...previous,

      {

        role: "user",

        text: `Upload my resume: ${selectedFile.name}`,

      },

      {

        role: "assistant",

        text: "I'm processing your resume, generating embeddings, and identifying suitable career roles. Please wait.",

      },

    ]);

    try {

      const formData = new FormData();

      formData.append("file", selectedFile);

      const response = await fetch(

        `${API_BASE_URL}/api/resume/upload`,

        {

          method: "POST",

          body: formData,

        }

      );

      const data = await response.json();

      if (!response.ok) {

        throw new Error(

          data.detail || "Resume upload failed."

        );

      }

      const roles = Array.isArray(data.suggested_roles)

        ? data.suggested_roles

        : [];

      setSessionId(data.session_id);

      setSuggestedRoles(roles);

      setUploadStatus("success");

      setMessages((previous) => [

        ...previous,

        {

          role: "assistant",

          text:

            `Your resume has been processed successfully. ` +

            `I found ${roles.length} suggested career role(s). ` +

            "Select a role to run your actual CareerPilot analysis.",

        },

      ]);

    } catch (error) {

      const message =

        error instanceof TypeError

          ? "Unable to connect to the backend. Check that FastAPI is running at http://127.0.0.1:8000."

          : error.message;

      setUploadStatus("error");

      setUploadError(message);

      addAssistantMessage(

        `I couldn't process your resume. ${message}`

      );

    }

  }

  async function handleRoleSelection(role) {

    if (!sessionId) {

      setUploadError("Please upload your resume first.");

      return;

    }

    if (analysisStatus === "loading") {

      return;

    }

    setSelectedRole(role);

    setAnalysisStatus("loading");

    setUploadError("");

    setAnalysis(null);

    setActiveTab("Resume analysis");

    setMessages((previous) => [

      ...previous,

      {

        role: "user",

        text: `Analyze my resume for ${role}.`,

      },

      {

        role: "assistant",

        text:

          `I'm running the actual CareerPilot analysis for ${role}. ` +

          "I'm evaluating your skills, calculating the match, and preparing recommendations...",

      },

    ]);

    try {

      const response = await fetch(

        `${API_BASE_URL}/api/analysis`,

        {

          method: "POST",

          headers: {

            "Content-Type": "application/json",

          },

          body: JSON.stringify({

            session_id: sessionId,

            role,

          }),

        }

      );

      const data = await response.json();

      if (!response.ok) {

        throw new Error(

          data.detail || "Career analysis failed."

        );

      }

      setAnalysis(data);

      setAnalysisStatus("success");

      const match = data.match_result || {};

      const candidate = data.candidate_analysis || {};

      const missingSkills = getSkills(match.missing_skills);

      const candidateSkills = getSkills(

        candidate.candidate_skills

      );

      const percentage =

        match.match_percentage ??

        match.matchPercentage ??

        match.match_percent ??

        match.percentage ??

        match.match_score;

      const summary = [

        `Career analysis completed for ${data.target_role || role}.`,

        "",

        `Match percentage: ${

          percentage === undefined

            ? "Check the detailed results panel"

            : `${percentage}${

                typeof percentage === "number" && percentage <= 1

                  ? " (score from 0 to 1)"

                  : "%"

              }`

        }`,

        "",

        `Existing skills: ${

          candidateSkills.length

            ? candidateSkills.join(", ")

            : "See detailed analysis"

        }`,

        "",

        `Missing skills: ${

          missingSkills.length

            ? missingSkills.join(", ")

            : "See detailed analysis"

        }`,

        "",

        "Your full results are displayed in the Resume analysis panel.",

      ].join("\n");

      addAssistantMessage(summary);

    } catch (error) {

      setAnalysisStatus("error");

      addAssistantMessage(

        `I couldn't complete the analysis for ${role}. ${error.message}`

      );

    }

  }

  async function handleSend(event) {

    event.preventDefault();

    const question = input.trim();

    if (!question || !sessionId) {

      return;

    }

    setInput("");

    setMessages((previous) => [

      ...previous,

      { role: "user", text: question },

      { role: "assistant", text: "Thinking..." },

    ]);

    try {

      const response = await fetch(`${API_BASE_URL}/api/chat`, {

        method: "POST",

        headers: {

          "Content-Type": "application/json",

        },

        body: JSON.stringify({

          session_id: sessionId,

          message: question,

        }),

      });

      const data = await response.json();

      if (!response.ok) {

        throw new Error(data.detail || "Chat request failed.");

      }

      setMessages((previous) => [

        ...previous.slice(0, -1),

        { role: "assistant", text: data.answer },

      ]);

    } catch (error) {

      setMessages((previous) => [

        ...previous.slice(0, -1),

        {

          role: "assistant",

          text: `Sorry, I couldn't answer that question: ${error.message}`,

        },

      ]);

    }

  }

  const match = analysis?.match_result || {};

  const candidate = analysis?.candidate_analysis || {};

  const roleAnalysis = analysis?.role_analysis || {};

  const plan = analysis?.learning_plan || {};

  const candidateSkills = getSkills(

    candidate.candidate_skills

  );

  const missingSkills = getSkills(

    match.missing_skills

  );

  const matchedSkills = getSkills(

    match.matched_skills

  );

  const requiredSkills = getSkills(

    roleAnalysis.technical_skills

  );

  const learningItems = getLearningItems(plan);

  const rawPercentage =

    match.match_percentage ??

    match.matchPercentage ??

    match.match_percent ??

    match.percentage ??

    match.match_score;

  const matchPercentage =

    typeof rawPercentage === "number"

      ? rawPercentage <= 1

        ? rawPercentage * 100

        : rawPercentage

      : null;

  const agentStatus =

    uploadStatus === "uploading"

      ? "Processing resume"

      : analysisStatus === "loading"

        ? "Analyzing career fit"

        : analysisStatus === "success"

          ? "Analysis completed"

          : sessionId

            ? "Resume analyzed"

            : "Ready to assist";

  return (

    <div className="app-shell">

      <aside className="sidebar">

        <a className="brand" href="#home">

          <span className="brand-icon">✳</span>

          <span>

            career<span className="brand-accent">pilot</span>

          </span>

        </a>

        <button

          className="new-chat"

          onClick={handleNewConversation}

        >

          <span>＋</span> New conversation

        </button>

        <div className="side-label">WORKSPACE</div>

        {[

          "Overview",

          "Resume analysis",

          "Skill assessment",

          "Learning roadmap",

        ].map((item) => (

          <button

            key={item}

            className={`nav-item ${activeTab === item ? "active" : ""}`}

            aria-current={activeTab === item ? "page" : undefined}

            onClick={() => setActiveTab(item)}

          >

            <span className="nav-dot" />

            {item}

          </button>

        ))}

        <div className="sidebar-bottom">

          <div className="online-indicator">

            <span className="status-dot" />

            Agent workspace

          </div>

          <div className="profile">

            <div className="avatar">R</div>

            <div>

              <strong>Your workspace</strong>

              <span>Career development</span>

            </div>

            <span className="profile-menu">···</span>

          </div>

        </div>

      </aside>

      <main className="main-panel">

        <header className="topbar">

          <div className="breadcrumb">

            Workspace <span>/</span>{" "}

            <strong>{activeTab}</strong>

          </div>

          <div className="topbar-right">

            <span className="model-status">

              <span className="status-dot" />

              {agentStatus}

            </span>

            <div className="avatar small">R</div>

          </div>

        </header>

        <div className="content">

          {activeTab === "Overview" ? (

            <>

              <section className="welcome" aria-labelledby="welcome-heading">

                <div className="eyebrow">

                  <span className="sparkle">✦</span>{" "}

                  YOUR PERSONAL AI CAREER AGENT

                </div>

                <h1 id="welcome-heading">

                  Build your next chapter<span>.</span>

                </h1>

                <p>

                  Upload your resume to discover suitable roles,

                  understand your strengths, and plan your next

                  career move.

                </p>

              </section>

              <section className="stats-grid">

                <article className="stat-card">

                  <span className="stat-label">AGENT STATUS</span>

                  <div className="stat-main">

                    <span className="status-dot" />

                    <strong>{agentStatus}</strong>

                  </div>

                  <span className="stat-note">

                    {analysisStatus === "success"

                      ? "Your role analysis is ready"

                      : sessionId

                        ? "Your resume is ready"

                        : "Upload a resume to begin"}

                  </span>

                </article>

                <article className="stat-card">

                  <span className="stat-label">CAREER PROFILE</span>

                  <div className="stat-main">

                    <strong>

                      {sessionId ? "Resume connected" : "Not uploaded"}

                    </strong>

                  </div>

                  <span className="stat-note">

                    Personalized career guidance

                  </span>

                </article>

                <article className="stat-card">

                  <span className="stat-label">AGENT WORKFLOW</span>

                  <div className="stat-main">

                    <strong>LangGraph</strong>

                  </div>

                  <span className="stat-note">

                    Multi-step analysis pipeline

                  </span>

                </article>

              </section>

              <section className="workspace-grid">

                <article className="panel chat-panel">

                  <div className="panel-heading">

                    <div>

                      <div className="panel-title">

                        CareerPilot assistant

                      </div>

                      <div className="panel-subtitle">

                        Your career, one conversation at a time

                      </div>

                    </div>

                    <span className="live-badge">

                      <span className="status-dot" />{" "}

                      {analysisStatus === "loading" ||

                      uploadStatus === "uploading"

                        ? "WORKING"

                        : "READY"}

                    </span>

                  </div>

                  <div className="messages">

                    {messages.map((message, index) => (

                      <div

                        key={`${index}-${message.role}`}

                        className={`message-row ${message.role}`}

                      >

                        {message.role === "assistant" && (

                          <div className="message-avatar">✳</div>

                        )}

                        <div className="message-bubble">

                          {message.text}

                        </div>

                      </div>

                    ))}

                  </div>

                  <form className="composer" onSubmit={handleSend}>

                    <input

                      value={input}

                      onChange={(event) =>

                        setInput(event.target.value)

                      }

                      placeholder="Ask CareerPilot anything..."

                      aria-label="Ask CareerPilot"

                      disabled={!sessionId}

                    />

                    <button

                      type="submit"

                      aria-label="Send message"

                      disabled={!sessionId || !input.trim()}

                    >

                      ↑

                    </button>

                  </form>

                  <div className="composer-note">

                    CareerPilot can make mistakes. Verify important

                    career decisions.

                  </div>

                </article>

                <div className="right-column">

                  <article className="panel activity-panel">

                    <div className="panel-heading">

                      <div>

                        <div className="panel-title">

                          Agent workflow

                        </div>

                        <div className="panel-subtitle">

                          How your agent works

                        </div>

                      </div>

                      <span className="workflow-icon">⌘</span>

                    </div>

                    <div className="activity-list">

                      {activities.map((activity, index) => {

                        const completed =

                          index === 0

                            ? Boolean(sessionId)

                            : analysisStatus === "success";

                        const current =

                          index === 0

                            ? !sessionId

                            : analysisStatus === "loading" &&

                              index === 1;

                        return (

                          <div

                            className="activity-item"

                            key={activity}

                          >

                            <div

                              className={`activity-icon ${

                                current || completed ? "current" : ""

                              }`}

                            >

                              {completed ? "✓" : index + 1}

                            </div>

                            <div className="activity-copy">

                              <strong>{activity}</strong>

                              <span>

                                {index === 0

                                  ? sessionId

                                    ? "Resume processed"

                                    : "Ready when you are"

                                  : index === 1 &&

                                    analysisStatus === "loading"

                                    ? "Running analysis..."

                                    : analysisStatus === "success"

                                      ? "Analysis completed"

                                      : "Runs during analysis"}

                              </span>

                            </div>

                          </div>

                        );

                      })}

                    </div>

                  </article>

                  <article className="panel roadmap-panel">

                    <div className="panel-heading">

                      <div>

                        <div className="panel-title">

                          Your next steps

                        </div>

                        <div className="panel-subtitle">

                          A path to your next opportunity

                        </div>

                      </div>

                      <span className="roadmap-icon">↗</span>

                    </div>

                    {!sessionId ? (

                      <div className="roadmap-empty">

                        <div className="roadmap-illustration">✧</div>

                        <strong>Your roadmap starts here</strong>

                        <p>

                          Upload your resume to discover roles suited

                          to your skills.

                        </p>

                      </div>

                    ) : (

                      <div className="role-results">

                        <div className="panel-title">

                          Suggested career roles

                        </div>

                        {suggestedRoles.length === 0 ? (

                          <p>No suggested roles were returned.</p>

                        ) : (

                          suggestedRoles.map((item, index) => {

                            const role =

                              typeof item === "string"

                                ? item

                                : item.role;

                            const reason =

                              typeof item === "string"

                                ? ""

                                : item.reason;

                            return (

                              <div

                                className="role-card"

                                key={`${role}-${index}`}

                              >

                                <strong>{role}</strong>

                                {reason && <p>{reason}</p>}

                                <button

                                  type="button"

                                  disabled={analysisStatus === "loading"}

                                  onClick={() =>

                                    handleRoleSelection(role)

                                  }

                                >

                                  {analysisStatus === "loading" &&

                                  selectedRole === role

                                    ? "Analyzing..."

                                    : analysisStatus === "success" &&

                                      selectedRole === role

                                      ? "Analyze again →"

                                      : "Select role →"}

                                </button>

                              </div>

                            );

                          })

                        )}

                      </div>

                    )}

                  </article>

                </div>

              </section>

              {analysisStatus === "loading" && (

                <section className="panel upload-panel">

                  <p>

                    Analyzing your resume for {selectedRole}. Please

                    wait while CareerPilot runs the analysis.

                  </p>

                </section>

              )}

              {analysisStatus === "error" && (

                <section className="panel upload-panel">

                  <p className="upload-error">

                    The role analysis failed. Please check the assistant

                    message and backend terminal.

                  </p>

                </section>

              )}

              {analysisStatus === "success" && analysis && (

                <section className="panel upload-panel analysis-results">

                  <div className="panel-heading">

                    <div>

                      <div className="panel-title">

                        Resume analysis results

                      </div>

                      <div className="panel-subtitle">

                        Actual results returned by your CareerPilot backend

                      </div>

                    </div>

                  </div>

                  <div className="stats-grid">

                    <article className="stat-card">

                      <span className="stat-label">TARGET ROLE</span>

                      <div className="stat-main">

                        <strong>

                          {analysis.target_role || selectedRole}

                        </strong>

                      </div>

                    </article>

                    <article className="stat-card">

                      <span className="stat-label">SKILL MATCH</span>

                      <div className="stat-main">

                        <strong>

                          {matchPercentage !== null

                            ? `${matchPercentage.toFixed(1)}%`

                            : "See match details below"}

                        </strong>

                      </div>

                      {matchPercentage !== null && (

                        <div

                          style={{

                            height: 7,

                            borderRadius: 10,

                            overflow: "hidden",

                            background: "rgba(148,163,184,.2)",

                            marginTop: 12,

                          }}

                        >

                          <div

                            style={{

                              width: `${Math.max(

                                0,

                                Math.min(100, matchPercentage)

                              )}%`,

                              height: "100%",

                              background: "#8585f5",

                            }}

                          />

                        </div>

                      )}

                    </article>

                    <article className="stat-card">

                      <span className="stat-label">MISSING SKILLS</span>

                      <div className="stat-main">

                        <strong>{missingSkills.length}</strong>

                      </div>

                    </article>

                  </div>

                  <div className="results-section">

                    <h3>Existing candidate skills</h3>

                    {candidateSkills.length ? (

                      <div className="skill-list">

                        {candidateSkills.map((skill, index) => (

                          <span

                            className="skill-chip"

                            key={`${skill}-${index}`}

                          >

                            {skill}

                          </span>

                        ))}

                      </div>

                    ) : (

                      <pre>{formatValue(candidate)}</pre>

                    )}

                  </div>

                  <div className="results-section">

                    <h3>Matched skills</h3>

                    {matchedSkills.length ? (

                      <div className="skill-list">

                        {matchedSkills.map((skill, index) => (

                          <span

                            className="skill-chip"

                            key={`${skill}-${index}`}

                          >

                            {skill}

                          </span>

                        ))}

                      </div>

                    ) : (

                      <pre>

                        {formatValue(

                          match.matched_skills ??

                          match.matched ??

                          "No matched-skill list was returned."

                        )}

                      </pre>

                    )}

                  </div>

                  <div className="results-section">

                    <h3>Missing skills to learn</h3>

                    {missingSkills.length ? (

                      <div className="skill-list">

                        {missingSkills.map((skill, index) => (

                          <span

                            className="skill-chip missing"

                            key={`${skill}-${index}`}

                          >

                            {skill}

                          </span>

                        ))}

                      </div>

                    ) : (

                      <pre>

                        {formatValue(

                          match.missing_skills ??

                          "No missing-skill list was returned."

                        )}

                      </pre>

                    )}

                  </div>

                  <div className="results-section">

                    <h3>Required technical skills</h3>

                    {requiredSkills.length ? (

                      <div className="skill-list">

                        {requiredSkills.map((skill, index) => (

                          <span

                            className="skill-chip"

                            key={`${skill}-${index}`}

                          >

                            {skill}

                          </span>

                        ))}

                      </div>

                    ) : (

                      <pre>{formatValue(roleAnalysis)}</pre>

                    )}

                  </div>

                  <div className="results-section">

                    <h3>Personalized learning plan</h3>

                    {learningItems.length ? (

                      <ol className="learning-list">

                        {learningItems.map((item, index) => (

                          <li key={`learning-${index}`}>

                            {formatLearningItem(item)}

                          </li>

                        ))}

                      </ol>

                    ) : (

                      <pre>{formatValue(plan)}</pre>

                    )}

                  </div>

                  <div className="results-section">

                    <h3>CareerPilot recommendation</h3>

                    <div className="recommendation-text markdown-content">

                      <ReactMarkdown>

                        {String(

                          analysis?.response ||

                          "The backend did not return a separate recommendation."

                        )}

                      </ReactMarkdown>

                    </div>

                  </div>

                  {analysis.resume_evidence && (

                    <details className="results-section">

                      <summary>View retrieved resume evidence</summary>

                      <pre>{analysis.resume_evidence}</pre>

                    </details>

                  )}

                  <div className="results-section">

                    <h3>Raw analysis data</h3>

                    <details>

                      <summary>Show complete backend response</summary>

                      <pre>{JSON.stringify(analysis, null, 2)}</pre>

                    </details>

                  </div>

                </section>

              )}

              <section className="panel upload-panel">

                <div className="panel-heading">

                  <div>

                    <div className="panel-title">Resume analysis</div>

                    <div className="panel-subtitle">

                      Upload your latest resume in PDF format

                    </div>

                  </div>

                </div>

                <form onSubmit={handleUpload}>

                  <label

                    className={`upload-dropzone ${

                      isDragging ? "dragging" : ""

                    }`}

                    onDragOver={(event) => {

                      event.preventDefault();

                      setIsDragging(true);

                    }}

                    onDragLeave={() => setIsDragging(false)}

                    onDrop={(event) => {

                      event.preventDefault();

                      setIsDragging(false);

                      handleFileSelection(

                        event.dataTransfer.files?.[0]

                      );

                    }}

                  >

                    <input

                      type="file"

                      accept=".pdf,application/pdf"

                      onChange={(event) =>

                        handleFileSelection(

                          event.target.files?.[0]

                        )

                      }

                      disabled={uploadStatus === "uploading"}

                    />

                    <span className="upload-symbol">↑</span>

                    <strong>

                      {selectedFile

                        ? selectedFile.name

                        : "Drop your resume here or click to browse"}

                    </strong>

                    <span>PDF format · Maximum file size 5 MB</span>

                  </label>

                  {uploadError && (

                    <p className="upload-error" role="alert">

                      {uploadError}

                    </p>

                  )}

                  {uploadStatus === "success" && (

                    <p className="upload-success" role="status">

                      Resume processed successfully.

                    </p>

                  )}

                  <button

                    className="upload-button"

                    type="submit"

                    disabled={

                      !selectedFile || uploadStatus === "uploading"

                    }

                  >

                    {uploadStatus === "uploading"

                      ? "Processing resume..."

                      : "Upload & analyze resume"}

                  </button>

                </form>

              </section>

              <footer className="footer">

                <span>

                  CAREERPILOT{" "}

                  <span className="footer-separator">/</span>{" "}

                  AI CAREER INTELLIGENCE

                </span>

                <span>Built with React · FastAPI · LangGraph · Gemini</span>

              </footer>

            </>

          ) : activeTab === "Resume analysis" ? (

            <section className="panel upload-panel analysis-results">

              <div className="panel-heading">

                <div>

                  <div className="panel-title">Resume analysis</div>

                  <div className="panel-subtitle">

                    Your resume insights and career recommendations

                  </div>

                </div>

              </div>

              {!sessionId ? (

                <div className="roadmap-empty">

                  <div className="roadmap-illustration">✧</div>

                  <strong>Upload your resume to begin</strong>

                  <p>

                    Go to Overview to upload a PDF resume and generate your

                    personalized analysis.

                  </p>

                  <button

                    type="button"

                    className="upload-button"

                    onClick={() => setActiveTab("Overview")}

                  >

                    Go to Overview

                  </button>

                </div>

              ) : !analysis ? (

                <div className="results-section">

                  <p>

                    Your resume is processed. Select a suggested role on

                    Overview to generate detailed analysis.

                  </p>

                  <button

                    type="button"

                    className="upload-button"

                    onClick={() => setActiveTab("Overview")}

                  >

                    Choose a role

                  </button>

                </div>

              ) : (

                <>

                  <div className="stats-grid">

                    <article className="stat-card">

                      <span className="stat-label">TARGET ROLE</span>

                      <div className="stat-main">

                        <strong>

                          {analysis.target_role || selectedRole}

                        </strong>

                      </div>

                    </article>

                    <article className="stat-card">

                      <span className="stat-label">SKILL MATCH</span>

                      <div className="stat-main">

                        <strong>

                          {matchPercentage !== null

                            ? `${matchPercentage.toFixed(1)}%`

                            : "Not available"}

                        </strong>

                      </div>

                    </article>

                    <article className="stat-card">

                      <span className="stat-label">MISSING SKILLS</span>

                      <div className="stat-main">

                        <strong>{missingSkills.length}</strong>

                      </div>

                    </article>

                  </div>

                  <div className="results-section">

                    <h3>CareerPilot recommendation</h3>

                    <div className="recommendation-text markdown-content">

                      <ReactMarkdown>

                        {String(

                          analysis.response ||

                          "No separate recommendation was returned."

                        )}

                      </ReactMarkdown>

                    </div>

                  </div>

                  <div className="results-section">

                    <h3>Existing candidate skills</h3>

                    {candidateSkills.length ? (

                      <div className="skill-list">

                        {candidateSkills.map((skill, index) => (

                          <span

                            className="skill-chip"

                            key={`${skill}-${index}`}

                          >

                            {skill}

                          </span>

                        ))}

                      </div>

                    ) : (

                      <pre>{formatValue(candidate)}</pre>

                    )}

                  </div>

                  {analysis.resume_evidence && (

                    <details className="results-section">

                      <summary>View retrieved resume evidence</summary>

                      <pre>{analysis.resume_evidence}</pre>

                    </details>

                  )}

                </>

              )}

            </section>

          ) : activeTab === "Skill assessment" ? (

            <section className="panel upload-panel analysis-results">

              <div className="panel-heading">

                <div>

                  <div className="panel-title">Skill assessment</div>

                  <div className="panel-subtitle">

                    Understand your strengths and the skills to develop next

                  </div>

                </div>

              </div>

              {!analysis ? (

                <div className="roadmap-empty">

                  <div className="roadmap-illustration">✧</div>

                  <strong>Complete a role analysis first</strong>

                  <p>

                    Upload your resume and select a role from Overview to

                    see your skill assessment.

                  </p>

                  <button

                    type="button"

                    className="upload-button"

                    onClick={() => setActiveTab("Overview")}

                  >

                    Go to Overview

                  </button>

                </div>

              ) : (

                <>

                  <div className="stats-grid">

                    <article className="stat-card">

                      <span className="stat-label">SKILL MATCH</span>

                      <div className="stat-main">

                        <strong>

                          {matchPercentage !== null

                            ? `${matchPercentage.toFixed(1)}%`

                            : "Not available"}

                        </strong>

                      </div>

                    </article>

                    <article className="stat-card">

                      <span className="stat-label">MATCHED SKILLS</span>

                      <div className="stat-main">

                        <strong>{matchedSkills.length}</strong>

                      </div>

                    </article>

                    <article className="stat-card">

                      <span className="stat-label">SKILL GAPS</span>

                      <div className="stat-main">

                        <strong>{missingSkills.length}</strong>

                      </div>

                    </article>

                  </div>

                  <div className="results-section">

                    <h3>Matched skills</h3>

                    {matchedSkills.length ? (

                      <div className="skill-list">

                        {matchedSkills.map((skill, index) => (

                          <span

                            className="skill-chip"

                            key={`${skill}-${index}`}

                          >

                            {skill}

                          </span>

                        ))}

                      </div>

                    ) : (

                      <p>No matched-skill list was returned.</p>

                    )}

                  </div>

                  <div className="results-section">

                    <h3>Skills to improve</h3>

                    {missingSkills.length ? (

                      <div className="skill-list">

                        {missingSkills.map((skill, index) => (

                          <span

                            className="skill-chip missing"

                            key={`${skill}-${index}`}

                          >

                            {skill}

                          </span>

                        ))}

                      </div>

                    ) : (

                      <p>No missing skills were returned.</p>

                    )}

                  </div>

                  <div className="results-section">

                    <h3>Required technical skills</h3>

                    {requiredSkills.length ? (

                      <div className="skill-list">

                        {requiredSkills.map((skill, index) => (

                          <span

                            className="skill-chip"

                            key={`${skill}-${index}`}

                          >

                            {skill}

                          </span>

                        ))}

                      </div>

                    ) : (

                      <pre>{formatValue(roleAnalysis)}</pre>

                    )}

                  </div>

                </>

              )}

            </section>

          ) : (

            <section className="panel upload-panel analysis-results">

              <div className="panel-heading">

                <div>

                  <div className="panel-title">Learning roadmap</div>

                  <div className="panel-subtitle">

                    A practical plan based on your target role and skill gaps

                  </div>

                </div>

              </div>

              {!analysis ? (

                <div className="roadmap-empty">

                  <div className="roadmap-illustration">✧</div>

                  <strong>Your roadmap starts here</strong>

                  <p>

                    Upload your resume and complete a role analysis to

                    receive personalized learning steps.

                  </p>

                  <button

                    type="button"

                    className="upload-button"

                    onClick={() => setActiveTab("Overview")}

                  >

                    Go to Overview

                  </button>

                </div>

              ) : (

                <>

                  <div className="results-section">

                    <h3>Target role</h3>

                    <p>{analysis.target_role || selectedRole}</p>

                  </div>

                  <div className="results-section">

                    <h3>Skills to prioritize</h3>

                    {missingSkills.length ? (

                      <ol className="learning-list">

                        {missingSkills.map((skill, index) => (

                          <li key={`${skill}-${index}`}>

                            <strong>{skill}</strong>

                            <p>

                              Focus on the fundamentals, build a small

                              practical example, and then use this skill in

                              a project.

                            </p>

                          </li>

                        ))}

                      </ol>

                    ) : (

                      <p>

                        No specific skill gaps were returned. Review the

                        recommended learning plan below.

                      </p>

                    )}

                  </div>

                  <div className="results-section">

                    <h3>Personalized learning plan</h3>

                    {learningItems.length ? (

                      <ol className="learning-list">

                        {learningItems.map((item, index) => (

                          <li key={`roadmap-${index}`}>

                            {formatLearningItem(item)}

                          </li>

                        ))}

                      </ol>

                    ) : (

                      <p>No learning plan was returned for this analysis.</p>

                    )}

                  </div>

                  <div className="results-section">

                    <h3>Suggested next action</h3>

                    <p>

                      Choose one priority skill, practice it with a small

                      feature, and add that feature to a real-world project.

                    </p>

                  </div>

                </>

              )}

            </section>

          )}

        </div>

      </main>

    </div>

  );

}

export default App;