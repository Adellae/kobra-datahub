import pandas as pd
import sqlite3
from db.db_utils import merge_dataframe_to_table
from config import DB_PATHS

# def transform_dw_dim_tym(connection: sqlite3.Connection) -> None:
#     df = pd.read_sql("SELECT * FROM raw_match_info", connection)

#     # Stack home/away teams into one column and drop duplicates
#     unikatni_tymy = pd.DataFrame(pd.concat([df["domaci"], df["hoste"]], axis=0).unique(), columns=["nazev"])
    
#     # Add surrogate key
#     unikatni_tymy.insert(0, "id_tym", range(1, len(unikatni_tymy) + 1))

#     merge_dataframe_to_table(
#         df = unikatni_tymy,
#         db_connection = connection,
#         table_name = "dw_dim_tym",
#         key_columns = ["nazev"])

def transform_dw_dim_tym(connection: sqlite3.Connection) -> None:
    df = pd.read_sql("SELECT * FROM raw_match_info", connection)

    # Stack home/away teams into one column and drop duplicates
    unikatni_tymy = pd.DataFrame(pd.concat([df["domaci"], df["hoste"]], axis=0).unique(), columns=["nazev"])

    # Připoj mapu aliasů → hlavní název (jednotny_nazev)
    df_map = pd.read_sql("SELECT puvodni_nazev, hlavni_nazev FROM map_nazev_tym", connection)

    # Left join, aby se při nenačtení aliasu zobrazilo původní jméno
    unikatni_tymy = unikatni_tymy.merge(df_map, how="left", left_on="nazev", right_on="puvodni_nazev")

    # Pokud jednotny_nazev (hlavni_nazev) chybí, použij původní název
    unikatni_tymy["jednotny_nazev"] = unikatni_tymy["hlavni_nazev"].fillna(unikatni_tymy["nazev"])

    # Přidej surrogate key
    unikatni_tymy.insert(0, "id_tym", range(1, len(unikatni_tymy) + 1))

    # Odeber nepotřebné sloupce (puvodni_nazev, hlavni_nazev)
    unikatni_tymy = unikatni_tymy[["id_tym", "nazev", "jednotny_nazev"]]

    merge_dataframe_to_table(
        df=unikatni_tymy,
        db_connection=connection,
        table_name="dw_dim_tym",
        key_columns=["nazev"]
    )

# conn = sqlite3.connect(DB_PATHS['DW'])
# transform_dw_dim_tym(conn)
# conn.close()