import pandas as pd
import sqlite3
from db.db_utils import merge_dataframe_to_table

def transform_fakt_akce(connection: sqlite3.Connection) -> None:
    # Načti potřebné tabulky
    raw_goals = pd.read_sql("SELECT * FROM raw_match_goals", connection)
    zapasy = pd.read_sql("SELECT id_zapas, datum, zapas_id FROM dw_dim_zapas", connection)
    datumy = pd.read_sql("SELECT id_datum, datum as datum_full FROM dw_dim_datum", connection)
    map_tymy = pd.read_sql("SELECT * FROM map_zkratka_tym", connection)
    dim_tymy = pd.read_sql("SELECT id_tym, nazev FROM dw_dim_tym", connection)
    hraci = pd.read_sql("SELECT id_hrac, jmeno FROM dw_dim_hrac", connection)

    # Pomocná funkce pro rozdělení na gól + asistence
    def explode_akce(row):
        zaznamy = [{
            "zapas_id": row["zapas_id"],
            "tym_code": row["tym"],
            "cas": row["cas"],
            "hrac": row["strelec"],
            "typ_akce": "G",
            "typ_hry": row["typ"]
        }]
        if pd.notna(row["asistence"]):
            for asistent in row["asistence"].split('\n'):
                a = asistent.strip()
                if a:
                    zaznamy.append({
                        "zapas_id": row["zapas_id"],
                        "tym_code": row["tym"],
                        "cas": row["cas"],
                        "hrac": a,
                        "typ_akce": "A",
                        "typ_hry": row["typ"]
                    })
        return zaznamy

    # Rozpadni každý řádek na samostatné akce
    akce = []
    for _, row in raw_goals.iterrows():
        akce.extend(explode_akce(row))
    df = pd.DataFrame(akce)

    # Převod času na celou minutu (např. 14:15 → 15)
    df["cas_minuta"] = df["cas"].str.extract(r"(\d+):")[0].astype(int) + 1
    # Fallback pro špatné časy a zaokrouhlení všeho nad 60 na 61
    df["id_minuta"] = df["cas_minuta"].apply(lambda x: 61 if pd.isna(x) or x > 60 else int(x))

    # Merge s dw_dim_zapas → připoj datum zápasu
    df = df.merge(zapasy, left_on="zapas_id", right_on="zapas_id", how="left")

    # Merge s dw_dim_datum → najdi odpovídající id_datum
    df = df.merge(datumy, left_on="datum", right_on="datum_full", how="left")

    # Merge přes map_zkratka_tym → získání názvu týmu
    df = df.merge(map_tymy, left_on="tym_code", right_on="zkratka", how="left")

    # Merge s dw_dim_tym → získání id_tym
    df = df.merge(dim_tymy, left_on="nazev_tymu", right_on='nazev', how="left")

    # Merge s dw_dim_hrac → získání id_hrac
    df = df.merge(hraci, left_on="hrac", right_on="jmeno", how="left")
    # Nahradit nenalezené hráče id_hrac = -1
    df["id_hrac"] = df["id_hrac"].fillna(-1).astype(int)

    # Výběr finálních sloupců
    final_df = df[[
        "id_zapas", "id_hrac", "id_tym", "id_datum",
        "id_minuta", "cas", "typ_akce", "typ_hry"
    ]].copy()


    # Uložení do faktové tabulky (merge nebo insert)
    merge_dataframe_to_table(
        df=final_df,
        db_connection = connection,
        table_name="dw_fakt_akce",
        key_columns=["id_zapas"]
    )