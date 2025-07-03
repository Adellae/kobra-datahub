import streamlit as st


st.title("⛔ Přehled trestů")


st.sidebar.header("Filtry trestů")
vyber_trest = st.sidebar.multiselect("Trest", ["2 - Menší trest", "5 - Osobní trest", "Trestné střílení"])
vyber_duvod_trestu = st.sidebar.multiselect("Důvod trestu", ["Bitka", "Krosček", "Sekání"])



# použij filtr ve výpisu dat
st.write(f"Zobrazuji tresty: {vyber_trest}")

