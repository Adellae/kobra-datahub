import pandas as pd
from db.db_utils import merge_dataframe_to_table

def transform_dw_dim_cas(connection: sqlite3.Connection) -> None:
    # Základní zápas má 60 minut, index od 1 do 60
    cas_minuty = pd.Series(range(1,61))

    df = pd.DataFrame({"cas_minuta": cas_minuty})
    
    # Textový formát MM:00 (sekundy budou vždy 00)
    df["cas_1min"] = df["cas_minuta"].apply(lambda x: f"{x:02d}:00")
    
    # Zaokrouhlení na 5 a 10 minut (v tomto případě vlastně rovnou)
    df["cas_5min"] = ((df["cas_minuta"] + 4) // 5) * 5
    df["cas_10min"] = ((df["cas_minuta"] + 9) // 10) * 10
    
    df["cas_5min"] = df["cas_5min"].apply(lambda x: f"{x:02d}:00")
    df["cas_10min"] = df["cas_10min"].apply(lambda x: f"{x:02d}:00")
    
    # Třetiny: minuty 1-20 -> 1, 21-40 -> 2, 41-60 -> 3
    df["cas_tretina"] = ((df["cas_minuta"] - 1) // 20) + 1
    df.loc[df["cas_tretina"] > 3, "cas_tretina"] = 3  # pro jistotu
    
    tretiny_map = {1: "První třetina", 2: "Druhá třetina", 3: "Třetí třetina", 4: "Prodloužení"}
    df["nazev_tretiny"] = df["cas_tretina"].map(tretiny_map)
    
    # Přidáme řádek pro prodloužení - id_cas = 61
    prodlouzeni = pd.DataFrame({
        "cas_minuta": [61],
        "cas_1min": ["Prodloužení"],
        "cas_5min": ["60:00+"],
        "cas_10min": ["60:00+"],
        "cas_tretina": [4],  # může být třeba 4 jako označení prodloužení
        "nazev_tretiny": ["Prodloužení"]
    })
    
    df = pd.concat([df, prodlouzeni], ignore_index=True)
    
    # id_cas jako surrogate key (použijeme cas_minuta)
    df["id_minuta"] = df["cas_minuta"]
    
    # Přeskládáme sloupce
    df = df[["id_minuta", "cas_1min", "cas_5min", "cas_10min", "cas_tretina", "nazev_tretiny"]]
    
    merge_dataframe_to_table(
        df = df,
        db_connection = connection,
        table_name = "dw_dim_cas",
        key_columns = ["id_minuta"])