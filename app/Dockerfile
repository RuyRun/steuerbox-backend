FROM python:3.12-slim

# verhindert .pyc Dateien
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
     libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libharfbuzz-subset0 \
    libffi-dev \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt


