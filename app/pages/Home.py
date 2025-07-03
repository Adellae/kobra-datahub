import streamlit as st
import altair as alt
import pandas as pd

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






# Globální filtry
sezona = st.session_state.get("sezona")
soutez = st.session_state.get("soutez")


st.title("🏒 Obecný přehled HC Kobra Ženy")
st.markdown("""

""")




# LOAD DAT
df_dim_datum = load_dim_datum()
df_dim_zapasy = load_dim_zapasy()
df_dim_tym = load_dim_tym()
df_dim_hrac = load_dim_hrac()
df_fakt_vyhry = load_fakt_vyhry()
df_fakt_hraci = load_fakt_hraci()
df_fakt_akce = load_fakt_akce()
df_fakt_brankari = load_fakt_brankari()






# FILTROVÁNÍ A PŘÍPRAVA DATASETU
# 1) Filtrovat tým, který chceš (máš)
df_dim_tym_filtered = df_dim_tym[df_dim_tym["jednotny_nazev"] == "HC Kobra Praha ženy"]

# 2) Filtrovat zápasy podle sezony a soutěže
df_dim_zapasy_filtered = df_dim_zapasy.copy()
if sezona != "Vše":
    df_dim_zapasy_filtered = df_dim_zapasy_filtered[df_dim_zapasy_filtered["sezona"] == sezona]
if soutez != "Vše":
    df_dim_zapasy_filtered = df_dim_zapasy_filtered[df_dim_zapasy_filtered["soutez"] == soutez]

# 3) Vytáhnout id týmu a zápasů, které chceme
ids_tym = df_dim_tym_filtered["id_tym"].unique()
ids_zapasu = df_dim_zapasy_filtered["id_zapas"].unique()

# 4) Filtrovat faktovku podle týmů a zápasů
df_fakt_vyhry_filtered = df_fakt_vyhry[
    (df_fakt_vyhry["id_tym"].isin(ids_tym)) & 
    (df_fakt_vyhry["id_zapas"].isin(ids_zapasu))
]

# 5) Spočítat metriky
pocet_vyher = (df_fakt_vyhry_filtered["flag_vyhra"] == 1).sum()
pocet_proher = (df_fakt_vyhry_filtered["flag_vyhra"] == -1).sum()
pocet_remiz = (df_fakt_vyhry_filtered["flag_vyhra"] == 0).sum()
pocet_zapasu = len(df_fakt_vyhry_filtered)
vyherni_pomer = pocet_vyher / pocet_zapasu if pocet_zapasu else 0

# Přetypování góly na čísla (int), chyby přetypování přetvoří na NaN
df_fakt_vyhry_filtered["goly"] = pd.to_numeric(df_fakt_vyhry_filtered["goly"], errors='coerce')
df_fakt_vyhry_filtered["souper_goly"] = pd.to_numeric(df_fakt_vyhry_filtered["souper_goly"], errors='coerce')

# Suma s vynecháním NaN
goly = int(df_fakt_vyhry_filtered["goly"].sum(skipna=True))
inkasovane = int(df_fakt_vyhry_filtered["souper_goly"].sum(skipna=True))

# 6) Výstup
col1, col2, col3, col4 = st.columns(4)
col1.metric("✅ Výhry", f"{pocet_vyher}", delta=f"{vyherni_pomer:.1%}")
col2.metric("⚠️ Prohry", f"{pocet_proher}")
col3.metric("🔄 Remízy", f"{pocet_remiz}")
col4.metric("📅 Zápasů", f"{pocet_zapasu}")

empty1, col5, col6, col7, empty2 = st.columns([1, 3, 3, 3, 1])
col5.metric("🏒 Góly (vstřelené)", f"{goly}")
col6.metric("🥅 Góly (inkasované)", f"{inkasovane}")
col7.metric("🔁 Rozdíl", f"{goly - inkasovane}")









# STATISTIKA HRÁČŮ
# Filtrovat akce podle zápasů i týmů (předpokládám, že v df_fakt_akce je sloupec id_tym)
# Filtrovat fakt_hraci podle zápasů a týmů
df_fakt_hraci_filtered = df_fakt_hraci[
    (df_fakt_hraci["id_zapas"].isin(ids_zapasu)) & 
    (df_fakt_hraci["id_tym"].isin(ids_tym))
]


# Kontrola, jestli máme zápasy
if df_fakt_hraci_filtered.empty:
    st.warning(f"Kobra se {sezona} neúčastnila {soutez}.")
    # Pak můžeš buď dát prázdné dataframe tam, kde bys dával další filtrování,
    # nebo rovnou return z funkce/ukončit vykreslování
    # Např.:
    # return
