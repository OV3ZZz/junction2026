# One container serves both the API and the built frontend from the same origin.

# 1) Build the React frontend.
FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# 2) Run the FastAPI backend and serve the built frontend from /app/static.
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY backend/pyproject.toml ./
COPY backend/app ./app
RUN pip install .
COPY --from=frontend /frontend/dist ./static
EXPOSE 8000
# Hosting platforms pass the port in $PORT; API keys come from the platform's env settings.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
