import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION
st.set_page_config(page_title="Baby Tracker Pro", page_icon="👶", layout="centered")
st.title("👶 Baby Tracker")

# 2. CONNEXION
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

# 3. ONGLETS
tabs = st.tabs(["🍼 Repas", "🧷 Changes", "😴 Sommeil", "🛁 Bain", "💊 Médocs", "🩺 Santé", "🏫 Crèche"])
t_repas, t_change, t_sommeil, t_bain, t_medoc, t_sante, t_creche = tabs

# --- CHARGEMENT DES DONNÉES ---
try: df_r = conn.read(worksheet="Repas", ttl=0)
except: df_r = pd.DataFrame()
try: df_c = conn.read(worksheet="Changes", ttl=0)
except: df_c = pd.DataFrame()
try: df_so = conn.read(worksheet="Sommeil", ttl=0)
except: df_so = pd.DataFrame()
try: df_b = conn.read(worksheet="Bains", ttl=0)
except: df_b = pd.DataFrame()
try: df_m = conn.read(worksheet="Medicaments", ttl=0)
except: df_m = pd.DataFrame()
try: df_s = conn.read(worksheet="Sante", ttl=0)
except: df_s = pd.DataFrame()
try: df_cr = conn.read(worksheet="Creche", ttl=0)
except: df_cr = pd.DataFrame()

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
            new = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Quantite": q, "Type": t, "Notes": n}])
            conn.update(worksheet="Repas", data=pd.concat([df_r, new], ignore_index=True))
            st.rerun()
    if not df_r.empty:
        if st.button("🗑️ Supprimer dernier repas", key="del_r"):
            conn.update(worksheet="Repas", data=df_r.iloc[:-1]); st.rerun()

# --- 2. CHANGES ---
with t_change:
    with st.form("c_f", clear_on_submit=True):
        dc = st.date_input("Date", datetime.now(), key="dc")
        hc = st.time_input("Heure", datetime.now().time(), key="hc")
        et = st.radio("Contenu", ["Urine", "Selles", "Les deux"], horizontal=True)
        nc = st.text_input("Note change", key="nc")
        if st.form_submit_button("Enregistrer Change"):
            new = pd.DataFrame([{"Date": dc.strftime("%d/%m/%Y"), "Heure": hc.strftime("%H:%M"), "Type": et, "Notes": nc}])
            conn.update(worksheet="Changes", data=pd.concat([df_c, new], ignore_index=True))
            st.rerun()
    if not df_c.empty:
        if st.button("🗑️ Supprimer dernier change", key="del_c"):
            conn.update(worksheet="Changes", data=df_c.iloc[:-1]); st.rerun()

# --- 3. SOMMEIL ---
with t_sommeil:
    with st.form("so_f", clear_on_submit=True):
        dso = st.date_input("Date", datetime.now(), key="dso")
        h_couch = st.time_input("Heure de coucher", key="hso_c")
        h_lev = st.time_input("Heure de lever", key="hso_l")
        nso = st.text_input("Note sommeil", key="nso")
        if st.form_submit_button("Enregistrer Sommeil"):
            t1, t2 = datetime.combine(dso, h_couch), datetime.combine(dso, h_lev)
            diff = t2 - t1
            dur_str = f"{diff.seconds//3600}h{(diff.seconds//60)%60:02d}"
            new = pd.DataFrame([{"Date": dso.strftime("%d/%m/%Y"), "Coucher": h_couch.strftime("%H:%M"), "Lever": h_lev.strftime("%H:%M"), "Duree": dur_str, "Notes": nso}])
            conn.update(worksheet="Sommeil", data=pd.concat([df_so, new], ignore_index=True))
            st.rerun()
    if not df_so.empty:
        if st.button("🗑️ Supprimer dernier sommeil", key="del_so"):
            conn.update(worksheet="Sommeil", data=df_so.iloc[:-1]); st.rerun()

# --- 4. BAIN ---
with t_bain:
    with st.form("b_f", clear_on_submit=True):
        db = st.date_input("Date", datetime.now(), key="db")
        hb = st.time_input("Heure", datetime.now().time(), key="hb")
        tb = st.selectbox("Type", ["Bain classique", "Bain libre", "Toilette"])
        nb = st.text_input("Note bain", key="nb")
        if st.form_submit_button("Enregistrer Bain"):
            new = pd.DataFrame([{"Date": db.strftime("%d/%m/%Y"), "Heure": hb.strftime("%H:%M"), "Type": tb, "Notes": nb}])
            conn.update(worksheet="Bains", data=pd.concat([df_b, new], ignore_index=True))
            st.rerun()
    if not df_b.empty:
        if st.button("🗑️ Supprimer dernier bain", key="del_b"):
            conn.update(worksheet="Bains", data=df_b.iloc[:-1]); st.rerun()

