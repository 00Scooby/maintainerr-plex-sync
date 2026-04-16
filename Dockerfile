# Wir nutzen ein extrem schlankes Python-Image
FROM python:3.9-slim

# Arbeitsverzeichnis im Container festlegen
WORKDIR /app

# UTF-8 Encoding für saubere Logs und Emojis erzwingen
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

# NEU: Fix für den PermissionError und Streamlit-Telemetry
ENV HOME=/tmp
ENV STREAMLIT_GATHER_USAGE_STATS=false

# Pakete installieren (Streamlit & Pillow sind dabei)
RUN pip install --no-cache-dir requests python-dotenv pyyaml plexapi schedule streamlit pillow

# Unseren kompletten Code in den Container kopieren
COPY . /app/

# Port für das Streamlit Web-Dashboard freigeben
EXPOSE 8501

# Befehl, der beim Starten ausgeführt wird
CMD ["python", "main.py"]