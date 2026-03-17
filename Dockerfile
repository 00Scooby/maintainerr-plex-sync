# Wir nutzen ein extrem schlankes Python-Image
FROM python:3.9-slim

# Arbeitsverzeichnis im Container festlegen
WORKDIR /app

# Das geniale requests-Modul installieren
RUN pip install --no-cache-dir requests python-dotenv pyyaml plexapi schedule

# Unser Skript in den Container kopieren
COPY main.py .

# Befehl, der beim Starten ausgeführt wird
CMD ["python", "main.py"]