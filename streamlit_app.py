import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuration de l'application
st.set_page_config(page_title="Baby Tracker", page_icon="👶", layout="centered")

st.title("👶 Baby Tracker")
st.write("Suivi partagé pour papa et maman")

# Connexion au Google Sheet (utilise les secrets configurés)
conn = st.connection("gsheets", type=GSheetsConnection)

# Création des onglets pour naviguer facilement
tab1, tab2, tab3 = st.tabs(["🍼 Repas", "🧷 Changes", "🩺 Médical"])

# --- ONGLET 1 : REPAS ---
with tab1:
    st.header("Noter un repas")
    with st.form("repas_form", clear_on_submit=True):
        date_r = st.date_input("Date", datetime.now(), key="date_repas")
        heure_r = st.time_input("Heure", datetime.now().time(), key="heure_repas")
        quantite = st.number_input("Quantité (ml)", min_value=0, value=120, step=10)
        type_lait = st.selectbox("Type de lait", ["Infantile", "Maternel"])
        note_r = st.text_input("Note libre (facultatif)", placeholder="Ex: a tout bu")
        submit_r = st.form_submit_button("En
