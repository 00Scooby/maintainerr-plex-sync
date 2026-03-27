# Wir nutzen ein extrem schlankes Python-Image
FROM python:3.9-slim

# Arbeitsverzeichnis im Container festlegen
WORKDIR /app

# UTF-8 Encoding für saubere Logs und Emojis erzwingen
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

# Pakete installieren (Streamlit ist neu dabei!)
RUN pip install --no-cache-dir requests python-dotenv pyyaml plexapi schedule streamlit

# Unseren kompletten Code in den Container kopieren
COPY . /app/

# Port für das Streamlit Web-Dashboard freigeben
EXPOSE 8501

# Befehl, der beim Starten ausgeführt wird (Startet die UI)
CMD ["streamlit", "run", "ui.py", "--server.port=8501", "--server.address=0.0.0.0"]