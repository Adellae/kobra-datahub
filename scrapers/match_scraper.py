import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import pandas as pd


# chybí soutěž a datum zápasu
def scrape_match_info(url: str) -> pd.DataFrame:
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    zapas_id = parse_qs(urlparse(url).query).get("zapasid", [None])[0]

    # Metainformace o zápasu
    metadata_div = soup.select_one("div.full_portlet_inner_box > div")
    metadata = metadata_div.get_text(strip=True) if metadata_div else None

    # Najdeme všechny divy s týmovými informacemi (mají 40% šířku a text-align center)
    team_divs = soup.select("div[style*='width: 40%'][style*='text-align:center']")

    home_team, away_team = None, None

    if len(team_divs) >= 2:
        try:
            home_team = team_divs[0].find_all("div")[1].get_text(strip=True)
            away_team = team_divs[1].find_all("div")[1].get_text(strip=True)
        except (IndexError, AttributeError):
            pass

    # Skóre
    score_div = soup.select_one("div[style*='width: 20%;'][style*='float: left']")
    score = score_div.find("div").get_text(strip=True) if score_div else None

    # Statistika zápasu
    stats = {}
    stats_table = soup.find("caption", string="Statistika zápasu")
    if stats_table:
        rows = stats_table.find_parent("table").find_all("tr")
        for row in rows:
            tds = row.find_all("td")
            if len(tds) == 2:
                key = tds[0].get_text(strip=True)
                val = tds[1].get_text(strip=True)
                stats[key] = val

    data = {
        "zapas_id": zapas_id,
        "zapas_url": url,
        "metadata": metadata,
        "domaci": home_team,
        "hoste": away_team,
        "vysledek": score,
        "stadion": stats.get("Stadion"),
        "rozhodci": stats.get("Rozhodčí"),
        "vylouceni": stats.get("Vyloučení"),
        "vyssi_tresty": stats.get("Vyšší tresty"),
        "vyuziti": stats.get("Využití"),
        "cas_v_pp": stats.get("Čas v PP"),
        "strely": stats.get("Střely")
    }

    return pd.DataFrame([data])
# print(scrape_match_info("https://www.ahl.cz/soutez/soutez_zen/zapas/?zapasid=36095"))



def scrape_match_events(url: str) -> pd.DataFrame:
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    zapas_id = parse_qs(urlparse(url).query).get("zapasid", [None])[0]

    goals = []
    penalties = []

    # Find all sections with match tables
    tables = soup.select("div.zapas_tabulka_box > table")

    for table in tables:
        caption = table.find("caption")
        if not caption:
            continue
        title = caption.get_text(strip=True)


        if title == "Branky":
            for row in table.select("tbody tr"):
                cols = row.find_all("td")
                if len(cols) >= 6:
                    goals.append({
                        "tym": cols[0].text.strip(),
                        "cas": cols[1].text.strip(),
                        "strelec": cols[2].text.strip(),
                        "asistence": cols[3].text.strip(),
                        "typ": cols[4].text.strip(),
                        "stav": cols[5].text.strip(),
                        "zapas_id": zapas_id
                    })

        elif title == "Tresty":
            for row in table.select("tbody tr"):
                cols = row.find_all("td")
                if len(cols) >= 5:
                    penalties.append({
                        "tym": cols[0].text.strip(),
                        "cas": cols[1].text.strip(),
                        "hrac": cols[2].text.strip(),
                        "trest": cols[3].text.strip(),
                        "duvod": cols[4].text.strip(),
                        "zapas_id": zapas_id
                    })

    goals_df = pd.DataFrame(goals)
    penalties_df = pd.DataFrame(penalties)

    return goals_df, penalties_df
# print(scrape_match_events("https://www.ahl.cz/soutez/soutez_zen/zapas/?zapasid=36095"))



