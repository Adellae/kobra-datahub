from bs4 import BeautifulSoup
import pandas as pd
import requests
import sqlite3
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from config import AHL_URL, AHL_KOBRA_URL, DB_PATHS


def extract_matches_from_html(url: str) -> pd.DataFrame:
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="tabulka vysledky")
    rows = table.find_all("tr", class_="tabulka_radek")

    matches = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        home_team_tag = cols[1].find("a")
        home_team_url = AHL_URL + home_team_tag["href"] if home_team_tag else None
        home_team_name = home_team_tag.get_text(strip=True) if home_team_tag else None

        away_team_tag = cols[2].find("a")
        away_team_url = AHL_URL + away_team_tag["href"] if away_team_tag else None
        away_team_name = away_team_tag.get_text(strip=True) if away_team_tag else None

        match_url_suffix = row.get("data-href")
        match_url = AHL_URL + match_url_suffix if match_url_suffix else None

        matches.append({
            "home_team": home_team_name,
            "home_team_url": home_team_url,
            "away_team": away_team_name,
            "away_team_url": away_team_url,
            "match_url": match_url,
        })

    return pd.DataFrame(matches)



def extract_zapas_id(url: str) -> str:
    return parse_qs(urlparse(url).query).get("zapasid", [None])[0]


def log_match_urls(match_urls, source_team_url):
    conn = sqlite3.connect(DB_PATHS["DW"])
    cursor = conn.cursor()
    for url in match_urls:
        zapas_id = extract_zapas_id(url)
        if zapas_id:  # logujeme pouze platné
            cursor.execute("""
                INSERT OR IGNORE INTO log_nactene_zapasy (zapas_id, match_url, source_team_url)
                VALUES (?, ?, ?)
            """, (zapas_id, url, source_team_url))
    conn.commit()
    conn.close()


# 1. Získání zápasů Kobra a unikátních týmů
df = extract_matches_from_html(AHL_KOBRA_URL)
team_urls = pd.concat([df["home_team_url"], df["away_team_url"]]).drop_duplicates().reset_index(drop=True)
team_result_urls = team_urls.apply(lambda url: url.rstrip("/") + "/vysledky/?&limit=500")

# 2. Iterace přes týmy a ukládání match_url
for url in team_result_urls:
    try:
        match_df = extract_matches_from_html(url)
        match_urls = match_df["match_url"].dropna().unique()
        log_match_urls(match_urls, source_team_url=url)
    except Exception as e:
        print(f"❌ Chyba při zpracování URL: {url}")
        print(e)
