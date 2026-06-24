FROM python:3.10-slim

# Instalar dependencias del sistema requeridas para algunas librerías
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Descargar el modelo de lenguaje de Spacy en español
RUN python -m spacy download es_core_news_sm

COPY . .

EXPOSE 3002

# Uvicorn arranca la aplicación (El puerto será controlado por docker-compose o por el CMD)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3002"]
