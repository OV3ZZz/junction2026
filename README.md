# Junction 2026 — Personal Task Agent (Exa-powered)

This repository is initialized for a Junction 2026 hackathon project focused on building a **personal agent** that takes tedious real-life tasks off users’ hands.

## Challenge focus

Build an agent that can:
- Find relevant, current information across the web using **Exa**
- Compare options and reason about next steps
- Bring a task as close to done as possible, leaving final approval to the user when needed
- Show clear sources for every important claim

## Real-user task areas

Example domains for the demo:
- Daily living and errands
- Benefits eligibility and paperwork research
- Housing/rent checks
- Special occasion planning (e.g., vegan anniversary dinner ideas)
- Business info and travel disruption handling

## Judging alignment

This project should demonstrate:
1. Strong use of Exa for information that is not just model pretraining knowledge
2. Practical usefulness for a clearly defined user group
3. Transparent source attribution
4. Originality
5. A working live demo, including judge-provided queries

## Starter plan for this repo

- Define the target user segment and 2–3 high-value workflows
- Implement Exa-backed search/retrieval and normalized source handling
- Add task orchestration logic (plan -> gather -> compare -> suggest action)
- Build a demo flow that supports live prompts and auditable answers

## Next steps for contributors

1. Choose the first concrete workflow (e.g., rent increase legality check)
2. Add project code scaffold (API/app) in a follow-up PR
3. Integrate Exa API calls and source rendering early
4. Add scenario-based tests once runtime code is introduced

## Setup and run

Requirements: Python 3.11–3.13, Node.js/npm, and `uv` (recommended). Copy `.env.example` to `.env` and add `GEMINI_API_KEY` and `EXA_API_KEY` to enable the live agent; without them the claim endpoint returns stub data so the app still runs end to end. Never commit real keys.

Backend:

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Run backend tests with `cd backend; uv run pytest`. If `uv` is unavailable, create a local virtual environment and install with `pip install -e ".[dev]"`.

Frontend (in a second terminal):

```powershell
cd frontend
npm install
npm run dev
```

In development the frontend calls `http://localhost:8000`; a production build calls the same origin that served it. Set `VITE_API_URL` to override either. Build with `cd frontend; npm run build`.

## Deployment

The root `Dockerfile` builds the frontend and runs the FastAPI backend in one container, which serves the API and the frontend from the same URL (no CORS setup needed). API keys are set as environment variables on the hosting platform and never stored in the repository.

Render (uses `render.yaml`):

1. In Render, choose **New → Blueprint** and connect this GitHub repository.
2. Enter `GEMINI_API_KEY` and `EXA_API_KEY` when asked.
3. Deploy, then open the service URL. `/health` should return `{"status":"ok"}`.

Any Docker host works the same way: build the root `Dockerfile` and set the environment variables below.

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY`, `EXA_API_KEY` | Enable the live agent |
| `GEMINI_MODEL` | Gemini model name (default `gemini-3.8-flash`) |
| `MAX_CLAIMS_PER_HOUR` | Global hourly `/claim` limit that protects API credits (default 60, `0` disables) |
| `ALLOWED_ORIGINS` | Comma-separated origins, only needed if the frontend is hosted on a different domain |
| `PORT` | Set by the platform; defaults to 8000 |
