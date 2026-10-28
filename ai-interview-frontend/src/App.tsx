

import { useEffect, useState, type FormEvent, type ReactNode } from "react";

import {

  LayoutDashboard,

  BrainCircuit,

  History,

  ChartNoAxesCombined,

  Settings,

  Bell,

  Search,

  ArrowUpRight,

  Clock3,

  CircleCheck,

  Play,

  Code2,

  Target,

  Zap,

  Menu,

  X,

  LogIn,

  UserPlus,

  Eye,

  EyeOff,

  LogOut,

  ShieldCheck,

} from "lucide-react";

import { useAuth } from "./context/AuthContext";

import "./App.css";


type Page =

  | "Dashboard"

  | "Start Interview"

  | "Interview History"

  | "Performance"

  | "Live Interview"

  | "Interview Complete";


type AuthMode = "login" | "signup";


type InterviewQuestion = {

  session_id: number;

  question_id: number;

  question_number: number;

  question: string;

  concept: string;

  question_type: string;

  difficulty: string;

};


type AnswerSubmissionResponse = {

  session_id?: number;

  completed?: boolean;

  answer_id?: number;

  score?: number;

  evaluation?: string;

  next_difficulty?: string;

  question?: InterviewQuestion | (Omit<InterviewQuestion, "session_id"> & { session_id?: number });

  [key: string]: unknown;

};


type InterviewSession = {
  session_id: number;
  topic: string;
  question_type: string;
  starting_difficulty: string;
  final_difficulty: string | null;
  total_questions: number;
  total_score: number;
  average_score: number | null;
  status: string;
  started_at: string | null;
  completed_at: string | null;
};

type InterviewHistoryResponse = {
  sessions: InterviewSession[];
  total_interviews: number;
  completed_interviews: number;
  average_score: number | null;
};

const API_BASE_URL =

  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";


const navItems = [

  { label: "Dashboard" as Page, icon: LayoutDashboard },

  { label: "Start Interview" as Page, icon: BrainCircuit },

  { label: "Interview History" as Page, icon: History },

  { label: "Performance" as Page, icon: ChartNoAxesCombined },

];


const authInputStyle = {

  width: "100%",

  boxSizing: "border-box" as const,

  padding: "13px 14px",

  border: "1px solid #d8dce8",

  borderRadius: "10px",

  background: "#ffffff",

  color: "#202338",

  fontSize: "14px",

  outline: "none",

};


