# Reklama project guide

## Project summary
Reklama helps consumers research potential compensation for delayed flights, defective products, and incorrect invoices. The user describes a problem; the agent researches it and prepares a complaint letter for the user to review. The app never sends a letter.

## Architecture
Frontend (Vite, React, TypeScript) -> FastAPI backend -> agent loop <-> Gemini (via its OpenAI-compatible endpoint) and Exa -> draft builder -> frontend approval. The agent may call `search_web` backed by Exa, read results, and repeat for up to `MAX_ROUNDS = 5`. All source URLs must come from Exa results; the model must not invent links. The initial scaffold uses deterministic stub data so the full API contract works without credentials.

## Commands
- Backend install: `cd backend; uv sync` (or create `.venv` and use `pip install -e ".[dev]"` if uv is unavailable)
- Backend run: `cd backend; uv run uvicorn app.main:app --reload`
- Frontend install: `cd frontend; npm install`
- Frontend run: `cd frontend; npm run dev`
- Backend tests: `cd backend; uv run pytest`
- Lint: `cd backend; uv run ruff check .` and `cd frontend; npm run lint`
- Frontend production build: `cd frontend; npm run build`

## Conventions
- Add type hints to Python code and keep functions small.
- Keep business logic out of `app/main.py`.
- Define API request and response shapes only in `app/schemas.py`.
- Keep the frontend aligned with the schema response shape.

## Hard rules
- Never commit secrets or `.env`; never hardcode API keys.
- Sources and source URLs must come only from Exa results.
- The app must never send complaint letters itself; the user approves and sends them.
- The UI must always show a “not legal advice” notice.
- No auth, database, or extra frameworks without a project decision.

## Git workflow
- Use feature branches and small, clear commits.
- Never push to `main` and never force-push.
- Do not commit until requested.

## Done means
- Backend tests pass and the app starts.
- Frontend production build succeeds.
- Update docs whenever commands change.
