import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Baby Tracker", page_icon="👶")

st.title("👶 Baby Tracker")

# Connexion sécurisée au Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# Création des onglets
tab1, tab2, tab3 = st.tabs(["🍼 Repas", "🧷 Changes", "🩺 Médical"])

# --- ONGLET REPAS ---
with tab1:
    st.header("Noter un repas")
    with st.form("repas_form"):
        heure_r = st.time_input("Heure du biberon", datetime.now().time())
        quantite = st.number_input("Quantité (ml)", min_value=0, value=120, step=10)
        type_lait = st.selectbox("Type de lait", ["Infantile", "Maternel"])
        submit_r = st.form_submit_button("Enregistrer le repas")
        
        if submit_r:
            new_data = pd.DataFrame([{"Date": datetime.now().strftime("%d/%m/%Y"), "Heure": heure_r.strftime("%H:%M"), "Quantite": quantite, "Type": type_lait}])
            existing = conn.read(worksheet="Repas")
            updated = pd.concat([existing, new_data], ignore_index=True)
            conn.update(worksheet="Repas", data=updated)
            st.success("Repas enregistré !")

# --- ONGLET CHANGES ---
with tab2:
    st.header("Suivi des changes")
    with st.form("change_form"):
        heure_c = st.time_input("Heure du change", datetime.now().time())
        etat = st.radio("Contenu", ["Urine", "Selles", "Les deux"])
        notes_c = st.text_input("Observations (ex: érythème)")
        submit_c = st.form_submit_button("Enregistrer le change")
        
        if submit_c:
            new_data = pd.DataFrame([{"Date": datetime.now().strftime("%d/%m/%Y"), "Heure": heure_c.strftime("%H:%M"), "Type": etat, "Notes": notes_c}])
            existing = conn.read(worksheet="Changes")
            updated = pd.concat([existing, new_data], ignore_index=True)
            conn.update(worksheet="Changes", data=updated)
            st.success("Change enregistré !")

# --- ONGLET MÉDICAL ---
with tab3:
    st.header("Rendez-vous & Santé")
    with st.form("sante_form"):
        date_s = st.date_input("Date du RDV", datetime.now())
        poids = st.number_input("Poids (kg)", min_value=0.0, step=0.1)
        taille = st.number_input("Taille (cm)", min_value=0.0, step=0.5)
        notes_s = st.text_area("Notes du médecin")
        submit_s = st.form_submit_button("Enregistrer les infos médicales")
        
        if submit_s:
            new_data = pd.DataFrame([{"Date": date_s.strftime("%d/%m/%Y"), "Type_RDV": "Pédiatre", "Poids": poids, "Taille": taille, "Notes": notes_s}])
            existing = conn.read(worksheet="Sante")
            updated = pd.concat([existing, new_data], ignore_index=True)
            conn.update(worksheet="Sante", data=updated)
            st.success("Données médicales enregistrées !")

# Affichage de l'historique rapide en bas
st.divider()
st.subheader("Dernières activités")
if st.checkbox("Afficher l'historique"):
    st.write("Derniers repas :")
    st.table(conn.read(worksheet="Repas").tail(3))