function App() {

  const { user, token, loading, login, signup, logout } = useAuth();


  const [authMode, setAuthMode] = useState<AuthMode>("login");

  const [page, setPage] = useState<Page>("Dashboard");

  const [mobileMenu, setMobileMenu] = useState(false);


  const [role, setRole] = useState("Python Developer");

  const [level, setLevel] = useState("Intermediate");

  const [questionCount, setQuestionCount] = useState("10");


  const [topics, setTopics] = useState<string[]>([]);

  const [selectedTopic, setSelectedTopic] = useState("");

  const [concepts, setConcepts] = useState<string[]>([]);

  const [selectedConcepts, setSelectedConcepts] = useState<string[]>([]);

  const [questionType, setQuestionType] = useState("Conceptual");

  const [candidateEducation, setCandidateEducation] = useState("");

  const [candidateSkills, setCandidateSkills] = useState("");

  const [candidateProjects, setCandidateProjects] = useState("");

  const [candidateExperience, setCandidateExperience] = useState("");

  const [startingInterview, setStartingInterview] = useState(false);

  const [interviewError, setInterviewError] = useState("");

  const [interviewQuestion, setInterviewQuestion] =

    useState<InterviewQuestion | null>(null);

  const [answerText, setAnswerText] = useState("");

  const [submittingAnswer, setSubmittingAnswer] = useState(false);

  const [answerError, setAnswerError] = useState("");

  const [lastEvaluation, setLastEvaluation] = useState("");

  const [lastScore, setLastScore] = useState<number | null>(null);

  const [finalResult, setFinalResult] = useState<AnswerSubmissionResponse | null>(null);

  const [historyData, setHistoryData] = useState<InterviewHistoryResponse | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");


  useEffect(() => {

    if (!token) return;


    let active = true;


    async function loadTopics() {

      try {

        const response = await fetch(`${API_BASE_URL}/api/interview/topics`, {

          headers: { Authorization: `Bearer ${token}` },

        });


        if (!response.ok) {

          throw new Error(

            response.status === 401

              ? "Your session has expired. Please log in again."

              : "Could not load interview topics.",

          );

        }


        const data = await response.json();

        if (active) {

          const loadedTopics: string[] = data.topics ?? [];

          setTopics(loadedTopics);

          setSelectedTopic((current) =>

            loadedTopics.includes(current) ? current : loadedTopics[0] ?? "",

          );

        }

      } catch (error) {

        if (active) {

          setInterviewError(

            error instanceof Error ? error.message : "Could not load topics.",

          );

        }

      }

    }


    void loadTopics();

    return () => {

      active = false;

    };

  }, [token]);


  useEffect(() => {

    if (!token || !selectedTopic) {

      setConcepts([]);

      setSelectedConcepts([]);

      return;

    }


    let active = true;


    async function loadConcepts() {

      setConcepts([]);

      setSelectedConcepts([]);

      setInterviewError("");


      try {

        const params = new URLSearchParams({ topic: selectedTopic });

        const response = await fetch(

          `${API_BASE_URL}/api/interview/concepts?${params.toString()}`,

          { headers: { Authorization: `Bearer ${token}` } },

        );


        if (!response.ok) {

          throw new Error(

            response.status === 401

              ? "Your session has expired. Please log in again."

              : response.status === 404

                ? "The selected topic was not found. Refresh the topic list and try again."

                : "Could not load concepts for this topic.",

          );

        }


        const data = await response.json();

        if (active) setConcepts(data.concepts ?? []);

      } catch (error) {

        if (active) {

          setInterviewError(

            error instanceof Error

              ? error.message

              : "Could not load concepts.",

          );

        }

      }

    }


    void loadConcepts();

    return () => {

      active = false;

    };

  }, [token, selectedTopic]);


  async function handleStartInterview(event: FormEvent<HTMLFormElement>) {

    event.preventDefault();


    if (!token || !user) {

      setInterviewError("Please log in before starting an interview.");

      return;

    }

    if (!selectedTopic) {

      setInterviewError("Please select a topic.");

      return;

    }

    if (selectedConcepts.length === 0) {

      setInterviewError("Please select at least one concept.");

      return;

    }


    setStartingInterview(true);

    setInterviewError("");


    const payload = {

      name: user.name,

      email: user.email,

      education: candidateEducation.trim(),

      skills: candidateSkills.split(",").map((item) => item.trim()).filter(Boolean),

      projects: candidateProjects.split("\n").map((item) => item.trim()).filter(Boolean),

      experience: candidateExperience.trim(),

      target_role: role,

      topic: selectedTopic,

      selected_concepts: selectedConcepts,

      question_type: questionType,

      starting_difficulty:

        level === "Beginner" ? "Easy" : level === "Advanced" ? "Hard" : "Medium",

      max_questions: Number(questionCount),

    };


    try {

      const response = await fetch(`${API_BASE_URL}/api/interview/start`, {

        method: "POST",

        headers: {

          "Content-Type": "application/json",

          Authorization: `Bearer ${token}`,

        },

        body: JSON.stringify(payload),

      });


      const data = await response.json().catch(() => ({}));

      if (!response.ok) {

        const detail = data.detail;

        const message = Array.isArray(detail)

          ? detail.map((item: { msg?: string }) => item.msg ?? "Invalid request").join("; ")

          : typeof detail === "string"

            ? detail

            : `Could not start interview (HTTP ${response.status}).`;

        throw new Error(message);

      }


      setInterviewQuestion(data as InterviewQuestion);

      changePage("Live Interview");

    } catch (error) {

      setInterviewError(

        error instanceof Error

          ? error.message

          : "An unexpected error occurred while starting the interview.",

      );

    } finally {

      setStartingInterview(false);

    }

  }


  async function handleSubmitAnswer(event: FormEvent<HTMLFormElement>) {

    event.preventDefault();


    if (!token || !interviewQuestion) {

      setAnswerError("Your interview session is unavailable. Please start a new interview.");

      return;

    }


    const trimmedAnswer = answerText.trim();

    if (!trimmedAnswer) {

      setAnswerError("Please enter your answer before submitting.");

      return;

    }


    setSubmittingAnswer(true);

    setAnswerError("");


    try {

      const response = await fetch(

        `${API_BASE_URL}/api/interview/${interviewQuestion.session_id}/answer`,

        {

          method: "POST",

          headers: {

            "Content-Type": "application/json",

            Authorization: `Bearer ${token}`,

          },

          body: JSON.stringify({ answer: trimmedAnswer }),

        },

      );


      const data = (await response.json().catch(() => ({}))) as AnswerSubmissionResponse & { detail?: unknown };

      if (!response.ok) {

        const detail = data.detail;

        const message = Array.isArray(detail)

          ? detail.map((item: { msg?: string }) => item.msg ?? "Invalid request").join("; ")

          : typeof detail === "string"

            ? detail

            : `Could not submit answer (HTTP ${response.status}).`;

        throw new Error(message);

      }


      setLastEvaluation(typeof data.evaluation === "string" ? data.evaluation : "");

      setLastScore(typeof data.score === "number" ? data.score : null);

      setAnswerText("");


      const next = data.question;

      if (data.completed === true || !next || typeof next.question !== "string") {

        setFinalResult(data);

        setInterviewQuestion(null);

        changePage("Interview Complete");

      } else {

        setInterviewQuestion({

          session_id: Number(next.session_id ?? data.session_id ?? interviewQuestion.session_id),

          question_id: Number(next.question_id),

          question_number: Number(next.question_number),

          question: next.question,

          concept: String(next.concept ?? ""),

          question_type: String(next.question_type ?? "Conceptual"),

          difficulty: String(next.difficulty ?? data.next_difficulty ?? "Medium"),

        });

      }

    } catch (error) {

      setAnswerError(

        error instanceof Error ? error.message : "An unexpected error occurred while submitting your answer.",

      );

    } finally {

      setSubmittingAnswer(false);

    }

  }


  function startAnotherInterview() {

    setInterviewQuestion(null);

    setAnswerText("");

    setAnswerError("");

    setInterviewError("");

    setLastEvaluation("");

    setLastScore(null);

    setFinalResult(null);

    changePage("Start Interview");

  }


  

  async function resumeInterview(sessionId: number) {
    if (!token) {
      setHistoryError("Please log in again to resume this interview.");
      return;
    }

    setHistoryError("");
    setAnswerError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/interview/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const detail = data.detail;
        throw new Error(
          typeof detail === "string"
            ? detail
            : `Could not resume session ${sessionId} (HTTP ${response.status}).`,
        );
      }

      if (String(data.status ?? "").toUpperCase() !== "IN_PROGRESS") {
        throw new Error("This interview is no longer in progress. Refresh Interview History.");
      }

      const current = data.current_question;
      if (!current || typeof current.question !== "string") {
        throw new Error(
          "This session has no saved current question. The backend must restore or generate a question for this existing session.",
        );
      }

      setInterviewQuestion({
        session_id: Number(data.session_id ?? sessionId),
        question_id: Number(current.question_id),
        question_number: Number(data.question_count ?? 1),
        question: current.question,
        concept: String(current.concept ?? ""),
        question_type: String(current.question_type ?? data.question_type ?? "Conceptual"),
        difficulty: String(current.difficulty ?? data.current_difficulty ?? data.starting_difficulty ?? "Easy"),
      });
      setAnswerText("");
      setLastEvaluation("");
      setLastScore(null);
      setFinalResult(null);
      changePage("Live Interview");
    } catch (error) {
      setHistoryError(
        error instanceof Error ? error.message : "Could not resume this interview.",
      );
    }
  }

  useEffect(() => {
    if (!token) {
      setHistoryData(null);
      setHistoryError("");
      return;
    }
    let active = true;

    async function loadInterviewHistory() {
      setHistoryLoading(true);
      setHistoryError("");
      try {
        const response = await fetch(`${API_BASE_URL}/api/interview/history`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) {
          throw new Error(
            response.status === 401
              ? "Your session has expired. Please log in again."
              : "Could not load interview history."
          );
        }
        const data = (await response.json()) as InterviewHistoryResponse;
        if (active) setHistoryData(data);
      } catch (error) {
        if (active) setHistoryError(error instanceof Error ? error.message : "Could not load interview history.");
      } finally {
        if (active) setHistoryLoading(false);
      }
    }

    void loadInterviewHistory();
    return () => { active = false; };
  }, [token, page]);

