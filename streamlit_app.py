import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION
st.set_page_config(page_title="Baby Tracker Pro", page_icon="👶", layout="centered")
st.title("👶 Baby Tracker")

# 2. CONNEXION SÉCURISÉE
try:
    # On crée la connexion
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

# 3. FONCTION DE LECTURE SANS CACHE (Pour éviter les données fantômes)
def load_sheet(name):
    try:
        # ttl=0 est CRUCIAL : il force Streamlit à relire le fichier réellement
        return conn.read(worksheet=name, ttl=0)
    except:
        return pd.DataFrame()

# Chargement immédiat des données
df_r = load_sheet("Repas")
df_c = load_sheet("Changes")
df_so = load_sheet("Sommeil")
df_b = load_sheet("Bains")
df_m = load_sheet("Medicaments")
df_s = load_sheet("Sante")
df_cr = load_sheet("Creche")

# 4. ONGLETS
tabs = st.tabs(["🍼 Repas", "🧷 Changes", "😴 Sommeil", "🛁 Bain", "💊 Médocs", "🩺 Santé", "🏫 Crèche"])
t_repas, t_change, t_sommeil, t_bain, t_medoc, t_sante, t_creche = tabs

# --- 1. REPAS ---
with t_repas:
    with st.form("r_f", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", datetime.now(), key="dr")
        h = col2.time_input("Heure", datetime.now().time(), key="hr")
        t = st.selectbox("Type", ["Tétée", "Biberon Infantile", "Biberon Maternel", "Diversification"])
        q = st.number_input("Quantité (ml)", 0, step=10)
        n = st.text_input("Note", key="nr")
        if st.form_submit_button("Enregistrer Repas"):
            new_line = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Quantite": q, "Type": t, "Notes": n}])
            updated = pd.concat([df_r, new_line], ignore_index=True)
            conn.update(worksheet="Repas", data=updated)
            st.success("Enregistré !")
            st.rerun()
    if not df_r.empty:
        if st.button("🗑️ Supprimer dernier", key="del_r"):
            conn.update(worksheet="Repas", data=df_r.iloc[:-1])
            st.rerun()

# --- 2. CHANGES ---
with t_change:
    with st.form("c_f", clear_on_submit=True):
        dc = st.date_input("Date", datetime.now(), key="dc")
        hc = st.time_input("Heure", datetime.now().time(), key="hc")
        et = st.radio("Contenu", ["Urine", "Selles", "Les deux"], horizontal=True)
        nc = st.text_input("Note change", key="nc")
        if st.form_submit_button("Enregistrer Change"):
            new_line = pd.DataFrame([{"Date": dc.strftime("%d/%m/%Y"), "Heure": hc.strftime("%H:%M"), "Type": et, "Notes": nc}])
            updated = pd.concat([df_c, new_line], ignore_index=True)
            conn.update(worksheet="Changes", data=updated)
            st.rerun()
    if not df_c.empty:
        if st.button("🗑️ Supprimer dernier", key="del_c"):
            conn.update(worksheet="Changes", data=df_c.iloc[:-1])
            st.rerun()

# --- 3. SOMMEIL ---
with t_sommeil:
    with st.form("so_f", clear_on_submit=True):
        dso = st.date_input("Date", datetime.now(), key="dso")
        h_couch = st.time_input("Coucher", key="h_c")
        h_lev = st.time_input("Lever", key="h_l")
        nso = st.text_input("Note", key="nso")
        if st.form_submit_button("Enregistrer Sommeil"):
            t1, t2 = datetime.combine(dso, h_couch), datetime.combine(dso, h_lev)
            diff = t2 - t1
            dur_str = f"{diff.seconds//3600}h{(diff.seconds//60)%60:02d}"
            new_line = pd.DataFrame([{"Date": dso.strftime("%d/%m/%Y"), "Coucher": h_couch.strftime("%H:%M"), "Lever": h_lev.strftime("%H:%M"), "Duree": dur_str, "Notes": nso}])
            updated = pd.concat([df_so, new_line], ignore_index=True)
            conn.update(worksheet="Sommeil", data=updated)
            st.rerun()
    if not df_so.empty:
        if st.button("🗑️ Supprimer dernier", key="del_so"):
            conn.update(worksheet="Sommeil", data=df_so.iloc[:-1])
            st.rerun()

# --- 4. BAIN ---
with t_bain:
    with st.form("b_f", clear_on_submit=True):
        db = st.date_input("Date", datetime.now(), key="db")
        hb = st.time_input("Heure", datetime.now().time(), key="hb")
        tb = st.selectbox("Type", ["Bain", "Toilette"])
        nb = st.text_input("Note", key="nb")
        if st.form_submit_button("Enregistrer Bain"):
            new_line = pd.DataFrame([{"Date": db.strftime("%d/%m/%Y"), "Heure": hb.strftime("%H:%M"), "Type": tb, "Notes": nb}])
            updated = pd.concat([df_b, new_line], ignore_index=True)
            conn.update(worksheet="Bains", data=updated)
            st.rerun()
    if not df_b.empty:
        if st.button("🗑️ Supprimer dernier", key="del_b"):
            conn.update(worksheet="Bains", data=df_b.iloc[:-1])
            st.rerun()

# --- 5. MÉDOCS ---
with t_medoc:
    with st.form("m_f", clear_on_submit=True):
        dm = st.date_input("Date", datetime.now(), key="dm")
        hm_m = st.time_input("Heure", key="hm_m")
        nom = st.text_input("Nom")
        nm = st.text_input("Note", key="nm")
        if st.form_submit_button("Enregistrer"):
            new_line = pd.DataFrame([{"Date": dm.strftime("%d/%m/%Y"), "Heure": hm_m.strftime("%H:%M"), "Nom": nom, "Notes": nm}])
            updated = pd.concat([df_m, new_line], ignore_index=True)
            conn.update(worksheet="Medicaments", data=updated)
            st.rerun()
    if not df_m.empty:
        if st.button("🗑️ Supprimer dernier", key="del_m"):
            conn.update(worksheet="Medicaments", data=df_m.iloc[:-1])
            st.rerun()

# --- 6. SANTÉ ---
with t_sante:
    with st.form("s_f", clear_on_submit=True):
        ds = st.date_input("Date", datetime.now(), key="ds")
        p = st.number_input("Poids (kg)", 0.0, step=0.01)
        te = st.number_input("Température (°C)", 35.0, 41.0, 37.0)
        ns = st.text_input("Note", key="ns")
        if st.form_submit_button("Enregistrer"):
            new_line = pd.DataFrame([{"Date": ds.strftime("%d/%m/%Y"), "Poids": p, "Temperature": te, "Notes": ns}])
            updated = pd.concat([df_s, new_line], ignore_index=True)
            conn.update(worksheet="Sante", data=updated)
            st.rerun()
    if not df_s.empty:
        if st.button("🗑️ Supprimer dernier", key="del_s"):
            conn.update(worksheet="Sante", data=df_s.iloc[:-1])
            st.rerun()

# --- 7. CRÈCHE ---
with t_creche:
    with st.form("cr_f", clear_on_submit=True):
        dcr = st.date_input("Date", datetime.now(), key="dcr")
        ha = st.time_input("Arrivée", key="ha")
        hd = st.time_input("Départ", key="hd")
        ncr = st.text_input("Note", key="ncr")
        if st.form_submit_button("Enregistrer"):
            t1, t2 = datetime.combine(dcr, ha), datetime.combine(dcr, hd)
            dur = t2 - t1
            dur_str = f"{dur.seconds//3600}h{(dur.seconds//60)%60:02d}"
            new_line = pd.DataFrame([{"Date": dcr.strftime("%d/%m/%Y"), "Arrivee": ha.strftime("%H:%M"), "Depart": hd.strftime("%H:%M"), "Duree": dur_str, "Notes": ncr}])
            updated = pd.concat([df_cr, new_line], ignore_index=True)
            conn.update(worksheet="Creche", data=updated)
            st.rerun()
    if not df_cr.empty:
        if st.button("🗑️ Supprimer dernier", key="del_cr"):
            conn.update(worksheet="Creche", data=df_cr.iloc[:-1])
            st.rerun()

# --- RÉCAPITULATIF (AVEC DONNÉES FRAICHES) ---
st.divider()
st.subheader("📊 Récapitulatif Global")

# On affiche les 3 derniers pour chaque catégorie
for label, data in [("🍼 Repas", df_r), ("🧷 Changes", df_c), ("😴 Sommeil", df_so), 
                    ("🛁 Bains", df_b), ("💊 Médocs", df_m), ("🏫 Crèche", df_cr), ("🩺 Santé", df_s)]:
    if not data.empty:
        st.write(f"**{label}**")
        st.dataframe(data.tail(3), use_container_width=True, hide_index=True)
