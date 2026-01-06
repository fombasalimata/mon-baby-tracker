import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. VOS ACCÈS (À REMPLIR) ---
# Copiez les valeurs exactes de votre fichier JSON
creds = {
    "type": "service_account",
    "project_id": "VOTRE_PROJECT_ID",
    "private_key_id": "VOTRE_PRIVATE_KEY_ID",
    "private_key": "VOTRE_PRIVATE_KEY_AVEC_LES_N",
    "client_email": "VOTRE_CLIENT_EMAIL",
    "client_id": "VOTRE_CLIENT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "VOTRE_CLIENT_X509_CERT_URL"
}
URL_SHEET = "VOTRE_URL_COMPLETE_GOOGLE_SHEET"

# --- 2. CONFIGURATION DE L'APPLI ---
st.set_page_config(page_title="Baby Tracker", page_icon="👶")

st.title("👶 Baby Tracker")

# Connexion corrigée (on ne met pas 'type=' deux fois)
try:
    conn = st.connection("gsheets", **creds, spreadsheet=URL_SHEET)
except Exception as e:
    st.error(f"Erreur de configuration : {e}")
    st.stop()

# Fonction pour calculer le temps écoulé
def temps_depuis_dernier(df):
    if df is None or df.empty:
        return "Aucun repas"
    try:
        derniere_ligne = df.iloc[-1]
        dernier_moment = datetime.strptime(f"{derniere_ligne['Date']} {derniere_ligne['Heure']}", "%d/%m/%Y %H:%M")
        diff = datetime.now() - dernier_moment
        heures, reste = divmod(diff.seconds, 3600)
        minutes, _ = divmod(reste, 60)
        return f"{heures}h {minutes}min"
    except:
        return "--"

# --- 3. LES ONGLETS ---
tab1, tab2, tab3 = st.tabs(["🍼 Repas & Tétées", "🧷 Changes", "🩺 Médical"])

# ONGLET REPAS
with tab1:
    try:
        df_r = conn.read(worksheet="Repas", ttl=0)
        st.info(f"🕒 Dernier repas il y a : **{temps_depuis_dernier(df_r)}**")
    except:
        df_r = pd.DataFrame()

    with st.form("repas_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_r = col1.date_input("Date", datetime.now())
        heure_r = col2.time_input("Heure",
