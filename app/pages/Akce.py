import streamlit as st


st.title("🏒 Přehled gólů a asistencí")



st.sidebar.header("Filtry akcí")
vyber_hrace = st.sidebar.multiselect("Hráč", ["Novák", "Svoboda", "Dvořák", "Krejčí"])
vyber_typ = st.sidebar.selectbox("Typ akce", ["Vše", "Gól", "Asistence", "Střela"])



# použij filtr ve výpisu dat
st.write(f"Zobrazuji akce typu: {vyber_typ}")



st.warning("Work in progress...")