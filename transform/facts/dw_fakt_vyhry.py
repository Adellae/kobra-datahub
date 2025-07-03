import pandas as pd
import sqlite3
from db.db_utils import merge_dataframe_to_table
from config import DB_PATHS


def parse_time_string(s):
    """Normalizuje časový string 'M:S' nebo 'MM:SS' → 'MM:SS'. Jinak vrací 'Nezadáno'."""
    if not s or s.strip() == "":
        return "Nezadáno"
    try:
        parts = s.strip().split(":")
        if len(parts) == 2:
            minuty = int(parts[0])
            sekundy = int(parts[1])
            return f"{minuty:02}:{sekundy:02}"
        else:
            return "Nezadáno"
    except:
        return "Nezadáno"


def split_time_stats(raw_string):
    """Zpracuje zápis jako '8:23\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t: 3:32' → ('08:23', '03:32')"""
    if not raw_string or ":" not in raw_string:
        return ("Nezadáno", "Nezadáno")
    
    try:
        clean = raw_string.strip().replace("\n", "").replace("\t", "")
        if " : " in clean:
            parts = clean.split(" : ")
        else:
            parts = clean.split(":")
            if len(parts) == 4:
                parts = [f"{parts[0]}:{parts[1]}", f"{parts[2]}:{parts[3]}"]
            elif len(parts) == 2:
                parts = [clean, "Nezadáno"]
            else:
                return ("Nezadáno", "Nezadáno")

        domaci = parse_time_string(parts[0])
        host = parse_time_string(parts[1])
        return (domaci, host)
    except:
        return ("Nezadáno", "Nezadáno")


def transform_dw_fakt_vyhry(connection: sqlite3.Connection) -> None:
    # Načti zdroj a dimenze
    df_raw = pd.read_sql("SELECT * FROM raw_match_info", connection)
    df_zapasy = pd.read_sql("SELECT id_zapas, zapas_id, datum FROM dw_dim_zapas", connection)
    df_datum = pd.read_sql("SELECT id_datum, datum FROM dw_dim_datum", connection)
    df_tymy = pd.read_sql("SELECT id_tym, nazev FROM dw_dim_tym", connection)

    # 1. Připrav dataframe s domacimi a hosty jako dva řádky
    records = []
    for _, row in df_raw.iterrows():
        # Rozdělení statistik na domácí/hosté podle ":"
        def split_stat(s):
            parts = s.split(":")
            return parts[0].strip(), parts[1].strip() if len(parts) == 2 else (None, None)
        
        domaci = row['domaci']
        hoste = row['hoste']
        zapas_id = row['zapas_id']

        # Vyparsuj výsledky
        goly_d, goly_h = split_stat(row['vysledek'])
        vylouceni_d, vylouceni_h = split_stat(row['vylouceni'])
        vyssi_tresty_d, vyssi_tresty_h = split_stat(row['vyssi_tresty'])
        vyuziti_d, vyuziti_h = split_stat(row['vyuziti'])
        strely_d, strely_h = split_stat(row['strely'])

        # Zpracování času v přesilovkách
        cas_v_pp_d, cas_v_pp_h = split_time_stats(row['cas_v_pp'])

        # Funkce pro vyhodnocení výhry/prohry/ remízy (flag 1 = výhra, 0 = remíza, -1 = prohra)
        def vyhra_flag(d, h):
            try:
                d = int(d)
                h = int(h)
                if d > h:
                    return 1   # výhra
                elif d == h:
                    return 0   # remíza
                else:
                    return -1  # prohra
            except:
                return None

        # Domácí záznam
        records.append({
            "zapas_id": zapas_id,
            "tym": domaci,
            "domaci_hoste": 1,
            "goly": int(goly_d) if goly_d and goly_d.isdigit() else None,
            "souper_goly": int(goly_h) if goly_h and goly_h.isdigit() else None,
            "vylouceni": int(vylouceni_d) if vylouceni_d and vylouceni_d.isdigit() else None,
            "souper_vylouceni": int(vylouceni_h) if vylouceni_h and vylouceni_h.isdigit() else None,
            "vyssi_tresty": int(vyssi_tresty_d) if vyssi_tresty_d and vyssi_tresty_d.isdigit() else None,
            "souper_vyssi_tresty": int(vyssi_tresty_h) if vyssi_tresty_h and vyssi_tresty_h.isdigit() else None,
            "vyuziti": int(vyuziti_d) if vyuziti_d and vyuziti_d.isdigit() else None,
            "souper_vyuziti": int(vyuziti_h) if vyuziti_h and vyuziti_h.isdigit() else None,
            "cas_v_pp": cas_v_pp_d,
            "souper_cas_v_pp": cas_v_pp_h,
            "strely": int(strely_d) if strely_d and strely_d.isdigit() else None,
            "souper_strely": int(strely_h) if strely_h and strely_h.isdigit() else None,
            "flag_vyhra": vyhra_flag(goly_d, goly_h)
        })

        # Hostující záznam
        records.append({
            "zapas_id": zapas_id,
            "tym": hoste,
            "domaci_hoste": 0,
            "goly": int(goly_h) if goly_h and goly_h.isdigit() else None,
            "souper_goly": int(goly_d) if goly_d and goly_d.isdigit() else None,
            "vylouceni": int(vylouceni_h) if vylouceni_h and vylouceni_h.isdigit() else None,
            "souper_vylouceni": int(vylouceni_d) if vylouceni_d and vylouceni_d.isdigit() else None,
            "vyssi_tresty": int(vyssi_tresty_h) if vyssi_tresty_h and vyssi_tresty_h.isdigit() else None,
            "souper_vyssi_tresty": int(vyssi_tresty_d) if vyssi_tresty_d and vyssi_tresty_d.isdigit() else None,
            "vyuziti": int(vyuziti_h) if vyuziti_h and vyuziti_h.isdigit() else None,
            "souper_vyuziti": int(vyuziti_d) if vyuziti_d and vyuziti_d.isdigit() else None,
            "cas_v_pp": cas_v_pp_h,
            "souper_cas_v_pp": cas_v_pp_d,
            "strely": int(strely_h) if strely_h and strely_h.isdigit() else None,
            "souper_strely": int(strely_d) if strely_d and strely_d.isdigit() else None,
            "flag_vyhra": vyhra_flag(goly_h, goly_d)
        })

    df_final = pd.DataFrame(records)

    # Napojení na dimenze podle zapas_id, tym
    df_final = df_final.merge(df_zapasy, on="zapas_id", how="left")
    df_final = df_final.merge(df_tymy, left_on="tym", right_on="nazev", how="left")

    # Napojení datum (z df_zapasy -> df_datum)
    df_final = df_final.merge(df_datum, on="datum", how="left")

    # Vyber sloupce
    df_final = df_final[[
        "id_zapas", "id_tym", "id_datum", "domaci_hoste",
        "goly", "souper_goly",
        "vylouceni", "souper_vylouceni",
        "vyssi_tresty", "souper_vyssi_tresty",
        "vyuziti", "souper_vyuziti",
        "cas_v_pp", "souper_cas_v_pp",
        "strely", "souper_strely",
        "flag_vyhra"
    ]]

    # Nahraď NaN None
    df_final = df_final.where(pd.notnull(df_final), None)

    # Uložení
    merge_dataframe_to_table(
        df=df_final,
        db_connection=connection,
        table_name="dw_fakt_vyhry",
        key_columns=["id_zapas", "id_tym", "domaci_hoste"]
    )






conn = sqlite3.connect(DB_PATHS['DW'])
transform_dw_fakt_vyhry(conn)
conn.close()

