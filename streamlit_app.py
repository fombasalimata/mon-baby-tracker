import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

# Configuration de l'application
st.set_page_config(page_title="Baby Tracker", page_icon="👶", layout="centered")

st.title("👶 Baby Tracker")
st.write("Suivi partagé - Allaitement mixte & Biberons")

# Connexion au Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# Fonction pour calculer le temps écoulé
def temps_depuis_dernier(df):
    if df.empty:
        return "Aucun repas enregistré"
    try:
        derniere_ligne = df.iloc[-1]
        dernier_moment = datetime.strptime(f"{derniere_ligne['Date']} {derniere_ligne['Heure']}", "%d/%m/%Y %H:%M")
        diff = datetime.now() - dernier_moment
        heures, reste = divmod(diff.seconds, 3600)
        minutes, _ = divmod(reste, 60)
        if diff.days > 0:
            return "Plus de 24h"
        return f"{heures}h {minutes}min"
    except:
        return "Calcul impossible"

# Création des onglets
tab1, tab2, tab3 = st.tabs(["🍼 Repas & Tétées", "🧷 Changes", "🩺 Médical"])

# --- ONGLET 1 : REPAS (ALLAITEMENT MIXTE) ---
with tab1:
    # Affichage du temps écoulé
    try:
        data_repas_actuel = conn.read(worksheet="Repas", ttl=0)
        temps_ecoule = temps_depuis_dernier(data_repas_actuel)
        st.info(f"🕒 Dernier repas il y a : **{temps_ecoule}**")
    except:
        pass

    st.header("Noter un repas")
    with st.form("repas_form", clear_on_submit=True):
        date_r = st.date_input("Date", datetime.now())
        heure_r = st.time_input("Heure", datetime.now().time())
        
        # Options pour l'allaitement mixte
        type_repas = st.selectbox("Type de repas", [
            "Tétée (Sein)", 
            "Biberon (Lait Infantile)", 
            "Biberon (Lait Maternel)"
        ])
        
        quantite = st.number_input("Quantité si biberon (ml)", min_value=0, value=0, step=10)
        note_r = st.text_input("Note (ex: sein gauche, a bien tété)")
        
        submit_r = st.form_submit_button("Enregistrer")
        
        if submit_r:
            new_data = pd.DataFrame([{
                "Date": date_r.strftime("%d/%m/%Y"),
                "Heure": heure_r.strftime("%H:%M"),
                "Quantite": quantite if "Biberon" in type_repas else "Tétée",
                "Type": type_repas,
                "Notes": note_r
            }])
            existing = conn.read(worksheet="Repas", ttl=0)
            updated = pd.concat([existing, new_data], ignore_index=True)
            conn.update(worksheet="Repas", data=updated)
            st.success("Enregistré ! L'affichage va se mettre à jour.")
            st.rerun()

# --- ONGLET 2 : CHANGES ---
with tab2:
    st.header("Suivi des changes")
    with st.form("change_form", clear_on_submit=True):
        date_c = st.date_input("Date", datetime.now(), key="d_c")
        heure_c = st.time_input("Heure", datetime.now().time(), key="h_c")
        etat = st.radio("Contenu", ["Urine", "Selles", "Les deux", "Rien"])
        note_c = st.text_input("Observations")
        submit_c = st.form_submit_button("Enregistrer le change")
        
        if submit_c:
            new_data = pd.DataFrame([{
                "Date": date_c.strftime("%d/%m/%Y"),
                "Heure": heure_c.strftime("%H:%M"),
                "Type": etat,
                "Notes": note_c
            }])
            existing = conn.read(worksheet="Changes", ttl=0)
            updated = pd.concat([existing, new_data], ignore_index=True)
            conn.update(worksheet="Changes", data=updated)
            st.success("Change enregistré !")
            st.rerun()

# --- ONGLET 3 : MÉDICAL ---
with tab3:
    st.header("Santé")
    with st.form("sante_form", clear_on_submit=True):
        date_s = st.date_input("Date", datetime.now())
        poids = st.number_input("Poids (kg)", min_value=0.0, step=0.01, format="%.2f")
        taille = st.number_input("Taille (cm)", min_value=0.0, step=0.5)
        notes_s = st.text_area("Notes")
        submit_s = st.form_submit_button("Enregistrer")
        
        if submit_s:
            new_data = pd.DataFrame([{
                "Date": date_s.strftime("%d/%m/%Y"),
                "Type_RDV": "Suivi",
                "Poids": poids,
                "Taille": taille,
                "Notes": notes_s
            }])
            existing = conn.read(worksheet="Sante", ttl=0)
            updated = pd.concat([existing, new_data], ignore_index=True)
            conn.update(worksheet="Sante", data=updated)
            st.success("Données médicales enregistrées !")

# --- HISTORIQUE RAPIDE ---
st.divider()
st.subheader("📊 Historique récent")
col1, col2 = st.columns(2)

with col1:
    try:
        st.write("**Derniers repas :**")
        df_r = conn.read(worksheet="Repas", ttl=0)
        st.dataframe(df_r.tail(5), use_container_width=True)
    except:
        st.info("Aucun repas.")

with col2:
    try:
        st.write("**Derniers changes :**")
        df_c = conn.read(worksheet="Changes", ttl=0)
        st.dataframe(df_c.tail(5), use_container_width=True)
    except:
        st.info("Aucun change.")