if (loading) {

    return (

      <div style={centeredStyle}>

        <BrainCircuit size={36} />

        <h2>Loading InterviewAI...</h2>

        <p>Checking your session</p>

      </div>

    );

  }


  if (!user) {

    return (

      <AuthScreen

        mode={authMode}

        onModeChange={setAuthMode}

        onLogin={login}

        onSignup={signup}

      />

    );

  }


  const changePage = (nextPage: Page) => {

    setPage(nextPage);

    setMobileMenu(false);

  };

  const sessions = historyData?.sessions ?? [];
  const completedSessions = sessions.filter(
    (session) => session.status.toUpperCase() === "COMPLETED"
  );
  const questionsAnswered = completedSessions.reduce(
    (total, session) => total + (session.total_questions || 0), 0
  );
  const averageScore = historyData?.average_score;


  return (

    <div className="app-shell">

      <aside className={`sidebar ${mobileMenu ? "sidebar-open" : ""}`}>

        <div className="brand">

          <div className="brand-icon">

            <BrainCircuit size={25} />

          </div>

          <div>

            <h2>InterviewAI</h2>

            <span>INTELLIGENCE PLATFORM</span>

          </div>

          <button

            className="close-menu"

            onClick={() => setMobileMenu(false)}

            aria-label="Close menu"

          >

            <X size={20} />

          </button>

        </div>


        <div className="workspace-label">WORKSPACE</div>


        <nav className="nav-list">

          {navItems.map(({ label, icon: Icon }) => (

            <button

              key={label}

              className={`nav-item ${page === label ? "active" : ""}`}

              onClick={() => changePage(label)}

            >

              <Icon size={19} />

              <span>{label}</span>

              {label === "Start Interview" && <span className="nav-dot" />}

            </button>

          ))}

        </nav>


        <div className="sidebar-bottom">

          <div className="upgrade-card">

            <div className="upgrade-icon">

              <Zap size={19} />

            </div>

            <h3>Level up your skills</h3>

            <p>

              Practice consistently to improve your interview performance.

            </p>

            <button onClick={() => changePage("Start Interview")}>

              Start practicing <ArrowUpRight size={15} />

            </button>

          </div>


          <button

            className="nav-item settings-item"

            onClick={() => alert("Settings will be added in a later phase.")}

          >

            <Settings size={19} />

            <span>Settings</span>

          </button>


          <div className="profile">

            <div className="avatar">

              {(user.name || user.email).charAt(0).toUpperCase()}

            </div>

            <div className="profile-text">

              <strong>{user.name}</strong>

              <span>{user.email}</span>

            </div>

            <button

              onClick={logout}

              title="Log out"

              aria-label="Log out"

              style={iconButtonStyle}

            >

              <LogOut size={17} />

            </button>

          </div>

        </div>

      </aside>


      {mobileMenu && (

        <button

          className="mobile-overlay"

          onClick={() => setMobileMenu(false)}

          aria-label="Close menu"

        />

      )}


      <main className="main-content">

        <header className="topbar">

          <button

            className="mobile-menu-button"

            onClick={() => setMobileMenu(true)}

            aria-label="Open menu"

          >

            <Menu />

          </button>


          <div className="breadcrumb">

            Workspace <span>/</span> <strong>{page}</strong>

          </div>


          <div className="topbar-actions">

            <div className="search-box">

              <Search size={17} />

              <input placeholder="Search..." />

            </div>

            <button className="icon-button" aria-label="Notifications">

              <Bell size={19} />

              <i />

            </button>

            <div className="top-avatar">

              {(user.name || user.email).charAt(0).toUpperCase()}

            </div>

          </div>

        </header>


        {page === "Dashboard" && (

          <div className="page-container">

            <section className="welcome-row">

              <div>

                <div className="eyebrow">

                  <span className="status-pulse" />

                  YOUR AI PRACTICE WORKSPACE

                </div>

                <h1>

                  Welcome back, {user.name} <span className="wave">✦</span>

                </h1>

                <p className="subtitle">

                  Build confidence. Practice smarter. Get interview-ready.

                </p>

              </div>

              <button

                className="primary-button"

                onClick={() => changePage("Start Interview")}

              >

                <Play size={17} fill="currentColor" /> Start an interview

              </button>

            </section>


            <section className="stats-grid">

              <StatCard

                icon={<BrainCircuit />}

                label="Total interviews"

                value={String(historyData?.total_interviews ?? 0)}

                note="All your interview sessions"

                color="purple"

              />

              <StatCard

                icon={<Target />}

                label="Average score"

                value={averageScore != null ? `${averageScore.toFixed(2)}/10` : "—"}

                note="Based on completed interviews"

                color="blue"

              />

              <StatCard

                icon={<CircleCheck />}

                label="Completed"

                value={String(historyData?.completed_interviews ?? 0)}

                note="Completed interview sessions"

                color="green"

              />

              <StatCard

                icon={<Clock3 />}

                label="Practice time"

                value="—"

                note="Duration data is not available yet"

                color="orange"

              />

            </section>


            <section className="content-grid">

              <div className="panel recent-panel">

                <div className="panel-heading">

                  <div>

                    <h2>Recent interviews</h2>

                    <p>Your latest practice sessions</p>

                  </div>

                  <button

                    className="text-button"

                    onClick={() => changePage("Interview History")}

                  >

                    View history <ArrowUpRight size={15} />

                  </button>

                </div>

                {historyLoading ? <p>Loading recent interviews...</p> :
                historyError ? <p role="alert" style={{ color: "#b42332" }}>{historyError}</p> :
                sessions.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon"><History size={25} /></div>
                    <h3>No interviews yet</h3>
                    <p>Start an interview to see your sessions and scores here.</p>
                    <button className="secondary-button" onClick={() => changePage("Start Interview")}>Start your first interview</button>
                  </div>
                ) : (
                  <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                      <thead><tr>
                        <th style={{ textAlign: "left", padding: 10 }}>Topic</th>
                        <th style={{ textAlign: "left", padding: 10 }}>Status</th>
                        <th style={{ textAlign: "left", padding: 10 }}>Score</th>
                      </tr></thead>
                      <tbody>{sessions.slice(0, 5).map((session) => (
                        <tr key={session.session_id}>
                          <td style={{ padding: 10 }}>{session.topic}</td>
                          <td style={{ padding: 10 }}>{session.status.replaceAll("_", " ")}</td>
                          <td style={{ padding: 10 }}>{session.average_score != null ? `${session.average_score.toFixed(2)}/10` : "Not completed"}</td>
                        </tr>
                      ))}</tbody>
                    </table>
                  </div>
                )}

              </div>


              <div className="panel quick-panel">

                <div className="panel-heading">

                  <div>

                    <h2>Quick practice</h2>

                    <p>Choose a focus area</p>

                  </div>

                </div>

                <QuickPractice

                  icon={<Code2 />}

                  title="Python fundamentals"

                  description="Core concepts and coding questions"

                  onClick={() => {

                    setRole("Python Developer");

                    changePage("Start Interview");

                  }}

                />

                <QuickPractice

                  icon={<BrainCircuit />}

                  title="AI & Machine Learning"

                  description="ML concepts, models, and evaluation"

                  onClick={() => {

                    setRole("AI / ML Engineer");

                    changePage("Start Interview");

                  }}

                />

                <QuickPractice

                  icon={<ChartNoAxesCombined />}

                  title="Data structures"

                  description="Lists, tuples, dictionaries, and more"

                  onClick={() => {

                    setRole("Software Developer");

                    changePage("Start Interview");

                  }}

                />

              </div>

            </section>


            <section className="bottom-banner">

              <div className="banner-symbol">

                <BrainCircuit size={28} />

              </div>

              <div>

                <h2>Your personal AI interview coach</h2>

                <p>

                  Get evaluated answers, identify weak areas, and improve with

                  every session.

                </p>

              </div>

              <button

                className="banner-button"

                onClick={() => changePage("Performance")}

              >

                Explore performance <ArrowUpRight size={16} />

              </button>

            </section>


            <p className="footer-note">

              InterviewAI <span>•</span> AI-powered interview practice

            </p>

          </div>

        )}


        {page === "Start Interview" && (

          <div className="page-container subpage">

            <div className="eyebrow">

              <span className="status-pulse" /> PERSONALIZED PRACTICE

            </div>

            <h1>Configure your interview</h1>

            <p className="subtitle">

              Choose your focus and prepare for a realistic interview session.

            </p>


            <div className="form-panel panel">

              <div className="form-heading">

                <div className="form-heading-icon">

                  <BrainCircuit size={23} />

                </div>

                <div>

                  <h2>Interview setup</h2>

                  <p>Customize your practice session</p>

                </div>

              </div>


              <form onSubmit={handleStartInterview}>

                <label htmlFor="target-role">Target job role</label>

                <select id="target-role" value={role} onChange={(e) => setRole(e.target.value)}>

                  {["Python Developer", "AI / ML Engineer", "Software Developer", "Frontend Developer", "Data Analyst", "Backend Developer"].map((item) => (

                    <option key={item} value={item}>{item}</option>

                  ))}

                </select>


                <label htmlFor="interview-topic">Interview topic</label>

                <select

                  id="interview-topic"

                  value={selectedTopic}

                  onChange={(e) => setSelectedTopic(e.target.value)}

                  required

                >

                  <option value="">Select a topic</option>

                  {topics.map((topic) => <option key={topic} value={topic}>{topic}</option>)}

                </select>

                {topics.length === 0 && !interviewError && (

                  <p className="form-footnote">Loading topics from the server...</p>

                )}


                <label>Concepts to practice</label>

                {concepts.length === 0 ? (

                  <p className="form-footnote">Select a topic to load its concepts.</p>

                ) : (

                  <div className="choice-grid">

                    {concepts.map((concept) => (

                      <label key={concept} style={{ display: "flex", alignItems: "center", gap: 8 }}>

                        <input

                          type="checkbox"

                          checked={selectedConcepts.includes(concept)}

                          onChange={(e) => setSelectedConcepts((current) =>

                            e.target.checked

                              ? [...current, concept]

                              : current.filter((item) => item !== concept)

                          )}

                        />

                        {concept}

                      </label>

                    ))}

                  </div>

                )}


                <label htmlFor="question-type">Question type</label>

                <select id="question-type" value={questionType} onChange={(e) => setQuestionType(e.target.value)}>

                  <option value="Conceptual">Conceptual</option>

                  <option value="Coding">Coding</option>

                </select>


                <label>Difficulty</label>

                <div className="choice-grid">

                  {["Beginner", "Intermediate", "Advanced"].map((item) => (

                    <button type="button" key={item} className={`choice ${level === item ? "selected" : ""}`} onClick={() => setLevel(item)}>

                      {item}

                    </button>

                  ))}

                </div>


                <label>Number of questions</label>

                <div className="choice-grid">

                  {["3", "5", "10", "15"].map((item) => (

                    <button type="button" key={item} className={`choice ${questionCount === item ? "selected" : ""}`} onClick={() => setQuestionCount(item)}>

                      {item} questions

                    </button>

                  ))}

                </div>


                <label htmlFor="education">Education</label>

                <input id="education" required value={candidateEducation} onChange={(e) => setCandidateEducation(e.target.value)} placeholder="Degree or qualification" />


                <label htmlFor="skills">Skills</label>

                <input id="skills" required value={candidateSkills} onChange={(e) => setCandidateSkills(e.target.value)} placeholder="Python, SQL, React (comma-separated)" />


                <label htmlFor="projects">Projects</label>

                <textarea id="projects" required value={candidateProjects} onChange={(e) => setCandidateProjects(e.target.value)} placeholder="Enter your projects, one per line" rows={3} />


                <label htmlFor="experience">Experience</label>

                <input id="experience" required value={candidateExperience} onChange={(e) => setCandidateExperience(e.target.value)} placeholder="Fresher, internship, or work experience" />


                <div className="setup-summary">

                  <Zap size={18} />

                  <span>

                    <strong>AI-powered evaluation</strong>

                    <br />Your answers will be evaluated and feedback generated by the interview system.

                  </span>

                </div>


                {interviewError && <p role="alert" style={{ color: "#b42332" }}>{interviewError}</p>}


                <button className="primary-button full-button" type="submit" disabled={startingInterview || !topics.length || !selectedTopic}>

                  <Play size={17} fill="currentColor" /> {startingInterview ? "Starting interview\..." : "Start interview session"}

                </button>


                <p className="form-footnote">

                  Selected: {role} · {selectedTopic || "No topic selected"} · {level} · {questionCount} questions

                </p>

              </form>

            </div>

          </div>

        )}


        {page === "Interview History" && (

          <div className="page-container subpage">

            <div className="eyebrow">

              <span className="status-pulse" /> YOUR JOURNEY

            </div>

            <h1>Interview history</h1>

            <p className="subtitle">

              Review your past sessions and track your progress over time.

            </p>

            <div className="panel" style={{ padding: 20 }}>
              <div className="panel-heading">
                <div><h2>Your sessions</h2><p>{historyData?.total_interviews ?? 0} total interviews · {historyData?.completed_interviews ?? 0} completed</p></div>
              </div>
              {historyLoading ? <p>Loading interview history...</p> :
               historyError ? <p role="alert" style={{ color: "#b42332" }}>{historyError}</p> :
               sessions.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon"><History size={26} /></div>
                  <h3>No interview history yet</h3>
                  <p>Your completed and in-progress sessions will appear here.</p>
                  <button className="primary-button" onClick={() => changePage("Start Interview")}>Start an interview</button>
                </div>
               ) : (
                <div style={{ overflowX: "auto" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 650 }}>
                    <thead><tr>{["Topic", "Question type", "Questions", "Average score", "Difficulty", "Status", "Date", "Action"].map((heading) => <th key={heading} style={{ textAlign: "left", padding: 12, borderBottom: "1px solid #e8eaf2", fontSize: 12 }}>{heading}</th>)}</tr></thead>
                    <tbody>{sessions.map((session) => (
                      <tr key={session.session_id}>
                        <td style={{ padding: 12 }}><strong>{session.topic}</strong><div style={{ fontSize: 11, color: "#777c91" }}>Session #{session.session_id}</div></td>
                        <td style={{ padding: 12 }}>{session.question_type}</td>
                        <td style={{ padding: 12 }}>{session.total_questions}</td>
                        <td style={{ padding: 12 }}>{session.average_score != null ? `${session.average_score.toFixed(2)}/10` : "—"}</td>
                        <td style={{ padding: 12 }}>{session.final_difficulty ?? session.starting_difficulty}</td>
                        <td style={{ padding: 12 }}>{session.status.replaceAll("_", " ")}</td>
                        <td style={{ padding: 12 }}>{session.started_at ? new Date(session.started_at).toLocaleDateString() : "—"}</td>
                        <td style={{ padding: 12, whiteSpace: "nowrap" }}>
                          {session.status.toUpperCase() === "IN_PROGRESS" ? (
                            <button
                              type="button"
                              className="primary-button"
                              onClick={() => void resumeInterview(session.session_id)}
                            >
                              <Play size={14} /> Resume interview
                            </button>
                          ) : (
                            <span style={{ color: "#777c91" }}>—</span>
                          )}
                        </td>
                      </tr>
                    ))}</tbody>
                  </table>
                </div>
               )}
            </div>

          </div>

        )}


        {page === "Performance" && (

          <div className="page-container subpage">

            <div className="eyebrow">

              <span className="status-pulse" /> YOUR GROWTH

            </div>

            <h1>Performance analytics</h1>

            <p className="subtitle">

              Understand your strengths and discover what to improve next.

            </p>

            <section className="stats-grid">

              <StatCard

                icon={<Target />}

                label="Average score"

                value={averageScore != null ? `${averageScore.toFixed(2)}/10` : "—"}

                note="Average across completed interviews"

                color="purple"

              />

              <StatCard

                icon={<CircleCheck />}

                label="Questions answered"

                value={String(questionsAnswered)}

                note="Questions in completed interviews"

                color="green"

              />

            </section>

            <div className="panel" style={{ padding: 22 }}>
              <h2 style={{ marginTop: 0 }}>Interview performance</h2>
              {historyLoading ? <p>Loading performance data...</p> :
               historyError ? <p role="alert" style={{ color: "#b42332" }}>{historyError}</p> :
               completedSessions.length === 0 ? <p>Complete an interview to see your performance here.</p> : (
                <>
                  <p style={{ color: "#71758a" }}>Scores from your completed interview sessions.</p>
                  {completedSessions.map((session) => (
                    <div key={session.session_id} style={{ padding: "15px 0", borderBottom: "1px solid #e8eaf2" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                        <strong>{session.topic} · Session #{session.session_id}</strong>
                        <strong>{session.average_score != null ? `${session.average_score.toFixed(2)}/10` : "—"}</strong>
                      </div>
                      <p style={{ marginBottom: 8, color: "#71758a", fontSize: 13 }}>{session.total_questions} questions · {session.final_difficulty ?? "Difficulty unavailable"}</p>
                      <div style={{ height: 8, background: "#ececf5", borderRadius: 10, overflow: "hidden" }}>
                        <div style={{ height: "100%", width: `${Math.max(0, Math.min(100, (session.average_score ?? 0) * 10))}%`, background: "#7057d9", borderRadius: 10 }} />
                      </div>
                    </div>
                  ))}
                </>
               )}
            </div>

          </div>

        )}


        {page === "Live Interview" && interviewQuestion && (

          <div className="page-container subpage">

            <div className="eyebrow">

              <span className="status-pulse" /> INTERVIEW IN PROGRESS

            </div>

            <h1>Question {interviewQuestion.question_number}</h1>

            <p className="subtitle">

              {interviewQuestion.concept} · {interviewQuestion.difficulty} · {interviewQuestion.question_type}

            </p>

            <div className="panel form-panel">

              <p className="form-footnote">

                Session {interviewQuestion.session_id} · Question {interviewQuestion.question_number}

              </p>

              <h2>{interviewQuestion.question}</h2>


              {lastEvaluation && (

                <EvaluationCard evaluation={lastEvaluation} score={lastScore} />

              )}


              <form onSubmit={handleSubmitAnswer}>

                <label htmlFor="interview-answer">Your answer</label>

                <textarea

                  id="interview-answer"

                  value={answerText}

                  onChange={(event) => setAnswerText(event.target.value)}

                  placeholder="Type your answer here..."

                  rows={7}

                  required

                  disabled={submittingAnswer}

                  style={{ width: "100%", boxSizing: "border-box", marginTop: 8, marginBottom: 16 }}

                />


                {answerError && (

                  <p role="alert" style={{ color: "#b42332" }}>{answerError}</p>

                )}


                <button

                  type="submit"

                  className="primary-button full-button"

                  disabled={submittingAnswer || !answerText.trim()}

                >

                  {submittingAnswer ? "Evaluating answer..." : "Submit answer and continue"}

                </button>

              </form>

              <button

                type="button"

                className="secondary-button"

                style={{ marginTop: 12 }}

                onClick={() => changePage("Dashboard")}

              >

                Return to dashboard

              </button>

            </div>

          </div>

        )}


        {page === "Interview Complete" && (

          <div className="page-container subpage">

            <div className="eyebrow">

              <span className="status-pulse" /> INTERVIEW FINISHED

            </div>

            <h1>Interview complete</h1>

            {finalResult && <InterviewResults result={finalResult} />}

            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 20 }}>

              <button className="primary-button" onClick={startAnotherInterview}>

                Start another interview

              </button>

              <button className="secondary-button" onClick={() => changePage("Dashboard")}>

                Return to dashboard

              </button>

            </div>

          </div>

        )}

      </main>

    </div>

  );

}


