import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Baby Tracker", page_icon="👶", layout="centered")

st.title("👶 Suivi de Bébé")

# Connexion à Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Onglets pour une navigation facile
tab1, tab2, tab3 = st.tabs(["🍼 Repas", "🧷 Changes", "🩺 Médical"])

with tab1:
    st.header("Noter un Biberon")
    with st.form("form_repas"):
        heure = st.time_input("Heure", datetime.now().time())
        quantite = st.number_input("Quantité (ml)", min_value=0, step=10, value=120)
        notes = st.text_input("Notes (ex: a bien bu)")
        submit = st.form_submit_button("Enregistrer le repas")
        
        if submit:
            new_row = pd.DataFrame([{"Date": datetime.now().strftime("%d/%m/%Y"), "Heure": heure.strftime("%H:%M"), "Quantite": quantite, "Notes": notes}])
            # Logique d'ajout ici
            st.success("Repas enregistré !")

with tab2:
    st.header("Suivi des changes")
    # ... même logique pour les changes

with tab3:
    st.header("Rendez-vous Médical")
    # ... même logique pour le médical
