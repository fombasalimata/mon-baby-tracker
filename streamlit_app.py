import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Baby Tracker", page_icon="👶", layout="centered")

st.title("👶 Baby Tracker")
st.write("Suivi Allaitement Mixte & Santé")

# 2. CONNEXION (Cherche les infos dans les Secrets Streamlit Cloud)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de configuration : {e}")
    st.stop()

# 3. FONCTION : CALCUL DU TEMPS ÉCOULÉ
def temps_depuis_dernier(df):
    if df is None or df.empty:
        return "Aucun repas enregistré"
    try:
        if 'Date' in df.columns and 'Heure' in df.columns:
            derniere_ligne = df.iloc[-1]
            dernier_moment = datetime.strptime(f"{derniere_ligne['Date']} {derniere_ligne['Heure']}", "%d/%m/%Y %H:%M")
            diff = datetime.now() - dernier_moment
            h, reste = divmod(int(diff.total_seconds()), 3600)
            m, _ = divmod(reste, 60)
            return f"{h}h {m}min"
    except:
        return "--"
    return "--"

# 4. INTERFACE PAR ONGLETS
tab1, tab2, tab3 = st.tabs(["🍼 Repas & Tétées", "🧷 Changes", "🩺 Médical"])

# --- ONGLET REPAS ---
with tab1:
    try:
        df_r = conn.read(worksheet="Repas", ttl=0)
        st.info(f"🕒 Dernier repas il y a : **{temps_depuis_dernier(df_r)}**")
    except Exception as e:
        st.warning("Impossible de lire l'historique des repas. Vérifiez vos Secrets.")
        df_r = pd.DataFrame()

    with st.form("repas_form", clear_on_submit=True):
        col_d, col_h = st.columns(2)
        date_r = col_d.date_input("Date", datetime.now())
        heure_r = col_h.time_input("Heure", datetime.now().time())
        type_re