function parseEvaluation(evaluation: string) {
  const labels = ["Correctness", "Relevance", "Technical Depth", "Clarity", "Missing Concepts", "Overall Feedback"];
  const normalized = evaluation.replace(/\\r\\n/g, "\n").replace(/\\n/g, "\n").replace(/\r\n/g, "\n");
  const cleaned = normalized.split("\n")
    .filter((line) => !/^\s*Score\s*:\s*\d+(?:\.\d+)?\s*\/\s*10\s*$/i.test(line.trim()))
    .join("\n").trim();
  const fields: { label: string; text: string }[] = [];
  for (let i = 0; i < labels.length; i += 1) {
    const label = labels[i];
    const escapeRegex = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const nextLabels = labels.slice(i + 1).map(escapeRegex).join("|");
    const pattern = new RegExp(`${escapeRegex(label)}\\s*:\\s*([\\s\\S]*?)(?=\\n\\s*(?:${nextLabels || "(?!)"})\\s*:|$)`, "i");
    const match = cleaned.match(pattern);
    if (match?.[1]?.trim()) fields.push({ label, text: match[1].trim() });
  }
  return { cleaned, fields };
}

function EvaluationCard({ evaluation, score }: { evaluation: string; score: number | null }) {

  const parsed = parseEvaluation(evaluation);

  return (

    <section className="panel" style={{ padding: 22, marginBottom: 20, background: "#fbf9ff", borderColor: "#e9ddff" }}>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16, flexWrap: "wrap", marginBottom: 18 }}>

        <div>

          <h3 style={{ margin: 0, color: "#30204f" }}>Previous answer evaluation</h3>

          <p style={{ margin: "5px 0 0", color: "#716781", fontSize: 13 }}>Feedback for your submitted answer</p>

        </div>

        {score !== null && (

          <div style={{ borderRadius: 14, padding: "10px 16px", background: "#eee5ff", color: "#6d35d5", textAlign: "center", minWidth: 82 }}>

            <div style={{ fontSize: 23, fontWeight: 800, lineHeight: 1.2 }}>{score}<span style={{ fontSize: 13, fontWeight: 600 }}>/10</span></div>

            <div style={{ fontSize: 11, fontWeight: 700 }}>SCORE</div>

          </div>

        )}

      </div>

      {parsed.fields.length > 0 ? (

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>

          {parsed.fields.map((field) => (

            <div key={field.label} style={{ background: "#fff", border: "1px solid #eee7f8", borderRadius: 11, padding: 14 }}>

              <h4 style={{ margin: "0 0 7px", color: "#6535bf", fontSize: 13 }}>{field.label}</h4>

              <p style={{ margin: 0, color: "#514961", fontSize: 13, lineHeight: 1.7, whiteSpace: "pre-wrap" }}>{field.text}</p>

            </div>

          ))}

        </div>

      ) : (

        <p style={{ margin: 0, color: "#514961", fontSize: 13, lineHeight: 1.7, whiteSpace: "pre-wrap" }}>{parsed.cleaned}</p>

      )}

    </section>

  );

}


