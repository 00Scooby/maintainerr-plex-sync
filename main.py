import os
import sys
import time
import requests
import yaml
import logging
from logging.handlers import RotatingFileHandler # <-- Diese Zeile ist neu
import schedule
from datetime import datetime, timezone
from dotenv import load_dotenv
from plexapi.server import PlexServer
from plexapi.exceptions import NotFound

load_dotenv()

PLEX_URL = os.environ.get("PLEX_URL")
PLEX_TOKEN = os.environ.get("PLEX_TOKEN")
MAINTAINERR_URL = os.environ.get("MAINTAINERR_URL")

def load_config():
    try:
        with open("config.yml", "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.error("❌ Fataler Fehler: config.yml nicht gefunden!")
        return None

def setup_logger(level_str, rotate=False):
    levels = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR}
    
    log_dir = "/logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "maintainerr_sync.log")
    
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    
    # NEU: RotatingFileHandler statt normalem FileHandler (behält maximal 10 Dateien)
    file_handler = RotatingFileHandler(log_file, backupCount=10, encoding="utf-8")
    
    # Rotiert die Datei (verschiebt .1 zu .2 etc.), wenn ein neuer Durchlauf startet
    if rotate and os.path.isfile(log_file) and os.path.getsize(log_file) > 0:
        file_handler.doRollover()
        
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(levels.get(level_str.upper(), logging.INFO))
    root_logger.handlers = []
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

