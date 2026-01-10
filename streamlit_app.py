import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

# 1. CONFIGURATION & FUSEAU HORAIRE
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

# 3. FONCTION DE LECTURE (SÉCURISÉE & SANS CACHE)
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

# --- 🍼 REPAS ---
with t_repas:
    with st.form("r_f", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", maintenant, key="dr")
        h = col2.time_input("Heure", maintenant.time(), key="hr")
        t = st.selectbox("Type", ["Tétée", "Biberon Infantile", "Biberon Maternel", "Diversification"])
        q = st.number_input("Quantité (ml)", 0, step=10)
        n = st.text_input("Note", key="nr")
        if st.form_submit_button("Enregistrer Repas"):
            new_line = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Quantite": q, "Type": t, "Notes": n}])
            updated = pd.concat([df_r, new_line], ignore_index=True)
            conn.update(worksheet="Repas", data=updated)
            st.rerun()

# --- 🧷 CHANGES ---
with t_change:
    with st.form("c_f", clear_on_submit=True):
        dc = st.date_input("Date", maintenant, key="dc")
        hc = st.time_input("Heure", maintenant.time(), key="hc")
        et = st.radio("Contenu", ["Urine", "Selles", "Les deux"], horizontal=True)
        nc = st.text_input("Note change", key="nc")
        if st.form_submit_button("Enregistrer Change"):
            new_line = pd.DataFrame([{"Date": dc.strftime("%d/%m/%Y"), "Heure": hc.strftime("%H:%M"), "Type": et, "Notes": nc}])
            updated = pd.concat([df_c, new_line], ignore_index=True)
            conn.update(worksheet="Changes", data=updated)
            st.rerun()

# --- 😴 SOMMEIL ---
with t_sommeil:
    with st.form("so_f", clear_on_submit=True):
        dso = st.date_input("Date", maintenant, key="dso")
        h_couch = st.time_input("Coucher", maintenant.time(), key="h_c")
        h_lev = st.time_input("Lever", maintenant.time(), key="h_l")
        nso = st.text_input("Note", key="nso")
        if st.form_submit_button("Enregistrer Sommeil"):
            t1, t2 = datetime.combine(dso, h_couch), datetime.combine(dso, h_lev)
            diff = t2 - t1
            dur_str = f"{diff.seconds//3600}h{(diff.seconds//60)%60:02d}"
            new_line = pd.DataFrame([{"Date": dso.strftime("%d/%m/%Y"), "Coucher": h_couch.strftime("%H:%M"), "Lever": h_lev.strftime("%H:%M"), "Duree": dur_str, "Notes": nso}])
            updated = pd.concat([df_so, new_line], ignore_index=True)
            conn.update(worksheet="Sommeil", data=updated)
            st.rerun()

# --- 🛁 BAIN ---
with t_bain:
    with st.form("b_f", clear_on_submit=True):
        db = st.date_input("Date", maintenant, key="db")
        hb = st.time_input("Heure", maintenant.time(), key="hb")
        tb = st.selectbox("Type", ["Bain", "Toilette"])
        nb = st.text_input("Note", key="nb")
        if st.form_submit_button("Enregistrer Bain"):
            new_line = pd.DataFrame([{"Date": db.strftime("%d/%m/%Y"), "Heure": hb.strftime("%H:%M"), "Type": tb, "Notes": nb}])
            updated = pd.concat([df_b, new_line], ignore_index=True)
            conn.update(worksheet="Bains", data=updated)
            st.rerun()

# --- 💊 MÉDOCS ---
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
            updated = pd.concat([df_m, new_line], ignore_index=True)
            conn.update(worksheet="Medicaments", data=updated)
            st.rerun()

# --- 🩺 SANTÉ ---
with t_sante:
    with st.form("s_f", clear_on_submit=True):
        ds = st.date_input("Date", maintenant, key="ds")
        p = st.number_input("Poids (kg)", 0.0, step=0.01)
        te = st.number_input("Température (°C)", 35.0, 41.0, 37.0)
        ns = st.text_input("Note", key="ns")
        if st.form_submit_button("Enregistrer"):
            new_line = pd.DataFrame([{"Date": ds.strftime("%d/%m/%Y"), "Poids": p, "Temperature": te, "Notes": ns}])
            updated = pd.concat([df_s, new_line], ignore_index=True)
            conn.update(worksheet="Sante", data=updated)
            st.rerun()

# --- 🏫 CRÈCHE ---
with t_creche:
    with st.form("cr_f", clear_on_submit=True):
        dcr = st.date_input("Date", maintenant, key="dcr")
        ha = st.time_input("Arrivée", maintenant.time(), key="ha")
        hd = st.time_input("Départ", maintenant.time(), key="hd")
        ncr = st.text_input("Note", key="ncr")
        if st.form_submit_button("Enregistrer"):
            t1, t2 = datetime.combine(dcr, ha), datetime.combine(dcr, hd)
            dur = t2 - t1
            dur_str = f"{dur.seconds//3600}h{(dur.seconds//60)%60:02d}"
            new_line = pd.DataFrame([{"Date": dcr.strftime("%d/%m/%Y"), "Arrivee": ha.strftime("%H:%M"), "Depart": hd.strftime("%H:%M"), "Duree": dur_str, "Notes": ncr}])
            updated = pd.concat([df_cr, new_line], ignore_index=True)
            conn.update(worksheet="Creche", data=updated)
            st.rerun()

# --- 5. RÉCAPITULATIFS (Anti-disparition) ---
st.divider()
st.subheader("📊 Récapitulatif Global")

categories = [
    ("🍼 Repas", "Repas"), ("🧷 Changes", "Changes"), ("😴 Sommeil", "Sommeil"),
    ("🛁 Bains", "Bains"), ("💊 Médocs", "Medicaments"), ("🏫 Crèche", "Creche"), ("🩺 Santé", "Sante")
]

for label, sheet_name in categories:
    # On recharge ici pour s'assurer que l'affichage est synchro
    df_final = load_sheet_safe(sheet_name)
    if not df_final.empty:
        with st.expander(f"{label} (Derniers enregistrements)", expanded=True):
            st.dataframe(df_final.tail(3), use_container_width=True, hide_index=True)