function InterviewResults({ result }: { result: AnswerSubmissionResponse }) {

  const totalQuestions = typeof result.total_questions === "number" ? result.total_questions : 0;

  const totalScore = typeof result.total_score === "number" ? result.total_score : null;

  const averageScore = typeof result.average_score === "number" ? result.average_score : null;

  const finalDifficulty = typeof result.final_difficulty === "string" ? result.final_difficulty : "—";

  const weakAreas = Array.isArray(result.weak_areas) ? result.weak_areas : [];

  const rawFeedback = typeof result.feedback_report === "string" ? result.feedback_report : "";

  // The backend report may contain literal escaped newlines (\n), rather than

  // actual newline characters. Normalize them before splitting into sections.

  const feedback = rawFeedback
    .replace(/\\\\n/g, "\n")
    .replace(/\\n/g, "\n")
    .replace(/\r\n/g, "\n");

  const reportSections = feedback
    .split(/\n\s*(?=(?:Strengths|Weak Areas|Technical Assessment|Recommendations|Areas for Improvement|Overall Performance|Weaknesses|Next Steps):)/i)
    .map((section) => section.trim())
    .filter(Boolean);

  const sectionTitle = (section: string) => {
    const match = section.match(/^([^:\n]+):\s*/);
    return match ? match[1] : "Interview feedback";
  };

  const sectionBody = (section: string) =>
    section.replace(/^[^:\n]+:\s*/, "").replace(/\\n/g, "\n").trim();


  return (

    <div style={{ display: "grid", gap: 18 }}>

      <section className="panel" style={{ padding: 24 }}>

        <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 22 }}>

          <div className="empty-icon"><CircleCheck size={28} /></div>

          <div>

            <h2 style={{ margin: 0 }}>Interview results</h2>

            <p style={{ margin: "5px 0 0", color: "#6d7285" }}>Session {String(result.session_id ?? "—")} · Completed successfully</p>

          </div>

        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 14 }}>

          <ResultMetric label="Average score" value={averageScore !== null ? `${averageScore.toFixed(2)}/10` : "—"} detail="Across all answers" />

          <ResultMetric label="Total score" value={totalScore !== null ? String(totalScore) : "—"} detail={totalQuestions ? `Out of ${totalQuestions * 10}` : "Across the interview"} />

          <ResultMetric label="Questions answered" value={totalQuestions ? String(totalQuestions) : "—"} detail="Completed questions" />

          <ResultMetric label="Final difficulty" value={finalDifficulty} detail="Adaptive interview level" />

        </div>

      </section>


      <section className="panel" style={{ padding: 24 }}>

        <h2 style={{ marginTop: 0 }}>Personalized feedback</h2>

        {reportSections.length ? (

          <div style={{ display: "grid", gap: 14 }}>

            {reportSections.map((section, index) => (

              <article key={`${sectionTitle(section)}-${index}`} style={{ border: "1px solid #e8eaf2", borderRadius: 12, padding: 16, background: "#fff" }}>

                <h3 style={{ margin: "0 0 8px", fontSize: 15, color: "#5145bf" }}>{sectionTitle(section)}</h3>

                <p style={{ margin: 0, lineHeight: 1.8, color: "#4c5265", whiteSpace: "pre-wrap" }}>{sectionBody(section)}</p>

              </article>

            ))}

          </div>

        ) : (

          <p style={{ color: "#4c5265", lineHeight: 1.8, whiteSpace: "pre-wrap" }}>

            {feedback

              ? feedback.replace(/\\n/g, "\n")

              : "No personalized feedback report was returned."}

          </p>

        )}

      </section>


      <section className="panel" style={{ padding: 24 }}>

        <h2 style={{ marginTop: 0 }}>Weak areas</h2>

        {weakAreas.length ? (

          <ul style={{ marginBottom: 0, paddingLeft: 22, lineHeight: 1.8 }}>

            {weakAreas.map((area, index) => <li key={index}>{typeof area === "string" ? area : JSON.stringify(area)}</li>)}

          </ul>

        ) : (

          <p style={{ marginBottom: 0, color: "#28734d" }}>No significant weak areas were detected in this interview.</p>

        )}

      </section>

    </div>

  );

}


