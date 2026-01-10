import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz # Import indispensable pour l'heure

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

# 3. FONCTION DE LECTURE SÉCURISÉE (Anti-écrasement)
def load_sheet_safe(name):
    try:
        data = conn.read(worksheet=name, ttl=0)
        return data if data is not None else pd.DataFrame()
    except:
        return pd.DataFrame()

# Chargement
df_r = load_sheet_safe("Repas")
df_m = load_sheet_safe("Medicaments")
# ... charger les autres ici de la même manière ...

# 4. ONGLETS
tabs = st.tabs(["🍼 Repas", "💊 Médocs", "🧷 Changes", "😴 Sommeil"])
t_repas, t_medoc, t_change, t_sommeil = tabs

# --- FOCUS : MÉDICAMENTS (Avec case à cocher) ---
with t_medoc:
    with st.form("m_f", clear_on_submit=True):
        dm = st.date_input("Date", maintenant, key="dm")
        hm = st.time_input("Heure", maintenant.time(), key="hm_m")
        nom = st.text_input("Nom du médicament")
        donne = st.checkbox("Médicament déjà donné ?", value=True)
        nm = st.text_input("Note", key="nm")
        
        if st.form_submit_button("Enregistrer"):
            statut = "Oui" if donne else "Non"
            new_line = pd.DataFrame([{
                "Date": dm.strftime("%d/%m/%Y"), 
                "Heure": hm.strftime("%H:%M"), 
                "Nom": nom, 
                "Donné": statut, 
                "Notes": nm
            }])
            
            # SÉCURITÉ CRITIQUE : On ne met à jour que si on a pu lire le fichier avant
            # pour éviter de supprimer l'historique en cas de bug réseau
            if df_m is not None:
                updated = pd.concat([df_m, new_line], ignore_index=True)
                conn.update(worksheet="Medicaments", data=updated)
                st.success("Enregistré !")
                st.rerun()
            else:
                st.error("Erreur de synchronisation. Réessayez.")

# --- FOCUS : REPAS (Exemple avec heure corrigée) ---
with t_repas:
    with st.form("r_f", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", maintenant, key="dr")
        h = col2.time_input("Heure", maintenant.time(), key="hr")
        t = st.selectbox("Type", ["Tétée", "Biberon", "Diversification"])
        q = st.number_input("Quantité (ml)", 0, step=10)
        
        if st.form_submit_button("Enregistrer Repas"):
            new_line = pd.DataFrame([{
                "Date": d.strftime("%d/%m/%Y"), 
                "Heure": h.strftime("%H:%M"), 
                "Quantite": q, 
                "Type": t
            }])
            if df_r is not None:
                updated = pd.concat([df_r, new_line], ignore_index=True)
                conn.update(worksheet="Repas", data=updated)
                st.rerun()

# --- AFFICHAGE RÉCAPITULATIF ---
st.divider()
if not df_m.empty:
    st.write("**Historique Médicaments**")
    st.dataframe(df_m.tail(5), use_container_width=True, hide_index=True)
