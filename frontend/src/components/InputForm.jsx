import { useState } from "react";

function InputForm({ onAnalyze, isLoading }) {
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [inputMode, setInputMode] = useState("text");
  const [validationMessage, setValidationMessage] = useState("");

  const handleModeChange = (nextMode) => {
    setInputMode(nextMode);
    setValidationMessage("");
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmedText = text.trim();
    const trimmedUrl = url.trim();

    if (inputMode === "text" && !trimmedText) {
      setValidationMessage("Enter article or claim text to analyze.");
      return;
    }

    if (inputMode === "text" && trimmedText.length < 50) {
      setValidationMessage("Enter at least 50 characters so the analysis has enough context.");
      return;
    }

    if (inputMode === "url" && !trimmedUrl) {
      setValidationMessage("Enter a public article URL to analyze.");
      return;
    }

    setValidationMessage("");
    onAnalyze({
      text: inputMode === "text" ? trimmedText : null,
      url: inputMode === "url" ? trimmedUrl : null,
    });
  };

  const handleClear = () => {
    setText("");
    setUrl("");
    setValidationMessage("");
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
          aria-pressed={inputMode === "text"}
          className={inputMode === "text" ? "active" : ""}
          type="button"
          onClick={() => handleModeChange("text")}
        >
          Text
        </button>
        <button
          aria-pressed={inputMode === "url"}
          className={inputMode === "url" ? "active" : ""}
          type="button"
          onClick={() => handleModeChange("url")}
        >
          URL
        </button>
      </div>

      {inputMode === "text" ? (
        <label>
          <span>Article or claim text</span>
          <textarea
            aria-describedby={validationMessage ? "analysis-form-message" : undefined}
            aria-invalid={Boolean(validationMessage) && inputMode === "text"}
            placeholder="Paste the content you want to verify..."
            value={text}
            onChange={(e) => {
              setText(e.target.value);
              if (validationMessage) {
                setValidationMessage("");
              }
            }}
          />
        </label>
      ) : (
        <label>
          <span>Article URL</span>
          <input
            aria-describedby={validationMessage ? "analysis-form-message" : undefined}
            aria-invalid={Boolean(validationMessage) && inputMode === "url"}
            type="url"
            placeholder="https://example.com/news/article"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              if (validationMessage) {
                setValidationMessage("");
              }
            }}
          />
        </label>
      )}

      {validationMessage && (
        <p className="field-message" id="analysis-form-message" role="alert">
          {validationMessage}
        </p>
      )}

      <div className="form-actions">
        <button className="primary-action" type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing..." : "Analyze"}
        </button>

        <button
          className="secondary-action"
          type="button"
          onClick={handleClear}
          disabled={isLoading}
        >
          Clear
        </button>
      </div>
    </form>
  );
}

export default InputForm;