function ResultMetric({ label, value, detail }: { label: string; value: string; detail: string }) {

  return (

    <div style={{ padding: 16, borderRadius: 13, background: "#f7f7fc", border: "1px solid #ececf5" }}>

      <p style={{ margin: "0 0 9px", fontSize: 12, color: "#71758a", fontWeight: 650 }}>{label}</p>

      <div style={{ fontSize: 25, fontWeight: 800, color: "#292444", overflowWrap: "anywhere" }}>{value}</div>

      <p style={{ margin: "7px 0 0", fontSize: 11, color: "#81859a" }}>{detail}</p>

    </div>

  );

}


function AuthScreen({

  mode,

  onModeChange,

  onLogin,

  onSignup,

}: {

  mode: AuthMode;

  onModeChange: (mode: AuthMode) => void;

  onLogin: (email: string, password: string) => Promise<void>;

  onSignup: (

    name: string,

    email: string,

    password: string,

  ) => Promise<void>;

}) {

  const [name, setName] = useState("");

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [confirmPassword, setConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);

  const [submitting, setSubmitting] = useState(false);

  const [error, setError] = useState("");

  const [success, setSuccess] = useState("");


  const isSignup = mode === "signup";


  async function handleSubmit(event: FormEvent<HTMLFormElement>) {

    event.preventDefault();

    setError("");

    setSuccess("");


    if (isSignup && password !== confirmPassword) {

      setError("Passwords do not match.");

      return;

    }


    if (password.length < 8) {

      setError("Password must contain at least 8 characters.");

      return;

    }


    setSubmitting(true);


    try {

      if (isSignup) {

        await onSignup(name.trim(), email.trim(), password);

      } else {

        await onLogin(email.trim(), password);

      }

    } catch (err) {

      setError(

        err instanceof Error ? err.message : "Something went wrong.",

      );

    } finally {

      setSubmitting(false);

    }

  }


  return (

    <div style={authPageStyle}>

      <section style={authCardStyle}>

        <div style={authBrandStyle}>

          <div style={authLogoStyle}>

            <BrainCircuit size={30} />

          </div>

          <div>

            <h1 style={{ margin: 0, fontSize: 25, color: "#202338" }}>

              InterviewAI

            </h1>

            <p style={{ margin: "5px 0 0", color: "#777c91", fontSize: 11 }}>

              INTELLIGENCE PLATFORM

            </p>

          </div>

        </div>


        <div style={{ marginTop: 34 }}>

          <div style={authEyebrowStyle}>

            <ShieldCheck size={15} /> YOUR PERSONAL AI INTERVIEW COACH

          </div>

          <h2 style={{ fontSize: 28, margin: "15px 0 8px", color: "#202338" }}>

            {isSignup ? "Create your account" : "Welcome back"}

          </h2>

          <p style={{ margin: 0, color: "#777c91", lineHeight: 1.6 }}>

            {isSignup

              ? "Create an account to start your personalized interview practice."

              : "Sign in to continue building your interview confidence."}

          </p>

        </div>


        <div style={authTabsStyle}>

          <button

            type="button"

            onClick={() => {

              onModeChange("login");

              setError("");

              setSuccess("");

            }}

            style={authTabStyle(mode === "login")}

          >

            <LogIn size={17} /> Login

          </button>

          <button

            type="button"

            onClick={() => {

              onModeChange("signup");

              setError("");

              setSuccess("");

            }}

            style={authTabStyle(mode === "signup")}

          >

            <UserPlus size={17} /> Sign up

          </button>

        </div>


        {error && (

          <div role="alert" style={messageStyle("error")}>

            {error}

          </div>

        )}


        {success && (

          <div role="status" style={messageStyle("success")}>

            {success}

          </div>

        )}


        <form onSubmit={handleSubmit}>

          {isSignup && (

            <div style={fieldStyle}>

              <label htmlFor="signup-name" style={labelStyle}>

                Full name

              </label>

              <input

                id="signup-name"

                autoComplete="name"

                required

                minLength={1}

                maxLength={100}

                placeholder="Enter your full name"

                value={name}

                onChange={(e) => setName(e.target.value)}

                style={authInputStyle}

              />

            </div>

          )}


          <div style={fieldStyle}>

            <label htmlFor="auth-email" style={labelStyle}>

              Email address

            </label>

            <input

              id="auth-email"

              type="email"

              autoComplete="email"

              required

              maxLength={150}

              placeholder="you@example.com"

              value={email}

              onChange={(e) => setEmail(e.target.value)}

              style={authInputStyle}

            />

          </div>


          <div style={fieldStyle}>

            <label htmlFor="auth-password" style={labelStyle}>

              Password

            </label>

            <div style={{ position: "relative" }}>

              <input

                id="auth-password"

                type={showPassword ? "text" : "password"}

                autoComplete={isSignup ? "new-password" : "current-password"}

                required

                minLength={8}

                maxLength={128}

                placeholder={

                  isSignup ? "At least 8 characters" : "Enter your password"

                }

                value={password}

                onChange={(e) => setPassword(e.target.value)}

                style={{ ...authInputStyle, paddingRight: 48 }}

              />

              <button

                type="button"

                onClick={() => setShowPassword((value) => !value)}

                aria-label={showPassword ? "Hide password" : "Show password"}

                style={passwordToggleStyle}

              >

                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}

              </button>

            </div>

          </div>


          {isSignup && (

            <div style={fieldStyle}>

              <label htmlFor="confirm-password" style={labelStyle}>

                Confirm password

              </label>

              <input

                id="confirm-password"

                type={showPassword ? "text" : "password"}

                autoComplete="new-password"

                required

                minLength={8}

                maxLength={128}

                placeholder="Re-enter your password"

                value={confirmPassword}

                onChange={(e) => setConfirmPassword(e.target.value)}

                style={authInputStyle}

              />

            </div>

          )}


          <button

            type="submit"

            disabled={submitting}

            style={submitButtonStyle(submitting)}

          >

            {submitting

              ? "Please wait..."

              : isSignup

                ? "Create account"

                : "Sign in"}

            {!submitting && <ArrowUpRight size={18} />}

          </button>

        </form>


        <p style={authFooterStyle}>

          {isSignup ? "Already have an account? " : "New to InterviewAI? "}

          <button

            type="button"

            onClick={() => {

              onModeChange(isSignup ? "login" : "signup");

              setError("");

              setSuccess("");

            }}

            style={linkButtonStyle}

          >

            {isSignup ? "Sign in" : "Create an account"}

          </button>

        </p>


        <div style={secureNoteStyle}>

          <ShieldCheck size={15} />

          Your account is protected by authenticated API access.

        </div>

      </section>


      <p style={{ color: "#777c91", fontSize: 12, marginTop: 20 }}>

        InterviewAI · AI-powered interview practice

      </p>

    </div>

  );

}


