FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências do sistema necessárias para psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Usuário não-root para execução
RUN adduser --disabled-password --gecos "" appuser
RUN mkdir -p /app/staticfiles && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
