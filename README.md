# MediaVerify

MediaVerify is a full-stack web application for evaluating the credibility of news content. It accepts either pasted text or a public article URL, extracts and normalizes the content, applies an explainable credibility scoring pipeline, and stores the result for later review.

The project was built to explore practical credibility analysis with an emphasis on transparency. Instead of relying on sentiment alone, MediaVerify uses source-aware and language-aware verification signals so that each result can be explained in a way that is meaningful to a user.

## Highlights

- Analyze either raw article text or a live article URL.
- Extract likely article-body content instead of scoring an entire webpage.
- Score credibility using explainable verification signals rather than pure sentiment.
- Return confidence and human-readable explanation signals with every result.
- Store previous analyses in SQLite and surface them in the frontend dashboard.
- Provide a clean React interface backed by a FastAPI API.

## What This Project Demonstrates

- End-to-end full-stack development with React, FastAPI, and SQLite.
- Practical backend service design with preprocessing, scoring, persistence, and API response modeling.
- Explainable scoring logic for a non-trivial problem domain.
- Real-world handling of article scraping, content normalization, and frontend-to-backend integration.
- Product-oriented UI work focused on usability, clarity, and workflow.

## How It Works

1. A user submits either article text or a public URL from the frontend.
2. The backend normalizes the input and extracts article-body text when a URL is provided.
3. The credibility engine evaluates the content using source trust, attribution cues, evidence signals, dates, quotes, and suspicious phrasing.
4. The backend returns a credibility score, label, confidence estimate, and explanation signals.
5. The result is stored in the history database and shown in the dashboard.

## Tech Stack

- Frontend: React, Vite
- Backend: FastAPI, Python
- Scraping and parsing: Requests, BeautifulSoup
- Storage: SQLite
- Local container setup: Docker, Docker Compose

## Credibility Engine

The current scoring pipeline is rule-based and feature-driven. It is designed to be interpretable and to behave more realistically than a sentiment classifier used as a credibility proxy.

Signals currently considered include:

- known or low-trust source domains
- attribution language such as "according to", "reported", or "confirmed"
- evidence-style wording such as "study", "data", or "statement"
- traceability cues such as dates and direct quotes
- sensational, conspiratorial, or absolutist phrasing

This makes the output easier to explain, inspect, and improve over time. It also creates a strong baseline for future work involving trained misinformation or claim-verification models.

## Project Structure

```text
mediaverify/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── db/
│   │   ├── models/
│   │   └── services/
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   └── services/
│   └── package.json
├── docker-compose.yml
├── IMPLEMENTATION_LOG.md
└── README.md
```

## Run Locally

Backend:

```bash
cd backend
../.venv/bin/uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm run dev
```

Docker Compose:

```bash
docker compose up --build
```

Default URLs:

- Frontend: `http://localhost:5173`
- Backend API: `http://127.0.0.1:8000`
- API documentation: `http://127.0.0.1:8000/docs`

## API Overview

- `GET /`
  Returns a basic backend status message.

- `GET /health`
  Returns a health-check response.

- `POST /analyze`
  Accepts text or a URL and returns a credibility score, label, confidence value, and explanation signals.

- `GET /history`
  Returns previously stored analysis results.

## Limitations

- Article extraction quality depends on the publisher layout and how cleanly the page structure can be parsed.
- The current scoring engine is explainable and practical, but it is still heuristic and not a substitute for full fact-checking.
- Domain trust coverage is limited and can be expanded for broader source handling.

## Future Improvements

- Add automated backend tests for scoring, preprocessing, and history endpoints.
- Add frontend tests for loading, error, and result states.
- Expand publisher-specific scraping rules for more reliable article extraction.
- Improve domain reputation coverage and explanation quality for borderline cases.
- Add a trained misinformation or claim-verification model on top of the current baseline.
