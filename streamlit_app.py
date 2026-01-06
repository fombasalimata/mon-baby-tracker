import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Baby Tracker", page_icon="👶", layout="centered")

st.title("👶 Baby Tracker")
st.write("Suivi Allaitement Mixte & Santé")

# 2. CONNEXION (Cherche les infos dans les Secrets Streamlit Cloud)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de configuration : {e}")
    st.stop()

# 3. FONCTION : CALCUL DU TEMPS ÉCOULÉ
def temps_depuis_dernier(df):
    if df is None or df.empty:
        return "Aucun repas enregistré"
    try:
        if 'Date' in df.columns and 'Heure' in df.columns:
            derniere_ligne = df.iloc[-1]
            dernier_moment = datetime.strptime(f"{derniere_ligne['Date']} {derniere_ligne['Heure']}", "%d/%m/%Y %H:%M")
            diff = datetime.now() - dernier_moment
            h, reste = divmod(int(diff.total_seconds()), 3600)
            m, _ = divmod(reste, 60)
            return f"{h}h {m}min"
    except:
        return "--"
    return "--"

# 4. INTERFACE PAR ONGLETS
tab1, tab2, tab3 = st.tabs(["🍼 Repas & Tétées", "🧷 Changes", "🩺 Médical"])

# --- ONGLET REPAS ---
with tab1:
    try:
        df_r = conn.read(worksheet="Repas", ttl=0)
        st.info(f"🕒 Dernier repas il y a : **{temps_depuis_dernier(df_r)}**")
    except Exception as e:
        st.warning("Impossible de lire l'historique des repas. Vérifiez vos Secrets.")
        df_r = pd.DataFrame()

    with st.form("repas_form", clear_on_submit=True):
        col_d, col_h = st.columns(2)
        date_r = col_d.date_input("Date", datetime.now())
        heure_r = col_h.time_input("Heure", datetime.now().time())
        type_repas = st.selectbox("Type", ["Tétée (Sein)", "Biberon (Infantile)", "Biberon (Maternel)"])
        quantite = st.number_input("Quantité (ml) - si biberon", min_value=0, value=0, step=10)
        note_r = st.text_input("Note (ex: Sein gauche, a bien bu)")
        
        if st.form_submit_button("Enregistrer le repas"):
            try:
                new_row = pd.DataFrame([{
                    "Date": date_r.strftime("%d/%m/%Y"),
                    "Heure": heure_r.strftime("%H:%M"),
                    "Quantite": quantite if "Biberon" in type_repas else "Tétée",
                    "Type": type_repas,
                    "Notes": note_r
                }])
                updated_df = pd.concat([df_r, new_row], ignore_index=True)
                conn.update(worksheet="Repas", data=updated_df)
                st.success("Repas enregistré sur Google Sheets !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur d'enregistrement : {e}")

# --- ONGLET CHANGES ---
with tab2:
    try:
        df_c = conn.read(worksheet="Changes", ttl=0)
    except:
        df_c = pd.DataFrame()

    with st.form("change_form", clear_on_submit=True):
        d_c = st.date_input("Date", datetime.now())
        h_c = st.time_input("Heure", datetime.now().time())
        etat = st.radio("Contenu", ["Urine", "Selles", "Les deux", "Rien"])
        note_c = st.text_input("Observations")
        
        if st.form_submit_button("Enregistrer change"):
            try:
                new_row_c = pd.DataFrame([{"Date": d_c.strftime("%d/%m/%Y"), "Heure": h_c.strftime("%H:%M"), "Type": etat, "Notes": note_c}])
                conn.update(worksheet="Changes", data=pd.concat([df_c, new_row_c], ignore_index=True))
                st.success("Change enregistré !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

# --- ONGLET SANTÉ ---
with tab3:
    try:
        df_s = conn.read(worksheet="Sante", ttl=0)
    except:
        df_s = pd.DataFrame()

    with st.form("sante_form", clear_on_submit=True):
        d_s = st.date_input("Date RDV", datetime.now())
        poids = st.number_input("Poids (kg)", min_value=0.0, step=0.01, format="%.2f")
        taille = st.number_input("Taille (cm)", min_value=0.0, step=0.5)
        if st.form_submit_button("Enregistrer santé"):
            try:
                new_row_s = pd.DataFrame([{"Date": d_s.strftime("%d/%m/%Y"), "Poids": poids, "Taille": taille}])
                conn.update(worksheet="Sante", data=pd.concat([df_s, new_row_s], ignore_index=True))
                st.success("Données enregistrées !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

# --- 5. HISTORIQUE BAS DE PAGE ---
st.divider()
st.subheader("📊 Dernières activités")
if not df_r.empty:
    st.write("**Derniers repas :**")
    st.dataframe(df_r.tail(5), hide_index=True, use_container_width=True)
elif 'df_r' in locals():
    st.write("Aucune donnée à afficher pour le moment.")
