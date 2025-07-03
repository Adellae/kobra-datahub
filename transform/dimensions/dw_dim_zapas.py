import pandas as pd
import re
from datetime import datetime
import sqlite3
from db.db_utils import merge_dataframe_to_table
from config import DB_PATHS



# Mapování ročníku na soutěž
SOUTEZ_MAPPING = {
    "SZ ": "AŽLH - nadregionální soutěž žen",
    "VC VALHALLA": "VALHALLA CUP",
    "WUC WARM": "WARM-UP CUP",
    "MR Malá": "Malá Republika",
    "MC MORAVIA CUP": "MORAVIA CUP",
    "Jiné": "Jiné soutěže"
}


def split_match_metadata(metadata: str) -> dict:
    parts = [p.strip() for p in metadata.split("|")]

    return {
        "rocnik": parts[0] if len(parts) > 0 else None,
        "skupina": parts[1] if len(parts) > 1 else None,
        "datum": parts[2] if len(parts) > 2 else None,
        "misto": parts[3] if len(parts) > 3 else None,
        "zapas_cislo": parts[4] if len(parts) > 4 else None,
    }

def map_soutez(rocnik: str) -> str:
    if not rocnik:
        return "Jiné soutěže"

    for prefix, mapped in SOUTEZ_MAPPING.items():
        if rocnik.startswith(prefix):
            return mapped
    return "Jiné soutěže"


def transform_dw_dim_zapas(connection: sqlite3.Connection) -> None:
    raw_df = pd.read_sql("SELECT * FROM raw_match_info", connection)
    rows = []
    
    for _, row in raw_df.iterrows():
        meta = split_match_metadata(row["metadata"])
        
        # Extrahuj datum a čas
        datum_raw = meta.get("datum")
        datum_str, cas_str = None, None
        
        if datum_raw:
            match = re.search(r"(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4}),\s*(\d{1,2}:\d{2})", datum_raw)
            if match:
                den, mesic, rok, cas_str = match.groups()
                datum_str = f"{rok}-{int(mesic):02d}-{int(den):02d}"

        # Odvodíme sezonu
        sezona = None
        if datum_str:
            dt = datetime.strptime(datum_str, "%Y-%m-%d")
            year = dt.year
            if dt.month >= 9:
                sezona = f"{year}/{year + 1}"
            else:
                sezona = f"{year - 1}/{year}"

        soutez = map_soutez(meta.get("rocnik"))

        rows.append({
            "zapas_id": int(row["zapas_id"]),
            "zapas_url": row["zapas_url"],
            "datum": datum_str,
            "cas": cas_str,
            "stadion": row["stadion"] or meta.get("misto"),
            "sezona": sezona,
            "soutez": soutez,
            "rocnik": meta.get("rocnik"),
            "skupina": meta.get("skupina"),
            "zapas_cislo": meta.get("zapas_cislo"),
        })

    df_result = pd.DataFrame(rows)
    df_result = df_result.drop_duplicates(subset=["zapas_id"])  # ochrana proti duplicitám


    # Přeskládej sloupce do požadovaného pořadí
    df_result = df_result[[
        "zapas_id",
        "zapas_url",
        "datum",
        "cas",
        "stadion",
        "sezona",
        "soutez",
        "rocnik",
        "skupina",
        "zapas_cislo"
    ]]

    # Přidej surrogate key
    df_result = df_result.reset_index(drop=True)
    df_result.insert(0, "id_zapas", df_result.index + 1)

    merge_dataframe_to_table(
        df = df_result,
        db_connection = connection,
        table_name = "dw_dim_zapas",
        key_columns = ["zapas_id"])




# conn = sqlite3.connect(DB_PATHS['DW'])
# transform_dw_dim_zapas(conn)
# conn.close()