# --- 5. MÉDOCS ---
with t_medoc:
    with st.form("m_f", clear_on_submit=True):
        dm = st.date_input("Date", datetime.now(), key="dm")
        hm = st.time_input("Heure", datetime.now().time(), key="hm_m")
        nom = st.text_input("Médicament")
        donne = st.checkbox("Donné", value=True)
        nm = st.text_input("Note", key="nm")
        if st.form_submit_button("Enregistrer Médoc"):
            new = pd.DataFrame([{"Date": dm.strftime("%d/%m/%Y"), "Heure": hm.strftime("%H:%M"), "Nom": nom, "Donne": "✅ Oui" if donne else "❌ Non", "Notes": nm}])
            conn.update(worksheet="Medicaments", data=pd.concat([df_m, new], ignore_index=True))
            st.rerun()
    if not df_m.empty:
        if st.button("🗑️ Supprimer dernier médicament", key="del_m"):
            conn.update(worksheet="Medicaments", data=df_m.iloc[:-1]); st.rerun()

# --- 6. SANTÉ & GRAPHIQUE ---
with t_sante:
    with st.form("s_f", clear_on_submit=True):
        ds = st.date_input("Date", datetime.now(), key="ds")
        p = st.number_input("Poids (kg)", 0.0, step=0.01)
        ta = st.number_input("Taille (cm)", 0.0, step=0.5)
        te = st.number_input("Température (°C)", 35.0, 41.0, 37.0)
        ns = st.text_input("Note santé", key="ns")
        if st.form_submit_button("Enregistrer Santé"):
            new = pd.DataFrame([{"Date": ds.strftime("%d/%m/%Y"), "Poids": p, "Taille": ta, "Temperature": te, "Notes": ns}])
            conn.update(worksheet="Sante", data=pd.concat([df_s, new], ignore_index=True))
            st.rerun()
    if not df_s.empty:
        if st.button("🗑️ Supprimer dernière santé", key="del_s"):
            conn.update(worksheet="Sante", data=df_s.iloc[:-1]); st.rerun()
    if not df_s.empty and len(df_s) >= 2:
        st.subheader("📈 Courbe de poids")
        df_chart = df_s.copy()
        df_chart['Date'] = pd.to_datetime(df_chart['Date'], format='%d/%m/%Y')
        st.line_chart(df_chart.sort_values('Date').set_index('Date')['Poids'])

# --- 7. CRÈCHE ---
with t_creche:
    with st.form("cr_f", clear_on_submit=True):
        dcr = st.date_input("Journée", datetime.now(), key="dcr")
        ha = st.time_input("Arrivée", key="ha_cr")
        hd = st.time_input("Départ", key="hd_cr")
        ncr = st.text_input("Note crèche", key="ncr")
        if st.form_submit_button("Enregistrer Crèche"):
            t1, t2 = datetime.combine(dcr, ha), datetime.combine(dcr, hd)
            dur = t2 - t1
            dur_str = f"{dur.seconds//3600}h{(dur.seconds//60)%60:02d}"
            new = pd.DataFrame([{"Date": dcr.strftime("%d/%m/%Y"), "Arrivee": ha.strftime("%H:%M"), "Depart": hd.strftime("%H:%M"), "Duree": dur_str, "Notes": ncr}])
            conn.update(worksheet="Creche", data=pd.concat([df_cr, new], ignore_index=True))
            st.rerun()
    if not df_cr.empty:
        if st.button("🗑️ Supprimer dernière crèche", key="del_cr"):
            conn.update(worksheet="Creche", data=df_cr.iloc[:-1]); st.rerun()

# --- RÉCAPITULATIF GLOBAL (TABLEAUX DÉTAILLÉS) ---
st.divider()
st.subheader("📊 Récapitulatif Global")

if not df_r.empty:
    st.write("**🍼 Repas (3 derniers)**")
    r_disp = df_r.tail(3).copy()
    r_disp['Quantite'] = r_disp['Quantite'].astype(str) + " ml"
    st.dataframe(r_disp, use_container_width=True, hide_index=True)

if not df_c.empty:
    st.write("**🧷 Changes (3 derniers)**")
    st.dataframe(df_c.tail(3), use_container_width=True, hide_index=True)

if not df_so.empty:
    st.write("**😴 Sommeil (3 derniers)**")
    st.dataframe(df_so.tail(3), use_container_width=True, hide_index=True)

if not df_b.empty:
    st.write("**🛁 Bains (3 derniers)**")
    st.dataframe(df_b.tail(3), use_container_width=True, hide_index=True)

if not df_m.empty:
    st.write("**💊 Médicaments (3 derniers)**")
    st.dataframe(df_m.tail(3), use_container_width=True, hide_index=True)

if not df_cr.empty:
    st.write("**🏫 Crèche (3 derniers)**")
    st.dataframe(df_cr.tail(3), use_container_width=True, hide_index=True)

if not df_s.empty:
    st.write("**🩺 Santé (3 derniers)**")
    s_disp = df_s.tail(3).copy()
    if 'Poids' in s_disp.columns: s_disp['Poids'] = s_disp['Poids'].astype(str) + " kg"
    if 'Taille' in s_disp.columns: s_disp['Taille'] = s_disp['Taille'].astype(str) + " cm"
    if 'Temperature' in s_disp.columns: s_disp['Temperature'] = s_disp['Temperature'].astype(str) + " °C"
    st.dataframe(s_disp, use_container_width=True, hide_index=True)
