import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Baby Tracker", page_icon="👶", layout="centered")

st.title("👶 Baby Tracker")
st.write("Suivi quotidien personnalisé")

# Connexion aux Secrets Streamlit Cloud
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

# Création des onglets
tab1, tab2, tab3 = st.tabs(["🍼 Repas", "🧷 Changes", "🩺 Santé"])

# --- 1. ONGLET REPAS ---
with tab1:
    try:
        df_r = conn.read(worksheet="Repas", ttl=0)
    except:
        df_r = pd.DataFrame()

    with st.form("repas_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", datetime.now(), key="date_r")
        h = col2.time_input("Heure", datetime.now().time(), key="time_r")
        t = st.selectbox("Type", ["Tétée", "Biberon Infantile", "Biberon Maternel", "Diversification"])
        q = st.number_input("Quantité (ml)", 0, step=10)
        n = st.text_input("Note (ex: Sein gauche, a bien bu...)")
        
        if st.form_submit_button("Enregistrer le repas"):
            new_data = pd.DataFrame([{
                "Date": d.strftime("%d/%m/%Y"),
                "Heure": h.strftime("%H:%M"),
                "Quantite": q,
                "Type": t,
                "Notes": n
            }])
            conn.update(worksheet="Repas", data=pd.concat([df_r, new_data], ignore_index=True))
            st.success("Repas enregistré !")
            st.rerun()

    if not df_r.empty:
        if st.button("🗑️ Supprimer le dernier repas"):
            conn.update(worksheet="Repas", data=df_r.iloc[:-1])
            st.warning("Dernier repas supprimé.")
            st.rerun()

# --- 2. ONGLET CHANGES ---
with tab2:
    try:
        df_c = conn.read(worksheet="Changes", ttl=0)
    except:
        df_c = pd.DataFrame()

    with st.form("change_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d_c = col1.date_input("Date", datetime.now(), key="date_c")
        h_c = col2.time_input("Heure", datetime.now().time(), key="time_c")
        etat = st.radio("Contenu", ["Urine", "Selles", "Les deux"])
        n_c = st.text_input("Note change")
        
        if st.form_submit_button("Enregistrer Change"):
            new_data_c = pd.DataFrame([{
                "Date": d_c.strftime("%d/%m/%Y"),
                "Heure": h_c.strftime("%H:%M"),
                "Type": etat,
                "Notes": n_c
            }])
            conn.update(worksheet="Changes", data=pd.concat([df_c, new_data_c], ignore_index=True))
            st.success("Change enregistré !")
            st.rerun()

    if not df_c.empty:
        if st.button("🗑️ Supprimer le dernier change"):
            conn.update(worksheet="Changes", data=df_c.iloc[:-1])
            st.warning("Dernier change supprimé.")
            st.rerun()

# --- 3. ONGLET SANTÉ ---
with tab3:
    try:
        df_s = conn.read(worksheet="Sante", ttl=0)
    except:
        df_s = pd.DataFrame()

    with st.form("sante_form", clear_on_submit=True):
        d_s = st.date_input("Date", datetime.now(), key="date_s")
        col_p, col_t = st.columns(2)
        poids = col_p.number_input("Poids (kg)", 0.0, step=0.01, format="%.2f")
        taille = col_t.number_input("Taille (cm)", 0.0, step=0.5)
        temp = st.number_input("Température (°C)", 35.0, 42.0, 37.0, step=0.1)
        n_s = st.text_input("Notes (Vaccins, vitamines...)")
        
        if st.form_submit_button("Enregistrer Santé"):
            new_data_s = pd.DataFrame([{
                "Date": d_s.strftime("%d/%m/%Y"),
                "Poids": poids,
                "Taille": taille,
                "Temperature": temp,
                "Notes": n_s
            }])
            conn.update(worksheet="Sante", data=pd.concat([df_s, new_data_s], ignore_index=True))
            st.success("Données de santé enregistrées !")
            st.rerun()

    if not df_s.empty:
        if st.button("🗑️ Supprimer la dernière donnée santé"):
            conn.update(worksheet="Sante", data=df_s.iloc[:-1])
            st.warning("Dernière donnée santé supprimée.")
            st.rerun()

# --- HISTORIQUE GLOBAL AVEC UNITÉS ---
st.divider()
st.subheader("📊 Récapitulatif")

col_hist1, col_hist2 = st.columns(2)

with col_hist1:
    if not df_r.empty:
        st.write("**Derniers repas**")
        res_r = df_r.tail(5).copy()
        # Formate l'affichage de la quantité
        res_r['Quantite'] = res_r['Quantite'].apply(lambda x: f"{x} ml" if str(x).replace('.','',1).isdigit() else x)
        st.dataframe(res_r[['Heure', 'Quantite', 'Type']], use_container_width=True, hide_index=True)

with col_hist2:
    if not df_s.empty:
        st.write("**Suivi Santé**")
        res_s = df_s.tail(5).copy()
        # Formate l'affichage poids/taille/temp
        res_s['Poids'] = res_s['Poids'].apply(lambda x: f"{x} kg" if x > 0 else "-")
        res_s['Temp.'] = res_s['Temperature'].apply(lambda x: f"{x} °C")
        st.dataframe(res_s[['Date', 'Poids', 'Temp.']], use_container_width=True, hide_index=True)
