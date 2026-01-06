import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuration de l'appli
st.set_page_config(page_title="Baby Tracker", page_icon="👶")

st.title("👶 Baby Tracker")

# Connexion standard (va chercher dans les Secrets)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"L'application attend les accès dans les Secrets. Erreur : {e}")
    st.stop()

# Fonction calcul temps
def temps_depuis_dernier(df):
    if df is None or df.empty: return "Aucun repas"
    try:
        derniere_ligne = df.iloc[-1]
        dernier_moment = datetime.strptime(f"{derniere_ligne['Date']} {derniere_ligne['Heure']}", "%d/%m/%Y %H:%M")
        diff = datetime.now() - dernier_moment
        return f"{diff.seconds // 3600}h {(diff.seconds % 3600) // 60}min"
    except: return "--"

# Onglets
tab1, tab2, tab3 = st.tabs(["🍼 Repas", "🧷 Changes", "🩺 Médical"])

with tab1:
    try:
        df_r = conn.read(worksheet="Repas", ttl=0)
        st.info(f"🕒 Dernier repas il y a : **{temps_depuis_dernier(df_r)}**")
    except: df_r = pd.DataFrame()

    with st.form("repas_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_r = col1.date_input("Date", datetime.now())
        heure_r = col2.time_input("Heure", datetime.now().time())
        type_r = st.selectbox("Type", ["Tétée", "Biberon (Infantile)", "Biberon (Maternel)"])
        quantite = st.number_input("Quantité (ml)", min_value=0, value=0)
        if st.form_submit_button("Enregistrer"):
            new_row = pd.DataFrame([{"Date": date_r.strftime("%d/%m/%Y"), "Heure": heure_r.strftime("%H:%M"), "Quantite": quantite if "Biberon" in type_r else "Tétée", "Type": type_r}])
            updated = pd.concat([df_r, new_row], ignore_index=True)
            conn.update(worksheet="Repas", data=updated)
            st.success("Enregistré !")
            st.rerun()
