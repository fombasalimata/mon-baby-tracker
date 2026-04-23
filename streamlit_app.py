import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

# 1. CONFIGURATION & FUSEAU HORAIRE
st.set_page_config(page_title="Baby Tracker Pro", page_icon="👶", layout="centered")
tz = pytz.timezone('Europe/Paris')
maintenant = datetime.now(tz)

st.title("👶 Baby Tracker Pro")

# 2. CONNEXION
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. CHARGEMENT GLOBAL OPTIMISÉ
@st.cache_data(ttl="5s")
def get_all_data():
    sheets = ["Repas", "Changes", "Sommeil", "Bains", "Medicaments", "Sante", "Creche"]
    all_dfs = {}
    for s in sheets:
        try:
            df = conn.read(worksheet=s, ttl=0)
            # Nettoyage des colonnes vides et conversion en DataFrame propre
            all_dfs[s] = pd.DataFrame(df).dropna(how='all') if df is not None else pd.DataFrame()
        except:
            all_dfs[s] = pd.DataFrame()
    return all_dfs

# Chargement initial
try:
    data = get_all_data()
except Exception as e:
    st.error("⚠️ Connexion Google Sheets interrompue. Patientez 30 secondes.")
    st.stop()

# 4. FONCTION DE SAUVEGARDE SÉCURISÉE
def save_data(sheet_name, updated_df):
    try:
        # Crucial : Convertir tout en string pour Google Sheets
        df_to_save = updated_df.astype(str)
        conn.update(worksheet=sheet_name, data=df_to_save)
        st.cache_data.clear() 
        st.success("✅ Enregistré !")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Erreur : {e}")

# 5. ONGLETS
tabs = st.tabs(["🍼 Repas", "🧷 Changes", "😴 Sommeil", "🛁 Bain", "💊 Médocs", "🩺 Santé", "🏫 Crèche"])
t_repas, t_change, t_sommeil, t_bain, t_medoc, t_sante, t_creche = tabs

