import streamlit as st
import yaml
import os
from main import sync_collections, CURRENT_VERSION

# Seiten-Konfiguration
st.set_page_config(
    page_title="Maintainerr Sync",
    page_icon="🚀",
    layout="wide"
)

# Titel und Header
st.title("🎬 Maintainerr-to-Plex Sync")
st.markdown(f"**Version:** `{CURRENT_VERSION}` | UI Powered by Streamlit")
st.divider()

# Funktion zum Laden der Config
def load_config():
    try:
        with open("config.yml", "r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        st.error("config.yml nicht gefunden!")
        return {}

# Funktion zum Speichern der Config
def save_config(config_data):
    with open("config.yml", "w", encoding="utf-8") as file:
        yaml.dump(config_data, file, default_flow_style=False, allow_unicode=True)
    st.toast("✅ Konfiguration erfolgreich gespeichert!", icon="💾")

# Config in den Speicher laden
config = load_config()
settings = config.get("settings", {})

# === UI LAYOUT ===
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
    
    # Farben mit Color Picker
    c1, c2 = st.columns(2)
    with c1:
        color_urgent = st.color_picker("Hintergrundfarbe (Dringend / <= 10 Tage)", value=settings.get("kometa_color_urgent", "#E31E24"))
        text_urgent = st.color_picker("Schriftfarbe (Dringend)", value=settings.get("kometa_text_color_urgent", "#FFFFFF"))
    with c2:
        color_warning = st.color_picker("Hintergrundfarbe (Warnung / > 10 Tage)", value=settings.get("kometa_color_warning", "#F1C40F"))
        text_warning = st.color_picker("Schriftfarbe (Warnung)", value=settings.get("kometa_text_color_warning", "#141414"))

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
        
        config["settings"] = settings
        save_config(config)

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