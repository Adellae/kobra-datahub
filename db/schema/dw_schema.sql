CREATE TABLE IF NOT EXISTS dw_dim_zapas (
    id_zapas INTEGER PRIMARY KEY,
    zapas_id INTEGER,
    zapas_url TEXT,
    datum TEXT,                         -- Formát: 'YYYY-MM-DD'
    cas TEXT,                           -- Formát: 'HH:MM'
    stadion TEXT,
    soutez TEXT,
    rocnik TEXT,
    skupina TEXT,
    zapas_cislo TEXT
);

CREATE TABLE IF NOT EXISTS dw_dim_datum (
    id_datum INTEGER PRIMARY KEY,       -- surrogate key YYYYMMDD
    datum TEXT,                -- formát 'YYYY-MM-DD'
    den INTEGER,               -- den v měsíci
    mesic INTEGER,             -- měsíc (1-12)
    rok INTEGER,               -- rok (např. 2025)
    den_v_tydnu INTEGER,       -- 1=pondělí ... 7=neděle
    tyden_v_roce INTEGER,      -- číslo týdne v roce (ISO)
    nazev_dne TEXT,            -- český název dne (Pondělí, Úterý, ...)
    nazev_mesice TEXT,         -- český název měsíce (Leden, Únor, ...)
    sezona TEXT                -- např. '2024/2025'
);

CREATE TABLE IF NOT EXISTS dw_dim_cas (
    id_minuta INTEGER PRIMARY KEY,
    cas_1min TEXT,
    cas_5min TEXT,
    cas_10min TEXT,
    cas_tretina INTEGER,
    nazev_tretiny TEXT
);

CREATE TABLE IF NOT EXISTS dw_dim_tym (
    id_tym INTEGER PRIMARY KEY,
    nazev TEXT,
    jednotny_nazev TEXT
);

CREATE TABLE IF NOT EXISTS map_nazev_tym (
    puvodni_nazev TEXT,
    hlavni_nazev TEXT
);

CREATE TABLE IF NOT EXISTS map_zkratka_tym (
    zkratka TEXT,
    nazev_tymu TEXT
);

CREATE TABLE IF NOT EXISTS dw_dim_hrac (
    id_hrac INTEGER PRIMARY KEY,
    jmeno TEXT,
    cislo TEXT,
    post TEXT,
    role TEXT,
    vek TEXT,
    rok_narozeni TEXT,
    misto_narozeni TEXT,
    vyska_cm TEXT,
    vaha_kg TEXT,
    hokejka TEXT
);



CREATE TABLE IF NOT EXISTS dw_fakt_akce (
    id_zapas INTEGER,
    id_hrac INTEGER,
    id_tym INTEGER,
    id_datum INTEGER,
    id_minuta INTEGER,
    cas TEXT,                       -- ve formátu MM:SS nebo HH:MM:SS
    typ_akce TEXT,                  -- 'G' = gól, 'A' = asistence
    typ_hry TEXT                    -- např. "5 na 4", může být NULL
)

CREATE TABLE IF NOT EXISTS dw_fakt_tresty (
    id_zapas INTEGER,
    id_hrac INTEGER,
    id_tym INTEGER,
    id_datum INTEGER,
    id_minuta INTEGER,
    cas TEXT,                       -- ve formátu MM:SS nebo HH:MM:SS
    typ_trestu TEXT,                -- např. '2 minuty', '5 minut'
    duvod_trestu TEXT               -- textový důvod (např. "Hákování")
)


CREATE TABLE IF NOT EXISTS dw_fakt_hraci (
    id_zapas INTEGER,
    id_hrac INTEGER,
    id_tym INTEGER,
    id_datum INTEGER,
    post TEXT,
    goly INTEGER,
    asistence INTEGER,
    body INTEGER,
    TM INTEGER
)



CREATE TABLE IF NOT EXISTS dw_fakt_brankari (
    id_zapas INTEGER,
    id_hrac INTEGER,
    id_tym INTEGER,
    id_datum INTEGER,
    minuty TEXT,
    inkasovane_goly TEXT,
    zakroky TEXT,
    uspesnost TEXT
)


CREATE TABLE IF NOT EXISTS dw_fakt_vyhry (
    id_zapas INTEGER,
    id_tym INTEGER,
    id_datum INTEGER,
    domaci_hoste INTEGER,  -- '1' pro domácí, '0' pro hosty
    goly TEXT,
    souper_goly TEXT,
    vylouceni TEXT,
    souper_vylouceni TEXT,
    vyssi_tresty TEXT,
    souper_vyssi_tresty TEXT,
    vyuziti TEXT,
    souper_vyuziti TEXT,
    cas_v_pp TEXT,
    souper_cas_v_pp TEXT,
    strely TEXT,
    souper_strely TEXT,
    flag_vyhra INTEGER  -- 1 = výhra, 0 = remíza, -1 = prohra
);