function StatCard({

  icon,

  label,

  value,

  note,

  color,

}: {

  icon: ReactNode;

  label: string;

  value: string;

  note: string;

  color: string;

}) {

  return (

    <div className="stat-card">

      <div className={`stat-icon ${color}`}>{icon}</div>

      <div className="stat-label">{label}</div>

      <div className="stat-value">{value}</div>

      <div className="stat-note">{note}</div>

    </div>

  );

}


function QuickPractice({

  icon,

  title,

  description,

  onClick,

}: {

  icon: ReactNode;

  title: string;

  description: string;

  onClick: () => void;

}) {

  return (

    <button className="quick-practice" onClick={onClick}>

      <div className="quick-icon">{icon}</div>

      <div className="quick-text">

        <strong>{title}</strong>

        <span>{description}</span>

      </div>

      <ArrowUpRight size={17} className="quick-arrow" />

    </button>

  );

}


const centeredStyle = {

  minHeight: "100vh",

  display: "flex",

  flexDirection: "column" as const,

  alignItems: "center",

  justifyContent: "center",

  gap: 10,

  color: "#6256d9",

  background: "#f7f8fc",

};


const authPageStyle = {

  minHeight: "100vh",

  padding: "36px 18px",

  boxSizing: "border-box" as const,

  display: "flex",

  flexDirection: "column" as const,

  alignItems: "center",

  justifyContent: "center",

  background:

    "radial-gradient(ellipse at top left, #eeecff 0%, transparent 48%), #f7f8fc",

  fontFamily: "Inter, system-ui, -apple-system, sans-serif",

};


