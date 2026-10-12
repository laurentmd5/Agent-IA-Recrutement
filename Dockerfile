# syntax=docker/dockerfile:1

# ==========================================
# Étape 1 : Builder (Installation des dépendances)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Installation des dépendances système nécessaires à la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Création de l'environnement virtuel pour isoler les dépendances
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copie du fichier de configuration des dépendances
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# Étape 2 : Runtime (Image finale allégée)
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Copie de l'environnement virtuel depuis le builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copie du code source de l'agent
COPY . .

# Définition des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Commande par défaut pour lancer l'agent FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
