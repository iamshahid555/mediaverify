import { useState } from "react";

function AuthPanel({ onLogin, onRegister, isLoading, error }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({
    fullName: "",
    email: "",
    password: "",
  });
  const [validationMessage, setValidationMessage] = useState("");

  const handleChange = (field, value) => {
    setForm((currentForm) => ({
      ...currentForm,
      [field]: value,
    }));

    if (validationMessage) {
      setValidationMessage("");
    }
  };

  const handleModeChange = (nextMode) => {
    setMode(nextMode);
    setValidationMessage("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const payload = {
      fullName: form.fullName.trim(),
      email: form.email.trim(),
      password: form.password,
    };

    if (mode === "register" && payload.fullName.length < 2) {
      setValidationMessage("Enter a full name with at least 2 characters.");
      return;
    }

    if (!payload.email) {
      setValidationMessage("Enter your email address.");
      return;
    }

    if (payload.password.length < 8) {
      setValidationMessage("Use a password with at least 8 characters.");
      return;
    }

    if (mode === "login") {
      await onLogin({
        email: payload.email,
        password: payload.password,
      });
      return;
    }

    await onRegister({
      full_name: payload.fullName,
      email: payload.email,
      password: payload.password,
    });
  };

  return (
    <form className="analysis-form auth-form" onSubmit={handleSubmit}>
      <div className="form-heading">
        <span className="panel-index">01</span>
        <div>
          <p className="eyebrow">Secure Access</p>
          <h2>{mode === "login" ? "Sign In" : "Create Account"}</h2>
        </div>
      </div>

      <p className="panel-copy">
        Keep your analyses private to your account and return to the same
        history whenever you sign back in.
      </p>

      <div className="mode-toggle" aria-label="Choose authentication mode">
        <button
          aria-pressed={mode === "login"}
          className={mode === "login" ? "active" : ""}
          type="button"
          onClick={() => handleModeChange("login")}
        >
          Sign In
        </button>
        <button
          aria-pressed={mode === "register"}
          className={mode === "register" ? "active" : ""}
          type="button"
          onClick={() => handleModeChange("register")}
        >
          Register
        </button>
      </div>

      {mode === "register" && (
        <label>
          <span>Full name</span>
          <input
            autoComplete="name"
            placeholder="Ariana Malik"
            type="text"
            value={form.fullName}
            onChange={(event) => handleChange("fullName", event.target.value)}
          />
        </label>
      )}

      <label>
        <span>Email</span>
        <input
          autoComplete="email"
          placeholder="name@example.com"
          type="email"
          value={form.email}
          onChange={(event) => handleChange("email", event.target.value)}
        />
      </label>

      <label>
        <span>Password</span>
        <input
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          placeholder="At least 8 characters"
          type="password"
          value={form.password}
          onChange={(event) => handleChange("password", event.target.value)}
        />
      </label>

      {validationMessage && (
        <p className="field-message" role="alert">
          {validationMessage}
        </p>
      )}

      {error && <p className="error-message auth-error">{error}</p>}

      <div className="form-actions auth-actions">
        <button className="primary-action" type="submit" disabled={isLoading}>
          {isLoading
            ? "Working..."
            : mode === "login"
              ? "Sign In"
              : "Create Account"}
        </button>
      </div>
    </form>
  );
}

export default AuthPanel;
