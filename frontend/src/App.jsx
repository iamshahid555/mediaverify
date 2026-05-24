import { useEffect, useMemo, useState } from "react";
import AuthPanel from "./components/AuthPanel";
import InputForm from "./components/InputForm";
import {
  analyzeContent,
  clearStoredSession,
  fetchCurrentUser,
  fetchHistory,
  getStoredSession,
  loginUser,
  logoutUser,
  registerUser,
  saveStoredSession,
} from "./services/api";
import "./App.css";

function getTone(label) {
  if (label === "Likely Credible") {
    return "positive";
  }

  if (label === "Needs Review") {
    return "review";
  }

  return "negative";
}

function App() {
  const [session, setSession] = useState(() => getStoredSession());
  const [currentUser, setCurrentUser] = useState(() => getStoredSession()?.user ?? null);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");
  const [authError, setAuthError] = useState("");
  const [historyError, setHistoryError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isAuthLoading, setIsAuthLoading] = useState(false);
  const [isBootstrapping, setIsBootstrapping] = useState(() => Boolean(getStoredSession()?.token));

  const resultPercent = useMemo(() => {
    if (!result) return 0;
    return Math.round(result.credibility_score * 100);
  }, [result]);

  const averageScore = useMemo(() => {
    if (!history.length) return 0;
    const total = history.reduce((sum, item) => sum + item.credibility_score, 0);
    return Math.round((total / history.length) * 100);
  }, [history]);

  const credibleCount = useMemo(
    () => history.filter((item) => item.credibility_label === "Likely Credible").length,
    [history],
  );

  const trackedSources = useMemo(
    () => new Set(history.map((item) => item.source_domain).filter(Boolean)).size,
    [history],
  );

  const userFirstName = currentUser?.full_name?.split(" ")[0] ?? "there";
  const resultTone = getTone(result?.credibility_label ?? "Needs Review");

  const loadHistory = async (token = session?.token) => {
    if (!token) {
      setHistory([]);
      return;
    }

    try {
      const response = await fetchHistory(token);
      setHistory(response.history ?? []);
      setHistoryError("");
    } catch (historyLoadError) {
      console.error(historyLoadError);
      setHistoryError(historyLoadError.message);
    }
  };

  useEffect(() => {
    let isMounted = true;

    if (!session?.token) {
      return () => {
        isMounted = false;
      };
    }

    fetchCurrentUser(session.token)
      .then(async (user) => {
        if (!isMounted) {
          return;
        }

        setCurrentUser(user);
        saveStoredSession({
          token: session.token,
          user,
        });

        const response = await fetchHistory(session.token);
        if (isMounted) {
          setHistory(response.history ?? []);
          setHistoryError("");
        }
      })
      .catch((sessionError) => {
        console.error(sessionError);
        if (isMounted) {
          clearStoredSession();
          setSession(null);
          setCurrentUser(null);
          setHistory([]);
          setAuthError("Your session expired. Please sign in again.");
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsBootstrapping(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [session?.token]);

  const handleAnalyze = async (data) => {
    if (!session?.token) {
      setError("Sign in to analyze content and save history.");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await analyzeContent(data, session.token);
      setResult(response);
      await loadHistory(session.token);
    } catch (analysisError) {
      console.error(analysisError);
      setError(analysisError.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAuthSuccess = async (authResponse) => {
    const nextSession = {
      token: authResponse.token,
      user: authResponse.user,
    };

    setIsBootstrapping(true);
    saveStoredSession(nextSession);
    setSession(nextSession);
    setCurrentUser(authResponse.user);
    setAuthError("");
    setError("");
    setHistoryError("");
    setResult(null);
    await loadHistory(nextSession.token);
  };

  const handleLogin = async (credentials) => {
    setIsAuthLoading(true);
    setAuthError("");

    try {
      const response = await loginUser(credentials);
      await handleAuthSuccess(response);
    } catch (loginError) {
      console.error(loginError);
      setAuthError(loginError.message);
    } finally {
      setIsAuthLoading(false);
    }
  };

  const handleRegister = async (registrationData) => {
    setIsAuthLoading(true);
    setAuthError("");

    try {
      const response = await registerUser(registrationData);
      await handleAuthSuccess(response);
    } catch (registrationError) {
      console.error(registrationError);
      setAuthError(registrationError.message);
    } finally {
      setIsAuthLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      if (session?.token) {
        await logoutUser(session.token);
      }
    } catch (logoutError) {
      console.error(logoutError);
    } finally {
      clearStoredSession();
      setSession(null);
      setCurrentUser(null);
      setHistory([]);
      setResult(null);
      setError("");
      setAuthError("");
      setHistoryError("");
    }
  };

  const getHistoryContext = (item) => {
    if (item.input_type === "url") {
      return item.source_domain ? item.source_domain : "URL analysis";
    }

    return "Text analysis";
  };

  return (
    <div className="app-shell">
      <nav className="topbar" aria-label="Main navigation">
        <a className="brand" href="#top">
          MediaVerify
        </a>
        <div className="nav-links">
          <a href="#workspace">Workspace</a>
          <a href="#result">Result</a>
          <a href="#history">History</a>
        </div>
        <div className="account-actions">
          {currentUser ? (
            <>
              <div className="account-badge">
                <strong>{currentUser.full_name}</strong>
                <span>{currentUser.email}</span>
              </div>
              <button className="ghost-button" type="button" onClick={handleLogout}>
                Sign Out
              </button>
            </>
          ) : (
            <div className="account-badge muted-badge">
              <strong>Private Workspace</strong>
              <span>Sign in to save your history</span>
            </div>
          )}
        </div>
      </nav>

      <header className="app-header" id="top">
        <div className="hero-copy">
          <p className="eyebrow">Verification Workspace</p>
          <h1>Assess credibility with clearer signals.</h1>
          <p>
            Review article text or URLs, understand why a result was assigned,
            and return to account-specific history whenever you sign back in.
          </p>
        </div>

        <div className="status-strip" aria-label="Platform overview">
          <div>
            <span>{history.length}</span>
            <p>Saved analyses</p>
          </div>
          <div>
            <span>{averageScore}%</span>
            <p>Average score</p>
          </div>
          <div>
            <span>{credibleCount}</span>
            <p>Likely credible</p>
          </div>
          <div>
            <span>{trackedSources}</span>
            <p>Tracked sources</p>
          </div>
        </div>
      </header>

      <main className="workspace" id="workspace">
        <section className="tool-panel">
          {currentUser ? (
            <>
              <div className="account-panel">
                <div>
                  <p className="eyebrow">Signed In</p>
                  <h2>Welcome back, {userFirstName}</h2>
                  <p className="panel-copy">
                    New analyses are saved directly to your personal workspace.
                  </p>
                </div>
                <div className="account-summary">
                  <span>{history.length}</span>
                  <p>records saved</p>
                </div>
              </div>
              <InputForm onAnalyze={handleAnalyze} isLoading={isLoading} />
            </>
          ) : (
            <AuthPanel
              error={authError}
              isLoading={isAuthLoading}
              onLogin={handleLogin}
              onRegister={handleRegister}
            />
          )}

          {error && <p className="error-message">{error}</p>}
        </section>

        <div className="side-stack">
          <section className="result-panel" id="result" aria-live="polite">
            <div className="section-heading">
              <span className="panel-index">02</span>
              <div>
                <p className="eyebrow">Latest Result</p>
                <h2>Credibility Assessment</h2>
              </div>
            </div>

            {currentUser ? (
              result ? (
                <div className="result-content">
                  <div className={`score-ring tone-${resultTone}`} style={{ "--score": `${resultPercent}%` }}>
                    <span>{resultPercent}%</span>
                  </div>
                  <div className="result-copy">
                    <div className="result-meta">
                      <span className={`status-pill tone-${resultTone}`}>
                        {result.credibility_label}
                      </span>
                      <span className="meta-pill">
                        Confidence {Math.round(result.explanation.confidence * 100)}%
                      </span>
                    </div>
                    <div className="meter" aria-hidden="true">
                      <span className={`tone-${resultTone}`} style={{ width: `${resultPercent}%` }} />
                    </div>
                    <ul className="signal-list">
                      {result.explanation.indicators.map((indicator) => (
                        <li key={indicator}>{indicator}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <strong>No result yet</strong>
                  <p>Run an analysis to see the latest credibility assessment.</p>
                </div>
              )
            ) : (
              <div className="empty-state">
                <strong>Sign in to start verifying</strong>
                <p>Your latest result will appear here once you analyze text or a URL.</p>
              </div>
            )}
          </section>

          <section className="history-panel" id="history">
            <div className="section-heading">
              <span className="panel-index">03</span>
              <div>
                <p className="eyebrow">Account History</p>
                <h2>Saved Analyses</h2>
              </div>
            </div>

            {historyError && <p className="error-message">{historyError}</p>}

            {currentUser ? (
              history.length > 0 ? (
                <div className="history-list">
                  {history.slice(0, 8).map((item) => {
                    const tone = getTone(item.credibility_label);

                    return (
                      <article className="history-item" key={item.id}>
                        <div className="history-copy">
                          <div className="history-heading">
                            <p className={`status-pill tone-${tone}`}>{item.credibility_label}</p>
                            <p className="history-context">{getHistoryContext(item)}</p>
                          </div>
                          {item.content_preview && (
                            <p className="history-preview">{item.content_preview}</p>
                          )}
                          <div className="history-footer">
                            <p className="muted">
                              {new Date(item.created_at).toLocaleString()}
                            </p>
                            {item.source_url && (
                              <a
                                className="history-link"
                                href={item.source_url}
                                rel="noreferrer"
                                target="_blank"
                              >
                                Open source
                              </a>
                            )}
                          </div>
                        </div>
                        <strong className={`history-score tone-${tone}`}>
                          {Math.round(item.credibility_score * 100)}%
                        </strong>
                      </article>
                    );
                  })}
                </div>
              ) : (
                <div className="empty-state">
                  <strong>No saved analyses yet</strong>
                  <p>Your account history will begin filling up after the first check.</p>
                </div>
              )
            ) : (
              <div className="empty-state">
                <strong>Account history stays private</strong>
                <p>Register or sign in to keep a saved timeline of your previous analyses.</p>
              </div>
            )}
          </section>
        </div>
      </main>

      {isBootstrapping && <div className="session-banner">Restoring your workspace...</div>}
    </div>
  );
}

export default App;
