import pandas as pd
from db.db_utils import merge_dataframe_to_table
import sqlite3
from config import DB_PATHS

def transform_map_nazev_tym(connection: sqlite3.Connection) -> None:
    # Ručně definovaná mapa aliasů na hlavní názvy
    data = [
        # HC Kobra Praha ženy
        ("HC Kobra Praha \"B\"", "HC Kobra Praha ženy"),
        ("HC Kobra Praha ženy", "HC Kobra Praha ženy"),
        ("HC Kobra Praha", "HC Kobra Praha ženy"),

        # Fejky
        ("HC Kobra Praha 2025", "HC Kobra Praha 2025"),

        # HC Lovosice ženy
        ("HC Lovosice ženy", "HC Lovosice ženy"),
        ("Hc Lovosice ženy", "HC Lovosice ženy"),

        # HC Berounské Lvice
        ("Berounské Lvice", "HC Berounské Lvice"),
        ("HC Berounské Lvice", "HC Berounské Lvice"),
    ]

    df = pd.DataFrame(data, columns=["puvodni_nazev", "hlavni_nazev"])

    # Drop duplikáty (pro jistotu)
    df = df.drop_duplicates().sort_values("hlavni_nazev").reset_index(drop=True)

    # Ulož do databáze (merge umožní pozdější rozšiřování)
    merge_dataframe_to_table(
        df=df,
        db_connection=connection,
        table_name="map_nazev_tym",
        key_columns=["puvodni_nazev"]
    )

    print(f"Mapa týmových aliasů připravena ({len(df)} záznamů).")



# conn = sqlite3.connect(DB_PATHS['DW'])
# transform_map_nazev_tym(conn)
# conn.close()

