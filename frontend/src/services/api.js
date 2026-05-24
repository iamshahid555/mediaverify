const BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
const SESSION_STORAGE_KEY = "mediaverify.session";

function buildHeaders(token, extraHeaders = {}) {
  const headers = {
    ...extraHeaders,
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

async function parseError(response, fallbackMessage) {
  const error = await response.json().catch(() => ({}));

  if (typeof error.detail === "string") {
    return error.detail;
  }

  if (Array.isArray(error.detail) && error.detail.length > 0) {
    return error.detail.map((item) => item.msg).join(" ");
  }

  return fallbackMessage;
}

async function request(path, { method = "GET", token, data } = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: buildHeaders(
      token,
      data ? { "Content-Type": "application/json" } : {},
    ),
    body: data ? JSON.stringify(data) : undefined,
  });

  if (!response.ok) {
    throw new Error(await parseError(response, "Request failed"));
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export function getStoredSession() {
  const rawSession = window.localStorage.getItem(SESSION_STORAGE_KEY);
  if (!rawSession) {
    return null;
  }

  try {
    return JSON.parse(rawSession);
  } catch {
    window.localStorage.removeItem(SESSION_STORAGE_KEY);
    return null;
  }
}

export function saveStoredSession(session) {
  window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
}

export function clearStoredSession() {
  window.localStorage.removeItem(SESSION_STORAGE_KEY);
}

export function registerUser(data) {
  return request("/auth/register", {
    method: "POST",
    data,
  });
}

export function loginUser(data) {
  return request("/auth/login", {
    method: "POST",
    data,
  });
}

export function fetchCurrentUser(token) {
  return request("/auth/me", {
    token,
  });
}

export function logoutUser(token) {
  return request("/auth/logout", {
    method: "POST",
    token,
  });
}

export function analyzeContent(data, token) {
  return request("/analyze", {
    method: "POST",
    token,
    data,
  });
}

export function fetchHistory(token) {
  return request("/history", {
    token,
  });
}