def calculate_days_left(add_date_str, delete_after_days):
    add_date = datetime.strptime(add_date_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    days_in_list = (now - add_date).days
    return max(0, delete_after_days - days_in_list)

def sync_collections():
    """Das ist unsere eigentliche Arbeitsmaschine."""
    config = load_config()
    if not config: return
        
    settings = config.get("settings", {})
    is_dry_run = settings.get("run_mode", "dry_run") == "dry_run"
    target_collections = settings.get("collection_names", [])
    
    # Kometa Setup & Variablen laden
    enable_kometa = settings.get("enable_kometa_overlays", False)
    kometa_allowed_libs = settings.get("kometa_allowed_libraries", [])
    threshold_days = settings.get("kometa_threshold_days", 10)
    
    color_urgent = settings.get("kometa_color_urgent", "#E31E24")
    color_warning = settings.get("kometa_color_warning", "#F1C40F")
    text_color_urgent = settings.get("kometa_text_color_urgent", "#FFFFFF")
    text_color_warning = settings.get("kometa_text_color_warning", "#FFFFFF")

    if isinstance(target_collections, str):
        target_collections = [target_collections]
        
    # NEU: Wir befehlen ihm, für diesen Sync eine neue Datei zu beginnen
    setup_logger(settings.get("log_level", "INFO"), rotate=True)
    logging.info("🚀 Starte Maintainerr-to-Plex Sync (Custom Sort Edition)...")
        
    if is_dry_run: logging.info("🛑 DRY RUN MODUS AKTIV: Plex wird nicht verändert.")

    if not all([PLEX_URL, PLEX_TOKEN, MAINTAINERR_URL]):
        logging.error("❌ Umgebungsvariablen fehlen.")
        return

    kometa_overlays = None

    try:
        logging.info("🔌 Verbinde mit Plex Server...")
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    except Exception as e:
        logging.error(f"❌ Fehler bei der Verbindung zu Plex: {e}")
        return

    maintainerr_api = f"{MAINTAINERR_URL}/api/collections"
    logging.info(f"📡 Verbinde mit Maintainerr: {maintainerr_api}")
    
    try:
        m_response = requests.get(maintainerr_api, headers={"Accept": "application/json"})
        m_response.raise_for_status()
        collections_data = m_response.json()
        
        found_any = False
        
        # Dictionary mit eingebautem Kometa-Template anlegen
        if enable_kometa:
            kometa_overlays = {
                "templates": {
                    "days_left_banner": {
                        "plex_search": {
                            "title": "<<item_title>>"
                        },
                        "overlay": {
                            # NEU: Variable umbenannt für bessere Kometa-Kompatibilität
                            "name": "text(<<banner_text>>)", 
                            "horizontal_align": "left",
                            "vertical_align": "top",
                            "horizontal_offset": 20, # Etwas mehr Abstand zum Rand
                            "vertical_offset": 20,   # Etwas mehr Abstand zum Rand
                            "back_color": "<<color>>",
                            "font_color": "<<font_color>>",
                            "back_radius": 20,       # Etwas runder
                            "font_size": 55,         # DEUTLICH größerer Text
                            "back_width": 380,       # Breiteres Banner für den großen Text
                            "back_height": 85        # Höheres Banner
                        }
                    }
                },
                "overlays": {}
            }
        else:
            kometa_overlays = None

        for coll in collections_data:
            coll_title = coll.get("title")
            
            if coll_title in target_collections:
                found_any = True
                delete_days = coll.get("deleteAfterDays", 30)
                media_list = coll.get("media", [])
                
                logging.info(f"✅ Kollektion '{coll_title}' in Maintainerr gefunden. Verarbeite {len(media_list)} Items...")
                
                sortable_items = []
                for item in media_list:
                    plex_id = item.get("mediaServerId")
                    add_date = item.get("addDate")
                    if not plex_id or not add_date: continue
                    
                    days_left = calculate_days_left(add_date, delete_days)
                    sortable_items.append({"plex_id": int(plex_id), "days_left": days_left})
                
                sortable_items.sort(key=lambda x: x["days_left"])

                try:
                    plex_colls = plex.library.search(title=coll_title, libtype="collection")
                    if not plex_colls:
                        logging.warning(f"⚠️ Kollektion '{coll_title}' in Plex nicht gefunden!")
                        continue
                    
                    plex_col = plex_colls[0]
                    
                    if not is_dry_run:
                        plex_col.sortUpdate(sort="custom")
                    
                    prev_item = None
                    position = 1
                    
                    for item_data in sortable_items:
                        p_id = item_data["plex_id"]
                        d_left = item_data["days_left"]
                        
                        try:
                            plex_item = plex.fetchItem(p_id)
                            
                            # 1. Plex-Item verschieben (oder simulieren)
                            if not is_dry_run:
                                plex_col.moveItem(plex_item, after=prev_item)
                                logging.info(f"✅ Platz {position:02d} | In {d_left} Tagen weg -> {plex_item.title}")
                            else:
                                logging.info(f"⏭️ DRY RUN: Würde '{plex_item.title}' auf Platz {position:02d} setzen (Noch {d_left} Tage).")
                                
                            # 2. Kometa-Daten dynamisch sammeln
                            if enable_kometa:
                                library_name = getattr(plex_item, "librarySectionTitle", "")
                                
                                if not kometa_allowed_libs or library_name in kometa_allowed_libs:
                                    # Farblogik anwenden
                                    current_color = color_urgent if d_left <= threshold_days else color_warning
                                    current_text_color = text_color_urgent if d_left <= threshold_days else text_color_warning
                                    
                                    kometa_overlays["overlays"][plex_item.title] = {
                                        "template": {
                                            "name": "days_left_banner",
                                            "item_title": plex_item.title,
                                            "banner_text": f"Noch {d_left} Tage", 
                                            "color": current_color,
                                            "font_color": current_text_color
                                        }
                                    }
                                else:
                                    logging.debug(f"Überspringe Kometa-Overlay für '{plex_item.title}' (Library '{library_name}' ist nicht freigegeben).")
                                    
                            prev_item = plex_item
                            position += 1
                            
                        except NotFound:
                            logging.warning(f"⚠️ Item mit ID {p_id} existiert in Plex nicht mehr. Übersprungen.")
                            
                except Exception as e:
                    logging.error(f"❌ Fehler bei der Plex-Verarbeitung für '{coll_title}': {e}", exc_info=True)
                        
        if not found_any:
            logging.warning("⚠️ Keine der angegebenen Kollektionen gefunden!")
            
    except Exception as e:
        logging.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}", exc_info=True)

    # === KOMETA EXPORT ===
    if enable_kometa and kometa_overlays and kometa_overlays.get("overlays"):
        try:
            if is_dry_run:
                # NEU: Speichert die Datei jetzt im gemappten /dry_run Ordner!
                export_path = "/dry_run/dry_run_overlays.yml"
                logging.info("🏜️ DRY RUN: Speichere Kometa-Datei lokal neben der config.yml...")
            else:
                export_path = "/app/kometa_export/maintainerr_overlays.yml"
                
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            with open(export_path, "w", encoding="utf-8") as f:
                yaml.dump(kometa_overlays, f, default_flow_style=False, allow_unicode=True)
            logging.info(f"📝 Kometa Overlay-Datei erfolgreich generiert: {export_path}")
        except Exception as e:
            logging.error(f"❌ Fehler beim Schreiben der Kometa-Datei: {e}")

    logging.info("🏁 Sync-Durchlauf beendet.")

def main():
    config = load_config()
    if not config:
        sys.exit(1)
        
    settings = config.get("settings", {})
    run_schedules = settings.get("run_schedules", ["NOW"])
    
    if isinstance(run_schedules, str):
        run_schedules = [run_schedules]
        
    # NEU: Beim Start des Skripts (ausserhalb des Syncs) noch nicht rotieren
    setup_logger(settings.get("log_level", "INFO"), rotate=False)
    
    if any(s.upper() == "NOW" for s in run_schedules):
        logging.info("⚡ Modus 'NOW' erkannt: Führe Sync sofort aus und beende danach.")
        sync_collections()
        logging.info("👋 Container/Skript wird beendet. Ciao!")
        sys.exit(0)
    else:
        logging.info(f"🕒 Standby-Modus aktiviert. Geplante Syncs täglich um: {', '.join(run_schedules)} Uhr.")
        
        for time_str in run_schedules:
            schedule.every().day.at(time_str).do(sync_collections)
            
        while True:
            schedule.run_pending()
            time.sleep(60) 

if __name__ == "__main__":
    main()