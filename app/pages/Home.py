import streamlit as st
import altair as alt
import pandas as pd

from src.models.vyhry_model import VyhryModel
from src.models.hraci_model import HraciModel
from src.models.brankari_model import BrankariModel



# Globální filtry
sezona = st.session_state.get("sezona")
soutez = st.session_state.get("soutez")
tym = st.session_state.get("tym")


st.title("🏒 Obecný dashboard")
st.markdown("""

""")



##########################################################
######################## LOAD DAT ########################
##########################################################

df_vyhry_model = VyhryModel().get_filtered(sezona = sezona, soutez = soutez, tym = tym)
df_hraci_model = HraciModel().get_filtered(sezona = sezona, soutez = soutez, tym = tym)
df_brankari_model = BrankariModel().get_filtered(sezona = sezona, soutez = soutez, tym = tym)


##########################################################
########### VÝHRY, PROHRY, REMÍZY, POČET ZÁPASŮ ##########
##########################################################

pocet_vyher = (df_vyhry_model["flag_vyhra"] == 1).sum()
pocet_proher = (df_vyhry_model["flag_vyhra"] == -1).sum()
pocet_remiz = (df_vyhry_model["flag_vyhra"] == 0).sum()
pocet_zapasu = len(df_vyhry_model)
vyherni_pomer = pocet_vyher / pocet_zapasu if pocet_zapasu else 0

# Zobrazení
col1, col2, col3, col4 = st.columns(4)
col1.metric("✅ Výhry", f"{pocet_vyher}", delta=f"{vyherni_pomer:.1%}")
col2.metric("⚠️ Prohry", f"{pocet_proher}")
col3.metric("🔄 Remízy", f"{pocet_remiz}")
col4.metric("📅 Zápasů", f"{pocet_zapasu}")


##########################################################
############## GÓLY, INKASOVANÉ GÓLY, ROZDÍL #############
##########################################################

# Přetypování góly na čísla (int), chyby přetypování přetvoří na NaN
df_vyhry_model["goly"] = pd.to_numeric(df_vyhry_model["goly"], errors='coerce')
df_vyhry_model["souper_goly"] = pd.to_numeric(df_vyhry_model["souper_goly"], errors='coerce')

# Suma s vynecháním NaN
goly = int(df_vyhry_model["goly"].sum(skipna=True))
inkasovane = int(df_vyhry_model["souper_goly"].sum(skipna=True))

# Zobrazení
empty1, col5, col6, col7, empty2 = st.columns([1, 3, 3, 3, 1])
col5.metric("🏒 Góly (vstřelené)", f"{goly}")
col6.metric("🥅 Góly (inkasované)", f"{inkasovane}")
col7.metric("🔁 Rozdíl", f"{goly - inkasovane}")



##########################################################
######################## TOP HRÁČI #######################
##########################################################

# Kontrola, jestli máme zápasy
if df_hraci_model.empty:
    st.warning(f"Tým {tym} se {sezona} neúčastnil {soutez}.")
    # return
else:

    # Sesumírovat hodnoty za každý zápas na úroveň hráče
    stats_hraci = df_hraci_model.groupby("jmeno").agg({
        "goly": "sum",
        "asistence": "sum",
        "body": "sum"
    }).reset_index()

    # Najít top hráče
    top_sniper = stats_hraci.sort_values(by="goly", ascending=False).iloc[0]
    top_assist = stats_hraci.sort_values(by="asistence", ascending=False).iloc[0]
    top_scorer = stats_hraci.sort_values(by="body", ascending=False).iloc[0]

    st.subheader("🌟 Nejlepší hráči sezóny")

    col1, col2, col3 = st.columns(3)
    col1.metric("🥇 Top střelec", top_sniper["jmeno"], f"{top_sniper['goly']} gólů")
    col2.metric("🅰️ Nejvíc asistencí", top_assist["jmeno"], f"{top_assist['asistence']} asistencí")
    col3.metric("📊 Nejvíc bodů", top_scorer["jmeno"], f"{top_scorer['body']} bodů")





##########################################################
######################## BRANKÁŘÍ ########################
##########################################################


# Kontrola, jestli máme zápasy
if df_brankari_model.empty:
    st.warning(f"Tým {tym} se {sezona} neúčastnil {soutez}.")
    # return
else:
    # Přetypovat sloupce na číselný typ (int nebo float podle potřeby)
    df_brankari_model["minuty"] = pd.to_numeric(df_brankari_model["minuty"], errors='coerce')
    df_brankari_model["zakroky"] = pd.to_numeric(df_brankari_model["zakroky"], errors='coerce')
    df_brankari_model["uspesnost"] = pd.to_numeric(df_brankari_model["uspesnost"], errors='coerce')

    # Sesumírovat minuty a zakroky, spočítat průměrnou úspěšnost za všechny zápasy
    stats_brankari = df_brankari_model.groupby("jmeno").agg({
        "minuty": "sum",
        "zakroky": "sum",
        "uspesnost": "mean"  # nebo vážený průměr podle minut, pokud chceš přesněji
    }).reset_index()

    # Najdi top hráče podle každé metriky
    top_minuty = stats_brankari.loc[stats_brankari["minuty"].idxmax()]
    top_zakroky = stats_brankari.loc[stats_brankari["zakroky"].idxmax()]
    top_uspesnost = stats_brankari.loc[stats_brankari["uspesnost"].idxmax()]

    # Zobrazení
    st.subheader("🧤 Brankář sezóny")
    col1, col2, col3 = st.columns(3)
    col1.metric("🕒 Nejvíc minut", top_minuty["jmeno"], f"{top_minuty['minuty']:.0f} min")
    col2.metric("🥅 Nejvíc zákroků", top_zakroky["jmeno"], f"{top_zakroky['zakroky']:.0f}")
    col3.metric("🎯 Nejlepší úspěšnost", top_uspesnost["jmeno"], f"{top_uspesnost['uspesnost']:.1f}%")






# # GRAF pro VÝVOJ VÝSLEDŮ V ČASE
# # Spoj s dim_datum pro získání skutečného data
# df_forma = df_fakt_vyhry_filtered.merge(
#     df_dim_datum[["id_datum", "datum"]],
#     on="id_datum",
#     how="left"
# )

# # Seřadíme podle data
# df_forma = df_forma.sort_values("datum")

# # Agregace (např. průměr výsledků za den)
# df_forma_agg = df_forma.groupby("datum").agg({"flag_vyhra": "mean"}).reset_index()


# st.subheader("📉 Vývoj formy")

# chart = alt.Chart(df_forma_agg).mark_line(point=True).encode(
#     x=alt.X("datum:T", title="Datum"),
#     y=alt.Y("flag_vyhra:Q", title="Výsledek (1=výhra, 0=remíza, -1=prohra)"),
#     tooltip=[alt.Tooltip("datum:T"), alt.Tooltip("flag_vyhra:Q", format=".2f")]
# ).properties(height=300)

# st.altair_chart(chart, use_container_width=True)