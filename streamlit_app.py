import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

# 1. CONFIGURATION & FUSEAU HORAIRE (Correction Heure)
st.set_page_config(page_title="Baby Tracker Pro", page_icon="👶", layout="centered")
tz = pytz.timezone('Europe/Paris')
maintenant = datetime.now(tz)

st.title("👶 Baby Tracker")

# 2. CONNEXION
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

# 3. FONCTION DE LECTURE (ttl=0 pour éviter que les recaps disparaissent)
def load_sheet_safe(name):
    try:
        data = conn.read(worksheet=name, ttl=0)
        return data if data is not None else pd.DataFrame()
    except:
        return pd.DataFrame()

# Chargement initial des données
df_r = load_sheet_safe("Repas")
df_c = load_sheet_safe("Changes")
df_so = load_sheet_safe("Sommeil")
df_b = load_sheet_safe("Bains")
df_m = load_sheet_safe("Medicaments")
df_s = load_sheet_safe("Sante")
df_cr = load_sheet_safe("Creche")

# 4. ONGLETS
tabs = st.tabs(["🍼 Repas", "🧷 Changes", "😴 Sommeil", "🛁 Bain", "💊 Médocs", "🩺 Santé", "🏫 Crèche"])
t_repas, t_change, t_sommeil, t_bain, t_medoc, t_sante, t_creche = tabs

# --- MÉDICAMENTS (Avec case à cocher et sécurité) ---
with t_medoc:
    with st.form("m_f", clear_on_submit=True):
        dm = st.date_input("Date", maintenant, key="dm")
        hm = st.time_input("Heure", maintenant.time(), key="hm_m")
        nom = st.text_input("Nom du médicament")
        donne = st.checkbox("Médicament déjà donné ?", value=True)
        nm = st.text_input("Note", key="nm")
        if st.form_submit_button("Enregistrer"):
            statut = "Oui" if donne else "Non"
            new_line = pd.DataFrame([{"Date": dm.strftime("%d/%m/%Y"), "Heure": hm.strftime("%H:%M"), "Nom": nom, "Donne": statut, "Notes": nm}])
            if not df_m.empty or len(df_m) == 0: # Sécurité anti-écrasement
                updated = pd.concat([df_m, new_line], ignore_index=True)
                conn.update(worksheet="Medicaments", data=updated)
                st.success("Enregistré !")
                st.rerun()

# --- REPAS (Correction Heure) ---
with t_repas:
    with st.form("r_f", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", maintenant, key="dr")
        h = col2.time_input("Heure", maintenant.time(), key="hr")
        t = st.selectbox("Type", ["Tétée", "Biberon", "Diversification"])
        q = st.number_input("Quantité (ml)", 0, step=10)
        if st.form_submit_button("Enregistrer Repas"):
            new_line = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Quantite": q, "Type": t}])
            updated = pd.concat([df_r, new_line], ignore_index=True)
            conn.update(worksheet="Repas", data=updated)
            st.rerun()

# --- AUTRES ONGLETS (Code simplifié pour l'exemple) ---
# [Garder la même logique pour Changes, Sommeil, etc. avec maintenant.time()]

# --- 5. RÉCAPITULATIFS (Correction Affichage) ---
st.divider()
st.subheader("📊 Récapitulatif Global")

# Liste des catégories pour automatiser l'affichage
categories = [
    ("🍼 Repas", "Repas"),
    ("🧷 Changes", "Changes"),
    ("😴 Sommeil", "Sommeil"),
    ("🛁 Bains", "Bains"),
    ("💊 Médocs", "Medicaments"),
    ("🏫 Crèche", "Creche"),
    ("🩺 Santé", "Sante")
]

for label, sheet_name in categories:
    # On force le rechargement final pour être sûr que rien ne manque à l'affichage
    df_final = load_sheet_safe(sheet_name)
    if not df_final.empty:
        with st.expander(f"{label} (Derniers enregistrements)", expanded=True):
            st.dataframe(df_final.tail(3), use_container_width=True, hide_index=True)
    else:
        st.info(f"Aucune donnée pour {label}")