else:

    # Sesumírovat hodnoty za každý zápas na úroveň hráče
    stats_hraci = df_fakt_hraci_filtered.groupby("id_hrac").agg({
        "goly": "sum",
        "asistence": "sum",
        "body": "sum"
    }).reset_index()

    # Přidat jména hráčů (pokud máš jméno v nějaké dimenzi, třeba df_dim_hrac)
    stats_hraci = stats_hraci.merge(df_dim_hrac[["id_hrac", "jmeno"]].drop_duplicates(), on="id_hrac", how="left")

    # Najít top hráče
    top_sniper = stats_hraci.sort_values(by="goly", ascending=False).iloc[0]
    top_assist = stats_hraci.sort_values(by="asistence", ascending=False).iloc[0]
    top_scorer = stats_hraci.sort_values(by="body", ascending=False).iloc[0]

    st.subheader("🌟 Nejlepší hráči sezóny")

    col1, col2, col3 = st.columns(3)
    col1.metric("🥇 Top střelec", top_sniper["jmeno"], f"{top_sniper['goly']} gólů")
    col2.metric("🅰️ Nejvíc asistencí", top_assist["jmeno"], f"{top_assist['asistence']} asistencí")
    col3.metric("📊 Nejvíc bodů", top_scorer["jmeno"], f"{top_scorer['body']} bodů")











# STATISTIKA BRANKAŘŮ
# Filtrovat brankáře podle zápasů a týmů
df_brankari_filtered = df_fakt_brankari[
    (df_fakt_brankari["id_zapas"].isin(ids_zapasu)) & 
    (df_fakt_brankari["id_tym"].isin(ids_tym))
]

# Kontrola, jestli máme zápasy
if df_brankari_filtered.empty:
    st.warning(f"Kobra se {sezona} neúčastnila {soutez}.")
    # Pak můžeš buď dát prázdné dataframe tam, kde bys dával další filtrování,
    # nebo rovnou return z funkce/ukončit vykreslování
    # Např.:
    # return
else:

    # Přetypovat sloupce na číselný typ (int nebo float podle potřeby)
    df_brankari_filtered["minuty"] = pd.to_numeric(df_brankari_filtered["minuty"], errors='coerce')
    df_brankari_filtered["zakroky"] = pd.to_numeric(df_brankari_filtered["zakroky"], errors='coerce')
    df_brankari_filtered["uspesnost"] = pd.to_numeric(df_brankari_filtered["uspesnost"], errors='coerce')

    # Sesumírovat minuty a zakroky, spočítat průměrnou úspěšnost za všechny zápasy
    stats_brankari = df_brankari_filtered.groupby("id_hrac").agg({
        "minuty": "sum",
        "zakroky": "sum",
        "uspesnost": "mean"  # nebo vážený průměr podle minut, pokud chceš přesněji
    }).reset_index()

    # Přidat jména brankářů (pokud máš dimenzi hráčů s jmény)
    stats_brankari = stats_brankari.merge(df_dim_hrac[["id_hrac", "jmeno"]].drop_duplicates(), on="id_hrac", how="left")

    # Najdi top hráče podle každé metriky
    top_minuty = stats_brankari.loc[stats_brankari["minuty"].idxmax()]
    top_zakroky = stats_brankari.loc[stats_brankari["zakroky"].idxmax()]
    top_uspesnost = stats_brankari.loc[stats_brankari["uspesnost"].idxmax()]

    # Zobraz v UI
    st.subheader("🧤 Brankář sezóny")
    col1, col2, col3 = st.columns(3)
    col1.metric("🕒 Nejvíc minut", top_minuty["jmeno"], f"{top_minuty['minuty']:.0f} min")
    col2.metric("🥅 Nejvíc zákroků", top_zakroky["jmeno"], f"{top_zakroky['zakroky']:.0f}")
    col3.metric("🎯 Nejlepší úspěšnost", top_uspesnost["jmeno"], f"{top_uspesnost['uspesnost']:.1f}%")











# GRAF pro VÝVOJ VÝSLEDŮ V ČASE
# Spoj s dim_datum pro získání skutečného data
df_forma = df_fakt_vyhry_filtered.merge(
    df_dim_datum[["id_datum", "datum"]],
    on="id_datum",
    how="left"
)

# Seřadíme podle data
df_forma = df_forma.sort_values("datum")

# Agregace (např. průměr výsledků za den)
df_forma_agg = df_forma.groupby("datum").agg({"flag_vyhra": "mean"}).reset_index()


st.subheader("📉 Vývoj formy")

chart = alt.Chart(df_forma_agg).mark_line(point=True).encode(
    x=alt.X("datum:T", title="Datum"),
    y=alt.Y("flag_vyhra:Q", title="Výsledek (1=výhra, 0=remíza, -1=prohra)"),
    tooltip=[alt.Tooltip("datum:T"), alt.Tooltip("flag_vyhra:Q", format=".2f")]
).properties(height=300)

st.altair_chart(chart, use_container_width=True)