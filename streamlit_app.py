import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. VOS ACCÈS (À REMPLIR AVEC VOTRE FICHIER JSON) ---
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
st.set_page_config(page_title="Baby Tracker", page_icon="👶", layout="centered")

st.title("👶 Baby Tracker")
st.write("Suivi Allaitement Mixte & Santé")

# Connexion forcée avec le type explicite
try:
    conn = st.connection("gsheets", type=GSheetsConnection, **creds, spreadsheet=URL_SHEET)
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

# Fonction pour calculer le temps écoulé
def temps_depuis_dernier(df):
    if df is None or df.empty:
        return "Aucun repas enregistré"
    try:
        if 'Date' in df.columns and 'Heure' in df.columns:
            derniere_ligne = df.iloc[-1]
            dernier_moment = datetime.strptime(f"{derniere_ligne['Date']} {derniere_ligne['Heure']}", "%d/%m/%Y %H:%M")
            diff = datetime.now() - dernier_moment
            heures, reste = divmod(diff.seconds, 3600)
            minutes, _ = divmod(reste, 60)
            if diff.days > 0:
                return "Plus de 24h"
            return f"{heures}h {minutes}min"
    except:
        return "--"
    return "--"

# --- 3. INTERFACE PAR ONGLETS ---
tab1, tab2, tab3 = st.tabs(["🍼 Repas & Tétées", "🧷 Changes", "🩺 Médical"])

# ONGLET 1 : REPAS
with tab1:
    try:
        df_r = conn.read(worksheet="Repas", ttl=0)
        st.info(f"🕒 Dernier repas il y a : **{temps_depuis_dernier(df_r)}**")
    except:
        df_r = pd.DataFrame()

    with st.form("repas_form", clear_on_submit=True):
        col_d, col_h = st.columns(2)
        date_r = col_d.date_input("Date", datetime.now())
        heure_r = col_h.time_input("Heure", datetime.now().time())
        
        type_repas = st.selectbox("Type", ["Tétée (Sein)", "Biberon (Infantile)", "Biberon (Maternel)"])
        quantite = st.number_input("Quantité (ml) - si biberon", min_value=0, value=0, step=10)
        note_r = st.text_input("Note (ex: Sein gauche, a bien tété)")
        
        if st.form_submit_button("Enregistrer le repas"):
            new_row = pd.DataFrame([{
                "Date": date_r.strftime("%d/%m/%Y"),
                "Heure": heure_r.strftime("%H:%M"),
                "Quantite": quantite if "Biberon" in type_repas else "Tétée",
                "Type": type_repas,
                "Notes": note_r
            }])
            updated = pd.concat([df_r, new_row], ignore_index=True)
            conn.update(worksheet="Repas", data=updated)
            st.success("Repas enregistré !")
            st.rerun()

# ONGLET 2 : CHANGES
with tab2:
    try:
        df_c = conn.read(worksheet="Changes", ttl=0)
    except:
        df_c = pd.DataFrame()

    with st.form("change_form", clear_on_submit=True):
        date_c = st.date_input("Date change", datetime.now())
        heure_c = st.time_input("Heure change", datetime.now().time())
        etat = st.radio("Contenu", ["Urine", "Selles", "Les deux", "Rien"])
        note_c = st.text_input("Observations")
        
        if st.form_submit_button("Enregistrer change"):
            new_row = pd.DataFrame([{
                "Date": date_c.strftime("%d/%m/%Y"),
                "Heure": heure_c.strftime("%H:%M"),
                "Type": etat,
                "Notes": note_c
            }])
            updated = pd.concat([df_c, new_row], ignore_index=True)
            conn.update(worksheet="Changes", data=updated)
            st.success("Change enregistré !")
            st.rerun()

# ONGLET 3 : MÉDICAL
with tab3:
    try:
        df_s = conn.read(worksheet="Sante", ttl=0)
    except:
        df_s = pd.DataFrame()

    with st.form("sante_form", clear_on_submit=True):
        date_s = st.date_input("Date RDV", datetime.now())
        poids = st.number_input("Poids (kg)", min_value=0.0, step=0.01, format="%.2f")
        taille = st.number_input("Taille (cm)", min_value=0.0, step=0.5, format="%.1f")
        notes_s = st.text_area("Compte-rendu médecin")
        
        if st.form_submit_button("Enregistrer santé"):
            new_row = pd.DataFrame([{
                "Date": date_s.strftime("%d/%m/%Y"),
                "Type_RDV": "Suivi",
                "Poids": poids,
                "Taille": taille,
                "Notes": notes_s
            }])
            updated = pd.concat([df_s, new_row], ignore_index=True)
            conn.update(worksheet="Sante", data=updated)
            st.success("Données médicales enregistrées !")
            st.rerun()

# --- 4. HISTORIQUE BAS DE PAGE ---
st.divider()
st.subheader("📊 Dernières activités")
col_l, col_r = st.columns(2)

with col_l:
    if not df_r.empty:
        st.write("**Repas :**")
        st.dataframe(df_r.tail(3), hide_index=True)

with col_r:
    if not df_c.empty:
        st.write("**Changes :**")
        st.dataframe(df_c.tail(3), hide_index=True)
