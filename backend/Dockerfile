# ============================================
# SERMUL Backend - FastAPI + Uvicorn
# Base: Python 3.11 (requisito techs_v3.md)
# ============================================

FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Directorio de trabajo (docker-compose monta ./backend aquí)
WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2-binary
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python primero (cache de capas Docker)
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-dev.txt

# Copiar código fuente
COPY . .

# Puerto expuesto (coincide con docker-compose.yml: "8000:8000")
EXPOSE 8000

# Uvicorn con --reload para hot-reload en desarrollo
# En producción se puede overridear con: --workers 4 --no-access-log
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
