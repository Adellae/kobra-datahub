import pandas as pd
import sqlite3
from db.db_utils import merge_dataframe_to_table
from config import DB_PATHS

def transform_dw_fakt_hraci(connection: sqlite3.Connection) -> None:
    # 1. Načtení zdrojových a dimenzních tabulek
    df_raw = pd.read_sql("SELECT * FROM raw_match_roster", connection)
    df_zapasy = pd.read_sql("SELECT id_zapas, datum, zapas_id FROM dw_dim_zapas", connection)
    df_datum = pd.read_sql("SELECT id_datum, datum FROM dw_dim_datum", connection)
    df_hraci = pd.read_sql("SELECT id_hrac, jmeno FROM dw_dim_hrac", connection)
    df_tymy = pd.read_sql("SELECT id_tym, nazev FROM dw_dim_tym", connection)

    # 2. Základní merge
    df = df_raw.copy()

    # Napojení na zápas (pomocí business key zapas_id)
    df = df.merge(df_zapasy, on="zapas_id", how="left").copy()

    # Napojení na datum (přes datum zápasu)
    df = df.merge(df_datum, on="datum", how="left").copy()

    # Napojení na hráče (pomocí jména)
    df = df.merge(df_hraci, left_on="jmeno", right_on="jmeno", how="left").copy()
    df["id_hrac"] = df["id_hrac"].fillna(-1).astype(int)

    # Napojení na tým (přes název týmu)
    df = df.merge(df_tymy, left_on="team", right_on="nazev", how="left").copy()
    df["id_tym"] = df["id_tym"].fillna(-1).astype(int)

    # 3. Výběr a přejmenování sloupců
    df_final = df[[
        "id_zapas",
        "id_hrac",
        "id_tym",
        "id_datum",
        "post",
        "goly",
        "asistence",
        "body",
        "TM"
    ]]

    # 4. Uložení do faktové tabulky
    merge_dataframe_to_table(
        df=df_final,
        db_connection=connection,
        table_name="dw_fakt_hraci",
        key_columns=["id_zapas", "id_hrac"]
    )




# conn = sqlite3.connect(DB_PATHS['DW'])
# transform_dw_fakt_hraci(conn)
# conn.close()