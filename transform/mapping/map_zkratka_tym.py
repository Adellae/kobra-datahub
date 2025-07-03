import pandas as pd
import sqlite3
from db.db_utils import merge_dataframe_to_table
from config import DB_PATHS


def transform_map_zkratka_tym(connection: sqlite3.Connection) -> None:
    # 1. Načti góly a tresty
    goals = pd.read_sql("SELECT zapas_id, tym, strelec AS hrac FROM raw_match_goals", connection)
    penalties = pd.read_sql("SELECT zapas_id, tym, hrac FROM raw_match_penalties", connection)

    # 2. Spoj je dohromady
    events = pd.concat([goals, penalties], ignore_index=True)

    # 3. Najdi jednoho hráče pro každou kombinaci team_code + zapas_id
    sample_players = (
        events
        .dropna(subset=["hrac"])
        .drop_duplicates(subset=["zapas_id", "tym"])
    )

    # 4. Načti roster (včetně všech hráčů)
    roster = pd.read_sql("SELECT zapas_id, jmeno AS hrac, team FROM raw_match_roster", connection)

    # 5. Spoj hráče z events s rosterem podle zapas_id + player
    merged = sample_players.merge(roster, on=["zapas_id", "hrac"], how="left")

    # 6. Vyber unikátní team_code + team_name (vynech nully)
    dim_teams = (
        merged[["tym", "team"]]
        .dropna()
        .drop_duplicates()
        .sort_values("tym")
        .reset_index(drop=True)
    )

    # 7. Připrav datový frame pro merge - bez surrogate key, nech to na merge funkci
    # Pokud chceš, můžeš to přejmenovat, aby byl sloupec "nazev" jako původně:
    dim_teams_rename = dim_teams.rename(columns={"tym": "zkratka", "team": "nazev_tymu"})


    # 8. Zavolej merge_dataframe_to_table (přizpůsob si cestu podle potřeby)
    merge_dataframe_to_table(
        df=dim_teams_rename,
        db_connection=connection,
        table_name="map_zkratka_tym",
        key_columns=["nazev_tymu"]
    )

    print(f"Mapa týmovů a jejich zkratek připravena s {len(dim_teams_rename)} záznamy.")


# conn = sqlite3.connect(DB_PATHS['DW'])
# transform_map_zkratka_tym(conn)
# conn.close()

