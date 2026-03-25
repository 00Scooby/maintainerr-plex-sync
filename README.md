# Maintainerr-to-Plex Sync 🚀
[🇩🇪 Deutsch](README_DE.md) | [🇬🇧 English](README.md)

[![Docker Build](https://github.com/00Scooby/maintainerr-plex-sync/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/00Scooby/maintainerr-plex-sync/actions/workflows/docker-publish.yml)
[![Docker Package](https://img.shields.io/badge/docker-ghcr.io-blue.svg)](https://github.com/00Scooby/maintainerr-plex-sync/pkgs/container/maintainerr-plex-sync)
[![Version](https://img.shields.io/badge/version-1.1.17-brightgreen.svg)](https://github.com/00Scooby/maintainerr-plex-sync/releases/latest)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Maintainerr-to-Plex Sync** is a fully automated Python microservice designed to bridge the gap between [Maintainerr](https://github.com/jorenn92/Maintainerr)'s deletion schedules and your Plex UI.

Instead of altering global metadata or manually checking when media expires, this script calculates the exact days remaining for each item in your Maintainerr collections. It then connects to your Plex server and seamlessly updates the collection's **custom sort order**. Items closest to their deletion date automatically rise to the top!

## ✨ Features
* **Safe Sorting:** Uses Plex's custom collection sorting. Your global library `titleSort` metadata remains completely untouched.
* **Multi-Collection Support:** Sync as many Maintainerr collections as you want simultaneously.
* **Smart Kometa Overlays:** Dynamically generates library-specific YAML files for [Kometa](https://kometa.wiki/). Includes native support for season-level overlays and smart grammar logic (e.g., "1 Tag" vs "2 Tage").
* **Built-in Scheduler:** Run it instantly (`NOW`) or set up multiple daily schedules (e.g., `04:30`, `12:00`). The container stays alive and waits for its cue.
* **Safety First:** Includes a `dry_run` mode to test your config, and an `undo` mode to revert a collection back to its default Plex sorting.
* **Lightweight:** Built on `python:3.9-slim` with minimal dependencies.

## 🚀 Installation (Docker Compose)

The easiest way to run this tool is via Docker. 

1. Create a directory for the project and navigate into it.
2. Create a `docker-compose.yml` file:

```yaml
version: "3.8"

services:
  maintainerr-plex-sync:
  # You can use :latest for automatic updates, or pin a specific version like :1.1.8
    image: ghcr.io/00scooby/maintainerr-plex-sync:latest
    container_name: maintainerr_sync
    restart: unless-stopped
    environment:
      - TZ=Europe/Zurich # Change to your timezone
      - PLEX_URL=[http://192.168.1.100:32400](http://192.168.1.100:32400)
      - PLEX_TOKEN=your_plex_token_here
      - MAINTAINERR_URL=[http://192.168.1.100:6246](http://192.168.1.100:6246)
    volumes:
      - ./config.yml:/app/config.yml:ro
      # OPTIONAL: Map this to access the exported YAML files during a 'dry_run'
      - ./:/dry_run/
      - ./logs:/logs
      # OPTIONAL: Map this if you want to use the Kometa Overlay feature
      - ./kometa/config:/app/kometa_export
```
3. Create your `config.yml` in the same directory (see Configuration below).

4. Run `docker compose up -d`.

## ⚙️ Configuration (`config.yml`)
Map this file into your container at `/app/config.yml`.

```YAML
# ==========================================
# Maintainerr-to-Plex Sync Configuration
# ==========================================

settings:
  # Modes: "run" (active), "dry_run" (testing), "undo" (revert Plex sorting)
  run_mode: "run"
  
  # Log levels: DEBUG, INFO, WARNING, ERROR
  log_level: "INFO"
  
  # "NOW" for a single immediate run (container exits afterwards)
  # OR a list of times for standby mode
  run_schedules:
    - "04:30"
    
  # Exact names of the collections in Maintainerr to sync
  collection_names:
    - "Series unseen for 360 days"
    - "Movies unseen for 1 year"

  # ==========================================
  # Kometa Overlay Integration (Optional)
  # ==========================================
  enable_kometa_overlays: false
  
  # Only generate overlays for these Plex libraries
  kometa_allowed_libraries:
    - "Filme"
    - "Serien"
    
  # Dynamic Color Thresholds
  kometa_threshold_days: 10
  kometa_color_urgent: "#E31E24"         # Background color for <= threshold (e.g., Red)
  kometa_text_color_urgent: "#FFFFFF"    # Text color for <= threshold (e.g., White)
  kometa_color_warning: "#F1C40F"        # Background color for > threshold (e.g., Yellow)
  kometa_text_color_warning: "#141414"   # Text color for > threshold (e.g., Dark Grey/Black for contrast)
```

## 🛠️ How it works
1. The script fetches the specified collections from your Maintainerr API.
2. It calculates the days left before deletion for each item based on `addDate` and `deleteAfterDays`.
3. It connects to Plex via the `plexapi` wrapper and updates the collection sorting.
4. If enabled, it automatically generates library-specific YAML files (e.g., `maintainerr_Filme.yml`, `maintainerr_Serien.yml`) that Kometa can read to add visual expiration banners to your media.

## 🎨 Kometa Setup
To utilize the generated overlay files, simply include them in your Kometa configuration under the respective libraries. Since the script splits the exports by library name, you avoid soft fails in your Kometa logs!

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
**Cause:** The script found the collection in Maintainerr, but it doesn't exist in Plex under that exact name.
**Solution:** Check the exact spelling in both Plex and Maintainerr. It must be a 100% match (including spaces and case sensitivity).

### ⚠️ Log: "DRY RUN MODUS AKTIV: Plex wird nicht verändert."
**Cause:** The script is only reading data. It won't reorder anything in Plex and saves the generated Kometa files to a test folder.
**Solution:** Change `run_mode: "dry_run"` to `run_mode: "run"` in your `config.yml` and restart the container to apply changes to Plex.

### ⚠️ No Kometa YAML files are being exported
**Cause 1:** The Kometa feature is disabled in your configuration.
**Solution 1:** Ensure `enable_kometa_overlays: true` is set in your `config.yml`.
**Cause 2:** The library names don't match.
**Solution 2:** Check the `kometa_allowed_libraries` block. The names (e.g., "Movies", "TV Shows") must exactly match the library names on your Plex server.

### ⚠️ Log: "Fehler bei der Verbindung zu Plex / Maintainerr"
**Cause:** The script cannot reach the respective APIs, or authentication failed.
**Solution:** Double-check your `docker-compose.yml` (or `.env` file) to ensure the `PLEX_URL`, `PLEX_TOKEN`, and `MAINTAINERR_URL` are correct and accessible from within the Docker container.