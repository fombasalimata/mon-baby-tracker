import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Baby Tracker Pro", page_icon="👶", layout="centered")

st.title("👶 Baby Tracker")

# Connexion aux Secrets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

# Création des 5 onglets
tabs = st.tabs(["🍼 Repas", "🧷 Changes", "💊 Médocs", "🩺 Santé", "🏫 Crèche"])
tab_repas, tab_change, tab_medoc, tab_sante, tab_creche = tabs

# --- 1. ONGLET REPAS ---
with tab_repas:
    try:
        df_r = conn.read(worksheet="Repas", ttl=0)
    except:
        df_r = pd.DataFrame()

    with st.form("repas_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", datetime.now(), key="d_r")
        h = col2.time_input("Heure", datetime.now().time(), key="h_r")
        t = st.selectbox("Type", ["Tétée", "Biberon Infantile", "Biberon Maternel", "Diversification"])
        q = st.number_input("Quantité (ml)", 0, step=10)
        n = st.text_input("Note (ex: Sein gauche...)")
        
        if st.form_submit_button("Enregistrer"):
            new_data = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Quantite": q, "Type": t, "Notes": n}])
            conn.update(worksheet="Repas", data=pd.concat([df_r, new_data], ignore_index=True))
            st.success("Repas noté !")
            st.rerun()
    
    if not df_r.empty:
        if st.button("🗑️ Supprimer dernier repas"):
            conn.update(worksheet="Repas", data=df_r.iloc[:-1])
            st.rerun()

# --- 2. ONGLET CHANGES ---
with tab_change:
    try:
        df_c = conn.read(worksheet="Changes", ttl=0)
    except:
        df_c = pd.DataFrame()

    with st.form("change_form", clear_on_submit=True):
        d_c = st.date_input("Date", datetime.now(), key="d_c")
        h_c = st.time_input("Heure", datetime.now().time(), key="h_c")
        etat = st.radio("Contenu", ["Urine", "Selles", "Les deux"])
        n_c = st.text_input("Note change")
        
        if st.form_submit_button("Enregistrer Change"):
            new_data_c = pd.DataFrame([{"Date": d_c.strftime("%d/%m/%Y"), "Heure": h_c.strftime("%H:%M"), "Type": etat, "Notes": n_c}])
            conn.update(worksheet="Changes", data=pd.concat([df_c, new_data_c], ignore_index=True))
            st.success("Change noté !")
            st.rerun()

    if not df_c.empty:
        if st.button("🗑️ Supprimer dernier change"):
            conn.update(worksheet="Changes", data=df_c.iloc[:-1])
            st.rerun()

