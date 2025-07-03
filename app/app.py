import streamlit as st
import pandas as pd
from src.models.vyhry_model import VyhryModel
import sys
from pathlib import Path

# Add root to sys.path for config import
sys.path.append(str(Path(__file__).resolve().parent.parent))


st.set_page_config(
    page_title="HC Kobra ženy - Datahub",
    page_icon="🏒",
    layout="wide")

#st.sidebar.success("Made with <3 by Krejzy")




# GLOBÁLNÍ FILTRY
st.sidebar.header("📊 Filtry")

# Načti zápasy
df_vyhry_model = VyhryModel().get_filtered()


# --- Výběr sezóny ---
sezony = ["Vše"] + sorted(df_vyhry_model["sezona"].dropna().unique().tolist(), reverse=True)
sezona = st.sidebar.selectbox("📅 Sezóna", sezony, key="sezona")

# --- Filtrování podle sezóny ---
if sezona != "Vše":
    df_filtered = df_vyhry_model[df_vyhry_model["sezona"] == sezona]
else:
    df_filtered = df_vyhry_model

# --- Výběr soutěže se zachováním předchozího výběru ---
souteze = ["Vše"] + sorted(df_filtered["soutez"].dropna().unique().tolist())

# Získat předchozí výběr
previous_soutez = st.session_state.get("soutez", "Vše")

# Pokud je předchozí výběr v nových možnostech, předvyber ho. Jinak "Vše".
default_soutez = previous_soutez if previous_soutez in souteze else "Vše"

soutez = st.sidebar.selectbox("🏆 Soutěž", souteze, index=souteze.index(default_soutez), key="soutez")


# --- Výběr týmu ---
tymy = ["Vše"] + sorted(df_vyhry_model["jednotny_nazev"].dropna().unique().tolist(), reverse=True)
tym = st.sidebar.selectbox("👥 Tým", tymy, key="tym")



home = st.Page(
    "pages/Home.py", title="🏠 Domovská stránka", default=True
)

akce = st.Page(
    "pages/Akce.py", title="🏒 Přehled akcí"
)

tresty = st.Page(
    "pages/Tresty.py", title="⛔ Přehled trestů"
)


pg = st.navigation(
        {
            "Home": [home],
            #"Tým": [prehled],
            "Individuál": [akce, tresty],
        }
)

pg.run()




# # všechny zápasy Kobry
# # https://www.ahl.cz/klub/kobrab/vysledky/?&limit=500


# ## STREAMLIT
# ## building a dashboard article
# ## https://blog.streamlit.io/crafting-a-dashboard-app-in-python-using-streamlit/

# ## CROSS FILTERING
# ## https://www.youtube.com/watch?v=htXgwEXwmNs&ab_channel=FaniloAndrianasolo