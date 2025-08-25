FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends  \
    curl  \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
