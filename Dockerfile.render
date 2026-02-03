FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY backend/app/ /app/
COPY frontend/ /app/frontend/

# Porta
EXPOSE 10000

# Comando
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
