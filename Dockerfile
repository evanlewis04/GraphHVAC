FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/
COPY web/ ./web/
COPY data/ ./data/

RUN pip install --no-cache-dir -e ".[voyage]"

ENV GRAPH_API_HOST=0.0.0.0

EXPOSE 8000

CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${GRAPH_API_PORT:-8000}"]
