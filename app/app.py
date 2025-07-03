import streamlit as st
from utils import (
    load_dim_zapasy,
    load_dim_datum,
    load_dim_cas,
    load_dim_tym,
    load_map_nazev_tym,
    load_map_zkratka_tym,
    load_dim_hrac,
    load_fakt_akce,
    load_fakt_tresty,
    load_fakt_hraci,
    load_fakt_brankari,
    load_fakt_vyhry,
)
import sys
from pathlib import Path

# Add root to sys.path for config import
sys.path.append(str(Path(__file__).resolve().parent.parent))


st.set_page_config(
    page_title="Kobří data",
    page_icon="🏒",
    layout="wide")


# st.title("Hokejový report")
#st.sidebar.success("Made with <3 by Krejzy")



# GLOBÁLNÍ FILTRY
st.sidebar.header("📊 Filtry")
# Načti zápasy
df_zapasy = load_dim_zapasy()
# Výběr sezóny
sezony = ["Vše"] + sorted(df_zapasy["sezona"].dropna().unique().tolist(), reverse=True)
vyber_sezonu = st.sidebar.selectbox("📅 Sezóna", sezony)
st.session_state["sezona"] = vyber_sezonu

# Výběr soutěže pro danou sezónu
df_filtered_sezona = df_zapasy.copy()
if st.session_state.get("sezona", "2023/24") != "Vše":
    df_filtered_sezona = df_zapasy[df_zapasy["sezona"] == vyber_sezonu]

souteze = ["Vše"] + sorted(df_filtered_sezona["soutez"].dropna().unique().tolist())
vyber_soutez = st.sidebar.selectbox("🏆 Soutěž", souteze)
st.session_state["soutez"] = vyber_soutez



# # # Sidebar filtry pro všechny stránky
# st.sidebar.header("📊 Filtry")
# vyber_sezonu = st.sidebar.selectbox("Sezóna", ["2023/24", "2022/23", "2021/22"])
# st.session_state["sezona"] = vyber_sezonu # pojistka, že bude aktivní na všech stránkách



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







# def main():
#     st.sidebar.title("Navigace")
#     page_name = st.sidebar.radio("Vyber stránku", list(PAGES.keys()))
#     page = PAGES[page_name]

#     filters = page.render_filters()
#     page.app(filters)

# if __name__ == "__main__":
#     main()



# DB_PATH = "data/database/dw.db"

# @st.cache_data
# def load_table(name):
#     with sqlite3.connect(DB_PATH) as conn:
#         return pd.read_sql(f"SELECT * FROM {name}", conn)

# # Načtení dimenzí
# df_hrac = load_table("dw_dim_hrac")
# df_tym = load_table("dw_dim_tym")
# df_datum = load_table("dw_dim_datum")
# df_zapas = load_table("dw_dim_zapas")
# akce_df = load_table("dw_fakt_akce")
# tresty_df =load_table("dw_fakt_tresty")



# # Spojení dat pro přehlednost
# def enrich(df):
#     df = df.merge(df_hrac, on="id_hrac", how="left")
#     df = df.merge(df_tym, on="id_tym", how="left")
#     df = df.merge(df_datum[["id_datum", "datum"]], on="id_datum", how="left")
#     return df

# akce_df = enrich(akce_df)

# # Převod datum na datetime (kvůli filtrování)
# akce_df["datum"] = pd.to_datetime(akce_df["datum"])

# # Sidebar filtry
# st.sidebar.header("Filtry")

# tym_options = sorted(akce_df["nazev"].dropna().unique())
# vybrany_tym = st.sidebar.selectbox("Vyber tým", ["Vše"] + tym_options)

# typ_akce_options = sorted(akce_df["typ_akce"].dropna().unique())
# vybrany_typ_akce = st.sidebar.multiselect("Typ akce", options=typ_akce_options, default=["G", "A"])

# datum_min = akce_df["datum"].min()
# datum_max = akce_df["datum"].max()
# vybrany_datum = st.sidebar.date_input("Datum od-do", value=(datum_min, datum_max))

# # Filtrace dat podle výběru
# df_filtered = akce_df.copy()

# if vybrany_tym != "Vše":
#     df_filtered = df_filtered[df_filtered["nazev"] == vybrany_tym]

# df_filtered = df_filtered[df_filtered["typ_akce"].isin(vybrany_typ_akce)]
# df_filtered = df_filtered[(df_filtered["datum"] >= pd.to_datetime(vybrany_datum[0])) & (df_filtered["datum"] <= pd.to_datetime(vybrany_datum[1]))]

# # Titulky
# st.title("🏒 Přehled gólů a asistencí")

# # Graf: počet akcí podle hráče
# st.subheader("Počet akcí podle hráče")
# graf_hraci = (
#     alt.Chart(df_filtered)
#     .mark_bar()
#     .encode(
#         y=alt.Y("jmeno:N", sort='-x', title="Hráč"),
#         x=alt.X("count():Q", title="Počet akcí"),
#         color="typ_akce:N",
#         tooltip=["jmeno", "typ_akce"]
#     )
#     .interactive()
# )
# st.altair_chart(graf_hraci, use_container_width=True)

# # Graf: rozložení akcí v čase zápasu
# st.subheader("Rozložení akcí v čase zápasu")
# graf_cas = (
#     alt.Chart(df_filtered)
#     .mark_bar(opacity=0.8)
#     .encode(
#         x=alt.X("id_minuta:O", title="Minuta zápasu"),
#         y=alt.Y("count():Q", title="Počet akcí"),
#         color="typ_akce:N",
#         tooltip=["id_minuta", "typ_akce"]
#     )
#     .interactive()
# )
# st.altair_chart(graf_cas, use_container_width=True)

# # Tabulka s detaily
# st.subheader("Detailní přehled akcí")
# st.dataframe(
#     df_filtered[["datum", "nazev", "jmeno", "typ_akce", "typ_hry", "cas"]],
#     use_container_width=True
# )







# # všechny zápasy Kobry
# # https://www.ahl.cz/klub/kobrab/vysledky/?&limit=500


# ## STREAMLIT
# ## building a dashboard article
# ## https://blog.streamlit.io/crafting-a-dashboard-app-in-python-using-streamlit/

# ## CROSS FILTERING
# ## https://www.youtube.com/watch?v=htXgwEXwmNs&ab_channel=FaniloAndrianasolo