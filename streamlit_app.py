import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. VOS ACCÈS (À REMPLIR) ---
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

# CONNEXION ULTRA-SIMPLIFIÉE (SANS ARGUMENT 'TYPE' EN DOUBLE)
try:
    # On utilise uniquement GSheetsConnection comme type direct
    conn = st.connection("gsheets", type=GSheetsConnection, **creds, spreadsheet=URL_SHEET)
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
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
tab1, tab2, tab3 = st.tabs(["🍼 Repas", "🧷 Changes", "🩺 Médical"])

with tab1:
    try:
        df_r = conn.read(worksheet="Repas", ttl=0)
        st.info(f"🕒 Dernier repas il y a : **{temps_depuis_dernier(df_r)}**")
    except:
        df_r = pd.DataFrame()

    with st.form("repas_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_r = col1.date_input("Date", datetime.now())
        heure_r = col2.time_input("Heure", datetime.now().time())
        type_repas = st.selectbox("Type", ["Tétée", "Biberon (Lait Infantile)", "Biberon (Lait Maternel)"])
        quantite = st.number_input("Quantité (ml)", min_value=0, value=0)
        note_r = st.text_input("Notes (ex: sein gauche)")
        if st.form_submit_button("Enregistrer"):
            new_row = pd.DataFrame([{"Date": date_r.strftime("%d/%m/%Y"), "Heure": heure_r.strftime("%H:%M"), "Quantite": quantite if "Biberon" in type_repas else "Tétée", "Type": type_repas, "Notes": note_r}])
            updated = pd.concat([df_r, new_row], ignore_index=True)
            conn.update(worksheet="Repas", data=updated)
            st.success("Enregistré !")
            st.rerun()

with tab2:
    try:
        df_c = conn.read(worksheet="Changes", ttl=0)
    except:
        df_c = pd.DataFrame()

    with st.form("change_form", clear_on_submit=True):
        date_c = st.date_input("Date change", datetime.now())
        heure_c = st.time_input("Heure change", datetime.now().time())
        etat = st.radio("Contenu", ["Urine", "Selles", "Les deux", "Rien"])
        if st.form_submit_button("Enregistrer change"):
            new_row = pd.DataFrame([{"Date": date_c.strftime("%d/%m/%Y"), "Heure": heure_c.strftime("%H:%M"), "Type": etat}])
            updated = pd.concat([df_c, new_row], ignore_index=True)
            conn.update(worksheet="Changes", data=updated)
            st.success("Change enregistré !")
            st.rerun()

with tab3:
    try:
        df_s = conn.read(worksheet="Sante", ttl=0)
    except:
        df_s = pd.DataFrame()

    with st.form("sante_form", clear_on_submit=True):
        poids = st.number_input("Poids (kg)", format="%.2f")
        taille = st.number_input("Taille (cm)")
        if st.form_submit_button("Enregistrer santé"):
            new_row = pd.DataFrame([{"Date": datetime.now().strftime("%d/%m/%Y"), "Poids": poids, "Taille": taille}])
            updated = pd.concat([df_s, new_row], ignore_index=True)
            conn.update(worksheet="Sante", data=updated)
            st.success("Santé enregistrée !")
            st.rerun()

st.divider()
st.subheader("📊 Dernières activités")
if not df_r.empty:
    st.dataframe(df_r.tail(3), use_container_width=True, hide_index=True)
