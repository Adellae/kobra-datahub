from scrapers.match_scraper import scrape_match_info, scrape_match_events, extract_roster, extract_goalkeeper_stats
from scrapers.player_scraper import scrape_eliteprospects_roster
from db.db_utils import get_connection, insert_dataframe_to_table, read_table_to_dataframe
from config import DB_PATHS

import sqlite3 # kvůli log funkcím
import pandas as pd # kvůli log funkcím - ty se postupně přesunou
import subprocess # init raw databáze



def get_pending_matches(log_db_path=DB_PATHS["DW"]):
    conn = sqlite3.connect(log_db_path)
    query = "SELECT match_url FROM log_nactene_zapasy WHERE status = 'pending'"
    df = pd.read_sql(query, conn)
    conn.close()
    return df["match_url"].tolist()


def update_status(match_url, status, log_db_path=DB_PATHS["DW"]):
    conn = sqlite3.connect(log_db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE log_nactene_zapasy
        SET status = ?, scraped_at = CURRENT_TIMESTAMP
        WHERE match_url = ?
    """, (status, match_url))
    conn.commit()
    conn.close()

  

def main():
    #print("✅ Initializing raw database...")
    
   # subprocess.run(["python", "db/init_scripts/init_raw_db.py"])
    # initialize_raw_db("data/database/raw.db")  # Drop & create raw tables

    print("📄 Loading pending matches from log...")
    match_urls = get_pending_matches()

    for match_url in match_urls:
        print(f"🔄 Processing match: {match_url}")
        try:
            # 1. Scrape and insert match info
            match_info = scrape_match_info(match_url)
            insert_dataframe_to_table(match_info, DB_PATHS["DW"], "raw_match_info")

            # 2. Scrape and insert events
            match_goals, match_penalties = scrape_match_events(match_url)
            insert_dataframe_to_table(match_goals, DB_PATHS["DW"], "raw_match_goals")
            insert_dataframe_to_table(match_penalties, DB_PATHS["DW"], "raw_match_penalties")

            # 3. Scrape and insert roster
            match_roster = extract_roster(match_url)
            insert_dataframe_to_table(match_roster, DB_PATHS["DW"], "raw_match_roster")

            # 4. Scrape and insert goalies
            match_goalies = extract_goalkeeper_stats(match_url)
            insert_dataframe_to_table(match_goalies, DB_PATHS["DW"], "raw_match_goalies")

            # 5. Update status to 'scraped'
            update_status(match_url, "scraped")

            print(f"✅ Done: {match_url}")

        except Exception as e:
            print(f"❌ Failed: {match_url}")
            print(e)
            update_status(match_url, "failed")

    print("🏁 Finished all pending matches.")


    # Scrape player info
    player_info = scrape_eliteprospects_roster("KOBRA")
    insert_dataframe_to_table(player_info, DB_PATHS["DW"], "raw_player_info", "replace")

if __name__ == "__main__":
    main()
