import { useEffect, useMemo, useState } from "react";
import InputForm from "./components/InputForm";
import { analyzeContent, fetchHistory } from "./services/api";
import "./App.css";

function App() {
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

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

  const loadHistory = async () => {
    try {
      const response = await fetchHistory();
      setHistory(response.history ?? []);
    } catch (historyError) {
      console.error(historyError);
    }
  };

  useEffect(() => {
    let isMounted = true;

    fetchHistory()
      .then((response) => {
        if (isMounted) {
          setHistory(response.history ?? []);
        }
      })
      .catch((historyError) => {
        console.error(historyError);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const handleAnalyze = async (data) => {
    setIsLoading(true);
    setError("");

    try {
      const response = await analyzeContent(data);
      setResult(response);
      await loadHistory();
    } catch (error) {
      console.error(error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <nav className="topbar" aria-label="Main navigation">
        <a className="brand" href="#top">MediaVerify</a>
        <div className="nav-links">
          <a href="#analyze">Analyze</a>
          <a href="#result">Result</a>
          <a href="#history">History</a>
        </div>
      </nav>

      <header className="app-header" id="top">
        <div className="hero-copy">
          <h1>MediaVerify</h1>
          <p>
            Cut through the noise with clear credibility scoring, explainable
            signals, and a review history built for ongoing verification.
          </p>
        </div>
        <div className="status-strip" aria-label="Platform overview">
          <div>
            <span>{history.length}</span>
            <p>Analyses</p>
          </div>
          <div>
            <span>{averageScore}%</span>
            <p>Average Score</p>
          </div>
          <div>
            <span>{credibleCount}</span>
            <p>Likely Credible</p>
          </div>
        </div>
      </header>

      <main className="workspace">
        <section className="tool-panel">
          <InputForm onAnalyze={handleAnalyze} isLoading={isLoading} />
          {error && <p className="error-message">{error}</p>}
        </section>

        <section className="result-panel" id="result" aria-live="polite">
          <div className="section-heading">
            <span className="panel-index">02</span>
            <div>
              <p className="eyebrow">Latest Result</p>
              <h2>Credibility Assessment</h2>
            </div>
          </div>

          {result ? (
            <div className="result-content">
              <div className="score-ring" style={{ "--score": `${resultPercent}%` }}>
                <span>{resultPercent}%</span>
              </div>
              <div>
                <p className="label">{result.credibility_label}</p>
                <p className="muted">
                  Confidence: {Math.round(result.explanation.confidence * 100)}%
                </p>
                <div className="meter" aria-hidden="true">
                  <span style={{ width: `${resultPercent}%` }} />
                </div>
                <ul>
                  {result.explanation.indicators.map((indicator) => (
                    <li key={indicator}>{indicator}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <strong>No result yet</strong>
              <p>Choose text or URL, then run an analysis.</p>
            </div>
          )}
        </section>

        <section className="history-panel" id="history">
          <div className="section-heading">
            <span className="panel-index">03</span>
            <div>
              <p className="eyebrow">Stored Analyses</p>
              <h2>History</h2>
            </div>
          </div>

          {history.length > 0 ? (
            <div className="history-list">
              {history.slice(0, 6).map((item) => (
                <article className="history-item" key={item.id}>
                  <div>
                    <p className="label">{item.credibility_label}</p>
                    <p className="muted">
                      {item.input_type.toUpperCase()} - {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                  <strong>{Math.round(item.credibility_score * 100)}%</strong>
                </article>
              ))}
            </div>
          ) : (
            <p className="empty-state">No saved analyses yet.</p>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
