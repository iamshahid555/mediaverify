# MediaVerify

MediaVerify is a web application for evaluating the credibility of news content. Users can submit either raw text or a public article URL, and the system analyzes the content using source-aware verification signals such as domain trust, attribution, evidence-style wording, dates, quotes, and suspicious language patterns.

The project combines a FastAPI backend, a React/Vite frontend, and SQLite-based history storage to provide a complete end-to-end workflow for credibility analysis and review.

## Core Features

- Analyze either pasted article text or a live article URL.
- Extract cleaner article-body content from supported web pages.
- Score credibility using feature-based verification signals instead of simple sentiment.
- Return explanation signals alongside the credibility score.
- Store previous analyses in SQLite and display them in the frontend.
- Provide a dashboard-style interface for running and reviewing analyses.

## Application Flow

1. A user submits text or a URL from the frontend.
2. The backend normalizes the input and extracts article content when a URL is provided.
3. The credibility engine evaluates source trust, attribution, evidence cues, dates, quotes, and suspicious phrasing.
4. The backend returns a credibility score, label, confidence estimate, and explanation signals.
5. The result is stored in the history database and shown in the frontend.

## Tech Stack

- Frontend: React, Vite
- Backend: FastAPI, Python
- Parsing and scraping: Requests, BeautifulSoup
- Storage: SQLite
- Container setup: Docker, Docker Compose

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
- API docs: `http://127.0.0.1:8000/docs`

## API Endpoints

- `GET /`
  Basic backend status message.

- `GET /health`
  Health-check endpoint.

- `POST /analyze`
  Accepts either text or a URL and returns a credibility score, label, confidence, and explanation signals.

- `GET /history`
  Returns previously stored analysis results.

## Current Credibility Logic

The scoring engine uses a rule-based and feature-driven baseline designed to behave more realistically than sentiment-based classification. It currently considers:

- known or low-trust source domains
- attribution language such as "according to" or "reported"
- evidence-style wording such as "data", "study", or "confirmed"
- traceability cues such as dates and quotes
- sensational or conspiratorial phrasing
- absolutist wording and excessive emphasis

This makes the system better suited to credibility analysis than a standard positive/negative tone model, while still remaining explainable.

## Notes

- URL quality depends on how well article text can be extracted from a given publisher layout.
- The current scoring engine is a strong baseline, but it is still heuristic and not a substitute for full fact-checking.
- Some domains may need custom extraction rules or expanded trust coverage over time.

## Next Improvements

- expand publisher-specific scraping rules
- improve domain trust coverage
- add automated backend and frontend tests
- support richer explanation breakdowns in the UI
- optionally add a trained misinformation or claim-verification model on top of the current baseline