def extract_roster(url: str) -> pd.DataFrame:
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    zapas_id = parse_qs(urlparse(url).query).get("zapasid", [None])[0]

    # Najdeme oba týmy podle stylu divů (domácí i hosté)
    team_divs = soup.select("div[style*='width: 40%'][style*='text-align:center']")
    if len(team_divs) < 2:
        raise ValueError("Nenalezeny oba týmy v hlavičce zápasu")

    # Text týmu je v druhém <div> uvnitř těchto bloků, podle tvého kódu:
    domaci = team_divs[0].find_all("div")[1].get_text(strip=True)
    hoste = team_divs[1].find_all("div")[1].get_text(strip=True)

    # Najdeme soupisky jako předtím
    rows = []
    tables = [
        table for table in soup.find_all("table", class_="tabulka")
        if table.caption and table.caption.get_text(strip=True).startswith("Hráči - ")
    ]

    teams = [domaci, hoste]

    for i, table in enumerate(tables):
        team_name = teams[i] if i < len(teams) else "Neznámý tým"

        tbody = table.find("tbody")
        if not tbody:
            continue

        for row in tbody.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 7:
                continue

            try:
                number = cols[0].text.strip()
                position = cols[1].text.strip()
                name = cols[2].text.strip()
                goals = int(cols[3].text.strip())
                assists = int(cols[4].text.strip())
                points = int(cols[5].text.strip())
                penalty_minutes = int(cols[6].text.strip())
            except ValueError:
                continue

            player = {
                "zapas_id": zapas_id,
                "team": team_name,
                "cislo": number,
                "post": position,
                "jmeno": name,
                "goly": goals,
                "asistence": assists,
                "body": points,
                "TM": penalty_minutes
            }

            rows.append(player)

    return pd.DataFrame(rows)
# print(extract_roster("https://www.ahl.cz/soutez/soutez_zen/zapas/?zapasid=36095"))





def extract_goalkeeper_stats(url: str) -> pd.DataFrame:
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    zapas_id = parse_qs(urlparse(url).query).get("zapasid", [None])[0]

    # Z hlavičky zápasu vytáhneme domácí a hostující tým
    team_divs = soup.select("div[style*='width: 40%'][style*='text-align:center']")
    if len(team_divs) < 2:
        raise ValueError("Nepodařilo se najít oba týmy v hlavičce zápasu.")

    domaci = team_divs[0].find_all("div")[1].get_text(strip=True)
    hoste = team_divs[1].find_all("div")[1].get_text(strip=True)
    teams = [domaci, hoste]

    # Najdeme tabulky s brankáři
    goalie_tables = [
        table for table in soup.find_all("table", class_="tabulka")
        if table.caption and table.caption.get_text(strip=True).startswith("Brankáři -")
    ]

    rows = []

    for i, table in enumerate(goalie_tables):
        team_name = teams[i] if i < len(teams) else "Neznámý tým"

        tbody = table.find("tbody")
        if not tbody:
            continue

        for row in tbody.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            jmeno = cols[0].get_text(strip=True)
            minuty = cols[1].get_text(strip=True)
            obdrzene_goly = cols[2].get_text(strip=True)
            zakroky = cols[3].get_text(strip=True)
            procenta = cols[4].get_text(strip=True)

            try:
                minuty_int = int(minuty) if minuty.isdigit() else None
                obdrzene_goly_int = int(obdrzene_goly) if obdrzene_goly.isdigit() else None
                zakroky_int = int(zakroky) if zakroky.isdigit() else None
                uspešnost_float = float(procenta.replace(",", ".").replace("%", "")) if procenta.replace(",", ".").replace("%", "").replace(".", "", 1).isdigit() else None
            except Exception:
                minuty_int = obdrzene_goly_int = zakroky_int = uspešnost_float = None

            goalie = {
                "zapas_id": zapas_id,
                "team": team_name,
                "jmeno": jmeno,
                "minuty": minuty_int,
                "OG": obdrzene_goly_int,
                "zakroky": zakroky_int,
                "uspesnost": uspešnost_float
            }

            rows.append(goalie)

    return pd.DataFrame(rows)

#print(extract_goalkeeper_stats("https://www.ahl.cz/soutez/soutez_zen/zapas/?zapasid=36095"))