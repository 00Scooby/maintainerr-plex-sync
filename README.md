# Maintainerr-to-Plex Sync 🚀

[🇩🇪 Deutsch](README_DE.md) | [🇬🇧 English](README.md)

[![Docker Build](https://github.com/00Scooby/maintainerr-plex-sync/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/00Scooby/maintainerr-plex-sync/actions/workflows/docker-publish.yml)
[![Docker Package](https://img.shields.io/badge/docker-ghcr.io-blue.svg)](https://github.com/00Scooby/maintainerr-plex-sync/pkgs/container/maintainerr-plex-sync)
[![Version](https://img.shields.io/badge/version-2.0.4-brightgreen.svg)](https://github.com/00Scooby/maintainerr-plex-sync/releases/latest)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🎉 **GREAT NEWS:** The core Plex collection sorting logic from this project has been officially **merged natively into Maintainerr**! Starting with Maintainerr v2.10.0+, you can sort your Plex collections directly from the Maintainerr Web UI without running an external script.

**Maintainerr-to-Plex Sync** is a fully automated Python microservice designed to bridge the gap between [Maintainerr](https://github.com/jorenn92/Maintainerr)'s deletion schedules, your Plex UI, and your Kometa overlays.

If you only need automatic collection sorting, we highly recommend using the new **native sorting feature** inside Maintainerr. However, if you want **beautiful, dynamic Kometa Overlays** showing the remaining days, this standalone microservice is still your ultimate companion!

## ✨ Features

- **Interactive Dashboard:** Manage all settings, design your overlays, and monitor logs via a modern web interface (Port 8501).
- **Live WYSIWYG Preview:** Real-time simulation of your Kometa banners. Upload your own posters to test the design before applying.
- **Safe Sorting:** Uses Plex's custom collection sorting. Your global library `titleSort` metadata remains completely untouched (now also available natively in Maintainerr!).
- **Smart Kometa Overlays:** Dynamically generates library-specific YAML files for [Kometa](https://kometa.wiki/). Includes native support for season-level overlays and customizable banner designs (Colors, Offsets, Radius).
- **Built-in Scheduler:** Set up multiple daily sync intervals directly in the UI. The background thread keeps everything in sync while you sleep.
- **Lightweight:** Built on `python:3.9-slim` with minimal dependencies.

## 🚀 Installation (Docker Compose)

The easiest way to run this tool is via Docker.

```yaml
version: "3.8"

services:
  maintainerr-plex-sync:
    image: ghcr.io/00scooby/maintainerr-plex-sync:latest
    container_name: maintainerr_sync
    restart: unless-stopped
    ports:
      - "8501:8501" # Access the Dashboard here
    environment:
      - TZ=Europe/Zurich
      - PLEX_URL=http://[YOUR-IP]:32400
      - PLEX_TOKEN=your_plex_token_here
      - MAINTAINERR_URL=http://[YOUR-IP]:6246
    volumes:
      - ./config.yml:/app/config.yml
      - ./logs:/logs
      - ./kometa/config:/app/kometa_export
```

## 🛠️ How it works

1. **Connect:** Access the Dashboard at `http://[YOUR-IP]:8501`.
2. **Configure:** Select your Plex libraries and Maintainerr collections via dynamic dropdowns.
3. **Design:** Use sliders to adjust your Kometa banners and check the live preview.
4. **Automate:** Set your sync times and let the background worker handle the rest.

## 🚑 Troubleshooting

Check the **Live Logs** section at the bottom of the Dashboard for real-time feedback on API connections and sync status.

## 🤖 AI Disclaimer

This project was developed with the active assistance of **Google Gemini**. It's a great example of how human creativity and Artificial Intelligence can team up to build cool and useful tools for the home server community.
