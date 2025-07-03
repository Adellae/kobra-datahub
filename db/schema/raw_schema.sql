DROP TABLE IF EXISTS raw_match_info;
CREATE TABLE IF NOT EXISTS raw_match_info (
    zapas_id INTEGER,
    zapas_url TEXT,
    metadata TEXT,
    domaci TEXT,
    hoste TEXT,
    vysledek TEXT,
    stadion TEXT,
    rozhodci TEXT,
    vylouceni TEXT,
    vyssi_tresty TEXT,
    vyuziti TEXT,
    cas_v_pp TEXT,
    strely TEXT
);

DROP TABLE IF EXISTS raw_match_goals;
CREATE TABLE IF NOT EXISTS raw_match_goals (
    zapas_id INTEGER,
    tym TEXT,
    cas TEXT,
    strelec TEXT,
    asistence TEXT,
    typ TEXT,
    stav TEXT
);

DROP TABLE IF EXISTS raw_match_penalties;
CREATE TABLE IF NOT EXISTS raw_match_penalties (
    zapas_id INTEGER,
    tym TEXT,
    cas TEXT,
    hrac TEXT,
    trest TEXT,
    duvod TEXT
);

DROP TABLE IF EXISTS raw_match_roster;
CREATE TABLE IF NOT EXISTS raw_match_roster (
    zapas_id INTEGER,
    team TEXT,
    cislo TEXT,
    post TEXT,
    jmeno TEXT,
    goly INTEGER,
    asistence INTEGER,
    body INTEGER,
    TM INTEGER
);

DROP TABLE IF EXISTS raw_match_goalies;
CREATE TABLE IF NOT EXISTS raw_match_goalies (
    zapas_id INTEGER,
    team TEXT,
    jmeno TEXT,
    minuty INTEGER,
    OG INTEGER,
    zakroky INTEGER,
    uspesnost REAL
);



-- PLAYER INFO - ELITEPROSPECTS
DROP TABLE IF EXISTS raw_player_info;
CREATE TABLE IF NOT EXISTS raw_player_info (
    cislo TEXT,
    jmeno TEXT,
    post TEXT,
    role TEXT,
    vek INTEGER,
    rok_narozeni INTEGER,
    misto_narozeni TEXT,
    vyska_cm TEXT,
    vaha_kg TEXT,
    hokejka TEXT
);
