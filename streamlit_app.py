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
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. CHARGEMENT GLOBAL OPTIMISÉ (Une seule fonction pour tout lire)
@st.cache_data(ttl="5s") # On garde en mémoire 5 secondes pour économiser les quotas
def get_all_data():
    sheets = ["Repas", "Changes", "Sommeil", "Bains", "Medicaments", "Sante", "Creche"]
    all_dfs = {}
    for s in sheets:
        try:
            # On lit chaque feuille
            df = conn.read(worksheet=s, ttl=0)
            all_dfs[s] = df if df is not None else pd.DataFrame()
        except:
            all_dfs[s] = pd.DataFrame()
    return all_dfs

# On récupère tout le dictionnaire de données
try:
    data = get_all_data()
except:
    st.error("Google Sheets sature. Attends 30 secondes sans rafraîchir la page.")
    st.stop()

# 4. ONGLETS
tabs = st.tabs(["🍼 Repas", "🧷 Changes", "😴 Sommeil", "🛁 Bain", "💊 Médocs", "🩺 Santé", "🏫 Crèche"])
t_repas, t_change, t_sommeil, t_bain, t_medoc, t_sante, t_creche = tabs

# FONCTION D'ENREGISTREMENT SÉCURISÉE
def save_data(sheet_name, updated_df):
    try:
        conn.update(worksheet=sheet_name, data=updated_df)
        st.cache_data.clear() # On vide le cache pour forcer la lecture au prochain tour
        st.success("Enregistré avec succès !")
        st.rerun()
    except Exception as e:
        if "429" in str(e):
            st.error("Quota Google atteint. Attends 1 minute avant de réessayer.")
        else:
            st.error(f"Erreur : {e}")

# --- 🍼 REPAS ---
with t_repas:
    df_r = data["Repas"]
    with st.form("r_f", clear_on_submit=True):
        d = st.date_input("Date", maintenant)
        h = st.time_input("Heure", maintenant.time())
        t = st.selectbox("Type", ["Tétée", "Biberon Infantile", "Biberon Maternel", "Diversification"])
        q = st.number_input("Quantité (ml)", 0, step=10)
        if st.form_submit_button("Enregistrer"):
            new = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Quantite": q, "Type": t}])
            save_data("Repas", pd.concat([df_r, new], ignore_index=True))
    if not df_r.empty and st.button("🗑️ Supprimer dernier", key="del_r"):
        save_data("Repas", df_r.iloc[:-1])

# --- 🧷 CHANGES ---
with t_change:
    df_c = data["Changes"]
    with st.form("c_f", clear_on_submit=True):
        dc = st.date_input("Date", maintenant)
        hc = st.time_input("Heure", maintenant.time())
        et = st.radio("Contenu", ["Urine", "Selles", "Les deux"], horizontal=True)
        if st.form_submit_button("Enregistrer Change"):
            new = pd.DataFrame([{"Date": dc.strftime("%d/%m/%Y"), "Heure": hc.strftime("%H:%M"), "Type": et}])
            save_data("Changes", pd.concat([df_c, new], ignore_index=True))
    if not df_c.empty and st.button("🗑️ Supprimer dernier", key="del_c"):
        save_data("Changes", df_c.iloc[:-1])

# --- 😴 SOMMEIL ---
with t_sommeil:
    df_so = data["Sommeil"]
    with st.form("so_f", clear_on_submit=True):
        dso = st.date_input("Date", maintenant)
        h1 = st.time_input("Coucher", maintenant.time())
        h2 = st.time_input("Lever", maintenant.time())
        if st.form_submit_button("Enregistrer"):
            diff = datetime.combine(dso, h2) - datetime.combine(dso, h1)
            dur = f"{diff.seconds//3600}h{(diff.seconds//60)%60:02d}"
            new = pd.DataFrame([{"Date": dso.strftime("%d/%m/%Y"), "Coucher": h1.strftime("%H:%M"), "Lever": h2.strftime("%H:%M"), "Duree": dur}])
            save_data("Sommeil", pd.concat([df_so, new], ignore_index=True))
    if not df_so.empty and st.button("🗑️ Supprimer dernier", key="del_so"):
        save_data("Sommeil", df_so.iloc[:-1])

# --- 🛁 BAIN ---
with t_bain:
    df_b = data["Bains"]
    with st.form("b_f", clear_on_submit=True):
        db = st.date_input("Date", maintenant)
        tb = st.selectbox("Type", ["Bain", "Toilette"])
        if st.form_submit_button("Enregistrer"):
            new = pd.DataFrame([{"Date": db.strftime("%d/%m/%Y"), "Type": tb}])
            save_data("Bains", pd.concat([df_b, new], ignore_index=True))
    if not df_b.empty and st.button("🗑️ Supprimer dernier", key="del_b"):
        save_data("Bains", df_b.iloc[:-1])

# --- 💊 MÉDOCS ---
with t_medoc:
    df_m = data["Medicaments"]
    with st.form("m_f", clear_on_submit=True):
        dm = st.date_input("Date", maintenant)
        nom = st.text_input("Médicament")
        donne = st.checkbox("Donné ?", value=True)
        if st.form_submit_button("Enregistrer"):
            new = pd.DataFrame([{"Date": dm.strftime("%d/%m/%Y"), "Nom": nom, "Donne": "Oui" if donne else "Non"}])
            save_data("Medicaments", pd.concat([df_m, new], ignore_index=True))
    if not df_m.empty and st.button("🗑️ Supprimer dernier", key="del_m"):
        save_data("Medicaments", df_m.iloc[:-1])

# --- 🩺 SANTÉ ---
with t_sante:
    df_s = data["Sante"]
    with st.form("s_f", clear_on_submit=True):
        ds = st.date_input("Date", maintenant)
        p = st.number_input("Poids (kg)", 0.0, step=0.01)
        te = st.number_input("Température (°C)", 35.0, 41.0, 37.0)
        if st.form_submit_button("Enregistrer"):
            new = pd.DataFrame([{"Date": ds.strftime("%d/%m/%Y"), "Poids": p, "Temperature": te}])
            save_data("Sante", pd.concat([df_s, new], ignore_index=True))
    if not df_s.empty and st.button("🗑️ Supprimer dernier", key="del_s"):
        save_data("Sante", df_s.iloc[:-1])

# --- 🏫 CRÈCHE ---
with t_creche:
    df_cr = data["Creche"]
    with st.form("cr_f", clear_on_submit=True):
        dcr = st.date_input("Date", maintenant)
        ha = st.time_input("Arrivée", maintenant.time())
        hd = st.time_input("Départ", maintenant.time())
        if st.form_submit_button("Enregistrer"):
            new = pd.DataFrame([{"Date": dcr.strftime("%d/%m/%Y"), "Arrivee": ha.strftime("%H:%M"), "Depart": hd.strftime("%H:%M")}])
            save_data("Creche", pd.concat([df_cr, new], ignore_index=True))
    if not df_cr.empty and st.button("🗑️ Supprimer dernier", key="del_cr"):
        save_data("Creche", df_cr.iloc[:-1])

# --- 5. RÉCAPITULATIFS (Affiche les données déjà chargées) ---
st.divider()
st.subheader("📊 Dernières activités")
for label, s_name in [("🍼 Repas", "Repas"), ("🧷 Changes", "Changes"), ("😴 Sommeil", "Sommeil"), ("💊 Médocs", "Medicaments")]:
    df_disp = data[s_name]
    if not df_disp.empty:
        st.write(f"**{label}**")
        st.dataframe(df_disp.tail(3), use_container_width=True, hide_index=True)
