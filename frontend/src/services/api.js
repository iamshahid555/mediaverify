const BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export async function analyzeContent(data) {
  const response = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail ?? "Unable to analyze content");
  }

  return response.json();
}

export async function fetchHistory() {
  const response = await fetch(`${BASE_URL}/history`);

  if (!response.ok) {
    throw new Error("Unable to load analysis history");
  }

  return response.json();
}
