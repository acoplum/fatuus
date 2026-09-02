FROM node:20-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY --from=frontend-build /frontend/dist ./frontend/dist

RUN pip install --no-cache-dir ".[serve]"

RUN useradd --create-home fatuus
USER fatuus

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn fatuus.api:app --host 0.0.0.0 --port ${PORT}"]
