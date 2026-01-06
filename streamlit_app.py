import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Baby Tracker", page_icon="👶")
st.title("👶 Baby Tracker Simple")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de configuration : {e}")
    st.stop()

# Onglets
tab1, tab2 = st.tabs(["🍼 Repas", "🧷 Changes"])

with tab1:
    try:
        df_r = conn.read(worksheet="Repas", ttl=0)
    except:
        df_r = pd.DataFrame()

    with st.form("repas_form"):
        d = st.date_input("Date", datetime.now())
        h = st.time_input("Heure", datetime.now().time())
        t = st.selectbox("Type", ["Tétée", "Biberon"])
        q = st.number_input("ML (si biberon)", 0)
        
        if st.form_submit_button("Enregistrer"):
            new_row = pd.DataFrame([{"Date": d.strftime("%d/%m/%Y"), "Heure": h.strftime("%H:%M"), "Quantite": q, "Type": t}])
            # On ajoute la ligne au tableau existant
            updated = pd.concat([df_r, new_row], ignore_index=True)
            conn.update(worksheet="Repas", data=updated)
            st.success("Enregistré !")
            st.rerun()

with tab2:
    try:
        df_c = conn.read(worksheet="Changes", ttl=0)
    except:
        df_c = pd.DataFrame()

    with st.form("change_form"):
        d_c = st.date_input("Date ", datetime.now())
        h_c = st.time_input("Heure ", datetime.now().time())
        etat = st.radio("Type", ["Urine", "Selles", "Les deux"])
        
        if st.form_submit_button("Enregistrer Change"):
            new_row_c = pd.DataFrame([{"Date": d_c.strftime("%d/%m/%Y"), "Heure": h_c.strftime("%H:%M"), "Type": etat}])
            conn.update(worksheet="Changes", data=pd.concat([df_c, new_row_c], ignore_index=True))
            st.success("Change noté !")
            st.rerun()

st.divider()
st.subheader("📊 Historique")
if not df_r.empty:
    st.dataframe(df_r.tail(5), use_container_width=True)