# --- 🍼 REPAS ---
with t_repas:
    df = data["Repas"]
    with st.form("r_f", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", maintenant, key="dr")
        h = col2.time_input("Heure", maintenant.time(), key="hr")
        t = st.selectbox("Type", ["Tétée", "Biberon Infantile", "Biberon Maternel", "Diversification"])
        q = st.number_input("Quantité (ml)", 0, step=10)
        n = st.text_input("Note", key="nr")
        if st.form_submit_button("Enregistrer Repas"):
            new = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Quantite": str(q), "Type": t, "Notes": n}])
            save_data("Repas", pd.concat([df, new], ignore_index=True))
    if not df.empty:
        if st.button("🗑️ Supprimer dernier repas"):
            save_data("Repas", df.iloc[:-1])

# --- 🧷 CHANGES ---
with t_change:
    df = data["Changes"]
    with st.form("c_f", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", maintenant, key="dc")
        h = col2.time_input("Heure", maintenant.time(), key="hc")
        et = st.radio("Contenu", ["Urine", "Selles", "Les deux"], horizontal=True)
        nc = st.text_input("Note", key="nc")
        if st.form_submit_button("Enregistrer Change"):
            new = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Type": et, "Notes": nc}])
            save_data("Changes", pd.concat([df, new], ignore_index=True))
    if not df.empty:
        if st.button("🗑️ Supprimer dernier change"):
            save_data("Changes", df.iloc[:-1])

# --- 😴 SOMMEIL ---
with t_sommeil:
    df = data["Sommeil"]
    with st.form("so_f", clear_on_submit=True):
        d = st.date_input("Date", maintenant, key="dso")
        h1 = st.time_input("Coucher", maintenant.time(), key="h1")
        h2 = st.time_input("Lever", maintenant.time(), key="h2")
        nso = st.text_input("Note", key="nso")
        if st.form_submit_button("Enregistrer Sommeil"):
            diff = datetime.combine(d, h2) - datetime.combine(d, h1)
            dur = f"{diff.seconds//3600}h{(diff.seconds//60)%60:02d}"
            new = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Coucher": h1.strftime("%H:%M"), "Lever": h2.strftime("%H:%M"), "Duree": dur, "Notes": nso}])
            save_data("Sommeil", pd.concat([df, new], ignore_index=True))
    if not df.empty:
        if st.button("🗑️ Supprimer dernier sommeil"):
            save_data("Sommeil", df.iloc[:-1])

# --- 🛁 BAIN ---
with t_bain:
    df = data["Bains"]
    with st.form("b_f", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", maintenant, key="db")
        h = col2.time_input("Heure", maintenant.time(), key="hb")
        tb = st.selectbox("Type", ["Bain", "Toilette"])
        nb = st.text_input("Note", key="nb")
        if st.form_submit_button("Enregistrer Bain"):
            new = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Type": tb, "Notes": nb}])
            save_data("Bains", pd.concat([df, new], ignore_index=True))
    if not df.empty:
        if st.button("🗑️ Supprimer dernier bain"):
            save_data("Bains", df.iloc[:-1])

# --- 💊 MÉDOCS ---
with t_medoc:
    df = data["Medicaments"]
    with st.form("m_f", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", maintenant, key="dm")
        h = col2.time_input("Heure", maintenant.time(), key="hm")
        nom = st.text_input("Médicament")
        donne = st.checkbox("Médicament déjà donné ?", value=True)
        nm = st.text_input("Note", key="nm")
        if st.form_submit_button("Enregistrer"):
            new = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Nom": nom, "Donne": "Oui" if donne else "Non", "Notes": nm}])
            save_data("Medicaments", pd.concat([df, new], ignore_index=True))
    if not df.empty:
        if st.button("🗑️ Supprimer dernier médicament"):
            save_data("Medicaments", df.iloc[:-1])

# --- 🩺 SANTÉ ---
with t_sante:
    df = data["Sante"]
    with st.form("s_f", clear_on_submit=True):
        ds = st.date_input("Date", maintenant, key="ds")
        p = st.number_input("Poids (kg)", 0.0, step=0.01)
        te = st.number_input("Température (°C)", 35.0, 41.0, 37.0)
        ns = st.text_input("Note", key="ns")
        if st.form_submit_button("Enregistrer Santé"):
            new = pd.DataFrame([{"Date": ds.strftime("%d/%m/%Y"), "Poids": str(p), "Temperature": str(te), "Notes": ns}])
            save_data("Sante", pd.concat([df, new], ignore_index=True))
    if not df.empty:
        if st.button("🗑️ Supprimer dernière donnée santé"):
            save_data("Sante", df.iloc[:-1])

# --- 🏫 CRÈCHE ---
with t_creche:
    df = data["Creche"]
    with st.form("cr_f", clear_on_submit=True):
        dcr = st.date_input("Date", maintenant, key="dcr")
        ha = st.time_input("Arrivée", maintenant.time(), key="ha")
        hd = st.time_input("Départ", maintenant.time(), key="hd")
        ncr = st.text_input("Note", key="ncr")
        if st.form_submit_button("Enregistrer Crèche"):
            new = pd.DataFrame([{"Date": dcr.strftime("%d/%m/%Y"), "Arrivee": ha.strftime("%H:%M"), "Depart": hd.strftime("%H:%M"), "Notes": ncr}])
            save_data("Creche", pd.concat([df, new], ignore_index=True))
    if not df.empty:
        if st.button("🗑️ Supprimer dernière donnée crèche"):
            save_data("Creche", df.iloc[:-1])

# --- 6. RÉCAPITULATIFS FINAUX ---
st.divider()
st.subheader("📊 Récapitulatif Global")

sections = [
    ("🍼 Repas", "Repas"), ("🧷 Changes", "Changes"), ("😴 Sommeil", "Sommeil"),
    ("🛁 Bains", "Bains"), ("💊 Médocs", "Medicaments"), ("🏫 Crèche", "Creche"), ("🩺 Santé", "Sante")
]

for label, s_name in sections:
    df_disp = data[s_name]
    if not df_disp.empty:
        with st.expander(f"{label} (Derniers enregistrements)", expanded=True):
            st.dataframe(df_disp.tail(5), use_container_width=True, hide_index=True)
    else:
        st.info(f"Aucune donnée pour {label}")
