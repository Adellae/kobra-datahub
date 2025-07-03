import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATHS = {
    "DW": os.path.join(BASE_DIR, "data", "dw.db"),
}

AHL_URL = "https://www.ahl.cz/"

AHL_KOBRA_URL = "https://www.ahl.cz/klub/kobrab/vysledky/?&limit=500"


ELITEPROSPECTS_URLS = {
    "KOBRA": "https://www.eliteprospects.com/team/21400/hc-kobra-praha"
}
