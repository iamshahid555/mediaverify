# MediaVerify

MediaVerify is a prototype for checking the credibility of news content. It accepts pasted text or an article URL, prepares the content, runs a credibility analysis, stores the result in SQLite, and displays the latest result plus analysis history in a React interface.

## Features Completed In Phase 2

- FastAPI backend with `/`, `/health`, `/analyze`, and `/history` endpoints.
- Text preprocessing for pasted content and URL-based article extraction.
- Cleaner article-body extraction that prefers real article paragraphs over page chrome.
- Feature-based credibility scoring using source/domain trust, attribution, dates, quotes, and suspicious-language signals.
- SQLite persistence for input type, credibility score, label, confidence, and timestamp.
- React/Vite frontend with input form, loading state, error state, score display, explanation indicators, and stored history.
- CORS configuration so the Vite frontend can call the backend locally.
- Docker and local development structure prepared for phase 3 deployment work.

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

## Phase 3 Starting Points

- Add a trained fake-news or claim-verification model on top of the current feature-based baseline.
- Add automated backend tests for `/analyze`, `/history`, preprocessing, and scraper failures.
- Add frontend component tests for loading, error, result, and history states.
- Store the original text preview or URL in history if required by the report.
- Add authentication only if the final assignment scope requires user-specific history.
- Expand domain-trust coverage and explainability for more nuanced source handling.
- Complete Docker Compose deployment and document production environment variables.
