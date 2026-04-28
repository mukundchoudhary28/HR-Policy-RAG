FROM python:3.12-slim

WORKDIR /app

RUN apt-get update --fix-missing && apt-get install -y \
    gcc \
    libxml2 \
    libxslt1.1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY uv.lock ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

COPY src/ ./src/

RUN adduser --disabled-password --gecos "" appuser

RUN mkdir -p /app/data /app/chroma_db \
    && chown -R appuser:appuser /app/data /app/chroma_db

USER appuser

EXPOSE 8000 8501