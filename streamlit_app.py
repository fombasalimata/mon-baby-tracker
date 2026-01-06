import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Baby Tracker", page_icon="👶", layout="centered")

st.title("👶 Baby Tracker")
st.write("Suivi Partagé - Allaitement Mixte & Santé")

# 2. CONNEXION (Cherche les infos dans les Secrets Streamlit)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

# 3. FONCTION : CALCUL DU TEMPS ÉCOULÉ
def temps_depuis_dernier(df):
    if df is None or df.empty:
        return "Aucun repas enregistré"
    try:
        # On récupère la dernière ligne du tableau
        derniere_ligne = df.iloc[-1]
        dernier_moment = datetime.strptime(f"{derniere_ligne['Date']} {derniere_ligne['Heure']}", "%d/%m/%Y %H:%M")
        diff = datetime.now() - dernier_moment
        
        heures, reste = divmod(int(diff.total_seconds()), 3600)
        minutes, _ = divmod(reste, 60)
        
        if diff.total_seconds() < 0: return "À l'instant"
        return f"{heures}h {minutes}min"
    except:
        return "--"

# 4. INTERFACE PAR ONGLETS
tab1, tab2, tab3 = st.tabs(["🍼 Repas & Tétées", "🧷 Changes", "🩺 Médical"])

# --- ONGLET REPAS ---
with tab1:
    try:
        df_r = conn.read(worksheet="Repas", ttl=0)
        st.info(f"🕒 Dernier repas il y a : **{temps_depuis_dernier(df_r)}**")
    except:
        df_r = pd.DataFrame()

    with st.form("repas_form", clear_on_submit=True):
        col_d, col_h = st.columns(2)
        date_r = col_d.date_input("Date", datetime.now())
        heure_r = col_h.time_input("Heure", datetime.now().time())
        
        type_repas = st.selectbox("Type", ["Tétée (Sein)", "Biberon (Infantile)", "Biberon (Maternel)"])
        quantite = st.number_input("Quantité (ml) - si biberon", min_value=0, value=0, step=10)
        note_r = st.text_input("Note (ex: Sein gauche, a bien tété)")
        
        if st.form_submit_button("Enregistrer le repas"):
            new_row = pd.DataFrame([{
                "Date": date_r.strftime("%d/%m/%Y"),
                "Heure": heure_r.strftime("%H:%M"),
                "Quantite": quantite if "Biberon" in type_repas else "Tétée",
                "Type": type_repas,
                "Notes": note_r
            }])
            updated = pd.concat([df_r, new_row], ignore_index=True)
            conn.update(worksheet="Repas", data=updated)
            st.success("Repas enregistré !")
            st.rerun()

# --- ONGLET CHANGES ---
with tab2:
    try:
        df_c = conn.read(worksheet="Changes", ttl=0)
    except:
        df_c = pd.DataFrame()

    with st.form("change_form", clear_on_submit=True):
        date_c = st.date_input("Date", datetime.now())
        heure_c = st.time_input("Heure", datetime.now().time())
        etat = st.radio("Contenu", ["Urine", "Selles", "Les deux", "Rien"])
        note_c = st.text_input("Observations")
        
        if st.form_submit_button("Enregistrer change"):
            new_row = pd.DataFrame([{
                "Date": date_c.strftime("%d/%m/%Y"),
                "Heure": heure_c.strftime("%H:%M"),
                "Type": etat,
                "Notes": note_c
            }])
            updated = pd.concat([df_c, new_row], ignore_index=True)
            conn.update(worksheet="Changes", data=updated)
            st.success("Change enregistré !")
            st.rerun()

# --- ONGLET SANTÉ ---
with tab3:
    try:
        df_s = conn.read(worksheet="Sante", ttl=0)
    except:
        df_s = pd.DataFrame()

    with st.form("sante_form", clear_on_submit=True):
        date_s = st.date_input("Date RDV", datetime.now())
        poids = st.number_input("Poids (kg)", min_value=0.0, step=0.01, format="%.2f")
        taille = st.number_input("Taille (cm)", min_value=0.0, step=0.5)
        notes_s = st.text_area("Notes médicales")
        
        if st.form_submit_button("Enregistrer santé"):
            new_row = pd.DataFrame([{
                "Date": date_s.strftime("%d/%m/%Y"),
                "Poids": poids,
                "Taille": taille,
                "Notes": notes_s
            }])
            updated = pd.concat([df_s, new_row], ignore_index=True)
            conn.update(worksheet="Sante", data=updated)
            st.success("Données enregistrées !")
            st.rerun()

# --- HISTORIQUE ---
st.divider()
st.subheader("📊 Dernières activités")
if not df_r.empty:
    st.write("**Derniers repas :**")
    st.dataframe(df_r.tail(5), hide_index=True, use_container_width=True)
