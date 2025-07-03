import pandas as pd
from datetime import datetime
import sqlite3
from db.db_utils import merge_dataframe_to_table


def transform_dw_dim_datum(start_year: int = 2022, db_path: str) -> None:
    end_year = datetime.now().year + 1
    start_date = pd.to_datetime(f"{start_year}-01-01")
    end_date = pd.to_datetime(f"{end_year}-12-31")

    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    df = pd.DataFrame({"datum": date_range.date})  # Zde odstraníme čas → pouze datum (date object)

    # Surrogate key ve formátu YYYYMMDD
    df["id_datum"] = pd.to_datetime(df["datum"]).dt.strftime("%Y%m%d").astype(int)

    # Datumové atributy
    df["den"] = pd.to_datetime(df["datum"]).dt.day
    df["mesic"] = pd.to_datetime(df["datum"]).dt.month
    df["rok"] = pd.to_datetime(df["datum"]).dt.year
    df["den_v_tydnu"] = pd.to_datetime(df["datum"]).dt.weekday + 1  # pondělí = 1
    df["tyden_v_roce"] = pd.to_datetime(df["datum"]).dt.isocalendar().week

    # České názvy dnů a měsíců (manuálně)
    dny_cz = {
        0: "Pondělí", 1: "Úterý", 2: "Středa", 3: "Čtvrtek",
        4: "Pátek", 5: "Sobota", 6: "Neděle"
    }
    mesice_cz = {
        1: "Leden", 2: "Únor", 3: "Březen", 4: "Duben",
        5: "Květen", 6: "Červen", 7: "Červenec", 8: "Srpen",
        9: "Září", 10: "Říjen", 11: "Listopad", 12: "Prosinec"
    }

    df["nazev_dne"] = pd.to_datetime(df["datum"]).dt.weekday.map(dny_cz)
    df["nazev_mesice"] = pd.to_datetime(df["datum"]).dt.month.map(mesice_cz)

    # Přidání sloupce sezona
    def season(row):
        if row["mesic"] >= 9:
            return f"{row['rok']}/{row['rok']+1}"
        else:
            return f"{row['rok']-1}/{row['rok']}"

    df["sezona"] = df.apply(season, axis=1)

    merge_dataframe_to_table(
        df=df,
        db_connection=connection: sqlite3.Connection,
        table_name="dw_dim_datum",
        key_columns=["id_datum"]
    )