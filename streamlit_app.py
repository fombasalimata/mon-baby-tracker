import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Baby Tracker", page_icon="👶")
st.title("👶 Baby Tracker")

# Connexion aux Secrets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

tab1, tab2, tab3 = st.tabs(["🍼 Repas", "🧷 Changes", "🩺 Santé"])

# --- 1. ONGLET REPAS ---
with tab1:
    try:
        df_r = conn.read(worksheet="Repas", ttl=0)
    except:
        df_r = pd.DataFrame()

    with st.form("repas_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", datetime.now())
        h = col2.time_input("Heure", datetime.now().time())
        t = st.selectbox("Type", ["Tétée", "Biberon Infantile", "Biberon Maternel", "Diversification"])
        q = st.number_input("Quantité (ml)", 0, step=10)
        n = st.text_input("Note (ex: Sein gauche...)")
        
        if st.form_submit_button("Enregistrer le repas"):
            new_data = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Quantite": q, "Type": t, "Notes": n}])
            conn.update(worksheet="Repas", data=pd.concat([df_r, new_data], ignore_index=True))
            st.success("Repas enregistré !")
            st.rerun()

    # Bouton de suppression pour le dernier repas
    if not df_r.empty:
        if st.button("🗑️ Supprimer le dernier repas enregistré"):
            updated_df = df_r.iloc[:-1] # On enlève la dernière ligne
            conn.update(worksheet="Repas", data=updated_df)
            st.warning("Dernier repas supprimé.")
            st.rerun()

# --- 2. ONGLET CHANGES ---
with tab2:
    try:
        df_c = conn.read(worksheet="Changes", ttl=0)
    except:
        df_c = pd.DataFrame()

    with st.form("change_form", clear_on_submit=True):
        d_c = st.date_input("Date ", datetime.now())
        h_c = st.time_input("Heure ", datetime.now().time())
        etat = st.radio("Contenu", ["Urine", "Selles", "Les deux"])
        n_c = st.text_input("Note ")
        
        if st.form_submit_button("Enregistrer Change"):
            new_data_c = pd.DataFrame([{"Date": d_c.strftime("%d/%m/%Y"), "Heure": h_c.strftime("%H:%M"), "Type": etat, "Notes": n_c}])
            conn.update(worksheet="Changes", data=pd.concat([df_c, new_data_c], ignore_index=True))
            st.success("Change enregistré !")
            st.rerun()

    if not df_c.empty:
        if st.button("🗑️ Supprimer le dernier change"):
            updated_df_c = df_c.iloc[:-1]
            conn.update(worksheet="Changes", data=updated_df_c)
            st.warning("Dernier change supprimé.")
            st.rerun()

# --- 3. ONGLET SANTÉ ---
with tab3:
    try:
        df_s = conn.read(worksheet="Sante", ttl=0)
    except:
        df_s = pd.DataFrame()

    with st.form("sante_form", clear_on_submit=True):
        d_s = st.date_input("Date de l'événement", datetime.now())
        poids = st.number_input("Poids (kg)", 0.0, step=0.01, format="%.2f")
        taille = st.number_input("Taille (cm)", 0.0, step=0.5)
        temp = st.number_input("Température (°C)", 36.0, 42.0, 37.0, step=0.1)
        n_s = st.text_input("Note ")
        
        if st.form_submit_button("Enregistrer Santé"):
            new_data_s = pd.DataFrame([{"Date": d_s.strftime("%d/%m/%Y"), "Poids": poids, "Taille": taille, "Temperature": temp, "Notes": n_s}])
            conn.update(worksheet="Sante", data=pd.concat([df_s, new_data_s], ignore_index=True))
            st.success("Santé enregistrée !")
            st.rerun()

    if not df_s.empty:
        if st.button("🗑️ Supprimer la dernière donnée santé"):
            updated_df_s = df_s.iloc[:-1]
            conn.update(worksheet="Sante", data=updated_df_s)
            st.warning("Dernière donnée supprimée.")
            st.rerun()

# --- AFFICHAGE HISTORIQUE (REPAS) ---
st.divider()
st.subheader("📊 Historique des derniers repas")
if not df_r.empty:
    st.dataframe(df_r.tail(10), use_container_width=True, hide_index=True)