const authCardStyle = {

  width: "100%",

  maxWidth: 450,

  boxSizing: "border-box" as const,

  padding: "34px 32px",

  borderRadius: 20,

  border: "1px solid #e8e9f1",

  background: "#ffffff",

  boxShadow: "0 24px 70px rgba(40, 36, 90, 0.09)",

};


const authBrandStyle = {

  display: "flex",

  alignItems: "center",

  gap: 12,

};


const authLogoStyle = {

  width: 52,

  height: 52,

  borderRadius: 15,

  display: "grid",

  placeItems: "center",

  color: "#ffffff",

  background: "linear-gradient(135deg, #7767ee, #5145bf)",

};


const authEyebrowStyle = {

  display: "flex",

  alignItems: "center",

  gap: 7,

  color: "#6557d9",

  fontSize: 10,

  fontWeight: 800,

  letterSpacing: "0.07em",

};


const authTabsStyle = {

  display: "grid",

  gridTemplateColumns: "1fr 1fr",

  gap: 5,

  padding: 5,

  margin: "26px 0 22px",

  background: "#f2f3f9",

  borderRadius: 12,

};


function authTabStyle(active: boolean) {

  return {

    display: "flex",

    justifyContent: "center",

    alignItems: "center",

    gap: 8,

    padding: "11px 8px",

    border: "none",

    borderRadius: 9,

    cursor: "pointer",

    fontWeight: 700,

    fontSize: 13,

    color: active ? "#5548c6" : "#73778b",

    background: active ? "#ffffff" : "transparent",

    boxShadow: active ? "0 2px 8px rgba(30, 30, 70, 0.07)" : "none",

  };

}


const fieldStyle = {

  display: "flex",

  flexDirection: "column" as const,

  gap: 8,

  marginBottom: 17,

};


const labelStyle = {

  fontSize: 13,

  fontWeight: 650,

  color: "#35384d",

};


const passwordToggleStyle = {

  position: "absolute" as const,

  top: 0,

  right: 0,

  height: "100%",

  width: 44,

  display: "grid",

  placeItems: "center",

  border: "none",

  background: "transparent",

  color: "#777c91",

  cursor: "pointer",

};


function submitButtonStyle(disabled: boolean) {

  return {

    width: "100%",

    marginTop: 6,

    padding: "14px 16px",

    border: "none",

    borderRadius: 11,

    display: "flex",

    alignItems: "center",

    justifyContent: "center",

    gap: 9,

    color: "#ffffff",

    background: disabled ? "#9991e8" : "linear-gradient(135deg, #7465e8, #5145bf)",

    fontSize: 14,

    fontWeight: 750,

    cursor: disabled ? "wait" : "pointer",

    opacity: disabled ? 0.8 : 1,

  };

}


function messageStyle(type: "error" | "success") {

  return {

    padding: "11px 12px",

    marginBottom: 18,

    borderRadius: 9,

    fontSize: 13,

    lineHeight: 1.5,

    color: type === "error" ? "#a62f3c" : "#176a45",

    background: type === "error" ? "#fff0f1" : "#eaf8f0",

    border: `1px solid ${type === "error" ? "#ffd8dc" : "#ccebd9"}`,

  };

}


const authFooterStyle = {

  margin: "22px 0 0",

  textAlign: "center" as const,

  color: "#777c91",

  fontSize: 13,

};


const linkButtonStyle = {

  border: "none",

  background: "transparent",

  color: "#5c4dcf",

  fontWeight: 750,

  cursor: "pointer",

  padding: 0,

  fontSize: 13,

};


const secureNoteStyle = {

  display: "flex",

  alignItems: "center",

  justifyContent: "center",

  gap: 7,

  marginTop: 24,

  paddingTop: 18,

  borderTop: "1px solid #eef0f5",

  color: "#85899a",

  fontSize: 11,

  textAlign: "center" as const,

};


const iconButtonStyle = {

  border: "none",

  background: "transparent",

  color: "inherit",

  cursor: "pointer",

  display: "grid",

  placeItems: "center",

};


export default App;
