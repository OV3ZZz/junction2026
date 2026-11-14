# Junction 2026 — Exa-powered job search

Describe in your own words what you are good at and what kind of work you want. The app finds job ads that are open right now, across job boards and employers' own careers pages, three at a time. Reject a batch (and optionally say why), and save interesting ads to a sidebar.

Built for the Exa challenge ("The Internet Butler"). The search runs on Exa deep search with a structured output schema; see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the flow and the benchmark behind that choice.

## Setup and run locally

Requirements: Python 3.11–3.13, Node.js/npm, and `uv`. Copy `.env.example` to `.env` and set `EXA_API_KEY`. Without it the backend returns a stub ad so the app still runs end to end. Never commit real keys.

Backend:

```powershell
cd backend
uv sync --extra dev
uv run uvicorn app.main:app --reload
```

If your default Python is newer than 3.13, use `uv sync --extra dev --python 3.12`. Run tests with `cd backend; uv run pytest`.

Frontend (in a second terminal):

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. In development the frontend calls `http://localhost:8000`; a production build calls the same origin that served it. Set `VITE_API_URL` to override either. Build with `cd frontend; npm run build`.

## Deployment (Render)

The root `Dockerfile` builds the frontend and runs the FastAPI backend in one container, which serves the API and the frontend from the same URL. The Exa key is set on the host as an environment variable and never stored in the repository.

1. Push the branch to GitHub.
2. In Render, choose **New → Blueprint** and connect this repository (Render reads `render.yaml`).
3. Enter `EXA_API_KEY` when asked, then deploy.
4. Open the service URL; `/health` should return `{"status":"ok"}`.

The free plan sleeps after about 15 minutes without traffic and takes about a minute to wake up. For judging, switch the service to the Starter plan or ping `/health` every 10 minutes. Repeated identical searches are cached in memory for an hour, so example searches answer instantly.

## Configuration

| Variable | Purpose |
|---|---|
| `EXA_API_KEY` | Enables live search |
| `MAX_SEARCHES_PER_HOUR` | Global hourly search limit that protects API credits (default 120, `0` disables) |
| `ALLOWED_ORIGINS` | Comma-separated browser origins allowed to call the API; only needed when the frontend runs on another origin (default: the Vite dev server) |
| `PORT` | Set by the host; defaults to 8000 |
