import streamlit as st

st.title("🍼 Coucou Bébé !")
st.write("L'application est en cours de construction.")

option = st.selectbox("Choisir une action", ["Biberon", "Change", "Médecin"])
st.write(f"Vous avez sélectionné : {option}")
