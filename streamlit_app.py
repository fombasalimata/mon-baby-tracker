import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Baby Tracker Pro", page_icon="👶", layout="centered")
st.title("👶 Baby Tracker")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

tabs = st.tabs(["🍼 Repas", "🧷 Changes", "💊 Médocs", "🩺 Santé", "🏫 Crèche"])
t_repas, t_change, t_medoc, t_sante, t_creche = tabs

# --- 1. REPAS ---
with t_repas:
    try: df_r = conn.read(worksheet="Repas", ttl=0)
    except: df_r = pd.DataFrame()
    with st.form("r_f", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", datetime.now(), key="dr")
        h = col2.time_input("Heure", datetime.now().time(), key="hr")
        t = st.selectbox("Type", ["Tétée", "Biberon Infantile", "Biberon Maternel", "Diversification"])
        q = st.number_input("Quantité (ml)", 0, step=10)
        if st.form_submit_button("Enregistrer Repas"):
            new = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Quantite": q, "Type": t}])
            conn.update(worksheet="Repas", data=pd.concat([df_r, new], ignore_index=True))
            st.rerun()

# --- 2. CHANGES ---
with t_change:
    try: df_c = conn.read(worksheet="Changes", ttl=0)
    except: df_c = pd.DataFrame()
    with st.form("c_f", clear_on_submit=True):
        dc = st.date_input("Date", datetime.now(), key="dc")
        hc = st.time_input("Heure", datetime.now().time(), key="hc")
        et = st.radio("Contenu", ["Urine", "Selles", "Les deux"])
        if st.form_submit_button("Enregistrer Change"):
            new = pd.DataFrame([{"Date": dc.strftime("%d/%m/%Y"), "Heure": hc.strftime("%H:%M"), "Type": et}])
            conn.update(worksheet="Changes", data=pd.concat([df_c, new], ignore_index=True))
            st.rerun()

# --- 3. MÉDOCS ---
with t_medoc:
    try: df_m = conn.read(worksheet="Medicaments", ttl=0)
    except: df_m = pd.DataFrame()
    with st.form("m_f", clear_on_submit=True):
        dm = st.date_input("Date", datetime.now(), key="dm")
        nom = st.text_input("Médicament")
        donne = st.checkbox("Donné", value=True)
        if st.form_submit_button("Enregistrer Médoc"):
            new = pd.DataFrame([{"Date": dm.strftime("%d/%m/%Y"), "Nom": nom, "Donne": "✅ Oui" if donne else "❌ Non"}])
            conn.update(worksheet="Medicaments", data=pd.concat([df_m, new], ignore_index=True))
            st.rerun()

# --- 4. SANTÉ & GRAPHIQUE ---
with t_sante:
    try: df_s = conn.read(worksheet="Sante", ttl=0)
    except: df_s = pd.DataFrame()

    with st.form("s_f", clear_on_submit=True):
        ds = st.date_input("Date", datetime.now(), key="ds")
        p = st.number_input("Poids (kg)", 0.0, step=0.01, format="%.2f")
        ta = st.number_input("Taille (cm)", 0.0, step=0.5)
        te = st.number_input("Température (°C)", 35.0, 41.0, 37.0, step=0.1)
        if st.form_submit_button("Enregistrer Santé"):
            new = pd.DataFrame([{"Date": ds.strftime("%d/%m/%Y"), "Poids": p, "Taille": ta, "Temperature": te}])
            conn.update(worksheet="Sante", data=pd.concat([df_s, new], ignore_index=True))
            st.rerun()

    # SECTION GRAPHIQUE DE POIDS
    if not df_s.empty and len(df_s) > 1:
        st.subheader("📈 Courbe de poids")
        try:
            # Préparation des données pour le graphique
            df_chart = df_s.copy()
            df_chart['Date'] = pd.to_datetime(df_chart['Date'], format='%d/%m/%Y')
            df_chart = df_chart.sort_values('Date')
            
            # Affichage du graphique
            st.line_chart(df_chart.set_index('Date')['Poids'])
        except Exception as e:
            st.info("Ajoutez quelques mesures de poids pour voir la courbe apparaître.")

# --- 5. CRÈCHE ---
with t_creche:
    try: df_cr = conn.read(worksheet="Creche", ttl=0)
    except: df_cr = pd.DataFrame()
    with st.form("cr_f", clear_on_submit=True):
        dcr = st.date_input("Journée", datetime.now())
        ha = st.time_input("Arrivée")
        hd = st.time_input("Départ")
        if st.form_submit_button("Enregistrer Crèche"):
            t1, t2 = datetime.combine(dcr, ha), datetime.combine(dcr, hd)
            dur = t2 - t1
            dur_str = f"{dur.seconds//3600}h{(dur.seconds//60)%60:02d}"
            new = pd.DataFrame([{"Date": dcr.strftime("%d/%m/%Y"), "Arrivee": ha.strftime("%H:%M"), "Depart": hd.strftime("%H:%M"), "Duree": dur_str}])
            conn.update(worksheet="Creche", data=pd.concat([df_cr, new], ignore_index=True))
            st.rerun()

# --- RÉCAPITULATIF FINAL ---
st.divider()
st.subheader("📊 Récapitulatif Global")

if not df_r.empty:
    st.write("**🍼 Repas**")
    r_disp = df_r.tail(3).copy()
    r_disp['Quantite'] = r_disp['Quantite'].astype(str) + " ml"
    st.dataframe(r_disp, use_container_width=True, hide_index=True)

if not df_m.empty:
    st.write("**💊 Médicaments**")
    st.dataframe(df_m.tail(3), use_container_width=True, hide_index=True)

if not df_cr.empty:
    st.write("**🏫 Crèche**")
    st.dataframe(df_cr.tail(3)[['Date', 'Arrivee', 'Depart', 'Duree']], use_container_width=True, hide_index=True)

if not df_s.empty:
    st.write("**🩺 Santé**")
    s_disp = df_s.tail(3).copy()
    s_disp['Poids'] = s_disp['Poids'].astype(str) + " kg"
    s_disp['Temperature'] = s_disp['Temperature'].astype(str) + " °C"
    st.dataframe(s_disp[['Date', 'Poids', 'Temperature']], use_container_width=True, hide_index=True)
