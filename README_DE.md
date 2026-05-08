# Maintainerr-to-Plex Sync 🚀

[🇩🇪 Deutsch](README_DE.md) | [🇬🇧 English](README.md)

[![Docker Build](https://github.com/00Scooby/maintainerr-plex-sync/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/00Scooby/maintainerr-plex-sync/actions/workflows/docker-publish.yml)
[![Docker Package](https://img.shields.io/badge/docker-ghcr.io-blue.svg)](https://github.com/00Scooby/maintainerr-plex-sync/pkgs/container/maintainerr-plex-sync)
[![Version](https://img.shields.io/badge/version-2.0.4-brightgreen.svg)](https://github.com/00Scooby/maintainerr-plex-sync/releases/latest)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🎉 **GENIALE NEWS:** Die grundlegende Plex-Kollektions-Sortierung aus diesem Projekt wurde offiziell **nativ in Maintainerr integriert**! Ab Maintainerr v3.11.0+ kannst du deine Kollektionen direkt in der Maintainerr-Weboberfläche sortieren, ohne ein externes Skript laufen zu lassen.

**Maintainerr-to-Plex Sync** ist ein vollautomatisierter Python-Microservice, der die Lücke zwischen den Löschplänen von [Maintainerr](https://github.com/jorenn92/Maintainerr), deiner Plex-Oberfläche und deinen Kometa-Overlays schliesst.

Wenn du nur die automatische Kollektionssortierung benötigst, empfehlen wir dir wärmstens, die neue **native Sortierfunktion** direkt in Maintainerr zu nutzen. Wenn du jedoch weiterhin **schicke, dynamische Kometa-Overlays** mit den verbleibenden Tagen auf deinen Postern haben möchtest, bleibt dieses Tool dein perfekter Begleiter!

## ✨ Features

- **Interaktives Dashboard:** Verwalte alle Einstellungen, gestalte deine Overlays und überwache Logs über eine moderne Web-Oberfläche (Port 8501).
- **Live WYSIWYG Vorschau:** Echtzeit-Simulation deiner Kometa-Banner. Lade eigene Poster hoch, um das Design vorab zu prüfen.
- **Sicheres Sortieren:** Nutzt die benutzerdefinierte Kollektionssortierung von Plex. Deine globalen Mediathek-Metadaten bleiben unangetastet (jetzt auch nativ direkt in Maintainerr verfügbar!).
- **Smarte Kometa-Overlays:** Generiert dynamisch Dateien für [Kometa](https://kometa.wiki/) mit anpassbaren Farben, Offsets und Radien.
- **Integrierter Scheduler:** Richte mehrere tägliche Zeitpläne direkt in der UI ein. Der Hintergrund-Thread hält alles synchron.
- **Leichtgewicht:** Basiert auf `python:3.9-slim` mit minimalem Ressourcenverbrauch.

## 🚀 Installation (Docker Compose)

```yaml
version: "3.8"

services:
  maintainerr-plex-sync:
    image: ghcr.io/00scooby/maintainerr-plex-sync:latest
    container_name: maintainerr_sync
    restart: unless-stopped
    ports:
      - "8501:8501" # Dashboard-Zugriff
    environment:
      - TZ=Europe/Zurich
      - PLEX_URL=http://[DEINE-IP]:32400
      - PLEX_TOKEN=dein_plex_token_hier
      - MAINTAINERR_URL=http://[DEINE-IP]:6246
    volumes:
      - ./config.yml:/app/config.yml
      - ./logs:/logs
      - ./kometa/config:/app/kometa_export
```

## 🛠️ Funktionsweise

1. **Dashboard:** Öffne `http://[DEINE-IP]:8501`.
2. **Konfiguration:** Wähle Mediatheken und Kollektionen bequem über Dropdowns aus.
3. **Design:** Nutze die Schieberegler für das Banner-Design und kontrolliere das Ergebnis in der Live-Vorschau.
4. **Automatisierung:** Speichere deine Sync-Uhrzeiten und lass den Hintergrund-Ninja die Arbeit erledigen.

## 🚑 Troubleshooting

Nutze den Bereich **Live-Logs** am Ende des Dashboards für Echtzeit-Feedback zu API-Verbindungen und dem Synchronisationsstatus.

## 🤖 AI Disclaimer

Dieses Projekt wurde mit der tatkräftigen Unterstützung von **Google Gemini** entwickelt. Es ist ein grossartiges Beispiel dafür, wie menschliche Ideen und Künstliche Intelligenz zusammenarbeiten können, um coole und nützliche Tools für die Home-Server-Community zu erschaffen.
