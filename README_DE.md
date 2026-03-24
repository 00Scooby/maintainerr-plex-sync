# Maintainerr-to-Plex Sync 🚀

[🇩🇪 Deutsch](README_DE.md) | [🇬🇧 English](README.md)

[![Docker Build](https://github.com/00Scooby/maintainerr-plex-sync/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/00Scooby/maintainerr-plex-sync/actions/workflows/docker-publish.yml)
[![Docker Package](https://img.shields.io/badge/docker-ghcr.io-blue.svg)](https://github.com/00Scooby/maintainerr-plex-sync/pkgs/container/maintainerr-plex-sync)
[![Version](https://img.shields.io/badge/version-1.1.14-brightgreen.svg)](https://github.com/00Scooby/maintainerr-plex-sync/releases/latest)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Maintainerr-to-Plex Sync** ist ein vollautomatisierter Python-Microservice, der die Lücke zwischen den Löschplänen von [Maintainerr](https://github.com/jorenn92/Maintainerr) und deiner Plex-Oberfläche schliesst.

Anstatt globale Metadaten zu ändern oder manuell zu prüfen, wann Medien ablaufen, berechnet dieses Skript die exakten verbleibenden Tage für jedes Item in deinen Maintainerr-Kollektionen. Anschliessend verbindet es sich mit deinem Plex-Server und aktualisiert nahtlos die **benutzerdefinierte Sortierung** der Kollektion. Items, die kurz vor der Löschung stehen, wandern automatisch nach oben!

## ✨ Features
* **Sicheres Sortieren:** Nutzt die benutzerdefinierte Kollektionssortierung von Plex. Deine globalen `titleSort`-Metadaten der Mediathek bleiben komplett unangetastet.
* **Multi-Collection Support:** Synchronisiere so viele Maintainerr-Kollektionen gleichzeitig, wie du möchtest.
* **Smarte Kometa-Overlays:** Generiert dynamisch bibliotheksspezifische YAML-Dateien für [Kometa](https://kometa.wiki/). Enthält native Unterstützung für Overlays auf Staffel-Ebene und eine intelligente Grammatik-Logik (z. B. "1 Tag" vs. "2 Tage").
* **Integrierter Scheduler:** Führe das Skript sofort aus (`NOW`) oder richte mehrere tägliche Zeitpläne ein (z. B. `04:30`, `12:00`). Der Container bleibt aktiv und wartet auf seinen Einsatz.
* **Safety First:** Beinhaltet einen `dry_run`-Modus, um deine Konfiguration zu testen, sowie einen `undo`-Modus, um eine Kollektion auf die Standard-Plex-Sortierung zurückzusetzen.
* **Leichtgewicht:** Basiert auf `python:3.9-slim` mit minimalen Abhängigkeiten.

## 🚀 Installation (Docker Compose)

Der einfachste Weg, dieses Tool auszuführen, ist über Docker. 

1. Erstelle ein Verzeichnis für das Projekt und wechsle dorthin.
2. Erstelle eine `docker-compose.yml`-Datei:

```yaml
version: "3.8"

services:
  maintainerr-plex-sync:
  # Du kannst :latest für automatische Updates nutzen oder eine Version pinnen, z.B. :1.1.10
    image: ghcr.io/00scooby/maintainerr-plex-sync:latest
    container_name: maintainerr_sync
    restart: unless-stopped
    environment:
      - TZ=Europe/Zurich # Zeitzone anpassen
      - PLEX_URL=[http://192.168.1.100:32400](http://192.168.1.100:32400)
      - PLEX_TOKEN=dein_plex_token_hier
      - MAINTAINERR_URL=[http://192.168.1.100:6246](http://192.168.1.100:6246)
    volumes:
      - ./config.yml:/app/config.yml:ro
      # OPTIONAL: Mappe dies, um während eines 'dry_run' auf die exportierten YAML-Dateien zuzugreifen
      - ./:/dry_run/
      - ./logs:/logs
      # OPTIONAL: Mappe dies, wenn du das Kometa-Overlay-Feature nutzen möchtest
      - ./kometa/config:/app/kometa_export
```
3. Erstelle deine `config.yml` im selben Verzeichnis (siehe Konfiguration unten).
4. Führe `docker compose up -d` aus.

## ⚙️ Konfiguration (`config.yml`)
Mappe diese Datei in deinen Container unter `/app/config.yml`.

```YAML
# ==========================================
# Maintainerr-to-Plex Sync Configuration
# ==========================================

settings:
  # Modi: "run" (aktiv), "dry_run" (testen), "undo" (Plex-Sortierung zurücksetzen)
  run_mode: "run"
  
  # Log-Level: DEBUG, INFO, WARNING, ERROR
  log_level: "INFO"
  
  # "NOW" für einen sofortigen, einmaligen Start (Container beendet sich danach)
  # ODER eine Liste von Uhrzeiten für den Standby-Modus
  run_schedules:
    - "04:30"
    
  # Exakte Namen der Maintainerr-Kollektionen, die synchronisiert werden sollen
  collection_names:
    - "Series unseen for 360 days"
    - "Movies unseen for 1 year"

  # ==========================================
  # Kometa Overlay Integration (Optional)
  # ==========================================
  enable_kometa_overlays: false
  
  # Generiere Overlays nur für diese Plex-Mediatheken
  kometa_allowed_libraries:
    - "Filme"
    - "Serien"
    
  # Dynamische Farb-Schwellenwerte
  kometa_threshold_days: 10
  kometa_color_urgent: "#E31E24"         # Hintergrundfarbe für <= Schwelle (z. B. Rot)
  kometa_text_color_urgent: "#FFFFFF"    # Textfarbe für <= Schwelle (z. B. Weiss)
  kometa_color_warning: "#F1C40F"        # Hintergrundfarbe für > Schwelle (z. B. Gelb)
  kometa_text_color_warning: "#141414"   # Textfarbe für > Schwelle (z. B. Dunkelgrau/Schwarz für Kontrast)
```

## 🛠️ Wie es funktioniert
1. Das Skript ruft die angegebenen Kollektionen über deine Maintainerr-API ab.
2. Es berechnet die verbleibenden Tage bis zur Löschung für jedes Item basierend auf `addDate` und `deleteAfterDays`.
3. Es verbindet sich via `plexapi`-Wrapper mit Plex und aktualisiert die benutzerdefinierte Sortierung der Kollektion.
4. Falls aktiviert, generiert es automatisch bibliotheksspezifische YAML-Dateien (z. B. `maintainerr_Filme.yml`, `maintainerr_Serien.yml`), die Kometa lesen kann, um visuelle Ablauf-Banner zu deinen Medien hinzuzufügen.

## 🎨 Kometa Setup
Um die generierten Overlay-Dateien zu nutzen, füge sie einfach unter den jeweiligen Mediatheken in deine Kometa-Konfiguration ein. Da das Skript die Exporte nach Mediatheken-Namen aufteilt, vermeidest du Soft Fails in deinen Kometa-Logs!

```YAML
libraries:
  Filme:
    overlay_path:
      - file: config/maintainerr_Filme.yml
  Serien:
    overlay_path:
      - file: config/maintainerr_Serien.yml
```

## 🚑 Troubleshooting

### ⚠️ Log: "Kollektion '[Name]' in Plex nicht gefunden!"
**Ursache:** Das Skript hat die Kollektion zwar in Maintainerr gefunden, aber in Plex existiert sie unter diesem exakten Namen nicht.
**Lösung:** Prüfe die genaue Schreibweise in Plex und Maintainerr. Sie muss zu 100 % identisch sein (inklusive Leerzeichen und Gross-/Kleinschreibung).

### ⚠️ Log: "DRY RUN MODUS AKTIV: Plex wird nicht verändert."
**Ursache:** Das Skript liest nur Daten. Es sortiert nichts in Plex um und schreibt die generierten Kometa-Dateien in einen Testordner.
**Lösung:** Ändere in deiner `config.yml` den Wert `run_mode: "dry_run"` zu `run_mode: "run"` und starte den Container neu, um die Änderungen auf Plex anzuwenden.

### ⚠️ Es werden keine Kometa YAML-Dateien exportiert
**Ursache 1:** Die Kometa-Funktion ist in deiner Konfiguration deaktiviert.
**Lösung 1:** Stelle sicher, dass `enable_kometa_overlays: true` in der `config.yml` gesetzt ist.
**Ursache 2:** Die Mediatheken-Namen stimmen nicht überein.
**Lösung 2:** Prüfe den Block `kometa_allowed_libraries`. Die Namen (z. B. "Filme", "Serien") müssen exakt so heissen wie die Mediatheken auf deinem Plex-Server.

### ⚠️ Log: "Fehler bei der Verbindung zu Plex / Maintainerr"
**Ursache:** Das Skript kann die jeweiligen APIs nicht erreichen oder die Authentifizierung schlägt fehl.
**Lösung:** Kontrolliere in deiner `docker-compose.yml` (oder `.env` Datei), ob die `PLEX_URL`, der `PLEX_TOKEN` und die `MAINTAINERR_URL` absolut korrekt und aus dem Docker-Container heraus erreichbar sind.