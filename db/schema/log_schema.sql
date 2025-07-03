CREATE TABLE IF NOT EXISTS log_nactene_zapasy (
    zapas_id TEXT PRIMARY KEY,
    match_url TEXT,
    source_team_url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending'
)