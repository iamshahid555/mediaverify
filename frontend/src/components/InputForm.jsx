import { useState } from "react";

function InputForm({ onAnalyze, isLoading }) {
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [inputMode, setInputMode] = useState("text");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (inputMode === "text" && !text.trim()) {
      alert("Enter article text");
      return;
    }

    if (inputMode === "url" && !url.trim()) {
      alert("Enter article URL");
      return;
    }

    onAnalyze({
      text: inputMode === "text" ? text.trim() : null,
      url: inputMode === "url" ? url.trim() : null,
    });
  };

  const handleClear = () => {
    setText("");
    setUrl("");
  };

  return (
    <form className="analysis-form" id="analyze" onSubmit={handleSubmit}>
      <div className="form-heading">
        <span className="panel-index">01</span>
        <div>
          <p className="eyebrow">Analyze</p>
          <h2>Check Content</h2>
        </div>
      </div>

      <div className="mode-toggle" aria-label="Choose input type">
        <button
          className={inputMode === "text" ? "active" : ""}
          type="button"
          onClick={() => setInputMode("text")}
        >
          Text
        </button>
        <button
          className={inputMode === "url" ? "active" : ""}
          type="button"
          onClick={() => setInputMode("url")}
        >
          URL
        </button>
      </div>

      {inputMode === "text" ? (
        <label>
          <span>Article or claim text</span>
          <textarea
            placeholder="Paste the content you want to verify..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </label>
      ) : (
        <label>
          <span>Article URL</span>
          <input
            type="url"
            placeholder="https://example.com/news/article"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
        </label>
      )}

      <div className="form-actions">
        <button className="primary-action" type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing..." : "Analyze"}
        </button>

        <button className="secondary-action" type="button" onClick={handleClear}>
          Clear
        </button>
      </div>
    </form>
  );
}

export default InputForm;