# --- 3. ONGLET MÉDICAMENTS ---
with tab_medoc:
    try:
        df_m = conn.read(worksheet="Medicaments", ttl=0)
    except:
        df_m = pd.DataFrame()

    with st.form("medoc_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d_m = col1.date_input("Date", datetime.now(), key="d_m")
        h_m = col2.time_input("Heure", datetime.now().time(), key="h_m")
        nom_m = st.text_input("Médicament (ex: Vitamine D, Doliprane)")
        donne = st.checkbox("Cocher si la dose a été donnée", value=True)
        n_m = st.text_input("Notes médicaments")
        
        if st.form_submit_button("Enregistrer Médicament"):
            statut = "✅ OUI" if donne else "❌ NON"
            new_data_m = pd.DataFrame([{"Date": d_m.strftime("%d/%m/%Y"), "Heure": h_m.strftime("%H:%M"), "Nom": nom_m, "Donne": statut, "Notes": n_m}])
            conn.update(worksheet="Medicaments", data=pd.concat([df_m, new_data_m], ignore_index=True))
            st.success("Prise enregistrée !")
            st.rerun()

    if not df_m.empty:
        if st.button("🗑️ Supprimer dernier médicament"):
            conn.update(worksheet="Medicaments", data=df_m.iloc[:-1])
            st.rerun()

# --- 4. ONGLET SANTÉ ---
with tab_sante:
    try:
        df_s = conn.read(worksheet="Sante", ttl=0)
    except:
        df_s = pd.DataFrame()

    with st.form("sante_form", clear_on_submit=True):
        d_s = st.date_input("Date", datetime.now(), key="d_s")
        col_p, col_t = st.columns(2)
        poids = col_p.number_input("Poids (kg)", 0.0, step=0.01)
        taille = col_t.number_input("Taille (cm)", 0.0, step=0.5)
        temp = st.number_input("Température (°C)", 35.0, 41.0, 37.0, step=0.1)
        n_s = st.text_input("Notes santé")
        
        if st.form_submit_button("Enregistrer Santé"):
            new_data_s = pd.DataFrame([{"Date": d_s.strftime("%d/%m/%Y"), "Poids": poids, "Taille": taille, "Temperature": temp, "Notes": n_s}])
            conn.update(worksheet="Sante", data=pd.concat([df_s, new_data_s], ignore_index=True))
            st.success("Santé enregistrée !")
            st.rerun()

    if not df_s.empty:
        if st.button("🗑️ Supprimer dernière santé"):
            conn.update(worksheet="Sante", data=df_s.iloc[:-1])
            st.rerun()

# --- 5. ONGLET CRÈCHE ---
with tab_creche:
    try:
        df_cr = conn.read(worksheet="Creche", ttl=0)
    except:
        df_cr = pd.DataFrame()

    with st.form("creche_form", clear_on_submit=True):
        d_cr = st.date_input("Journée", datetime.now(), key="d_cr")
        h_arr = st.time_input("Arrivée")
        h_dep = st.time_input("Départ")
        n_cr = st.text_input("Note crèche")
        
        if st.form_submit_button("Enregistrer Crèche"):
            t1 = datetime.combine(d_cr, h_arr)
            t2 = datetime.combine(d_cr, h_dep)
            duree = t2 - t1
            heures, secondes = divmod(duree.seconds, 3600)
            minutes = secondes // 60
            duree_str = f"{heures}h{minutes:02d}"
            
            new_data_cr = pd.DataFrame([{"Date": d_cr.strftime("%d/%m/%Y"), "Arrivee": h_arr.strftime("%H:%M"), "Depart": h_dep.strftime("%H:%M"), "Duree": duree_str, "Notes": n_cr}])
            conn.update(worksheet="Creche", data=pd.concat([df_cr, new_data_cr], ignore_index=True))
            st.success(f"Crèche notée ! ({duree_str})")
            st.rerun()

    if not df_cr.empty:
        if st.button("🗑️ Supprimer dernière crèche"):
            conn.update(worksheet="Creche", data=df_cr.iloc[:-1])
            st.rerun()

# --- RÉCAPITULATIF COMPLET ---
st.divider()
st.subheader("📊 Récapitulatif Global")

# On affiche les résumés par catégorie
if not df_r.empty:
    st.write("**🍼 Repas (3 derniers)**")
    st.dataframe(df_r.tail(3)[['Date', 'Heure', 'Quantite', 'Type']], use_container_width=True, hide_index=True)

if not df_c.empty:
    st.write("**🧷 Changes (3 derniers)**")
    st.dataframe(df_c.tail(3)[['Date', 'Heure', 'Type']], use_container_width=True, hide_index=True)

if not df_m.empty:
    st.write("**💊 Médicaments (Suivi des prises)**")
    st.dataframe(df_m.tail(3)[['Date', 'Heure', 'Nom', 'Donne']], use_container_width=True, hide_index=True)

if not df_cr.empty:
    st.write("**🏫 Crèche (Historique des journées)**")
    st.dataframe(df_cr.tail(3)[['Date', 'Arrivee', 'Depart', 'Duree']], use_container_width=True, hide_index=True)

if not df_s.empty:
    st.write("**🩺 Santé (Poids/Taille/Temp)**")
    st.dataframe(df_s.tail(3)[['Date', 'Poids', 'Taille', 'Temperature']], use_container_width=True, hide_index=True)
