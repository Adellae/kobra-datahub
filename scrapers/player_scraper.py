import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from config import ELITEPROSPECTS_URLS, DB_PATHS

def parse_name_role(text):
    """
    Parses name, position, and optional role from text like:
        'Sofie Broďáková (D)"A"'
        'Lenka Kosejková (F)'
        'Weird entry with no brackets'
    Returns ('N/A', '', '') if format doesn't match
    """
    
    pattern = r'^(.+?)\s+\((.*?)\)(?:"([CA])")?$'
    match = re.match(pattern, text.strip())

    if match:
        name = match.group(1).strip()
        position = match.group(2).strip()
        role = match.group(3) or ''
        return name, position, role
    else:
        return "N/A", "", ""


# tady do budoucna udělat input jako list of team_keys, aby šlo jednou funkcí vrátit jeden, ale i víc týmů

def scrape_eliteprospects_roster(team_key: str) -> pd.DataFrame:
    url = ELITEPROSPECTS_URLS.get(team_key)
    if not url:
        raise ValueError(f"Neplatný team_key: {team_key}")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.select("tbody.SortTable_tbody__VrcrZ tr.SortTable_tr__L9yVC")

    players = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 10:
            continue

        number = cols[1].text.strip()
        full_text = cols[3].get_text()
        base_name, position, role = parse_name_role(full_text)

        age = cols[4].text.strip()
        birth_year = cols[5].text.strip()
        birthplace = cols[6].text.strip()
        height = cols[7].text.strip()
        weight = cols[8].text.strip()
        shoots = cols[9].text.strip()

        players.append({
            "cislo": number,
            "jmeno": base_name,
            "post": position,
            "role": role,
            "vek": age,
            "rok_narozeni": birth_year,
            "misto_narozeni": birthplace,
            "vyska_cm": height,
            "vaha_kg": weight,
            "hokejka": shoots
        })

    df = pd.DataFrame(players)
    return df[df["jmeno"] != "N/A"]