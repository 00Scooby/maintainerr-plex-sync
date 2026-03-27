import streamlit as st
import yaml
import os
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
from main import sync_collections, CURRENT_VERSION
import requests
from dotenv import load_dotenv
from plexapi.server import PlexServer
import threading
import time
import schedule

load_dotenv()

PLEX_URL = os.environ.get("PLEX_URL")
PLEX_TOKEN = os.environ.get("PLEX_TOKEN")
MAINTAINERR_URL = os.environ.get("MAINTAINERR_URL")

@st.cache_data(ttl=300)
def get_plex_libraries():
    if not PLEX_URL or not PLEX_TOKEN: return []
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        return [lib.title for lib in plex.library.sections()]
    except Exception:
        return []

@st.cache_data(ttl=300)
def get_maintainerr_collections():
    if not MAINTAINERR_URL: return []
    try:
        res = requests.get(f"{MAINTAINERR_URL}/api/collections", timeout=5, headers={"Accept": "application/json"})
        if res.status_code == 200:
            return [c.get("title") for c in res.json() if c.get("title")]
    except Exception:
        pass
    return []

# --- HINTERGRUND TIMER LOGIK ---

def run_timer():
    """Diese Funktion läuft in einem eigenen Thread und prüft den Zeitplan."""
    # Hier definieren wir den Zeitplan (z.B. täglich um 04:30 Uhr)
    # Später können wir das auch noch über die UI konfigurierbar machen!
    schedule.every().day.at("04:30").do(sync_collections)
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Alle 60 Sekunden prüfen

# Den Thread nur einmalig starten
if 'timer_started' not in st.session_state:
    threading.Thread(target=run_timer, daemon=True).start()
    st.session_state['timer_started'] = True

# NEU: Optimiertes Laden des Vorschaubildes (RGBA Konvertierung nur ein einziges Mal!)
@st.cache_resource
def load_base_poster_optimized():
    try:
        # Wir laden und konvertieren ONCE. Spart massive CPU-Zeit bei jedem Regler-Zucken!
        return Image.open("img/maintainerr_preview.png").convert("RGBA")
    except FileNotFoundError:
        return None

# Seiten-Konfiguration mit eigenem Logo-Favicon
st.set_page_config(
    page_title="MaintainerrSYNC - Dashboard",
    page_icon="img/msync_favicon.png", # <-- Pfad zu deinem Logo
    layout="wide"
)

