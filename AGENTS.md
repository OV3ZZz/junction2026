# Project guide

## Project summary
A job search for the Junction 2026 Exa challenge. The user writes an area and a vague wish ("good with Excel and people, no sales"); the app finds job ads that are open right now, shows three at a time, lets the user reject them (optionally saying why), find similar ads, and save ads to a sidebar. The app never applies for jobs.

## Architecture
Frontend (Vite, React, TypeScript) -> FastAPI backend -> Exa deep search with an output schema. There is no LLM call of our own: Exa expands the raw wish itself. All job URLs must come from Exa results; anything else is dropped. Without `EXA_API_KEY` the backend returns stub data so the full API contract works. See `docs/ARCHITECTURE.md`.

## Commands
- Backend install: `cd backend; uv sync --extra dev` (use `--python 3.12` if the default Python is newer than 3.13)
- Backend run: `cd backend; uv run uvicorn app.main:app --reload`
- Frontend install: `cd frontend; npm install`
- Frontend run: `cd frontend; npm run dev`
- Backend tests: `cd backend; uv run pytest`
- Lint: `cd backend; uv run ruff check .` and `cd frontend; npm run lint`
- Frontend production build: `cd frontend; npm run build`

## Conventions
- Add type hints to Python code and keep functions small.
- Keep business logic out of `app/main.py` (it lives in `app/jobs.py`; Exa calls in `app/exa_client.py`).
- Define API request and response shapes only in `app/schemas.py`.
- Keep the frontend types aligned with the schema response shape.

## Hard rules
- Never commit secrets or `.env`; never hardcode API keys.
- Job ads and their URLs must come only from Exa results.
- The app never applies for jobs or contacts employers on the user's behalf.
- The UI must always tell the user to check details and deadlines from the original ad.
- No auth, database, or extra frameworks without a project decision. The app runs locally.

## Git workflow
- Use feature branches and small, clear commits.
- Never push to `main` and never force-push.
- Do not commit until requested.

## Done means
- Backend tests pass and the app starts.
- Frontend production build succeeds.
- Update docs whenever commands change.
