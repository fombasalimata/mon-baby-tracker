import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Baby Tracker", page_icon="👶", layout="centered")

st.title("👶 Baby Tracker")

# Connexion aux Secrets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur : {e}")
    st.stop()

# Fonction calcul du temps
def temps_depuis_dernier(df):
    if df is None or df.empty:
        return "Aucun repas enregistré"
    try:
        derniere_ligne = df.iloc[-1]
        dernier_moment = datetime.strptime(f"{derniere_ligne['Date']} {derniere_ligne['Heure']}", "%d/%m/%Y %H:%M")
        diff = datetime.now() - dernier_moment
        h, reste = divmod(int(diff.total_seconds()), 3600)
        m, _ = divmod(reste, 60)
        return f"{h}h {m}min" if diff.total_seconds() > 0 else "À l'instant"
    except: return "--"

# Onglets
tab1, tab2, tab3 = st.tabs(["🍼 Repas & Tétées", "🧷 Changes", "🩺 Médical"])

with tab1:
    try:
        df_r = conn.read(worksheet="Repas", ttl=0)
        st.info(f"🕒 Dernier repas il y a : **{temps_depuis_dernier(df_r)}**")
    except: df_r = pd.DataFrame()

    with st.form("repas_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d_r = col1.date_input("Date", datetime.now())
        h_r = col2.time_input("Heure", datetime.now().time())
        type_r = st.selectbox("Type", ["Tétée (Sein)", "Biberon (Infantile)", "Biberon (Maternel)"])
        quantite = st.number_input("Quantité (ml)", min_value=0, value=0, step=10)
        note_r = st.text_input("Note (ex: Sein gauche)")
        if st.form_submit_button("Enregistrer"):
            new_row = pd.DataFrame([{"Date": d_r.strftime("%d/%m/%Y"), "Heure": h_r.strftime("%H:%M"), "Quantite": quantite if "Biberon" in type_r else "Tétée", "Type": type_r, "Notes": note_r}])
            conn.update(worksheet="Repas", data=pd.concat([df_r, new_row], ignore_index=True))
            st.success("Enregistré !")
            st.rerun()

with tab2:
    try: df_c = conn.read(worksheet="Changes", ttl=0)
    except: df_c = pd.DataFrame()
    with st.form("change_form", clear_on_submit=True):
        d_c = st.date_input("Date", datetime.now())
        h_c = st.time_input("Heure", datetime.now().time())
        etat = st.radio("Contenu", ["Urine", "Selles", "Les deux", "Rien"])
        note_c = st.text_input("Observations")
        if st.form_submit_button("Enregistrer change"):
            new_row = pd.DataFrame([{"Date": d_c.strftime("%d/%m/%Y"), "Heure": h_c.strftime("%H:%M"), "Type": etat, "Notes": note_c}])
            conn.update(worksheet="Changes", data=pd.concat([df_c, new_row], ignore_index=True))
            st.success("Change enregistré !")
            st.rerun()

with tab3:
    try: df_s = conn.read(worksheet="Sante", ttl=0)
    except: df_s = pd.DataFrame()
    with st.form("sante_form", clear_on_submit=True):
        d_s = st.date_input("Date RDV", datetime.now())
        p = st.number_input("Poids (kg)", format="%.2f", step=0.01)
        t = st.number_input("Taille (cm)", step=0.5)
        if st.form_submit_button("Enregistrer santé"):
            new_row = pd.DataFrame([{"Date": d_s.strftime("%d/%m/%Y"), "Poids": p, "Taille": t}])
            conn.update(worksheet="Sante", data=pd.concat([df_s, new_row], ignore_index=True))
            st.success("Santé enregistrée !")
            st.rerun()

st.divider()
st.subheader("📊 Historique")
if not df_r.empty: st.dataframe(df_r.tail(5), use_container_width=True, hide_index=True)
