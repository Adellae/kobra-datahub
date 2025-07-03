import pandas as pd
import sqlite3
from datetime import datetime
from db.db_utils import merge_dataframe_to_table
import re
import unicodedata
from config import DB_PATHS


def normalize_name(name: str) -> str:
    """
    Normalizuje jméno tak, aby bylo ve formátu:
    "Jméno Příjmení", bez diakritiky, bez interpunkce, malými písmeny.
    """

    name = name.strip()

    # Pokud je tam čárka, přehodíme příjmení a jméno
    if "," in name:
        parts = [part.strip() for part in name.split(",")]
        if len(parts) == 2:
            name = f"{parts[1]} {parts[0]}"

    # Odstraň diakritiku
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('utf-8')

    # Odstraň interpunkci a speciální znaky (ponecháme jen písmena, čísla a mezery)
    name = re.sub(r"[^\w\s]", "", name)

    # Na malá písmena + oříznutí bílých znaků
    return name.lower().strip()




def transform_dw_dim_hrac(connection: sqlite3.Connection) -> None:
    # Načti hráče z obou tabulek
    roster_df = pd.read_sql("SELECT zapas_id, jmeno, cislo, post FROM raw_match_roster", connection)
    info_df = pd.read_sql("SELECT * FROM raw_player_info", connection)

    # Normalizuj jména pro spojení
    roster_df["jmeno_normalizovane"] = roster_df["jmeno"].apply(normalize_name)
    info_df["jmeno_normalizovane"] = info_df["jmeno"].apply(normalize_name)

    # Vyber nejnovější záznam každého hráče z rosteru
    roster_df = roster_df.sort_values("zapas_id").drop_duplicates(subset="jmeno", keep="last")

    # JOIN s eliteprospects na základě normalizovaného jména
    merged = pd.merge(
        roster_df,
        info_df,  # tyhle už máme z rosteru
        on="jmeno_normalizovane",
        how="left"
    )

    # Spočítej věk z roku narození
    current_year = datetime.now().year
    merged["vek_vypocet"] = merged["rok_narozeni"].apply(
        lambda x: str(current_year - int(x)) if pd.notnull(x) and str(x).isdigit() else None
    )

    for col in ["role" ,"vek_vypocet", "rok_narozeni", "misto_narozeni", "vyska_cm", "vaha_kg", "hokejka"]:
        merged[col] = merged[col].fillna("Nezadáno")

    # Vyber finální sloupce
    df = pd.DataFrame({
        "jmeno": merged["jmeno_x"],
        "cislo": merged["cislo_x"],
        "post": merged["post_x"],
        "role": merged["role"],
        "vek": merged["vek_vypocet"],  # už spočítaný věk
        "rok_narozeni": merged["rok_narozeni"],
        "misto_narozeni": merged["misto_narozeni"],
        "vyska_cm": merged["vyska_cm"],
        "vaha_kg": merged["vaha_kg"],
        "hokejka": merged["hokejka"]
    })

    # Přidej surrogate key
    df = df.drop_duplicates(subset="jmeno").reset_index(drop=True)
    df.insert(0, "id_hrac", df.index + 1)

    # Přidej záznam pro nevyplněné hráče
    missing_row = {
        "id_hrac": -1,
        "jmeno": "Nezadáno",
        "cislo": "-",
        "post": "-",
        "role": '-',
        "vek": '-',
        "rok_narozeni": '-',
        "misto_narozeni": '-',
        "vyska_cm": '-',
        "vaha_kg": '-',
        "hokejka": '-'
    }
    df = pd.concat([df, pd.DataFrame([missing_row])], ignore_index=True)

    # Ulož do DW tabulky
    merge_dataframe_to_table(
        df=df,
        db_connection=connection,
        table_name="dw_dim_hrac",
        key_columns=["jmeno"]
    )


# conn = sqlite3.connect(DB_PATHS['DW'])
# transform_dw_dim_hrac(conn)
# conn.close()