# Maintainerr-to-Plex Sync 🚀

**Maintainerr-to-Plex Sync** is a fully automated Python microservice designed to bridge the gap between [Maintainerr](https://github.com/jorenn92/Maintainerr)'s deletion schedules and your Plex UI.

Instead of altering global metadata or manually checking when media expires, this script calculates the exact days remaining for each item in your Maintainerr collections. It then connects to your Plex server and seamlessly updates the collection's **custom sort order**. Items closest to their deletion date automatically rise to the top!

## ✨ Features
* **Safe Sorting:** Uses Plex's custom collection sorting. Your global library `titleSort` metadata remains completely untouched.
* **Multi-Collection Support:** Sync as many Maintainerr collections as you want simultaneously.
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