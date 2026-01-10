import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

# 1. CONFIGURATION
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

# 3. CHARGEMENT UNIQUE (Pour éviter l'API Error)
# On charge tout au début une seule fois avec un petit cache de 2 secondes
# pour éviter de bombarder Google à chaque micro-rafraîchissement.
def load_all_data():
    return {
        "Repas": conn.read(worksheet="Repas", ttl="2s"),
        "Changes": conn.read(worksheet="Changes", ttl="2s"),
        "Sommeil": conn.read(worksheet="Sommeil", ttl="2s"),
        "Bains": conn.read(worksheet="Bains", ttl="2s"),
        "Medicaments": conn.read(worksheet="Medicaments", ttl="2s"),
        "Sante": conn.read(worksheet="Sante", ttl="2s"),
        "Creche": conn.read(worksheet="Creche", ttl="2s"),
    }

try:
    data_dict = load_all_data()
except Exception as e:
    st.error("Google Sheets est temporairement indisponible (Quota atteint). Attendez 1 minute.")
    st.stop()

# 4. ONGLETS
tabs = st.tabs(["🍼 Repas", "🧷 Changes", "😴 Sommeil", "🛁 Bain", "💊 Médocs", "🩺 Santé", "🏫 Crèche"])
t_repas, t_change, t_sommeil, t_bain, t_medoc, t_sante, t_creche = tabs

# --- FONCTION DE MISE À JOUR COMMUNE ---
def update_and_refresh(sheet_name, new_df):
    try:
        conn.update(worksheet=sheet_name, data=new_df)
        st.cache_data.clear() # On vide le cache local
        st.success("Enregistré !")
        st.rerun()
    except Exception as e:
        st.error(f"Erreur lors de l'enregistrement : {e}")

# --- 🍼 REPAS ---
with t_repas:
    df = data_dict["Repas"]
    with st.form("r_f", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", maintenant, key="dr")
        h = col2.time_input("Heure", maintenant.time(), key="hr")
        t = st.selectbox("Type", ["Tétée", "Biberon Infantile", "Biberon Maternel", "Diversification"])
        q = st.number_input("Quantité (ml)", 0, step=10)
        n = st.text_input("Note", key="nr")
        if st.form_submit_button("Enregistrer"):
            new_line = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Quantite": q, "Type": t, "Notes": n}])
            update_and_refresh("Repas", pd.concat([df, new_line], ignore_index=True))
    if not df.empty:
        if st.button("🗑️ Supprimer dernier repas"):
            update_and_refresh("Repas", df.iloc[:-1])

# --- 💊 MÉDOCS ---
with t_medoc:
    df = data_dict["Medicaments"]
    with st.form("m_f", clear_on_submit=True):
        dm = st.date_input("Date", maintenant, key="dm")
        hm = st.time_input("Heure", maintenant.time(), key="hm_m")
        nom = st.text_input("Nom")
        donne = st.checkbox("Donné ?", value=True)
        if st.form_submit_button("Enregistrer"):
            new_line = pd.DataFrame([{"Date": dm.strftime("%d/%m/%Y"), "Heure": hm.strftime("%H:%M"), "Nom": nom, "Donne": "Oui" if donne else "Non"}])
            update_and_refresh("Medicaments", pd.concat([df, new_line], ignore_index=True))
    if not df.empty:
        if st.button("🗑️ Supprimer dernier médicament"):
            update_and_refresh("Medicaments", df.iloc[:-1])

# --- (Appliquer la même logique simplifiée pour Changes, Sommeil, Bain, Santé, Crèche) ---
# Utilisez `df = data_dict["NomDuSheet"]` au début de chaque onglet.

# --- 5. RÉCAPITULATIFS (Utilise les données déjà chargées) ---
st.divider()
st.subheader("📊 Récapitulatif Global")

for label, sheet_name in [("🍼 Repas", "Repas"), ("🧷 Changes", "Changes"), ("😴 Sommeil", "Sommeil"), 
                          ("🛁 Bains", "Bains"), ("💊 Médocs", "Medicaments"), ("🏫 Crèche", "Creche"), ("🩺 Santé", "Sante")]:
    df_display = data_dict[sheet_name]
    if not df_display.empty:
        with st.expander(f"{label} (Derniers enregistrements)", expanded=True):
            st.dataframe(df_display.tail(3), use_container_width=True, hide_index=True)
