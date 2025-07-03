import pandas as pd
import sqlite3
from db.db_utils import merge_dataframe_to_table

def transform_dw_fakt_tresty(connection: sqlite3.Connection) -> None:
    # 1. Načtení zdrojových tabulek
    df_raw = pd.read_sql("SELECT * FROM raw_match_penalties", connection)
    df_zapasy = pd.read_sql("SELECT id_zapas, datum, zapas_id FROM dw_dim_zapas", connection)
    df_datum = pd.read_sql("SELECT id_datum, datum FROM dw_dim_datum", connection)
    df_zkratky = pd.read_sql("SELECT * FROM map_zkratka_tym", connection)
    df_tymy = pd.read_sql("SELECT id_tym, nazev FROM dw_dim_tym", connection)
    df_hraci = pd.read_sql("SELECT id_hrac, jmeno FROM dw_dim_hrac", connection)

    # 2. Sloučení základních údajů
    df = df_raw.copy()
    df = df.merge(df_zapasy, left_on="zapas_id", right_on="zapas_id", how="left")
    df = df.merge(df_datum, on="datum", how="left")

    df = df.merge(df_hraci, left_on="hrac", right_on="jmeno", how="left")
    # Nahradit nenalezené hráče id_hrac = -1
    df["id_hrac"] = df["id_hrac"].fillna(-1).astype(int)

    # 3. Napojení týmu (přes zkratku)
    df = df.merge(df_zkratky, left_on="tym", right_on="zkratka", how="left")
    df = df.merge(df_tymy, left_on="nazev_tymu", right_on="nazev", how="left")

    # 4. Výpočet id_minuta z času (např. "10:23" → 11)
    df["cas_minuta"] = df["cas"].str.extract(r"(\d+):")[0].astype(int) + 1
    # Fallback pro špatné časy a zaokrouhlení všeho nad 60 na 61
    df["id_minuta"] = df["cas_minuta"].apply(lambda x: 61 if pd.isna(x) or x > 60 else int(x))

    # 5. Výběr a přejmenování sloupců
    df_final = df[[
        "id_zapas",
        "id_hrac",
        "id_tym",
        "id_datum",
        "id_minuta",
        "cas",
        "trest",
        "duvod"
    ]].rename(columns={
        "trest": "typ_trestu",
        "duvod": "duvod_trestu"
    })

    # 6. Uložení do faktové tabulky
    merge_dataframe_to_table(
        df=df_final,
        db_connection = connection,
        table_name="dw_fakt_tresty",
        key_columns=["id_zapas"]
    )