# Funktion zum Laden der Config
def load_config():
    try:
        with open("config.yml", "r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        st.error("❌ config.yml nicht gefunden!")
        return {}

# Funktion zum Speichern der Config
def save_config(config_data):
    with open("config.yml", "w", encoding="utf-8") as file:
        yaml.dump(config_data, file, default_flow_style=False, allow_unicode=True)
    st.toast("✅ Konfiguration erfolgreich gespeichert!", icon="💾")

# Config in den Speicher laden
config = load_config()
settings = config.get("settings", {})

# === UI HEADER ===
header_col1, header_col2 = st.columns([1, 6])
with header_col1:
    # NEU: Wir laden dein neues Logo (als Platzhalter, du musst die Datei maintainerr_logo.png im Projektordner haben)
    try:
        logo_img = Image.open("img/maintainerr_logo.png")
        st.image(logo_img, width=150)
    except FileNotFoundError:
        st.warning("⚠️ Logo maintainerr_logo.png nicht gefunden!")

with header_col2:
    st.title("🎬 Maintainerr-to-Plex Sync")
    st.markdown(f"**Version:** `{CURRENT_VERSION}` | UI Powered by Streamlit")

st.divider()

# === UI LAYOUT (2 Spalten) ===
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("⚙️ Allgemeine Einstellungen")
    
    # Run Mode Dropdown
    run_modes = ["run", "dry_run", "undo"]
    current_mode = settings.get("run_mode", "dry_run")
    new_mode = st.selectbox("Ausführungsmodus", run_modes, index=run_modes.index(current_mode) if current_mode in run_modes else 1)
    
    # Log Level
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    current_log = settings.get("log_level", "INFO")
    new_log = st.selectbox("Log-Level", log_levels, index=log_levels.index(current_log) if current_log in log_levels else 1)

    st.subheader("🎨 Kometa Overlay Design")
    enable_kometa = st.toggle("Kometa Overlays generieren", value=settings.get("enable_kometa_overlays", True))

    # Plex Libraries live laden
    available_libs = get_plex_libraries()
    current_libs = settings.get("kometa_allowed_libraries", [])
    
    if available_libs:
        # Nur die markieren, die auch wirklich noch existieren
        valid_defaults = [l for l in current_libs if l in available_libs]
        new_allowed_libs = st.multiselect("Erlaubte Plex-Mediatheken (Leer = Alle)", available_libs, default=valid_defaults)
    else:
        # Fallback, falls Plex offline ist
        st.warning("Plex nicht erreichbar. Manuelle Eingabe nötig.")
        libs_text = st.text_input("Erlaubte Plex-Mediatheken (Komma-getrennt)", value=", ".join(current_libs))
        new_allowed_libs = [l.strip() for l in libs_text.split(",") if l.strip()]
    
    # Farben mit Color Picker
    c1, c2 = st.columns(2)
    with c1:
        color_urgent = st.color_picker("Hintergrundfarbe (Dringend / <= 10 Tage)", value=settings.get("kometa_color_urgent", "#E31E24"))
        text_urgent = st.color_picker("Schriftfarbe (Dringend)", value=settings.get("kometa_text_color_urgent", "#FFFFFF"))
    with c2:
        color_warning = st.color_picker("Hintergrundfarbe (Warnung / > 10 Tage)", value=settings.get("kometa_color_warning", "#F1C40F"))
        text_warning = st.color_picker("Schriftfarbe (Warnung)", value=settings.get("kometa_text_color_warning", "#141414"))

    # Aufbohren des Overlay-Designs (Alle Parameter!)
    st.subheader("📏 Position & Grösse (Alle Design-Parameter)")
    st.markdown("Alle Parameter des Kometa Overlay Design sind nun konfigurierbar.")
    
    # Ausrichtung (Alignment)
    align_h_options = ["left", "center", "right"]
    align_v_options = ["top", "center", "bottom"]
    
    ca1, ca2 = st.columns(2)
    with ca1:
        new_align_h = st.selectbox("Horizontale Ausrichtung", align_h_options, index=align_h_options.index(settings.get("kometa_horizontal_align", "left")))
        new_offset_h = st.slider("Horizontaler Offset (Pixel)", min_value=0, max_value=500, value=settings.get("kometa_horizontal_offset", 20))
    with ca2:
        new_align_v = st.selectbox("Vertikale Ausrichtung", align_v_options, index=align_v_options.index(settings.get("kometa_vertical_align", "top")))
        new_offset_v = st.slider("Vertikaler Offset (Pixel)", min_value=0, max_value=500, value=settings.get("kometa_vertical_offset", 20))

    # Grössen & Form mit Sliders
    cs1, cs2, cs3 = st.columns(3)
    with cs1:
        new_font_size = st.slider("Schriftgrösse (Pixel)", min_value=10, max_value=150, value=settings.get("kometa_font_size", 55))
        new_radius = st.slider("Ecken-Radius (Pixel)", min_value=0, max_value=100, value=settings.get("kometa_back_radius", 20))
    with cs2:
        new_back_width = st.slider("Banner-Breite (Pixel)", min_value=50, max_value=1000, value=settings.get("kometa_back_width", 380))
    with cs3:
        new_back_height = st.slider("Banner-Höhe (Pixel)", min_value=20, max_value=300, value=settings.get("kometa_back_height", 85))

    # Kollektionen
    st.subheader("📚 Kollektionen (Zu synchronisierende Listen)")
    st.markdown("Wähle hier deine Maintainerr-Kollektionen aus.")
    
    available_collections = get_maintainerr_collections()
    current_collections_list = settings.get("collection_names", [])
    
    if available_collections:
        valid_colls = [c for c in current_collections_list if c in available_collections]
        new_collections_list = st.multiselect("Aktive Kollektionen", available_collections, default=valid_colls)
    else:
        st.warning("Maintainerr nicht erreichbar. Manuelle Eingabe nötig.")
        colls_text = st.text_area("Kollektionsnamen (einer pro Zeile)", value="\n".join(current_collections_list), height=150)
        new_collections_list = [name.strip() for name in colls_text.split("\n") if name.strip()]

with col2:
    st.subheader("🚀 Aktionen")
    
    # Speichern Button
    if st.button("💾 Konfiguration speichern", use_container_width=True, type="primary"):
        # Werte zurück in das Dictionary schreiben
        settings["run_mode"] = new_mode
        settings["log_level"] = new_log
        settings["enable_kometa_overlays"] = enable_kometa
        settings["kometa_color_urgent"] = color_urgent
        settings["kometa_text_color_urgent"] = text_urgent
        settings["kometa_color_warning"] = color_warning
        settings["kometa_text_color_warning"] = text_warning
        
        # Alle neuen Design-Parameter speichern
        settings["kometa_horizontal_align"] = new_align_h
        settings["kometa_vertical_align"] = new_align_v
        settings["kometa_horizontal_offset"] = new_offset_h
        settings["kometa_vertical_offset"] = new_offset_v
        settings["kometa_font_size"] = new_font_size
        settings["kometa_back_radius"] = new_radius
        settings["kometa_back_width"] = new_back_width
        settings["kometa_back_height"] = new_back_height

        # Die neuen Listen direkt speichern
        settings["kometa_allowed_libraries"] = new_allowed_libs
        settings["collection_names"] = new_collections_list
        
        config["settings"] = settings
        save_config(config)

    st.divider()
    st.subheader("🕒 Automatisierung")
    
    # Wir berechnen, wann der nächste Run ist
    next_run = schedule.next_run()
    if next_run:
        st.info(f"Nächster automatischer Sync: **{next_run.strftime('%d.%m.%Y %H:%M')}**")
    else:
        st.warning("Kein automatischer Zeitplan aktiv.")
    
    st.caption("Der Timer läuft im Hintergrund (Täglich um 04:30 Uhr).")

    st.divider()
    
    # Manueller Sync Button
    st.markdown("Klicke hier, um den Sync-Prozess sofort im Hintergrund zu starten.")
    if st.button("▶️ SYNC JETZT STARTEN", use_container_width=True):
        with st.spinner("Sync läuft... Bitte warten..."):
            try:
                # Wir rufen einfach deine geniale Funktion aus der main.py auf!
                sync_collections()
                st.success("Sync erfolgreich abgeschlossen!")
                st.balloons() # Ein bisschen Spass muss sein
            except Exception as e:
                st.error(f"Fehler beim Sync: {e}")

    # NEU: Live WYSIWYG Vorschau mit Uploader
    st.subheader("🔍 Live-Vorschau (WYSIWYG Simulation)")
    st.markdown("Lade ein eigenes Poster hoch, um deine Design-Einstellungen live auf deinen echten Bildern zu testen. (Referenzgrösse intern: 2000x3000px).")

    # 1. Der geniale Uploader
    uploaded_poster = st.file_uploader("🖼️ Eigenes Poster testen (Optional)", type=["png", "jpg", "jpeg"])

    # Wir wrappen alles in einen Spinner für sauberes Lade-Feedback
    with st.spinner("⏳ Berechne Live-Vorschau..."):
        try:
            # 2. Base Poster laden (Upload oder Starbound)
            if uploaded_poster is not None:
                # Eigene Datei laden und auf Kometa-Referenz skalieren
                base_poster = Image.open(uploaded_poster).convert("RGBA")
                base_poster = base_poster.resize((2000, 3000), Image.Resampling.LANCZOS)
            else:
                # Starbound Fallback aus dem Cache
                try:
                    base_poster = Image.open("img/maintainerr_preview.png").convert("RGBA")
                except FileNotFoundError:
                    st.warning("⚠️ Standard-Vorschaubild img/maintainerr_preview.png nicht gefunden!")
                    base_poster = None

            if base_poster is not None:
                # Transparente Ebene in der Grösse des Posters erstellen
                overlay_layer = Image.new("RGBA", base_poster.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(overlay_layer)

                # --- LIVE-Werte nutzen ---
                banner_w = int(new_back_width)
                banner_h = int(new_back_height)
                offset_h = int(new_offset_h)
                offset_v = int(new_offset_v)
                font_size = int(new_font_size)
                radius = int(new_radius)
                
                canvas_w, canvas_h = 2000, 3000
                
                # Horizontale Position
                if new_align_h == "left":
                    start_x = offset_h
                elif new_align_h == "right":
                    start_x = canvas_w - banner_w - offset_h
                else: # center
                    start_x = (canvas_w - banner_w) // 2 + offset_h
                    
                # Vertikale Position
                if new_align_v == "top":
                    start_y = offset_v
                elif new_align_v == "bottom":
                    start_y = canvas_h - banner_h - offset_v
                else: # center
                    start_y = (canvas_h - banner_h) // 2 + offset_v

                # Das Banner zeichnen
                banner_coords = [start_x, start_y, start_x + banner_w, start_y + banner_h]
                draw.rounded_rectangle(banner_coords, radius=radius, fill=color_urgent)

                # Schriftart laden (Fallback-System)
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except OSError:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                    except OSError:
                        try:
                            font = ImageFont.load_default(size=font_size)
                        except TypeError:
                            font = ImageFont.load_default()

                # Text zeichnen
                text = "Noch 10 Tage"
                try:
                    bbox = font.getbbox(text)
                    text_w = bbox[2] - bbox[0]
                    text_h = bbox[3] - bbox[1]
                except AttributeError:
                    text_w, text_h = draw.textsize(text, font)

                text_x = start_x + (banner_w - text_w) / 2
                text_y = start_y + (banner_h - text_h) / 2 - (font_size * 0.1)
                
                draw.text((text_x, text_y), text, fill=text_urgent, font=font)

                # Ebenen zusammenfügen und anzeigen
                final_img = Image.alpha_composite(base_poster, overlay_layer)
                
                st.image(final_img, caption="Live Preview", use_container_width=True)

        except Exception as e:
            st.error(f"❌ Fehler bei der Vorschau-Generierung: {e}")