import sqlite3
import pandas as pd
import streamlit as st
import sys
from pathlib import Path

# Add root to sys.path for config import
sys.path.append(str(Path(__file__).resolve().parents[3]))
from config import DB_PATHS


# 📥 Dimenze
@st.cache_data
def load_dim_zapasy():
    conn = sqlite3.connect(DB_PATHS["DW"])
    return pd.read_sql("SELECT * FROM dw_dim_zapas", conn)

@st.cache_data
def load_dim_datum():
    conn = sqlite3.connect(DB_PATHS["DW"])
    return pd.read_sql("SELECT * FROM dw_dim_datum", conn)

@st.cache_data
def load_dim_cas():
    conn = sqlite3.connect(DB_PATHS["DW"])
    return pd.read_sql("SELECT * FROM dw_dim_cas", conn)

@st.cache_data
def load_dim_tym():
    conn = sqlite3.connect(DB_PATHS["DW"])
    return pd.read_sql("SELECT * FROM dw_dim_tym", conn)

@st.cache_data
def load_map_nazev_tym():
    conn = sqlite3.connect(DB_PATHS["DW"])
    return pd.read_sql("SELECT * FROM map_nazev_tym", conn)

@st.cache_data
def load_map_zkratka_tym():
    conn = sqlite3.connect(DB_PATHS["DW"])
    return pd.read_sql("SELECT * FROM map_zkratka_tym", conn)

@st.cache_data
def load_dim_hrac():
    conn = sqlite3.connect(DB_PATHS["DW"])
    return pd.read_sql("SELECT * FROM dw_dim_hrac", conn)



# 📈 Fakta
@st.cache_data
def load_fakt_akce():
    conn = sqlite3.connect(DB_PATHS["DW"])
    return pd.read_sql("SELECT * FROM dw_fakt_akce", conn)

@st.cache_data
def load_fakt_tresty():
    conn = sqlite3.connect(DB_PATHS["DW"])
    return pd.read_sql("SELECT * FROM dw_fakt_tresty", conn)

@st.cache_data
def load_fakt_hraci():
    conn = sqlite3.connect(DB_PATHS["DW"])
    return pd.read_sql("SELECT * FROM dw_fakt_hraci", conn)

@st.cache_data
def load_fakt_brankari():
    conn = sqlite3.connect(DB_PATHS["DW"])
    return pd.read_sql("SELECT * FROM dw_fakt_brankari", conn)

@st.cache_data
def load_fakt_vyhry():
    conn = sqlite3.connect(DB_PATHS["DW"])
    return pd.read_sql("SELECT * FROM dw_fakt_vyhry", conn)


