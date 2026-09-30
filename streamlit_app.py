import streamlit as st
import pandas as pd
import plotly.express as px
import io
import re
import ast
import tempfile
import numpy as np
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

import folium
from folium import plugins
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import pydeck as pdk

# =========================================================
# BLOCO 1 — CONFIGURAÇÃO BASE DO APP
# =========================================================

st.set_page_config(
    page_title="Waze Foz do Iguaçu",
    page_icon="https://cdn.simpleicons.org/waze",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg:           #f0f4f8;
    --surface:      #ffffff;
    --surface-soft: #f8fafc;
    --surface-2:    #e8edf2;
    --text:         #1e293b;
    --text-strong:  #0f172a;
    --text-muted:   #475569;
    --text-faint:   #94a3b8;
    --border:       #dde3ea;
    --primary:      #2563eb;
    --primary-dark: #1d4ed8;
    --primary-soft: #eff6ff;
    --primary-hover:#1e40af;
    --success:      #16a34a;
    --success-soft: #f0fdf4;
    --warning:      #d97706;
    --warning-soft: #fffbeb;
    --danger:       #dc2626;
    --danger-soft:  #fef2f2;
    --purple:       #7c3aed;
    --radius:       12px;
    --shadow-sm:    0 1px 3px rgba(15,23,42,0.07), 0 1px 2px rgba(15,23,42,0.04);
    --shadow-md:    0 4px 12px rgba(15,23,42,0.10), 0 2px 6px rgba(15,23,42,0.06);
    --shadow-lg:    0 10px 30px rgba(15,23,42,0.12), 0 4px 10px rgba(15,23,42,0.07);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
}

body { color: var(--text); }

.stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
}

.main .block-container {
    background: transparent !important;
    padding-top: 1.5rem !important;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 2px 0 8px rgba(15,23,42,0.05) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] .stMarkdown h4 {
    color: var(--text-strong) !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: var(--primary) !important;
    font-weight: 700 !important;
}

.stButton > button[kind="primary"] {
    background: var(--primary) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    box-shadow: var(--shadow-md) !important;
    transition: background 160ms ease, box-shadow 160ms ease, transform 120ms ease !important;
}

.stButton > button[kind="primary"]:hover {
    background: var(--primary-hover) !important;
    box-shadow: var(--shadow-lg) !important;
    transform: translateY(-1px) !important;
}

.stButton > button[kind="primary"]:active {
    transform: translateY(0) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stButton > button[kind="secondary"] {
    background: var(--surface) !important;
    color: var(--primary) !important;
    border: 1.5px solid var(--primary) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

.stButton > button[kind="secondary"]:hover {
    background: var(--primary-soft) !important;
}

[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem 1.2rem !important;
    box-shadow: var(--shadow-sm) !important;
    transition: box-shadow 160ms ease !important;
}

[data-testid="metric-container"]:hover {
    box-shadow: var(--shadow-md) !important;
}

[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.9px !important;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text-strong) !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--surface-soft) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 8px 18px !important;
    transition: color 140ms ease, background 140ms ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: var(--surface-2) !important;
    color: var(--text) !important;
}

.stTabs [aria-selected="true"] {
    background: var(--primary) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.30) !important;
}

[data-testid="stDataFrame"] {
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    box-shadow: var(--shadow-sm) !important;
}

[data-testid="stAlert"] {
    background: var(--primary-soft) !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 10px !important;
    color: var(--primary-dark) !important;
}

[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    box-shadow: var(--shadow-sm) !important;
}

[data-testid="stExpander"]:hover {
    border-color: #bcd0f0 !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
}

[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: var(--primary) !important;
    border-color: var(--primary) !important;
}

hr { border-color: var(--border) !important; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--surface-soft); border-radius: 3px; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

.card-light {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow-sm);
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.4px;
}
.badge-success { background: var(--success-soft); color: var(--success); border: 1px solid #bbf7d0; }
.badge-warning { background: var(--warning-soft); color: var(--warning); border: 1px solid #fde68a; }
.badge-danger  { background: var(--danger-soft);  color: var(--danger);  border: 1px solid #fecaca; }
.badge-primary { background: var(--primary-soft); color: var(--primary); border: 1px solid #bfdbfe; }
</style>
""", unsafe_allow_html=True)

TIMEZONE_FOZ = ZoneInfo("America/Sao_Paulo")


def get_current_foz_time() -> datetime:
    return datetime.now(TIMEZONE_FOZ).replace(tzinfo=None)


if "app_start_time" not in st.session_state:
    st.session_state.app_start_time = get_current_foz_time()

if "manual_refreshes" not in st.session_state:
    st.session_state.manual_refreshes = 0

session_elapsed_seconds = (get_current_foz_time() - st.session_state.app_start_time).total_seconds()
seconds_until_next_refresh = 600 - (session_elapsed_seconds % 600)
minutes_until_next_refresh = int(seconds_until_next_refresh // 60)
remaining_seconds = int(seconds_until_next_refresh % 60)
session_elapsed_total_seconds = int(session_elapsed_seconds)

FOLDER_ALERTS_ID = "1xKkqLEusWuNoGzy5-UYuevUbMHAvc-bL"
FOLDER_JAMS_ID = "192MCefe9vQwYhQcu-uZXekMbgdslTcgC"
FOLDER_ALERTS_ID2 = "1kQfYRJz0-EwY4gcsjTTVBCgK9zO5BAR0"
FOLDER_JAMS_ID2 = "16bblUG7NQmLMZM7BQUGAa3-GZIFYMka0"

CSV_FILES_TO_MERGE = [
    "Waze for Cities Data _ tabelas alertas_20240101_20260306.csv",
    "Waze for Cities Data _ buracos na via maio 2025 a maio 2026.csv",
    "Waze for Cities Data _ todos os alertas maio 2025 a maio 2026.csv",
    "Waze for Cities Data _Dashboard_Traffic Alerts_Tabela_2025-01-01-2026-07-04.csv",
]

LAT_MIN, LAT_MAX = -25.70, -25.40
LON_MIN, LON_MAX = -54.75, -54.45

def get_congestion_color(speed_kmh: float) -> str:
    if speed_kmh >= 80:
        return "#2196F3"
    elif speed_kmh >= 60:
        return "#4CAF50"
    elif speed_kmh >= 40:
        return "#8BC34A"
    elif speed_kmh >= 20:
        return "#FF9800"
    elif speed_kmh >= 5:
        return "#F44336"
    return "#7B1FA2"


def get_incident_severity_color(incident_type: str, incident_subtype: str | None = None) -> str:
    low_severity_subtypes = {
        "ACIDENTE LEVE",
        "TRÂNSITO MODERADO",
        "PERIGO NA VIA",
        "OBJETO NA VIA",
        "ANIMAL NA VIA",
        "VEÍCULO PARADO",
        "CONDIÇÕES CLIMÁTICAS",
    }

    normalized_type = str(incident_type).upper().strip() if incident_type else ""
    normalized_subtype = str(incident_subtype).upper().strip() if incident_subtype else ""
    is_low_severity = normalized_subtype in low_severity_subtypes

    base_color_by_type = {
        "ACIDENTE": "#F44336" if not is_low_severity else "#EF9A9A",
        "VIA FECHADA": "#B71C1C",
        "CONGESTIONAMENTO": "#7B1FA2" if not is_low_severity else "#CE93D8",
        "PERIGO": "#FF9800" if not is_low_severity else "#FFCC80",
        "PERIGO CLIMÁTICO": "#29B6F6",
        "OBRAS": "#78909C",
        "ALERTA": "#FDD835",
    }

    subtype_override_color = {
        "ACIDENTE GRAVE": "#B71C1C",
        "ACIDENTE LEVE": "#EF9A9A",
        "BURACO NA VIA": "#FF9800",
        "OBRAS NA VIA": "#78909C",
        "SEMÁFORO QUEBRADO": "#FDD835",
        "INUNDAÇÃO": "#0288D1",
        "NEBLINA": "#B0BEC5",
        "TRÂNSITO PARADO": "#7B1FA2",
        "TRÂNSITO PESADO": "#F44336",
        "TRÂNSITO MODERADO": "#FF9800",
    }

    if normalized_subtype in subtype_override_color:
        return subtype_override_color[normalized_subtype]

    return base_color_by_type.get(normalized_type, "#90A4AE")


# =========================================================
# BLOCO 2 — CONEXÃO, INGESTÃO E NORMALIZAÇÃO DOS DADOS
# =========================================================

import os
from pathlib import Path


@st.cache_resource(show_spinner=False)
def get_drive_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    creds_info = st.secrets["gcp_service_account"]
    creds = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds)


def get_latest_h5_id(folder_id: str) -> str | None:
    service = get_drive_service()
    query = f"'{folder_id}' in parents and name contains '.h5' and trashed=false"

    results = service.files().list(
        q=query,
        fields="files(id, name, modifiedTime)",
        orderBy="modifiedTime desc",
        pageSize=20
    ).execute()

    files = results.get("files", [])
    if not files:
        return None

    latest_id = None
    latest_ts = -1

    for file_meta in files:
        match = re.search(r"(\d{8,})", file_meta["name"])
        if match:
            ts = int(match.group(1))
            if ts > latest_ts:
                latest_ts = ts
                latest_id = file_meta["id"]

    return latest_id if latest_id else files[0]["id"]


@st.cache_data(ttl=600, show_spinner="📥 Baixando dados do Drive...")
def load_hdf_from_drive(file_id: str) -> pd.DataFrame:
    from googleapiclient.http import MediaIoBaseDownload

    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)

    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    buffer.seek(0)
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".h5") as tmp:
            tmp.write(buffer.getvalue())
            tmp_path = tmp.name

        dataframe = pd.read_hdf(tmp_path, key="s")
        return dataframe

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def normalize_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    normalized_dataframe = df.copy()

    if "pubMillis" in normalized_dataframe.columns:
        normalized_dataframe["timestamp"] = (
            pd.to_datetime(normalized_dataframe["pubMillis"], unit="ms", utc=True, errors="coerce")
            .dt.tz_convert("America/Sao_Paulo")
            .dt.tz_localize(None)
        )
    elif "timestamp" in normalized_dataframe.columns:
        normalized_dataframe["timestamp"] = pd.to_datetime(
            normalized_dataframe["timestamp"],
            errors="coerce"
        )
    else:
        for alternative_timestamp_column in [
            "pub_utc_date",
            "pubDate",
            "date",
            "data",
            "datetime",
            "datahora",
            "data_hora",
        ]:
            if alternative_timestamp_column in normalized_dataframe.columns:
                normalized_dataframe["timestamp"] = pd.to_datetime(
                    normalized_dataframe[alternative_timestamp_column],
                    errors="coerce", dayfirst=True, format="mixed",
                )
                break
        else:
            normalized_dataframe["timestamp"] = pd.NaT

    normalized_dataframe["timestamp"] = pd.to_datetime(normalized_dataframe["timestamp"], errors="coerce")
    normalized_dataframe["date"] = normalized_dataframe["timestamp"].dt.date
    normalized_dataframe["hour"] = normalized_dataframe["timestamp"].dt.hour
    normalized_dataframe["day_of_week"] = normalized_dataframe["timestamp"].dt.day_name()

    return normalized_dataframe


def _parse_dict_like(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except Exception:
            return None
    return None


def _extract_lat_lon_from_location(value):
    parsed = _parse_dict_like(value)
    if isinstance(parsed, dict):
        try:
            return float(parsed.get("y")), float(parsed.get("x"))
        except Exception:
            return None, None
    return None, None


def extract_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    coordinates_dataframe = df.copy()

    if "lat" in coordinates_dataframe.columns and "lon" in coordinates_dataframe.columns:
        coordinates_dataframe["lat"] = pd.to_numeric(coordinates_dataframe["lat"], errors="coerce")
        coordinates_dataframe["lon"] = pd.to_numeric(coordinates_dataframe["lon"], errors="coerce")
        return coordinates_dataframe

    if "location" in coordinates_dataframe.columns:
        coords = coordinates_dataframe["location"].apply(
            lambda value: pd.Series(_extract_lat_lon_from_location(value), index=["lat", "lon"])
        )
        coordinates_dataframe["lat"] = coords["lat"]
        coordinates_dataframe["lon"] = coords["lon"]

    if "lat" not in coordinates_dataframe.columns and "y" in coordinates_dataframe.columns:
        coordinates_dataframe["lat"] = pd.to_numeric(coordinates_dataframe["y"], errors="coerce")

    if "lon" not in coordinates_dataframe.columns and "x" in coordinates_dataframe.columns:
        coordinates_dataframe["lon"] = pd.to_numeric(coordinates_dataframe["x"], errors="coerce")

    return coordinates_dataframe


def _extract_midpoint_from_line(value):
    try:
        points = value if isinstance(value, list) else ast.literal_eval(str(value))
        if not points:
            return None, None
        midpoint = points[len(points) // 2]
        return float(midpoint.get("y")), float(midpoint.get("x"))
    except Exception:
        return None, None


def extract_jams_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    jams_dataframe = df.copy()

    if "lat" in jams_dataframe.columns and "lon" in jams_dataframe.columns:
        jams_dataframe["lat"] = pd.to_numeric(jams_dataframe["lat"], errors="coerce")
        jams_dataframe["lon"] = pd.to_numeric(jams_dataframe["lon"], errors="coerce")
        if jams_dataframe["lat"].notna().any():
            return jams_dataframe

    if "line" in jams_dataframe.columns:
        coords = jams_dataframe["line"].apply(
            lambda value: pd.Series(_extract_midpoint_from_line(value), index=["lat", "lon"])
        )
        jams_dataframe["lat"] = coords["lat"]
        jams_dataframe["lon"] = coords["lon"]
        if jams_dataframe["lat"].notna().any():
            return jams_dataframe

    if "location" in jams_dataframe.columns:
        coords = jams_dataframe["location"].apply(
            lambda value: pd.Series(_extract_lat_lon_from_location(value), index=["lat", "lon"])
        )
        jams_dataframe["lat"] = coords["lat"]
        jams_dataframe["lon"] = coords["lon"]

    if "lat" not in jams_dataframe.columns and "y" in jams_dataframe.columns:
        jams_dataframe["lat"] = pd.to_numeric(jams_dataframe["y"], errors="coerce")

    if "lon" not in jams_dataframe.columns and "x" in jams_dataframe.columns:
        jams_dataframe["lon"] = pd.to_numeric(jams_dataframe["x"], errors="coerce")

    return jams_dataframe


def normalize_speed(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    normalized_dataframe = df.copy()

    if "speed" in normalized_dataframe.columns:
        normalized_dataframe["speed"] = pd.to_numeric(normalized_dataframe["speed"], errors="coerce")
        return normalized_dataframe

    for alternative_speed_column in ["speedKMH", "speedkmh", "speed_kmh", "velocity", "velocidade"]:
        if alternative_speed_column in normalized_dataframe.columns:
            normalized_dataframe["speed"] = pd.to_numeric(
                normalized_dataframe[alternative_speed_column],
                errors="coerce"
            ) / 3.6
            return normalized_dataframe

    normalized_dataframe["speed"] = float("nan")
    return normalized_dataframe


TYPE_MAP = {
    "ROAD_CLOSED": "VIA FECHADA",
    "ROAD_CLOSED_CONSTRUCTION": "VIA FECHADA",
    "ROAD_CLOSED_EVENT": "VIA FECHADA",
    "HAZARD": "PERIGO",
    "ACCIDENT": "ACIDENTE",
    "JAM": "CONGESTIONAMENTO",
    "WEATHERHAZARD": "PERIGO CLIMÁTICO",
}

SUBTYPE_MAP = {
    "ROAD_CLOSED_CONSTRUCTION": "OBRAS",
    "ROAD_CLOSED_EVENT": "EVENTO",
    "HAZARD_ON_ROAD": "PERIGO NA VIA",
    "HAZARD_ON_ROAD_POT_HOLE": "BURACO NA VIA",
    "HAZARD_ON_ROAD_ROAD_KILL": "ANIMAL NA VIA",
    "HAZARD_ON_ROAD_CAR_STOPPED": "VEÍCULO PARADO NA VIA",
    "HAZARD_ON_ROAD_CONSTRUCTION": "OBRAS NA VIA",
    "HAZARD_ON_ROAD_OBJECT": "OBJETO NA VIA",
    "HAZARD_ON_ROAD_TRAFFIC_LIGHT_FAULT": "SEMÁFORO QUEBRADO",
    "HAZARD_ON_ROAD_ICE": "PISTA COM GELO",
    "HAZARD_ON_ROAD_LANE_CLOSED": "FAIXA INTERDITADA",
    "HAZARD_ON_SHOULDER": "PERIGO NO ACOSTAMENTO",
    "HAZARD_ON_SHOULDER_CAR_STOPPED": "VEÍCULO PARADO NO ACOSTAMENTO",
    "HAZARD_ON_SHOULDER_ANIMALS": "ANIMAIS NO ACOSTAMENTO",
    "HAZARD_ON_SHOULDER_MISSING_SIGN": "SINALIZAÇÃO AUSENTE",
    "HAZARD_WEATHER": "CONDIÇÕES CLIMÁTICAS",
    "HAZARD_WEATHER_FOG": "NEBLINA",
    "HAZARD_WEATHER_HAIL": "GRANIZO",
    "HAZARD_WEATHER_HEAVY_RAIN": "CHUVA FORTE",
    "HAZARD_WEATHER_FLOOD": "INUNDAÇÃO",
    "HAZARD_WEATHER_MONSOON": "TEMPORAL",
    "HAZARD_WEATHER_TORNADO": "TORNADO",
    "HAZARD_WEATHER_HEAT_WAVE": "ONDA DE CALOR",
    "HAZARD_WEATHER_HEAVY_SNOW": "NEVE INTENSA",
    "HAZARD_WEATHER_FREEZING_RAIN": "CHUVA COM GELO",
    "ACCIDENT_MAJOR": "ACIDENTE GRAVE",
    "ACCIDENT_MINOR": "ACIDENTE LEVE",
    "JAM_HEAVY_TRAFFIC": "TRÂNSITO PESADO",
    "JAM_MODERATE_TRAFFIC": "TRÂNSITO MODERADO",
    "JAM_STAND_STILL_TRAFFIC": "TRÂNSITO PARADO",
    "JAM_LIGHT_TRAFFIC": "TRÂNSITO LEVE",
}


def translate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    translated_dataframe = df.copy()

    if "type" in translated_dataframe.columns:
        translated_dataframe["type"] = translated_dataframe["type"].replace(TYPE_MAP)

    if "subtype" in translated_dataframe.columns:
        translated_dataframe["subtype"] = translated_dataframe["subtype"].replace(SUBTYPE_MAP)

        known_values = set(SUBTYPE_MAP.values())
        unknown_mask = translated_dataframe["subtype"].notna() & ~translated_dataframe["subtype"].isin(known_values)

        translated_dataframe.loc[unknown_mask, "subtype"] = (
            translated_dataframe.loc[unknown_mask, "subtype"]
            .astype(str)
            .str.replace(
                r"^(HAZARD_ON_ROAD_|HAZARD_ON_SHOULDER_|HAZARD_WEATHER_|HAZARD_|ACCIDENT_|JAM_|ROAD_CLOSED_)",
                "",
                regex=True
            )
            .str.replace("_", " ", regex=False)
            .str.title()
        )

    return translated_dataframe


def standardize_csv_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    standardized_dataframe = df.copy()

    standardized_dataframe.columns = [
        str(column_name).strip().replace(" ", "_").replace("-", "_").replace("/", "_").lower()
        for column_name in standardized_dataframe.columns
    ]

    alias_map = {
        "latitude": "lat",
        "longitude": "lon",
        "lng": "lon",
        "long": "lon",
        "rua": "street",
        "logradouro": "street",
        "tipo": "type",
        "subtipo": "subtype",
        "natureza": "subtype",
        "velocidade": "speed",
        "velocidade_kmh": "speedkmh",
        "velocidade_km_h": "speedkmh",
        "data_hora": "timestamp",
        "datahora": "timestamp",
        "datetime": "timestamp",
        "data": "date",
    }

    standardized_dataframe = standardized_dataframe.rename(
        columns={column_name: alias_map.get(column_name, column_name) for column_name in standardized_dataframe.columns}
    )

    return standardized_dataframe


def read_local_csv(csv_path: str | Path) -> pd.DataFrame:
    csv_path = Path(csv_path)
    if not csv_path.is_absolute():
        csv_path = Path(__file__).resolve().parent / csv_path

    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

    candidate_encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252"]
    candidate_separators = [",", ";", "\t"]

    for encoding_name in candidate_encodings:
        for separator in candidate_separators:
            try:
                dataframe = pd.read_csv(
                    csv_path,
                    sep=separator,
                    encoding=encoding_name,
                    engine="python"
                )

                if dataframe is not None and not dataframe.empty and dataframe.shape[1] > 1:
                    dataframe.columns = [str(column_name).strip() for column_name in dataframe.columns]
                    return dataframe

            except Exception:
                continue

    return pd.read_csv(csv_path, sep=None, engine="python")


def filter_bbox_foz(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    bounded_dataframe = df.copy()

    if "lat" not in bounded_dataframe.columns or "lon" not in bounded_dataframe.columns:
        return pd.DataFrame()

    bounded_dataframe["lat"] = pd.to_numeric(bounded_dataframe["lat"], errors="coerce")
    bounded_dataframe["lon"] = pd.to_numeric(bounded_dataframe["lon"], errors="coerce")

    return bounded_dataframe[
        bounded_dataframe["lat"].between(LAT_MIN, LAT_MAX) &
        bounded_dataframe["lon"].between(LON_MIN, LON_MAX)
    ].copy()


@st.cache_data(show_spinner="📚 Carregando base histórica local...")
def load_and_merge_local_alert_csvs() -> pd.DataFrame:
    merged_frames = []

    for csv_file_name in CSV_FILES_TO_MERGE:
        try:
            local_dataframe = read_local_csv(csv_file_name)
            local_dataframe = standardize_csv_columns(local_dataframe)
            local_dataframe = normalize_timestamps(local_dataframe)
            local_dataframe = extract_coordinates(local_dataframe)
            local_dataframe = translate_dataframe(local_dataframe)

            if "street" not in local_dataframe.columns:
                local_dataframe["street"] = "N/A"

            local_dataframe["source_file"] = csv_file_name
            merged_frames.append(local_dataframe)

        except FileNotFoundError:
            continue
        except Exception:
            continue

    if not merged_frames:
        return pd.DataFrame()

    merged_dataframe = pd.concat(merged_frames, ignore_index=True)

    dedup_columns = [column_name for column_name in ["uuid", "pubMillis", "street", "timestamp", "type", "subtype"] if column_name in merged_dataframe.columns]
    if dedup_columns:
        merged_dataframe = merged_dataframe.drop_duplicates(subset=dedup_columns)

    merged_dataframe = filter_bbox_foz(merged_dataframe)
    merged_dataframe["year"] = pd.to_datetime(merged_dataframe["timestamp"], errors="coerce").dt.year

    return merged_dataframe


@st.cache_data(ttl=600, show_spinner="🔄 Carregando dados do Google Drive...")
def load_all_data():
    if use_drive:
        alerts_id_1 = get_latest_h5_id(FOLDER_ALERTS_ID)
        alerts_id_2 = get_latest_h5_id(FOLDER_ALERTS_ID2)
        jams_id_1 = get_latest_h5_id(FOLDER_JAMS_ID)
        jams_id_2 = get_latest_h5_id(FOLDER_JAMS_ID2)
    else:
        alerts_id_1 = alerts_id_2 = jams_id_1 = jams_id_2 = None

    # =====================================================
    # 1) ALERTAS HDF5 (FONTE PRINCIPAL)
    # =====================================================
    alert_hdf_frames = []

    if alerts_id_1:
        alert_hdf_frames.append(load_hdf_from_drive(alerts_id_1))
    if alerts_id_2:
        alert_hdf_frames.append(load_hdf_from_drive(alerts_id_2))

    if alert_hdf_frames:
        alerts_hdf_dataframe = pd.concat(alert_hdf_frames, ignore_index=True)

        dedup_columns = ["uuid"] if "uuid" in alerts_hdf_dataframe.columns else [
            column_name
            for column_name in ["pubMillis", "street", "type", "subtype"]
            if column_name in alerts_hdf_dataframe.columns
        ]

        if dedup_columns:
            alerts_hdf_dataframe = alerts_hdf_dataframe.drop_duplicates(subset=dedup_columns)
    else:
        alerts_hdf_dataframe = pd.DataFrame()

    if not alerts_hdf_dataframe.empty:
        alerts_hdf_dataframe = normalize_timestamps(alerts_hdf_dataframe)
        alerts_hdf_dataframe = extract_coordinates(alerts_hdf_dataframe)
        alerts_hdf_dataframe = translate_dataframe(alerts_hdf_dataframe)
        alerts_hdf_dataframe = filter_bbox_foz(alerts_hdf_dataframe)

        if "street" not in alerts_hdf_dataframe.columns:
            alerts_hdf_dataframe["street"] = "N/A"

        alerts_hdf_dataframe["data_source"] = "hdf5"

    # =====================================================
    # 2) CSV HISTÓRICO (SOMENTE COMPLEMENTO DOS ALERTAS)
    # =====================================================
    try:
        alerts_csv_dataframe = load_and_merge_local_alert_csvs()
    except Exception:
        alerts_csv_dataframe = pd.DataFrame()

    if not alerts_csv_dataframe.empty:
        if "street" not in alerts_csv_dataframe.columns:
            alerts_csv_dataframe["street"] = "N/A"

        alerts_csv_dataframe["data_source"] = "csv"

    # =====================================================
    # 3) ALERTAS FINAIS:
    #    HDF5 TEM PRIORIDADE, CSV COMPLEMENTA
    # =====================================================
    if alerts_hdf_dataframe.empty and alerts_csv_dataframe.empty:
        alerts_dataframe = pd.DataFrame()

    elif alerts_hdf_dataframe.empty:
        alerts_dataframe = alerts_csv_dataframe.copy()

    elif alerts_csv_dataframe.empty:
        alerts_dataframe = alerts_hdf_dataframe.copy()

    else:
        common_columns = sorted(
            set(alerts_hdf_dataframe.columns).union(set(alerts_csv_dataframe.columns))
        )

        alerts_hdf_aligned = alerts_hdf_dataframe.reindex(columns=common_columns)
        alerts_csv_aligned = alerts_csv_dataframe.reindex(columns=common_columns)

        alerts_dataframe = pd.concat(
            [alerts_hdf_aligned, alerts_csv_aligned],
            ignore_index=True
        )

        # remove duplicados mantendo prioridade do HDF5
        alerts_dataframe["source_priority"] = alerts_dataframe["data_source"].map({
            "hdf5": 0,
            "csv": 1
        }).fillna(9)

        dedup_columns = [
            column_name
            for column_name in ["uuid", "pubMillis", "timestamp", "street", "type", "subtype", "lat", "lon"]
            if column_name in alerts_dataframe.columns
        ]

        if dedup_columns:
            alerts_dataframe = (
                alerts_dataframe
                .sort_values(by=["source_priority"])
                .drop_duplicates(subset=dedup_columns, keep="first")
                .copy()
            )

        alerts_dataframe = alerts_dataframe.drop(columns=["source_priority"], errors="ignore")

    if not alerts_dataframe.empty:
        if "timestamp" in alerts_dataframe.columns:
            alerts_dataframe["timestamp"] = pd.to_datetime(alerts_dataframe["timestamp"], errors="coerce")
            alerts_dataframe["date"] = alerts_dataframe["timestamp"].dt.date
            alerts_dataframe["hour"] = alerts_dataframe["timestamp"].dt.hour
            alerts_dataframe["day_of_week"] = alerts_dataframe["timestamp"].dt.day_name()

        if "street" not in alerts_dataframe.columns:
            alerts_dataframe["street"] = "N/A"

        alerts_dataframe = filter_bbox_foz(alerts_dataframe)

    # =====================================================
    # 4) JAMS HDF5 (CONTINUAM COM PRIORIDADE TOTAL)
    # =====================================================
    jam_hdf_frames = []

    if jams_id_1:
        jam_hdf_frames.append(load_hdf_from_drive(jams_id_1))
    if jams_id_2:
        jam_hdf_frames.append(load_hdf_from_drive(jams_id_2))

    if jam_hdf_frames:
        jams_dataframe = pd.concat(jam_hdf_frames, ignore_index=True)

        dedup_columns = ["uuid"] if "uuid" in jams_dataframe.columns else [
            column_name
            for column_name in ["pubMillis", "street"]
            if column_name in jams_dataframe.columns
        ]

        if dedup_columns:
            jams_dataframe = jams_dataframe.drop_duplicates(subset=dedup_columns)
    else:
        jams_dataframe = pd.DataFrame()

    if not jams_dataframe.empty:
        jams_dataframe = normalize_timestamps(jams_dataframe)
        jams_dataframe = extract_jams_coordinates(jams_dataframe)
        jams_dataframe = normalize_speed(jams_dataframe)
        jams_dataframe = filter_bbox_foz(jams_dataframe)

        if "street" not in jams_dataframe.columns:
            jams_dataframe["street"] = "Via"

        jams_dataframe["data_source"] = "hdf5"

    return alerts_dataframe, jams_dataframe

# =========================================================
# BLOCO 3 — MAPAS E VISUALIZAÇÕES GEOESPACIAIS
# =========================================================

FOZ_LATITUDE_MIN, FOZ_LATITUDE_MAX = -25.70, -25.40
FOZ_LONGITUDE_MIN, FOZ_LONGITUDE_MAX = -54.75, -54.45


def filter_to_foz_bounding_box(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        return dataframe

    bounded_dataframe = dataframe.copy()

    if "lat" not in bounded_dataframe.columns or "lon" not in bounded_dataframe.columns:
        return pd.DataFrame()

    bounded_dataframe["lat"] = pd.to_numeric(bounded_dataframe["lat"], errors="coerce")
    bounded_dataframe["lon"] = pd.to_numeric(bounded_dataframe["lon"], errors="coerce")

    return bounded_dataframe[
        bounded_dataframe["lat"].between(FOZ_LATITUDE_MIN, FOZ_LATITUDE_MAX) &
        bounded_dataframe["lon"].between(FOZ_LONGITUDE_MIN, FOZ_LONGITUDE_MAX)
    ].copy()


def create_folium_map_with_compass(center_latitude: float, center_longitude: float, zoom_level: int = 13) -> folium.Map:
    folium_map = folium.Map(
        location=[center_latitude, center_longitude],
        zoom_start=zoom_level,
        tiles="OpenStreetMap",
        max_bounds=True,
        control_scale=False
    )

    plugins.MousePosition(
        position="topright",
        separator=" | ",
        prefix="Lat/Lon: ",
        num_digits=5
    ).add_to(folium_map)

    plugins.Fullscreen(
        position="topleft",
        title="Expandir mapa",
        title_cancel="Sair da tela cheia",
        force_separate_button=True
    ).add_to(folium_map)

    scale_control_script = """
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        setTimeout(function() {
            var maps = Object.values(window).filter(function(v) {
                return v && v._leaflet_id && typeof v.addControl === 'function';
            });

            maps.forEach(function(map) {
                L.control.scale({
                    position: 'bottomleft',
                    metric: true,
                    imperial: false,
                    maxWidth: 120
                }).addTo(map);

                var ZoomIndicator = L.Control.extend({
                    options: { position: 'bottomleft' },
                    onAdd: function(map) {
                        var div = L.DomUtil.create('div');
                        div.style.cssText = [
                            'background:white',
                            'border:2px solid #555',
                            'border-radius:6px',
                            'padding:3px 8px',
                            'font-size:12px',
                            'font-family:Arial,sans-serif',
                            'font-weight:bold',
                            'color:#333',
                            'box-shadow:0 2px 6px rgba(0,0,0,0.3)',
                            'min-width:64px',
                            'text-align:center',
                            'margin-bottom:4px'
                        ].join(';');

                        div.innerHTML = '🔍 Zoom: ' + map.getZoom();

                        map.on('zoomend', function() {
                            div.innerHTML = '🔍 Zoom: ' + map.getZoom();
                        });

                        return div;
                    }
                });

                new ZoomIndicator().addTo(map);
            });
        }, 800);
    });
    </script>
    """
    folium_map.get_root().html.add_child(folium.Element(scale_control_script))

    compass_html = """
    <div style="
        position:absolute;
        bottom:110px;
        left:10px;
        z-index:9999;
        pointer-events:none;
    ">
      <svg width="54" height="54" viewBox="0 0 54 54"
           xmlns="http://www.w3.org/2000/svg"
           style="filter:drop-shadow(0 2px 6px rgba(0,0,0,0.5));">
        <circle cx="27" cy="27" r="26" fill="white" stroke="#555" stroke-width="2"/>
        <polygon points="27,4 22,27 27,22 32,27" fill="#d32f2f"/>
        <polygon points="27,50 22,27 27,32 32,27" fill="#999"/>
        <polygon points="50,27 27,22 32,27 27,32" fill="#ccc"/>
        <polygon points="4,27 27,22 22,27 27,32" fill="#ccc"/>
        <circle cx="27" cy="27" r="4" fill="#555"/>
        <text x="27" y="16" text-anchor="middle" font-size="9" font-weight="bold"
              font-family="Arial" fill="#d32f2f">N</text>
        <text x="27" y="51" text-anchor="middle" font-size="9" font-weight="bold"
              font-family="Arial" fill="#777">S</text>
        <text x="49" y="30" text-anchor="middle" font-size="8"
              font-family="Arial" fill="#888">L</text>
        <text x="6" y="30" text-anchor="middle" font-size="8"
              font-family="Arial" fill="#888">O</text>
      </svg>
    </div>
    """
    folium_map.get_root().html.add_child(folium.Element(compass_html))

    folium.LayerControl(position="topright", collapsed=True).add_to(folium_map)
    return folium_map


def load_json_as_dataframe(dataframe_json: str) -> pd.DataFrame:
    try:
        parsed_dataframe = pd.read_json(io.StringIO(dataframe_json))
        return parsed_dataframe if parsed_dataframe is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def format_time_label(timestamp_value) -> str:
    try:
        if pd.notna(timestamp_value):
            return pd.to_datetime(timestamp_value).strftime("%H:%M")
    except Exception:
        pass
    return "--"


def generate_incidents_map(dataframe_json: str) -> folium.Map | None:
    incidents_dataframe = load_json_as_dataframe(dataframe_json)
    if incidents_dataframe.empty:
        return None

    if ("lat" not in incidents_dataframe.columns or incidents_dataframe["lat"].isna().all()) and "location" in incidents_dataframe.columns:
        def get_location_lat(location_value):
            try:
                parsed_location = ast.literal_eval(location_value) if isinstance(location_value, str) else location_value
                return float(parsed_location.get("y"))
            except Exception:
                return None

        def get_location_lon(location_value):
            try:
                parsed_location = ast.literal_eval(location_value) if isinstance(location_value, str) else location_value
                return float(parsed_location.get("x"))
            except Exception:
                return None

        incidents_dataframe["lat"] = incidents_dataframe["location"].apply(get_location_lat)
        incidents_dataframe["lon"] = incidents_dataframe["location"].apply(get_location_lon)

    if "lat" not in incidents_dataframe.columns and "y" in incidents_dataframe.columns:
        incidents_dataframe["lat"] = pd.to_numeric(incidents_dataframe["y"], errors="coerce")
    if "lon" not in incidents_dataframe.columns and "x" in incidents_dataframe.columns:
        incidents_dataframe["lon"] = pd.to_numeric(incidents_dataframe["x"], errors="coerce")

    if "lat" not in incidents_dataframe.columns or "lon" not in incidents_dataframe.columns:
        return None

    map_incidents_dataframe = filter_to_foz_bounding_box(
        incidents_dataframe.dropna(subset=["lat", "lon"])
    ).head(50)

    if map_incidents_dataframe.empty:
        return None

    incident_map = create_folium_map_with_compass(
        map_incidents_dataframe["lat"].mean(),
        map_incidents_dataframe["lon"].mean()
    )

    for _, incident_row in map_incidents_dataframe.iterrows():
        try:
            incident_type = str(incident_row.get("type", "?"))
            incident_subtype = str(incident_row.get("subtype", ""))
            street_name = str(incident_row.get("street", "N/A"))
            marker_color = get_incident_severity_color(incident_type, incident_row.get("subtype"))
            formatted_time = format_time_label(incident_row.get("timestamp"))
            latitude = float(incident_row["lat"])
            longitude = float(incident_row["lon"])

            popup_html = f"""
            <div style='min-width:200px;font-family:Arial,sans-serif;'>
                <b style='color:{marker_color};font-size:16px;'>🚨 {incident_type}</b><br>
                <b>{incident_subtype}</b><br>
                🛣️ <i>{street_name}</i><br>
                🕒 {formatted_time}<br>
                📍 {latitude:.4f}, {longitude:.4f}
            </div>
            """

            folium.CircleMarker(
                location=[latitude, longitude],
                radius=9,
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=f"{incident_type}: {street_name}",
                color=marker_color,
                fill=True,
                fillColor=marker_color,
                fillOpacity=0.8,
                weight=2
            ).add_to(incident_map)

        except Exception:
            continue

    return incident_map


def generate_jams_map(dataframe_json: str) -> folium.Map | None:
    jams_dataframe = load_json_as_dataframe(dataframe_json)
    if jams_dataframe.empty:
        return None

    if ("lat" not in jams_dataframe.columns or jams_dataframe["lat"].isna().all()) and "line" in jams_dataframe.columns:
        def get_line_midpoint(line_value):
            try:
                line_points = line_value if isinstance(line_value, list) else ast.literal_eval(str(line_value))
                if not line_points:
                    return None, None
                midpoint = line_points[len(line_points) // 2]
                return float(midpoint.get("y")), float(midpoint.get("x"))
            except Exception:
                return None, None

        extracted_coordinates = jams_dataframe["line"].apply(
            lambda line_value: pd.Series(get_line_midpoint(line_value), index=["lat", "lon"])
        )
        jams_dataframe["lat"] = extracted_coordinates["lat"]
        jams_dataframe["lon"] = extracted_coordinates["lon"]

    if ("lat" not in jams_dataframe.columns or jams_dataframe["lat"].isna().all()) and "location" in jams_dataframe.columns:
        def get_location_lat(location_value):
            try:
                parsed_location = ast.literal_eval(location_value) if isinstance(location_value, str) else location_value
                return float(parsed_location.get("y"))
            except Exception:
                return None

        def get_location_lon(location_value):
            try:
                parsed_location = ast.literal_eval(location_value) if isinstance(location_value, str) else location_value
                return float(parsed_location.get("x"))
            except Exception:
                return None

        jams_dataframe["lat"] = jams_dataframe["location"].apply(get_location_lat)
        jams_dataframe["lon"] = jams_dataframe["location"].apply(get_location_lon)

    if "lat" not in jams_dataframe.columns and "y" in jams_dataframe.columns:
        jams_dataframe["lat"] = pd.to_numeric(jams_dataframe["y"], errors="coerce")
    if "lon" not in jams_dataframe.columns and "x" in jams_dataframe.columns:
        jams_dataframe["lon"] = pd.to_numeric(jams_dataframe["x"], errors="coerce")

    if "speed" not in jams_dataframe.columns:
        for alternative_speed_column in ["speedKMH", "speedkmh", "speed_kmh", "velocity"]:
            if alternative_speed_column in jams_dataframe.columns:
                jams_dataframe["speed"] = pd.to_numeric(jams_dataframe[alternative_speed_column], errors="coerce") / 3.6
                break
        else:
            jams_dataframe["speed"] = float("nan")

    if "lat" not in jams_dataframe.columns or "lon" not in jams_dataframe.columns:
        return None

    valid_jams_dataframe = filter_to_foz_bounding_box(
        jams_dataframe.dropna(subset=["lat", "lon"])
    ).head(40)

    if valid_jams_dataframe.empty:
        return None

    jam_map = create_folium_map_with_compass(
        valid_jams_dataframe["lat"].mean(),
        valid_jams_dataframe["lon"].mean()
    )

    for _, jam_row in valid_jams_dataframe.iterrows():
        try:
            speed_meters_per_second = jam_row.get("speed", float("nan"))
            speed_kmh = float(speed_meters_per_second) * 3.6 if pd.notna(speed_meters_per_second) else 0.0
            marker_color = get_congestion_color(speed_kmh)
            street_name = str(jam_row.get("street", "Via"))
            formatted_time = format_time_label(jam_row.get("timestamp"))
            latitude = float(jam_row["lat"])
            longitude = float(jam_row["lon"])
            speed_label = f"{speed_kmh:.0f} km/h"

            popup_html = f"""
            <div style='min-width:180px;font-family:Arial,sans-serif;'>
                <b style='color:{marker_color}'>🚗 {speed_label}</b><br>
                🛣️ <i>{street_name}</i><br>
                🕒 {formatted_time}
            </div>
            """

            folium.CircleMarker(
                location=[latitude, longitude],
                radius=7,
                popup=folium.Popup(popup_html, max_width=220),
                tooltip=f"{speed_label} — {street_name}",
                color=marker_color,
                fill=True,
                fillColor=marker_color,
                fillOpacity=0.7,
                weight=2
            ).add_to(jam_map)

        except Exception:
            continue

    return jam_map


def generate_heatmap(dataframe_json: str) -> folium.Map | None:
    heatmap_dataframe = load_json_as_dataframe(dataframe_json)
    if heatmap_dataframe.empty:
        return None

    if "lat" not in heatmap_dataframe.columns and "y" in heatmap_dataframe.columns:
        heatmap_dataframe["lat"] = pd.to_numeric(heatmap_dataframe["y"], errors="coerce")
    if "lon" not in heatmap_dataframe.columns and "x" in heatmap_dataframe.columns:
        heatmap_dataframe["lon"] = pd.to_numeric(heatmap_dataframe["x"], errors="coerce")

    if "lat" not in heatmap_dataframe.columns or "lon" not in heatmap_dataframe.columns:
        return None

    bounded_heatmap_dataframe = filter_to_foz_bounding_box(
        heatmap_dataframe.dropna(subset=["lat", "lon"])
    )
    if bounded_heatmap_dataframe.empty:
        return None

    heatmap = create_folium_map_with_compass(
        bounded_heatmap_dataframe["lat"].mean(),
        bounded_heatmap_dataframe["lon"].mean()
    )

    heat_points = [[row["lat"], row["lon"]] for _, row in bounded_heatmap_dataframe.iterrows()]
    plugins.HeatMap(
        heat_points,
        radius=15,
        blur=10,
        min_opacity=0.35
    ).add_to(heatmap)

    return heatmap


# =========================================================
# BLOCO 3B — VISUALIZAÇÃO 3D SOB DEMANDA
# =========================================================
FOZ_CENTER_LAT, FOZ_CENTER_LON = -25.545, -54.585
DECK_MAP_STYLES = {"Claro": "light", "Escuro": "dark", "Ruas": "road"}


def prepare_points_for_deck(frame):
    if frame is None or frame.empty or not {"lat", "lon"}.issubset(frame.columns):
        return pd.DataFrame()
    result = frame.copy()
    result["lat"] = pd.to_numeric(result["lat"], errors="coerce")
    result["lon"] = pd.to_numeric(result["lon"], errors="coerce")
    result = result.loc[
        result["lat"].between(FOZ_LATITUDE_MIN, FOZ_LATITUDE_MAX)
        & result["lon"].between(FOZ_LONGITUDE_MIN, FOZ_LONGITUDE_MAX)
    ].copy()
    if result.empty:
        return result
    for col in ("type", "subtype", "street"):
        if col not in result:
            result[col] = "N/D"
        result[col] = result[col].fillna("N/D").astype(str)
    result["hora_label"] = (
        pd.to_datetime(result["timestamp"], errors="coerce")
        .dt.strftime("%d/%m %H:%M").fillna("N/D")
        if "timestamp" in result else "N/D"
    )
    return result


def hex_color_to_rgba(color, alpha=200):
    value = str(color).lstrip("#")
    try:
        return [int(value[i:i+2], 16) for i in (0, 2, 4)] + [alpha]
    except (ValueError, TypeError):
        return [144, 164, 174, alpha]


def colorize_3d(frame):
    if frame.empty:
        return frame
    result = frame.copy()
    result["rgb_color"] = result.apply(
        lambda row: hex_color_to_rgba(get_incident_severity_color(
            row.get("type"), row.get("subtype"))), axis=1)
    return result


def aggregate_streets_3d(frame, top_n=20):
    if frame.empty or not {"street", "lat", "lon"}.issubset(frame.columns):
        return pd.DataFrame()
    base = frame.loc[~frame["street"].fillna("N/D").astype(str).isin(
        ["NA", "nan", "", "N/A", "N/D"])]
    if base.empty:
        return pd.DataFrame()
    result = (base.groupby("street")
              .agg(ocorrencias=("street", "size"), lat=("lat", "mean"), lon=("lon", "mean"))
              .reset_index().nlargest(top_n, "ocorrencias"))
    ratio = result["ocorrencias"] / max(int(result["ocorrencias"].max()), 1)
    result["width_px"] = 2 + ratio * 10
    result["rgb_color"] = ratio.map(
        lambda x: [int(60+195*x), int(190-170*x), int(120-90*x), 210])
    return result


def build_jams_paths_3d(frame):
    if frame is None or frame.empty or "line" not in frame:
        return None
    records = []
    for _, row in frame.head(3000).iterrows():
        try:
            raw = row["line"]
            values = raw if isinstance(raw, list) else ast.literal_eval(str(raw))
            path = [[float(v["x"]), float(v["y"])] for v in values
                    if isinstance(v, dict) and "x" in v and "y" in v]
            if len(path) < 2:
                continue
            speed = pd.to_numeric(row.get("speed"), errors="coerce")
            speed_kmh = float(speed) * 3.6 if pd.notna(speed) else 0.0
            records.append({"path": path, "street": str(row.get("street", "Via")),
                            "speed_kmh": round(speed_kmh, 1),
                            "rgb_color": hex_color_to_rgba(get_congestion_color(speed_kmh), 220)})
        except (TypeError, ValueError, SyntaxError, KeyError):
            continue
    if not records:
        return None
    return pdk.Layer("PathLayer", data=pd.DataFrame(records), get_path="path",
                     get_color="rgb_color", get_width=8, width_min_pixels=3,
                     pickable=True, auto_highlight=True)


def render_3d_map(frame, jams_frame, mode, style, zoom, pitch, bearing, radius, elevation,
                  element_key="city3d", height=620, flat=False):
    if mode == "Fluxo de congestionamento":
        layer = build_jams_paths_3d(jams_frame)
        layers = [layer] if layer is not None else []
        tooltip = {"html": "<b>{street}</b><br>{speed_kmh} km/h"}
        point_count = len(jams_frame) if jams_frame is not None else 0
    else:
        points = colorize_3d(prepare_points_for_deck(frame))
        point_count = len(points)
        if len(points) > 40000:
            points = points.sample(40000, random_state=42)
            st.caption("Mapa amostrado em 40.000 registros; os indicadores usam a base inteira.")
        aggregate = aggregate_streets_3d(points, 25)
        tooltip = {"html": "<b>{street}</b><br>{ocorrencias} registros"}
        layers = []
        if mode == "Densidade hexagonal" and not points.empty:
            layers = [pdk.Layer("HexagonLayer", data=points[["lat", "lon"]],
                       get_position="[lon, lat]", radius=radius, elevation_scale=elevation,
                       extruded=True, pickable=True, auto_highlight=True)]
            tooltip = {"html": "<b>{elevationValue}</b> registros"}
        elif mode == "Colunas por via" and not aggregate.empty:
            layers = [pdk.Layer("ColumnLayer", data=aggregate,
                       get_position="[lon, lat]", get_elevation="ocorrencias",
                       elevation_scale=elevation*4, radius=90,
                       get_fill_color="rgb_color", extruded=True, pickable=True)]
        elif mode == "Pontos + calor" and not points.empty:
            layers = [pdk.Layer("HeatmapLayer", data=points[["lat", "lon"]],
                        get_position="[lon, lat]", radius_pixels=50),
                      pdk.Layer("ScatterplotLayer", data=points,
                        get_position="[lon, lat]", get_fill_color="rgb_color",
                        get_radius=50, radius_min_pixels=3, pickable=True)]
            tooltip = {"html": "<b>{type}</b><br>{subtype}<br>{street}<br>{hora_label}"}
        elif mode == "Arcos de criticidade" and not aggregate.empty:
            arcs = aggregate.copy()
            arcs["origem_lon"], arcs["origem_lat"] = FOZ_CENTER_LON, FOZ_CENTER_LAT
            layers = [pdk.Layer("ArcLayer", data=arcs,
                         get_source_position="[origem_lon, origem_lat]",
                         get_target_position="[lon, lat]", get_source_color=[37, 99, 235, 140],
                         get_target_color="rgb_color", get_width="width_px", pickable=True),
                      pdk.Layer("ColumnLayer", data=aggregate,
                         get_position="[lon, lat]", get_elevation="ocorrencias",
                         elevation_scale=elevation*3, radius=90,
                         get_fill_color="rgb_color", extruded=True, pickable=True)]
    st.caption(f"Registros com coordenadas: {point_count}. Camadas construídas: {len(layers)}.")
    if not layers:
        st.warning("Não há dados para esta camada. Amplie o período, escolha Histórico ou ative HDF5 para congestionamentos.")
        return
    deck = pdk.Deck(
        layers=layers, map_style=None,
        show_error=True,
        initial_view_state=pdk.ViewState(latitude=FOZ_CENTER_LAT,
            longitude=FOZ_CENTER_LON, zoom=zoom,
            pitch=0 if flat else pitch, bearing=0 if flat else bearing),
        tooltip=tooltip)
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:.4rem;background:#fff;border:1px solid #cbd5e1;border-radius:10px;padding:5px 12px;color:#dc2626;font-weight:800">'
        f'N <span style="display:inline-block;transform:rotate({-bearing if not flat else 0}deg);font-size:22px">↑</span></div>',
        unsafe_allow_html=True,
    )
    st.pydeck_chart(deck, width="stretch", height=height, key=element_key)
    st.caption("Camadas 2D/3D sem basemap; para ruas e bússola sobre o mapa use a opção 2D com OpenStreetMap.")


# =========================================================
# BLOCO EXTRA — PIPELINE CIENTÍFICO
# =========================================================

def build_daily_series(
    alerts_dataframe: pd.DataFrame,
    jams_dataframe: pd.DataFrame,
    selected_category: str = "TODOS",
    categoria: str | None = None
) -> pd.Series:
    if categoria is not None:
        selected_category = categoria

    source_frames = []

    if alerts_dataframe is not None and not alerts_dataframe.empty:
        alerts_series_dataframe = alerts_dataframe.copy()
        alerts_series_dataframe["origem"] = "ALERTA"
        alerts_series_dataframe["categoria_artigo"] = (
            alerts_series_dataframe["type"]
            if "type" in alerts_series_dataframe.columns
            else "ALERTA"
        )
        source_frames.append(
            alerts_series_dataframe[["timestamp", "categoria_artigo", "origem"]]
        )

    if jams_dataframe is not None and not jams_dataframe.empty:
        jams_series_dataframe = jams_dataframe.copy()
        jams_series_dataframe["origem"] = "JAM"
        jams_series_dataframe["categoria_artigo"] = "CONGESTIONAMENTO"
        source_frames.append(
            jams_series_dataframe[["timestamp", "categoria_artigo", "origem"]]
        )

    if not source_frames:
        return pd.Series(dtype=float)

    combined_series_base = pd.concat(source_frames, ignore_index=True)
    combined_series_base["timestamp"] = pd.to_datetime(
        combined_series_base["timestamp"],
        errors="coerce"
    )
    combined_series_base = combined_series_base.dropna(subset=["timestamp"]).copy()
    combined_series_base["date"] = combined_series_base["timestamp"].dt.floor("D")

    if selected_category != "TODOS":
        combined_series_base = combined_series_base[
            combined_series_base["categoria_artigo"] == selected_category
        ]

    daily_occurrence_series = combined_series_base.groupby("date").size().sort_index()

    if daily_occurrence_series.empty:
        return pd.Series(dtype=float)

    full_date_index = pd.date_range(
        daily_occurrence_series.index.min(),
        daily_occurrence_series.index.max(),
        freq="D"
    )

    daily_occurrence_series = daily_occurrence_series.reindex(
        full_date_index,
        fill_value=0
    )
    daily_occurrence_series.index.name = "date"
    daily_occurrence_series.name = "ocorrencias"

    return daily_occurrence_series


def run_stl_analysis(time_series: pd.Series, period: int = 7):
    try:
        from statsmodels.tsa.seasonal import STL
        stl_model = STL(time_series, period=period, robust=True)
        stl_result = stl_model.fit()
        return stl_result
    except Exception:
        return None


def run_pelt_analysis(time_series: pd.Series, model: str = "l2", min_size: int = 7, jump: int = 1, pen: float = 3.0):
    try:
        import ruptures as rpt
        signal_values = time_series.values.astype(float)
        pelt_model = rpt.Pelt(model=model, min_size=min_size, jump=jump).fit(signal_values)
        breakpoints = pelt_model.predict(pen=pen)
        return breakpoints
    except Exception:
        return []


def build_descriptive_table(alerts_dataframe: pd.DataFrame, jams_dataframe: pd.DataFrame) -> pd.DataFrame:
    descriptive_blocks = []

    if alerts_dataframe is not None and not alerts_dataframe.empty:
        processed_alerts = alerts_dataframe.copy()
        processed_alerts["timestamp"] = pd.to_datetime(processed_alerts["timestamp"], errors="coerce")
        processed_alerts = processed_alerts.dropna(subset=["timestamp"])
        processed_alerts["date"] = processed_alerts["timestamp"].dt.date
        processed_alerts["hour"] = processed_alerts["timestamp"].dt.hour

        daily_counts = processed_alerts.groupby(["date", "type"]).size().reset_index(name="n")
        hourly_peaks = processed_alerts.groupby(["type", "hour"]).size().reset_index(name="n_hora")
        hourly_peak_index = hourly_peaks.groupby("type")["n_hora"].idxmax()
        peak_hour_by_type = hourly_peaks.loc[hourly_peak_index][["type", "hour"]].rename(columns={"hour": "Hora_Pico"})

        alert_summary = daily_counts.groupby("type")["n"].agg(
            Total_Alertas="sum",
            Media_Diaria="mean",
            Desvio_Padrao="std"
        ).reset_index().rename(columns={"type": "Tipo"})

        alert_summary = alert_summary.merge(
            peak_hour_by_type,
            left_on="Tipo",
            right_on="type",
            how="left"
        ).drop(columns=["type"], errors="ignore")

        descriptive_blocks.append(alert_summary)

    if jams_dataframe is not None and not jams_dataframe.empty:
        processed_jams = jams_dataframe.copy()
        processed_jams["timestamp"] = pd.to_datetime(processed_jams["timestamp"], errors="coerce")
        processed_jams = processed_jams.dropna(subset=["timestamp"])
        processed_jams["date"] = processed_jams["timestamp"].dt.date
        processed_jams["hour"] = processed_jams["timestamp"].dt.hour

        daily_jam_counts = processed_jams.groupby("date").size().reset_index(name="n")
        jam_hourly_peak = processed_jams.groupby("hour").size().reset_index(name="n_hora")
        peak_hour = int(jam_hourly_peak.loc[jam_hourly_peak["n_hora"].idxmax(), "hour"]) if not jam_hourly_peak.empty else None

        jam_summary = pd.DataFrame([{
            "Tipo": "CONGESTIONAMENTO",
            "Total_Alertas": int(daily_jam_counts["n"].sum()) if not daily_jam_counts.empty else 0,
            "Media_Diaria": float(daily_jam_counts["n"].mean()) if not daily_jam_counts.empty else 0.0,
            "Desvio_Padrao": float(daily_jam_counts["n"].std()) if not daily_jam_counts.empty else 0.0,
            "Hora_Pico": peak_hour
        }])
        descriptive_blocks.append(jam_summary)

    if not descriptive_blocks:
        return pd.DataFrame(columns=["Tipo", "Total_Alertas", "Media_Diaria", "Desvio_Padrao", "Hora_Pico"])

    descriptive_table = pd.concat(descriptive_blocks, ignore_index=True)
    descriptive_table["Media_Diaria"] = descriptive_table["Media_Diaria"].round(2)
    descriptive_table["Desvio_Padrao"] = descriptive_table["Desvio_Padrao"].round(2)
    return descriptive_table


# =========================================================
# BLOCO 4 — SIDEBAR, CARGA OPERACIONAL E FILTROS
# =========================================================

current_foz_datetime = get_current_foz_time()

st.sidebar.header("⚙️ Controles")
st.sidebar.markdown("### ⏳ Status da Sessão")
st.sidebar.markdown(
    f"🕒 **Hora atual (Foz):** `{current_foz_datetime.strftime('%d/%m/%Y %H:%M:%S')}`"
)
st.sidebar.metric("⏳ Tempo online", f"{session_elapsed_total_seconds // 3600}h:{(session_elapsed_total_seconds % 3600) // 60:02d}m")
st.sidebar.metric("⏳ Próximo ciclo", f"{minutes_until_next_refresh}:{remaining_seconds:02d}")
st.sidebar.metric("🔄 Atualizações", st.session_state.manual_refreshes)

if st.sidebar.button("🔄 ATUALIZAR DADOS AGORA", width="stretch", type="primary"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.manual_refreshes += 1
    st.rerun()

st.sidebar.divider()

use_drive = st.sidebar.toggle("☁️ Ler HDF5 do Drive", value=False, key="use_drive")
try:
    raw_alerts_dataframe, raw_jams_dataframe = load_all_data()
except Exception as error:
    st.error(f"❌ Erro ao conectar com o Google Drive: {error}")
    st.markdown("""
    **Verifique:**
    - As credenciais `gcp_service_account` estão configuradas em **Settings → Secrets**
    - A Service Account tem acesso às pastas do Drive
    - Os arquivos `.h5` existem nas pastas configuradas
    """)
    st.stop()

for base_dataframe in [raw_alerts_dataframe, raw_jams_dataframe]:
    if not base_dataframe.empty and "timestamp" in base_dataframe.columns:
        if "hour" not in base_dataframe.columns:
            base_dataframe["hour"] = pd.to_datetime(base_dataframe["timestamp"], errors="coerce").dt.hour
        if "date" not in base_dataframe.columns:
            base_dataframe["date"] = pd.to_datetime(base_dataframe["timestamp"], errors="coerce").dt.date


def apply_base_time_filter(dataframe: pd.DataFrame, selected_date, selected_hour_range: tuple[int, int]) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        return pd.DataFrame()
    if "date" not in dataframe.columns or "hour" not in dataframe.columns:
        return pd.DataFrame()

    return dataframe[
        (dataframe["date"] == selected_date) &
        (dataframe["hour"].between(selected_hour_range[0], selected_hour_range[1]))
    ].copy()


def get_clean_unique_values(series: pd.Series, invalid_values=None):
    if series is None:
        return []
    invalid_values = set(invalid_values or [])
    normalized_values = series.dropna().astype(str).str.strip()
    normalized_values = normalized_values[~normalized_values.isin(invalid_values)]
    return sorted(normalized_values.unique().tolist())


def classify_traffic_status(mean_speed_kmh: float) -> str:
    if mean_speed_kmh < 20:
        return "🔴 Crítico"
    elif mean_speed_kmh < 40:
        return "🟠 Lento"
    elif mean_speed_kmh < 60:
        return "🟡 Moderado"
    return "🟢 Fluindo"


st.sidebar.divider()
st.sidebar.subheader("🧊 Controles 3D")
deck_map_style_label = st.sidebar.selectbox("Estilo de fundo 3D", list(DECK_MAP_STYLES), index=1, key="deck_style")
deck_pitch = st.sidebar.slider("Inclinação", 0, 70, 50, 5, key="deck_pitch")
deck_bearing = st.sidebar.slider("Rotação", -180, 180, 0, 10, key="deck_bearing")
deck_zoom = st.sidebar.slider("Zoom", 10.0, 17.0, 12.2, 0.2, key="deck_zoom")
deck_hex_radius = st.sidebar.slider("Raio hexagonal (m)", 60, 400, 140, 20, key="deck_radius")
deck_elevation_scale = st.sidebar.slider("Escala de altura", 5, 60, 20, 5, key="deck_height")

st.sidebar.subheader("🔍 Filtros")
today_foz_date = current_foz_datetime.date()

available_dates = set()
if not raw_alerts_dataframe.empty and "date" in raw_alerts_dataframe.columns:
    available_dates.update(pd.to_datetime(raw_alerts_dataframe["date"]).dt.date.unique())
if not raw_jams_dataframe.empty and "date" in raw_jams_dataframe.columns:
    available_dates.update(pd.to_datetime(raw_jams_dataframe["date"]).dt.date.unique())

available_dates = {date for date in available_dates if pd.notna(date)}
if available_dates:
    minimum_available_date = min(available_dates)
    maximum_available_date = max(available_dates)
    default_selected_date = today_foz_date if today_foz_date in available_dates else maximum_available_date
else:
    minimum_available_date = maximum_available_date = default_selected_date = today_foz_date

selected_date = st.sidebar.date_input(
    "📅 Data",
    value=default_selected_date,
    min_value=minimum_available_date,
    max_value=max(maximum_available_date, today_foz_date),
)

selected_hour_range = st.sidebar.slider("🕒 Horário", min_value=0, max_value=23, value=(0, 23))

alerts_filtered_by_date = apply_base_time_filter(raw_alerts_dataframe, selected_date, selected_hour_range)
jams_filtered_by_date = apply_base_time_filter(raw_jams_dataframe, selected_date, selected_hour_range)

available_incident_types = (
    get_clean_unique_values(alerts_filtered_by_date["type"])
    if not alerts_filtered_by_date.empty and "type" in alerts_filtered_by_date.columns
    else []
)

selected_incident_types = st.sidebar.multiselect(
    "🚨 Tipo",
    options=available_incident_types,
    default=available_incident_types
)

incident_subtype_base = alerts_filtered_by_date.copy()
if selected_incident_types and "type" in incident_subtype_base.columns:
    incident_subtype_base = incident_subtype_base[incident_subtype_base["type"].isin(selected_incident_types)]

available_incident_subtypes = (
    get_clean_unique_values(incident_subtype_base["subtype"], invalid_values=["nan", ""])
    if not incident_subtype_base.empty and "subtype" in incident_subtype_base.columns
    else []
)

selected_incident_subtypes = st.sidebar.multiselect(
    "🔍 Natureza",
    options=available_incident_subtypes,
    default=available_incident_subtypes
)

street_filter_base = incident_subtype_base.copy()
if selected_incident_subtypes and "subtype" in street_filter_base.columns:
    street_filter_base = street_filter_base[street_filter_base["subtype"].isin(selected_incident_subtypes)]

available_streets = (
    get_clean_unique_values(street_filter_base["street"], invalid_values=["NA", "nan", "", "N/A"])
    if not street_filter_base.empty and "street" in street_filter_base.columns
    else []
)

selected_street = st.sidebar.selectbox("🛣️ Rua", options=["(Todas)"] + available_streets, index=0)
selected_street = "" if selected_street == "(Todas)" else selected_street

minimum_speed_kmh = 0.0
maximum_speed_kmh = 120.0

if not jams_filtered_by_date.empty and "speed" in jams_filtered_by_date.columns:
    speed_values_kmh = jams_filtered_by_date["speed"].dropna() * 3.6
    if not speed_values_kmh.empty:
        minimum_speed_kmh = max(0.0, float(speed_values_kmh.min()))
        maximum_speed_kmh = max(5.0, float(speed_values_kmh.max()))

selected_speed_range_kmh = st.sidebar.slider(
    "🚗 Velocidade (km/h)",
    min_value=0.0,
    max_value=max(120.0, maximum_speed_kmh),
    value=(minimum_speed_kmh, max(minimum_speed_kmh, min(120.0, maximum_speed_kmh))),
    step=5.0,
)

if (
    not jams_filtered_by_date.empty
    and "speed" in jams_filtered_by_date.columns
    and jams_filtered_by_date["speed"].notna().any()
):
    mean_speed_kmh = jams_filtered_by_date["speed"].mean() * 3.6
    total_jams_in_period = len(jams_filtered_by_date)
    traffic_status_label = classify_traffic_status(mean_speed_kmh)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 Congestionamentos em** " + selected_date.strftime("%d/%m"))
    st.sidebar.metric("Vel. Média", f"{mean_speed_kmh:.1f} km/h", delta=traffic_status_label)
    st.sidebar.metric("Total de Jams", total_jams_in_period)
else:
    st.sidebar.info(f"Sem dados de congestionamento em {selected_date.strftime('%d/%m')}.")

filtered_alerts_dataframe = apply_base_time_filter(raw_alerts_dataframe, selected_date, selected_hour_range)

if not filtered_alerts_dataframe.empty:
    if selected_incident_types and "type" in filtered_alerts_dataframe.columns:
        filtered_alerts_dataframe = filtered_alerts_dataframe[filtered_alerts_dataframe["type"].isin(selected_incident_types)]
    if selected_incident_subtypes and "subtype" in filtered_alerts_dataframe.columns:
        filtered_alerts_dataframe = filtered_alerts_dataframe[filtered_alerts_dataframe["subtype"].isin(selected_incident_subtypes)]
    if selected_street and "street" in filtered_alerts_dataframe.columns:
        filtered_alerts_dataframe = filtered_alerts_dataframe[filtered_alerts_dataframe["street"] == selected_street]

filtered_jams_dataframe = apply_base_time_filter(raw_jams_dataframe, selected_date, selected_hour_range)

if not filtered_jams_dataframe.empty and "speed" in filtered_jams_dataframe.columns:
    filtered_jams_dataframe = filtered_jams_dataframe[
        (filtered_jams_dataframe["speed"].fillna(0) * 3.6).between(
            selected_speed_range_kmh[0],
            selected_speed_range_kmh[1]
        )
    ]

dashboard_alerts_base = filtered_alerts_dataframe.copy()
dashboard_jams_base = filtered_jams_dataframe.copy()


# =========================================================
# UPGRADE — ALGORITMO MULTICRITÉRIO (MCDA) E MODELO PREDITIVO
# =========================================================

def calculate_road_criticality(alerts_dataframe, jams_dataframe):
    if jams_dataframe.empty:
        return pd.DataFrame(columns=["street", "Volume_Jams", "Atraso_Medio_Seg", "Criticidade_Index"])

    aggregation_rules = {"Volume_Jams": ("street", "count")}
    if "delay" in jams_dataframe.columns:
        aggregation_rules["Atraso_Medio_Seg"] = ("delay", "mean")
    if "length" in jams_dataframe.columns:
        aggregation_rules["Comprimento_Medio_M"] = ("length", "mean")

    street_criticality_dataframe = jams_dataframe.groupby("street").agg(**aggregation_rules).reset_index()

    if "Atraso_Medio_Seg" not in street_criticality_dataframe.columns:
        street_criticality_dataframe["Atraso_Medio_Seg"] = 0.0
    if "Comprimento_Medio_M" not in street_criticality_dataframe.columns:
        street_criticality_dataframe["Comprimento_Medio_M"] = 0.0

    maximum_jam_volume = street_criticality_dataframe["Volume_Jams"].max() or 1
    maximum_average_delay = street_criticality_dataframe["Atraso_Medio_Seg"].max() or 1

    street_criticality_dataframe["Criticidade_Index"] = (
        (street_criticality_dataframe["Volume_Jams"] / maximum_jam_volume) * 0.4 +
        (street_criticality_dataframe["Atraso_Medio_Seg"] / maximum_average_delay) * 0.6
    ) * 100

    return street_criticality_dataframe.sort_values("Criticidade_Index", ascending=False)


def predict_traffic_delay_impact(queue_length_meters: float) -> float:
    angular_coefficient = 0.15
    intercept_seconds = 12.0
    return (queue_length_meters * angular_coefficient) + intercept_seconds


road_criticality_dataframe = calculate_road_criticality(dashboard_alerts_base, dashboard_jams_base)


# =========================================================
# BLOCO 5 — CABEÇALHO, RESUMO, KPIs E INDICADORES
# =========================================================

def classify_risk_level(total_incidents: int):
    if total_incidents >= 15:
        return "Crítico", "🔴", "Volume muito alto de incidentes no período filtrado."
    elif total_incidents >= 10:
        return "Alto", "🟠", "Quantidade elevada de ocorrências; atenção operacional recomendada."
    elif total_incidents >= 5:
        return "Moderado", "🟡", "Ocorrências acima do nível de normalidade para o recorte atual."
    return "Baixo", "🟢", "Baixa pressão operacional no período filtrado."


def classify_flow_status(mean_speed_kmh: float):
    if mean_speed_kmh < 20:
        return "Travado", "🔴", "Fluxo muito comprometido, com forte retenção nas vias."
    elif mean_speed_kmh < 40:
        return "Lento", "🟠", "Tráfego com perda relevante de fluidez."
    elif mean_speed_kmh < 60:
        return "Moderado", "🟡", "Fluxo estável, mas com redução perceptível de velocidade."
    return "Fluindo", "🟢", "Boas condições de circulação no recorte selecionado."


def classify_overall_road_status(total_incidents: int) -> str:
    if total_incidents >= 15:
        return "🚫 Crítico"
    elif total_incidents >= 5:
        return "⚠️ Moderado"
    return "✅ Normal"


def build_selection_label(selected_values, total_available, singular_name, plural_name):
    if not selected_values or len(selected_values) == total_available:
        return "Todos" if plural_name == "tipos" else "Todas"
    if len(selected_values) <= 2:
        return ", ".join(selected_values)
    return f"{len(selected_values)} {plural_name}"


st.markdown(f"""
<div style="
    background: linear-gradient(135deg,
        rgba(30,41,59,0.95) 0%,
        rgba(15,23,42,0.98) 50%,
        rgba(17,24,39,0.95) 100%);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
    position: relative;
    overflow: hidden;
">
  <div style="
      position:absolute; top:-60px; right:-60px;
      width:200px; height:200px;
      background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
      pointer-events:none;
  "></div>
  <div style="
      display:inline-flex; align-items:center; gap:6px;
      background: rgba(34,197,94,0.12);
      border: 1px solid rgba(34,197,94,0.25);
      border-radius: 20px;
      padding: 4px 12px;
      font-size: 0.72rem;
      font-weight: 600;
      color: #4ade80;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      margin-bottom: 0.75rem;
  ">
      <span style="width:7px;height:7px;background:#4ade80;border-radius:50%;
                   animation:pulse 2s infinite;display:inline-block;"></span>
      SISTEMA ATIVO — DADOS REAIS
  </div>
  <h1 style="
      margin: 0 0 0.25rem 0;
      font-size: clamp(1.4rem, 3vw, 2rem);
      font-weight: 800;
      color: #f1f5f9;
      letter-spacing: -0.5px;
      line-height: 1.2;
  ">
      <img src="https://cdn.simpleicons.org/waze/33CCC5" width="36" height="36"
           style="vertical-align:middle;margin-right:8px;" alt="Waze for Cities">
      Monitoramento de Tráfego
      <span style="
          background: linear-gradient(135deg, #3b82f6, #60a5fa);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
      "> — Foz do Iguaçu</span>
  </h1>
  <p style="
      margin: 0.4rem 0 0 0;
      color: #64748b;
      font-size: 0.88rem;
      font-weight: 400;
  ">
      📅 {selected_date.strftime('%d/%m/%Y')}
      &nbsp;·&nbsp;
      🕒 Hora local: <strong style="color:#94a3b8;">{current_foz_datetime.strftime('%H:%M:%S')}</strong>
      &nbsp;·&nbsp;
      🔄 Dados atualizados pelo botão na lateral
  </p>
  <div style="
      margin-top: 1rem;
      padding-top: 0.75rem;
      border-top: 1px solid rgba(255,255,255,0.06);
      font-size: 0.72rem;
      color: #475569;
      display: flex;
      gap: 1.5rem;
      flex-wrap: wrap;
      align-items: center;
  ">
      <span>🔬 <strong style="color:#64748b;">GPMME</strong> — Grupo de Pesquisa em Mobilidade e Matriz Energética</span>
      <span>🧪 <strong style="color:#64748b;">LAGGRA</strong> — Lab. de Geologia, Geotecnia e Recuperação Ambiental</span>
      <span>💻 <strong style="color:#64748b;">LACA</strong> — Laboratório de Computação Aplicada</span>
      <span style="margin-left:auto; color:#334155;">UNILA · FOZ DO IGUAÇU</span>
  </div>
</div>
<style>
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.4; }}
}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:12px;
    padding:16px 18px;
    margin-bottom:16px;
    box-shadow:0 1px 4px rgba(15,23,42,0.04);
">
    <div style="font-size:15px;font-weight:700;color:#0F172A;margin-bottom:6px;">
        Sobre o Sistema
    </div>
    <div style="font-size:14px;line-height:1.7;color:#475569;">
        Este sistema mostra o monitoramento de incidentes viários e congestionamentos em Foz do Iguaçu com base em dados do Waze.
        Os painéis reúnem mapas, filtros e indicadores para apoiar análises espaciais, temporais e históricas da mobilidade urbana.
        Os dados podem ser explorados por tipo de ocorrência, natureza, via, horário e intensidade do tráfego.
    </div>
</div>
""", unsafe_allow_html=True)

selected_type_label = build_selection_label(selected_incident_types, len(available_incident_types), "tipo", "tipos")
selected_subtype_label = build_selection_label(selected_incident_subtypes, len(available_incident_subtypes), "natureza", "naturezas")

filter_col_1, filter_col_2, filter_col_3, filter_col_4, filter_col_5 = st.columns(5)
filter_col_1.metric("📅 Data", selected_date.strftime("%d/%m/%Y"))
filter_col_2.metric("🚨 Tipo", selected_type_label)
filter_col_3.metric("🔍 Natureza", selected_subtype_label)
filter_col_4.metric("Road", selected_street if selected_street else "Todas")
filter_col_5.metric("🕒 Horário", f"{selected_hour_range[0]:02d}h – {selected_hour_range[1]:02d}h")

st.caption(
    f"🔍 Filtros ativos → {len(filtered_alerts_dataframe)} incidente(s) exibidos em "
    f"{selected_date.strftime('%d/%m/%Y')} | Congestionamentos: {len(filtered_jams_dataframe)}"
)

st.markdown("---")
st.subheader("📊 Resumo Estatístico")

total_incidents_in_period = len(filtered_alerts_dataframe)
total_accidents_in_period = (
    len(filtered_alerts_dataframe[filtered_alerts_dataframe["type"] == "ACIDENTE"])
    if not filtered_alerts_dataframe.empty and "type" in filtered_alerts_dataframe.columns
    else 0
)

mean_speed_in_period_kmh = (
    filtered_jams_dataframe["speed"].mean() * 3.6
    if not filtered_jams_dataframe.empty
    and "speed" in filtered_jams_dataframe.columns
    and filtered_jams_dataframe["speed"].notna().any()
    else 0
)

overall_road_status = classify_overall_road_status(total_incidents_in_period)

kpi_col_1, kpi_col_2, kpi_col_3, kpi_col_4 = st.columns(4)
kpi_col_1.metric("Total Alertas", total_incidents_in_period)
kpi_col_2.metric("Acidentes", total_accidents_in_period)
kpi_col_3.metric("Vel. Média", f"{mean_speed_in_period_kmh:.1f} km/h")
kpi_col_4.metric("Status da Via", overall_road_status)

most_critical_street = road_criticality_dataframe.iloc[0]["street"] if not road_criticality_dataframe.empty else "Nenhuma"
st.caption(f"🔴 Gargalo Operacional Prioritário (MCDA): **{most_critical_street}**")

st.markdown("---")
st.subheader("📈 Indicadores de Gravidade")

risk_level_name, risk_level_icon, risk_level_description = classify_risk_level(total_incidents_in_period)
flow_status_name, flow_status_icon, flow_status_description = classify_flow_status(mean_speed_in_period_kmh)

risk_col, flow_col = st.columns(2)

with risk_col:
    with st.container(border=True):
        st.markdown(f"### {risk_level_icon} Risco operacional")
        st.metric("Classificação", risk_level_name)
        st.metric("Incidentes no período", total_incidents_in_period)
        st.caption(risk_level_description)
        st.write(f"🚨 Acidentes: {total_accidents_in_period}")
        st.write(f"📍 Status geral: {overall_road_status}")
        st.caption("Faixas: 0–4 = Baixo · 5–9 = Moderado · 10–14 = Alto · 15+ = Crítico")

with flow_col:
    with st.container(border=True):
        st.markdown(f"### {flow_status_icon} Condição do tráfego")
        st.metric("Classificação", flow_status_name)
        st.metric("Velocidade média", f"{mean_speed_in_period_kmh:.1f} km/h")
        st.caption(flow_status_description)
        st.write(f"🚗 Média observada: {mean_speed_in_period_kmh:.1f} km/h")
        st.write(f"📍 Total de jams: {len(filtered_jams_dataframe)}")
        st.caption("Faixas: <20 = Travado · 20–39 = Lento · 40–59 = Moderado · 60+ = Fluindo")

st.caption(
    "Os indicadores acima resumem o comportamento do período filtrado: "
    "o risco operacional considera o volume de incidentes, enquanto a condição "
    "do tráfego é baseada na velocidade média observada nos congestionamentos."
)

st.markdown("---")
# =========================================================
# =========================================================
# BLOCO EXTRA — ANÁLISE TEMPORAL ANUAL DE BURACOS (PLANILHA)
# =========================================================

ANNUAL_YEARS_DEFAULT = [2024, 2025, 2026]
TOP_STREETS_PER_YEAR = 5
MAX_MARKERS_PER_STREET = 200
NOMINATIM_SLEEP_SECONDS = 1.2
LOCAL_ALERT_CSV_PATH = "Waze for Cities Data _ tabelas alertas_20240101_20260306.csv"

POTHOLE_SUBTYPE_VALUES = {
    "BURACO NA VIA",
    "HAZARD_ON_ROAD_POT_HOLE"
}


def standardize_alert_spreadsheet_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        return pd.DataFrame()

    standardized_dataframe = dataframe.copy()
    standardized_dataframe.columns = [str(column_name).strip() for column_name in standardized_dataframe.columns]

    rename_map = {}

    for original_column_name in standardized_dataframe.columns:
        normalized_column_name = (
            str(original_column_name)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
        )

        if normalized_column_name == "street":
            rename_map[original_column_name] = "street"
        elif normalized_column_name == "city":
            rename_map[original_column_name] = "city"
        elif normalized_column_name == "location":
            rename_map[original_column_name] = "location"
        elif normalized_column_name == "subtype":
            rename_map[original_column_name] = "subtype"
        elif normalized_column_name == "type":
            rename_map[original_column_name] = "type"
        elif normalized_column_name in ["date", "data"]:
            rename_map[original_column_name] = "date_text"
        elif normalized_column_name == "pubmillis":
            rename_map[original_column_name] = "pubMillis"
        elif normalized_column_name == "timestamp":
            rename_map[original_column_name] = "timestamp"
        elif normalized_column_name == "latitude":
            rename_map[original_column_name] = "latitude"
        elif normalized_column_name == "longitude":
            rename_map[original_column_name] = "longitude"
        elif normalized_column_name == "lat":
            rename_map[original_column_name] = "lat"
        elif normalized_column_name in ["lon", "lng", "long"]:
            rename_map[original_column_name] = "lon"
        elif normalized_column_name == "x":
            rename_map[original_column_name] = "x"
        elif normalized_column_name == "y":
            rename_map[original_column_name] = "y"

    standardized_dataframe = standardized_dataframe.rename(columns=rename_map)
    return standardized_dataframe


def parse_portuguese_date(date_value):
    if pd.isna(date_value):
        return pd.NaT

    date_text = str(date_value).strip()

    month_map = {
        "jan.": "Jan",
        "fev.": "Feb",
        "mar.": "Mar",
        "abr.": "Apr",
        "maio": "May",
        "mai.": "May",
        "jun.": "Jun",
        "jul.": "Jul",
        "ago.": "Aug",
        "set.": "Sep",
        "out.": "Oct",
        "nov.": "Nov",
        "dez.": "Dec"
    }

    for month_pt, month_en in month_map.items():
        date_text = date_text.replace(month_pt, month_en)

    return pd.to_datetime(date_text, format="%d de %b de %Y", errors="coerce")


def normalize_spreadsheet_timestamps(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        return pd.DataFrame()

    normalized_dataframe = dataframe.copy()

    if "pubMillis" in normalized_dataframe.columns:
        normalized_dataframe["timestamp"] = pd.to_datetime(
            normalized_dataframe["pubMillis"],
            unit="ms",
            errors="coerce",
            utc=True
        ).dt.tz_convert("America/Sao_Paulo").dt.tz_localize(None)

    elif "timestamp" in normalized_dataframe.columns:
        normalized_dataframe["timestamp"] = pd.to_datetime(
            normalized_dataframe["timestamp"],
            errors="coerce"
        )

    elif "date_text" in normalized_dataframe.columns:
        normalized_dataframe["timestamp"] = normalized_dataframe["date_text"].apply(parse_portuguese_date)

    else:
        normalized_dataframe["timestamp"] = pd.NaT

    normalized_dataframe = normalized_dataframe.dropna(subset=["timestamp"]).copy()

    if normalized_dataframe.empty:
        return normalized_dataframe

    normalized_dataframe["date"] = normalized_dataframe["timestamp"].dt.date
    normalized_dataframe["hour"] = normalized_dataframe["timestamp"].dt.hour
    normalized_dataframe["day_of_week"] = normalized_dataframe["timestamp"].dt.day_name()
    normalized_dataframe["year"] = normalized_dataframe["timestamp"].dt.year

    return normalized_dataframe


def extract_wkt_point_coordinates(location_value):
    if location_value is None or (not isinstance(location_value, (dict, list, tuple)) and pd.isna(location_value)):
        return None, None

    location_text = str(location_value).strip()
    point_match = re.search(r"Point\(([-+]?\d+\.?\d*)\s+([-+]?\d+\.?\d*)\)", location_text)

    if point_match:
        longitude = float(point_match.group(1))
        latitude = float(point_match.group(2))
        return latitude, longitude

    return None, None


def extract_dict_point_coordinates(location_value):
    if location_value is None or (not isinstance(location_value, (dict, list, tuple)) and pd.isna(location_value)):
        return None, None

    if isinstance(location_value, dict):
        try:
            return float(location_value.get("y")), float(location_value.get("x"))
        except Exception:
            return None, None

    if isinstance(location_value, str):
        try:
            parsed_value = ast.literal_eval(location_value)
            if isinstance(parsed_value, dict):
                return float(parsed_value.get("y")), float(parsed_value.get("x"))
        except Exception:
            return None, None

    return None, None


def extract_hybrid_location_coordinates(location_value):
    latitude, longitude = extract_wkt_point_coordinates(location_value)
    if latitude is not None and longitude is not None:
        return latitude, longitude

    latitude, longitude = extract_dict_point_coordinates(location_value)
    if latitude is not None and longitude is not None:
        return latitude, longitude

    return None, None


def normalize_annual_analysis_coordinates(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        return pd.DataFrame()

    normalized_dataframe = dataframe.copy()

    if "latitude" in normalized_dataframe.columns:
        normalized_dataframe["latitude"] = pd.to_numeric(normalized_dataframe["latitude"], errors="coerce")

    if "longitude" in normalized_dataframe.columns:
        normalized_dataframe["longitude"] = pd.to_numeric(normalized_dataframe["longitude"], errors="coerce")

    if "lat" in normalized_dataframe.columns:
        if "latitude" not in normalized_dataframe.columns:
            normalized_dataframe["latitude"] = pd.to_numeric(normalized_dataframe["lat"], errors="coerce")
        else:
            normalized_dataframe["latitude"] = normalized_dataframe["latitude"].fillna(
                pd.to_numeric(normalized_dataframe["lat"], errors="coerce")
            )

    if "lon" in normalized_dataframe.columns:
        if "longitude" not in normalized_dataframe.columns:
            normalized_dataframe["longitude"] = pd.to_numeric(normalized_dataframe["lon"], errors="coerce")
        else:
            normalized_dataframe["longitude"] = normalized_dataframe["longitude"].fillna(
                pd.to_numeric(normalized_dataframe["lon"], errors="coerce")
            )

    if "y" in normalized_dataframe.columns:
        if "latitude" not in normalized_dataframe.columns:
            normalized_dataframe["latitude"] = pd.to_numeric(normalized_dataframe["y"], errors="coerce")
        else:
            normalized_dataframe["latitude"] = normalized_dataframe["latitude"].fillna(
                pd.to_numeric(normalized_dataframe["y"], errors="coerce")
            )

    if "x" in normalized_dataframe.columns:
        if "longitude" not in normalized_dataframe.columns:
            normalized_dataframe["longitude"] = pd.to_numeric(normalized_dataframe["x"], errors="coerce")
        else:
            normalized_dataframe["longitude"] = normalized_dataframe["longitude"].fillna(
                pd.to_numeric(normalized_dataframe["x"], errors="coerce")
            )

    if "location" in normalized_dataframe.columns:
        extracted_coordinates = normalized_dataframe["location"].apply(
            lambda location_value: pd.Series(
                extract_hybrid_location_coordinates(location_value),
                index=["latitude_from_location", "longitude_from_location"]
            )
        )

        if "latitude" not in normalized_dataframe.columns:
            normalized_dataframe["latitude"] = extracted_coordinates["latitude_from_location"]
        else:
            normalized_dataframe["latitude"] = normalized_dataframe["latitude"].fillna(
                extracted_coordinates["latitude_from_location"]
            )

        if "longitude" not in normalized_dataframe.columns:
            normalized_dataframe["longitude"] = extracted_coordinates["longitude_from_location"]
        else:
            normalized_dataframe["longitude"] = normalized_dataframe["longitude"].fillna(
                extracted_coordinates["longitude_from_location"]
            )

    if "latitude" in normalized_dataframe.columns:
        normalized_dataframe["latitude"] = pd.to_numeric(normalized_dataframe["latitude"], errors="coerce")

    if "longitude" in normalized_dataframe.columns:
        normalized_dataframe["longitude"] = pd.to_numeric(normalized_dataframe["longitude"], errors="coerce")

    return normalized_dataframe


def extract_spreadsheet_coordinates(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        return pd.DataFrame()

    return normalize_annual_analysis_coordinates(dataframe)


def normalize_pothole_subtype_labels(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        return pd.DataFrame()

    normalized_dataframe = dataframe.copy()

    if "subtype" in normalized_dataframe.columns:
        normalized_dataframe["subtype"] = normalized_dataframe["subtype"].replace({
            "HAZARD_ON_ROAD_POT_HOLE": "BURACO NA VIA"
        })

    return normalized_dataframe


def sample_street_points(dataframe: pd.DataFrame, max_points: int) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        return pd.DataFrame()

    if len(dataframe) <= max_points:
        return dataframe.copy()

    return dataframe.sample(n=max_points, random_state=42).copy()


@st.cache_data(ttl=3600, show_spinner="📄 Carregando planilha histórica de alertas...")
def load_alert_spreadsheet_for_annual_analysis(csv_path: str = LOCAL_ALERT_CSV_PATH) -> pd.DataFrame:
    spreadsheet_dataframe = read_local_csv(csv_path)
    spreadsheet_dataframe = standardize_alert_spreadsheet_columns(spreadsheet_dataframe)
    spreadsheet_dataframe = normalize_spreadsheet_timestamps(spreadsheet_dataframe)
    spreadsheet_dataframe = normalize_pothole_subtype_labels(spreadsheet_dataframe)
    spreadsheet_dataframe = extract_spreadsheet_coordinates(spreadsheet_dataframe)

    if "street" not in spreadsheet_dataframe.columns:
        spreadsheet_dataframe["street"] = pd.NA

    if "city" not in spreadsheet_dataframe.columns:
        spreadsheet_dataframe["city"] = "Foz do Iguaçu"

    spreadsheet_dataframe["street"] = spreadsheet_dataframe["street"].fillna("N/A").astype(str).str.strip()
    spreadsheet_dataframe["city"] = spreadsheet_dataframe["city"].fillna("Foz do Iguaçu").astype(str).str.strip()

    return spreadsheet_dataframe


@st.cache_data(ttl=86400, show_spinner=False)
def get_street_geometry_from_nominatim(
    street_name: str,
    city_name: str,
    country_name: str = "Brazil"
):
    search_query = f"{street_name}, {city_name}, {country_name}"
    request_url = "https://nominatim.openstreetmap.org/search"
    request_params = {
        "q": search_query,
        "format": "json",
        "limit": 1,
        "polygon_geojson": 1
    }
    request_headers = {
        "User-Agent": "WazeFozAnnualStreetAnalysis/1.0"
    }

    try:
        response = requests.get(
            request_url,
            params=request_params,
            headers=request_headers,
            timeout=20
        )
        response.raise_for_status()
        response_data = response.json()

        if not response_data:
            return None

        geojson_data = response_data[0].get("geojson")
        if not geojson_data:
            return None

        geometry_type = geojson_data.get("type")

        if geometry_type == "LineString":
            return [[coordinate[1], coordinate[0]] for coordinate in geojson_data["coordinates"]]

        if geometry_type == "MultiLineString":
            merged_coordinates = []
            for segment in geojson_data["coordinates"]:
                merged_coordinates.extend([[coordinate[1], coordinate[0]] for coordinate in segment])
            return merged_coordinates if merged_coordinates else None

        return None

    except Exception:
        return None


def build_top_streets_by_year(
    dataframe: pd.DataFrame,
    year_value: int,
    top_n: int = 5
) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        return pd.DataFrame(columns=["street", "city", "pothole_count"])

    if "year" not in dataframe.columns or "subtype" not in dataframe.columns:
        return pd.DataFrame(columns=["street", "city", "pothole_count"])

    year_dataframe = dataframe[dataframe["year"] == year_value].copy()
    if year_dataframe.empty:
        return pd.DataFrame(columns=["street", "city", "pothole_count"])

    potholes_dataframe = year_dataframe[
        year_dataframe["subtype"].astype(str).str.upper().isin(POTHOLE_SUBTYPE_VALUES)
    ].copy()

    if potholes_dataframe.empty:
        return pd.DataFrame(columns=["street", "city", "pothole_count"])

    if "street" not in potholes_dataframe.columns:
        potholes_dataframe["street"] = "N/A"

    if "city" not in potholes_dataframe.columns:
        potholes_dataframe["city"] = "Foz do Iguaçu"

    potholes_dataframe["street"] = potholes_dataframe["street"].fillna("N/A").astype(str).str.strip()
    potholes_dataframe["city"] = potholes_dataframe["city"].fillna("Foz do Iguaçu").astype(str).str.strip()

    potholes_dataframe = potholes_dataframe[
        ~potholes_dataframe["street"].isin(["", "nan", "N/A", "NA"])
    ].copy()

    if potholes_dataframe.empty:
        return pd.DataFrame(columns=["street", "city", "pothole_count"])

    top_streets_dataframe = (
        potholes_dataframe
        .groupby(["street", "city"])
        .size()
        .reset_index(name="pothole_count")
        .sort_values("pothole_count", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    return top_streets_dataframe


def build_annual_pothole_map(
    dataframe: pd.DataFrame,
    year_value: int,
    top_n: int = 5
):
    if dataframe is None or dataframe.empty:
        return None, pd.DataFrame(columns=["street", "city", "pothole_count"])

    top_streets_dataframe = build_top_streets_by_year(dataframe, year_value, top_n=top_n)
    if top_streets_dataframe.empty:
        return None, top_streets_dataframe

    if "year" not in dataframe.columns or "subtype" not in dataframe.columns:
        return None, top_streets_dataframe

    annual_dataframe = dataframe[
        (dataframe["year"] == year_value) &
        (dataframe["subtype"].astype(str).str.upper().isin(POTHOLE_SUBTYPE_VALUES))
    ].copy()

    if annual_dataframe.empty:
        return None, top_streets_dataframe

    if "street" not in annual_dataframe.columns:
        annual_dataframe["street"] = "N/A"

    if "city" not in annual_dataframe.columns:
        annual_dataframe["city"] = "Foz do Iguaçu"

    annual_dataframe["street"] = annual_dataframe["street"].fillna("N/A").astype(str).str.strip()
    annual_dataframe["city"] = annual_dataframe["city"].fillna("Foz do Iguaçu").astype(str).str.strip()

    annual_dataframe = normalize_annual_analysis_coordinates(annual_dataframe)

    has_valid_coordinate_columns = (
        "latitude" in annual_dataframe.columns and
        "longitude" in annual_dataframe.columns
    )

    if has_valid_coordinate_columns:
        annual_dataframe["latitude"] = pd.to_numeric(annual_dataframe["latitude"], errors="coerce")
        annual_dataframe["longitude"] = pd.to_numeric(annual_dataframe["longitude"], errors="coerce")

    street_geometry_registry = {}
    map_bounds = []

    for _, street_row in top_streets_dataframe.iterrows():
        street_name = str(street_row["street"]).strip()
        city_name = str(street_row["city"]).strip()
        pothole_count = int(street_row["pothole_count"])

        street_geometry = get_street_geometry_from_nominatim(street_name, city_name)

        if street_geometry and len(street_geometry) >= 2:
            street_geometry_registry[(street_name, city_name)] = {
                "geometry": street_geometry,
                "pothole_count": pothole_count
            }
            map_bounds.extend(street_geometry)

    if street_geometry_registry:
        initial_key = list(street_geometry_registry.keys())[0]
        initial_point = street_geometry_registry[initial_key]["geometry"][0]

        annual_map = folium.Map(
            location=[initial_point[0], initial_point[1]],
            zoom_start=13,
            tiles="OpenStreetMap"
        )
    else:
        if not has_valid_coordinate_columns:
            return None, top_streets_dataframe

        fallback_dataframe = annual_dataframe.dropna(subset=["latitude", "longitude"]).copy()
        if fallback_dataframe.empty:
            return None, top_streets_dataframe

        annual_map = folium.Map(
            location=[fallback_dataframe["latitude"].mean(), fallback_dataframe["longitude"].mean()],
            zoom_start=13,
            tiles="OpenStreetMap"
        )

    for _, street_row in top_streets_dataframe.iterrows():
        street_name = str(street_row["street"]).strip()
        city_name = str(street_row["city"]).strip()
        pothole_count = int(street_row["pothole_count"])

        street_group = folium.FeatureGroup(
            name=f"Rua: {street_name} ({city_name})",
            show=True
        )

        if (street_name, city_name) in street_geometry_registry:
            geometry_data = street_geometry_registry[(street_name, city_name)]

            folium.PolyLine(
                locations=geometry_data["geometry"],
                color="blue",
                weight=5,
                opacity=0.75,
                tooltip=(
                    f"<b>Rua:</b> {street_name}<br>"
                    f"<b>Cidade:</b> {city_name}<br>"
                    f"<b>Buracos:</b> {geometry_data['pothole_count']}"
                )
            ).add_to(street_group)

        if has_valid_coordinate_columns:
            street_points_dataframe = annual_dataframe[
                (annual_dataframe["street"] == street_name) &
                (annual_dataframe["city"] == city_name)
            ].dropna(subset=["latitude", "longitude"]).copy()
        else:
            street_points_dataframe = pd.DataFrame()

        sampled_street_points = sample_street_points(
            street_points_dataframe,
            MAX_MARKERS_PER_STREET
        )

        marker_cluster = MarkerCluster(
            name=f"Buracos em {street_name}",
            disableClusteringAtZoom=17
        ).add_to(street_group)

        for _, point_row in sampled_street_points.iterrows():
            popup_date_value = point_row.get("timestamp", pd.NaT)
            popup_date_text = (
                pd.to_datetime(popup_date_value).strftime("%d/%m/%Y")
                if pd.notna(popup_date_value)
                else "N/D"
            )

            popup_text = (
                f"Rua: {point_row.get('street', 'N/D')}<br>"
                f"Cidade: {point_row.get('city', 'N/D')}<br>"
                f"Data: {popup_date_text}<br>"
                f"Tipo: {point_row.get('subtype', 'N/D')}"
            )

            folium.CircleMarker(
                location=[point_row["latitude"], point_row["longitude"]],
                radius=4,
                color="darkred",
                fill=True,
                fill_color="red",
                fill_opacity=0.75,
                popup=popup_text
            ).add_to(marker_cluster)

            map_bounds.append([point_row["latitude"], point_row["longitude"]])

        street_group.add_to(annual_map)

    if map_bounds:
        annual_map.fit_bounds(map_bounds)

    folium.LayerControl(collapsed=False).add_to(annual_map)
    return annual_map, top_streets_dataframe


# =========================================================
from branca.element import MacroElement, Template
from html import escape as html_escape


def add_north_to_folium(m):
    control = MacroElement()
    control._template = Template("""
    {% macro script(this, kwargs) %}
      var north = L.control({position: 'topright'});
      north.onAdd = function(map) {
        var div = L.DomUtil.create('div', 'leaflet-bar');
        div.style.cssText = 'background:white;border-radius:9px;padding:5px 9px;box-shadow:0 1px 5px #999;font-weight:800;color:#dc2626;font-family:sans-serif;pointer-events:none';
        div.innerHTML = 'N &#8593;';
        return div;
      };
      north.addTo({{ this._parent.get_name() }});
    {% endmacro %}
    """)
    m.add_child(control)
    return m


def overview_filter(frame, day, hour_range, search, kinds=None):
    if frame is None or frame.empty or 'timestamp' not in frame: return pd.DataFrame()
    out=frame.copy(); times=pd.to_datetime(out['timestamp'],errors='coerce')
    out=out.loc[times.dt.date.eq(day)&times.dt.hour.between(hour_range[0],hour_range[1])].copy()
    if kinds is not None and 'type' in out: out=out[out['type'].isin(kinds)].copy()
    if search.strip():
        matches=pd.Series(False,index=out.index)
        for c in ('street','type','subtype'):
            if c in out: matches|=out[c].fillna('').astype(str).str.contains(search.strip(),case=False,regex=False,na=False)
        out=out.loc[matches].copy()
    return out


def overview_2d(alerts,jams,layer='Ambos'):
    pts=prepare_points_for_deck(alerts)
    center=[float(pts['lat'].mean()),float(pts['lon'].mean())] if not pts.empty else [FOZ_CENTER_LAT,FOZ_CENTER_LON]
    m=folium.Map(location=center,zoom_start=12,tiles='OpenStreetMap',control_scale=True)
    if layer in ('Ambos','Congestionamentos') and jams is not None and not jams.empty and 'line' in jams:
        group=folium.FeatureGroup(name='Congestionamentos').add_to(m)
        for _,r in jams.head(250).iterrows():
            try:
                raw=r['line']; values=raw if isinstance(raw,list) else ast.literal_eval(str(raw))
                path=[[float(x['y']),float(x['x'])] for x in values if isinstance(x,dict) and 'x' in x and 'y' in x]
                speed=pd.to_numeric(r.get('speed'),errors='coerce');kmh=float(speed)*3.6 if pd.notna(speed) else 0.0
                if len(path)>1: folium.PolyLine(path,weight=5,opacity=.85,color=get_congestion_color(kmh),tooltip=f"{html_escape(str(r.get('street','Via')))} · {kmh:.1f} km/h").add_to(group)
            except (ValueError,TypeError,SyntaxError,KeyError): pass
    if layer in ('Ambos','Alertas') and not pts.empty:
        group=MarkerCluster(name='Alertas').add_to(m)
        for _,r in pts.head(1200).iterrows():
            kind=str(r.get('type','N/D'));sub=str(r.get('subtype','N/D'));street=str(r.get('street','N/D'))
            folium.CircleMarker([float(r['lat']),float(r['lon'])],radius=5,color=get_incident_severity_color(kind,sub),fill=True,fill_opacity=.85,tooltip=f"{html_escape(kind)} — {html_escape(street)}").add_to(group)
    folium.LayerControl(collapsed=True).add_to(m)
    return add_north_to_folium(m)

# BLOCO 6 — VISUALIZAÇÕES PRINCIPAIS
# =========================================================
# =========================================================
# COMPATIBILIZAÇÃO DE NOMES PARA O BLOCO 6
# =========================================================
df_filtered = filtered_alerts_dataframe.copy() if "filtered_alerts_dataframe" in locals() else pd.DataFrame()
df_jams_filtered = filtered_jams_dataframe.copy() if "filtered_jams_dataframe" in locals() else pd.DataFrame()

df_alerts_raw = raw_alerts_dataframe.copy() if "raw_alerts_dataframe" in locals() else pd.DataFrame()
df_jams_raw = raw_jams_dataframe.copy() if "raw_jams_dataframe" in locals() else pd.DataFrame()

hora_range = selected_hour_range if "selected_hour_range" in locals() else (0, 23)
filtro_tipo = selected_incident_types if "selected_incident_types" in locals() else []
filtro_natureza = selected_incident_subtypes if "selected_incident_subtypes" in locals() else []
filtro_rua = selected_street if "selected_street" in locals() and selected_street else None

df_criticidade_vias = road_criticality_dataframe.copy() if "road_criticality_dataframe" in locals() else pd.DataFrame()
selected_date = selected_date if "selected_date" in locals() else datetime.now().date()
st.markdown("""<style>
.main .block-container{max-width:100% !important;padding:.7rem 1.1rem 1.6rem !important}
.stTabs [data-baseweb="tab-list"]{overflow-x:auto;white-space:nowrap}
.stTabs [data-baseweb="tab"]{border-radius:999px;padding:.45rem .8rem !important}
</style>""",unsafe_allow_html=True)
st.caption("WazeFoz · explore registros por local e horário")

(
    tab_inicio,
    tab_resultados,
    tab_inc,
    tab_jams,
    tab_calor,
    tab_3d,
    tab_temporal_danos,
    tab_temporal_anual,
    tab_graficos,
    tab_criticidade,
    tab_dados
) = st.tabs(
    [
        "⌂ Visão geral",
        "🖼️ Resultados visuais",
        "Incidentes",
        "Congestionamentos",
        "Mapa de Calor",
        "🧊 Cidade 3D",
        "📅 Análise Temporal",
        "🗺️ Análisis Temporal Anual",
        "Gráficos",
        "📊 Criticidade (MCDA)",
        "Dados"
    ]
)

with tab_inicio:
    st.subheader("🗺️ WazeFoz — mapa temporal da mobilidade")
    st.caption("Pesquise vias, filtre ocorrências e explore a linha do tempo. Fundo 2D: OpenStreetMap, sem Carto.")
    days=set()
    for frame in (df_alerts_raw,df_jams_raw):
        if not frame.empty and 'timestamp' in frame:
            days.update(pd.to_datetime(frame['timestamp'],errors='coerce').dropna().dt.date.tolist())
    default_day=selected_date if selected_date in days else (max(days) if days else current_foz_datetime.date())
    a,b=st.columns([1.3,4.7],gap='small')
    with a:
        search=st.text_input("Rua ou evento",placeholder="Ex.: Avenida Paraná",key="map_search")
        chosen_day=st.date_input("Data",value=default_day,key="map_date")
        base_layer=st.radio("Dados",["Ambos","Alertas","Congestionamentos"],key="map_data")
        kinds=sorted(df_alerts_raw['type'].dropna().astype(str).unique().tolist()) if not df_alerts_raw.empty and 'type' in df_alerts_raw else []
        kinds_sel=st.multiselect("Tipos",kinds,default=kinds,key="map_kinds")
        period_mode=st.radio("Tempo",["Acumulado","Hora","Intervalo"],key="map_time_mode")
        if period_mode=='Intervalo': hours=st.slider("Horas",0,23,(0,23),key="map_hours")
        else:
            current_hour=st.slider("Hora local",0,23,12,format="%02d:00",key="map_hour")
            hours=(0,current_hour) if period_mode=='Acumulado' else (current_hour,current_hour)
        display_mode=st.segmented_control("Visualização",["2D","3D"],default="2D",key="overview_2d3d")
    points=overview_filter(df_alerts_raw,chosen_day,hours,search,kinds_sel)
    jams=overview_filter(df_jams_raw,chosen_day,hours,search)
    with b:
        c1,c2,c3=st.columns(3)
        c1.metric("Alertas",len(points))
        c2.metric("Buracos",int(points['subtype'].astype(str).str.upper().eq('BURACO NA VIA').sum()) if not points.empty and 'subtype' in points else 0)
        c3.metric("Congestionamentos",len(jams))
        if display_mode=='2D':
            st_folium(overview_2d(points,jams,base_layer),height=630,width="100%",returned_objects=[],key="overview_2d_map")
            st.caption("N ↑ · Norte no topo do mapa. OpenStreetMap; linhas apenas quando há geometria observada.")
        else:
            layer_3d='Fluxo de congestionamento' if base_layer=='Congestionamentos' else 'Densidade hexagonal'
            render_3d_map(points,jams,layer_3d,deck_map_style_label,deck_zoom,deck_pitch,deck_bearing,
                          deck_hex_radius,deck_elevation_scale,element_key="overview_3d_map")
    day_series=overview_filter(df_alerts_raw,chosen_day,(0,23),search,kinds_sel)
    if not day_series.empty:
        histogram=pd.to_datetime(day_series['timestamp'],errors='coerce').dt.hour.value_counts().reindex(range(24),fill_value=0).rename_axis('Hora').reset_index(name='Ocorrências')
        fig=px.area(histogram,x='Hora',y='Ocorrências',title='Linha do tempo do dia')
        fig.update_layout(height=215,margin=dict(l=5,r=5,t=35,b=5))
        fig.update_xaxes(tickvals=list(range(0,24,2)),ticktext=[f"{h:02d}:00" for h in range(0,24,2)])
        st.plotly_chart(fig,width="stretch")
    with st.expander("Metodologia e limitações"):
        st.write("Registros colaborativos Waze podem ter duplicidades, subnotificação e diferenças de cobertura temporal. Mapa 3D não representa edifícios ou deslocamentos individuais.")

with tab_resultados:
    st.subheader("🖼️ Resultados visuais")
    st.caption("Exibe figuras realmente adicionadas a assets/resultados/ no repositório; não inclui imagens de exemplo como resultados.")
    gallery_path=Path(__file__).resolve().parent/'assets'/'resultados'
    imgs=sorted(p for p in gallery_path.iterdir() if p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.webp'}) if gallery_path.exists() else []
    if not imgs: st.info("Nenhuma imagem em assets/resultados/. Publique ali seus gráficos e mapas finais para exibi-los aqui.")
    else:
        q=st.text_input("Filtrar pelo nome",key="gallery_query")
        filtered=[p for p in imgs if q.strip().casefold() in p.stem.casefold()]
        for i in range(0,len(filtered),2):
            c1,c2=st.columns(2)
            for col,p in zip((c1,c2),filtered[i:i+2]):
                with col:
                    st.image(str(p),caption=p.stem.replace('_',' ').replace('-',' '),width="stretch")
                    st.caption("Verifique a fonte, data e período da figura antes da apresentação.")
        if not filtered: st.info("Nenhuma imagem corresponde ao filtro.")

with tab_inc:
    st.caption("📍 Centro: -25.54, -54.58 · Norte ↑ · Clique nos pontos para detalhes")

    if not df_filtered.empty:
        m_inc = generate_incidents_map(df_filtered.to_json(date_format="iso"))

        if m_inc:
            st_folium(m_inc, width="100%", height=500, key=f"mapa_inc_{len(df_filtered)}")

            st.markdown("""
            | Cor | Tipo / Natureza |
            |---|---|
            | 🔴 | Acidente grave / Alta gravidade |
            | 💗 | Acidente leve / Baixa gravidade |
            | 🟥 | Via fechada / Obras / Bloqueio total |
            | 🟧 | Perigo / Buraco na via / Risco moderado |
            | 🟨 | Alerta / Semáforo / Atenção |
            | 🟦 | Perigo climático / Condições adversas |
            | 🟪 | Congestionamento / Trânsito parado |
            """)
        else:
            st.info("Nenhum incidente dentro da área de Foz do Iguaçu.")
    else:
        st.info("Nenhum incidente com os filtros aplicados.")

with tab_jams:
    st.caption("🚦 Escala métrica · Livre → Parado")

    if not df_jams_filtered.empty:
        m_jam = generate_jams_map(df_jams_filtered.to_json(date_format="iso"))

        if m_jam:
            st_folium(m_jam, width="100%", height=500, key=f"mapa_jam_{len(df_jams_filtered)}")

            st.markdown("""
            | Cor | Velocidade | Status |
            |---|---:|---|
            | 🔵 | 80+ km/h | Livre / Fluindo |
            | 🟢 | 60–80 km/h | Bom |
            | 🟡 | 40–60 km/h | Moderado |
            | 🟠 | 20–40 km/h | Lento |
            | 🔴 | 5–20 km/h | Muito lento |
            | 🟣 | <5 km/h | Parado / Travado |
            """)
        else:
            st.warning("Nenhum congestionamento na área filtrada.")

        cols_diag = [c for c in ["lat", "lon", "line", "speed", "street"] if c in df_jams_filtered.columns]
        if cols_diag:
            st.caption("Amostra dos dados de congestionamentos")
            st.dataframe(df_jams_filtered[cols_diag].head(5), width="stretch")
    else:
        st.info("Nenhum congestionamento para exibir.")

with tab_calor:
    st.subheader("🔥 Zonas de Concentração de Incidentes")

    if not df_filtered.empty:
        df_heat = df_filtered.copy()

        if {"lat", "lon"}.issubset(df_heat.columns):
            df_heat = df_heat.dropna(subset=["lat", "lon"])
            df_heat = df_heat[
                df_heat["lat"].between(FOZ_LATITUDE_MIN, FOZ_LATITUDE_MAX)
                & df_heat["lon"].between(FOZ_LONGITUDE_MIN, FOZ_LONGITUDE_MAX)
            ]

            if not df_heat.empty:
                m_heat = folium.Map(
                    location=[df_heat["lat"].mean(), df_heat["lon"].mean()],
                    zoom_start=13,
                    tiles="OpenStreetMap"
                )

                heat_data = [[row["lat"], row["lon"]] for _, row in df_heat.iterrows()]
                plugins.HeatMap(
                    heat_data,
                    radius=20,
                    blur=15,
                    min_opacity=0.35,
                    gradient={
                        0.2: "#ffffb2",
                        0.4: "#fecc5c",
                        0.6: "#fd8d3c",
                        0.8: "#f03b20",
                        1.0: "#bd0026",
                    }
                ).add_to(m_heat)

                st_folium(m_heat, width="100%", height=500, key=f"mapa_heat_{len(df_heat)}")

                st.markdown("""
                | Cor | Concentração |
                |---|---|
                | 🟨 | Baixa — poucos registros |
                | 🟧 | Média — atenção |
                | 🟥 | Alta — ponto crítico |
                | 🟫 | Crítica — intervenção prioritária |
                """)

                tipos_no_mapa = df_heat["type"].value_counts().reset_index()
                tipos_no_mapa.columns = ["Tipo", "Qtd"]
                st.dataframe(tipos_no_mapa, hide_index=True, width="stretch")
            else:
                st.info("Nenhum ponto dentro da área de Foz do Iguaçu.")
        else:
            st.info("Sem coordenadas válidas para gerar o mapa de calor.")
    else:
        st.info("Sem dados suficientes para mapa de calor.")

with tab_3d:
    st.subheader("🧊 Cidade 3D — exploração interativa")
    st.caption("O mapa 3D é construído após o clique em Exibir mapa, reduzindo o carregamento de mapas WebGL em abas ocultas.")
    modo_3d = st.radio("Camada", ["Densidade hexagonal", "Colunas por via",
                                 "Pontos + calor", "Fluxo de congestionamento",
                                 "Arcos de criticidade"], horizontal=True, key="modo_3d")
    hist_3d = st.toggle("Usar histórico completo", value=False, key="hist_3d")
    base_3d = df_alerts_raw if hist_3d else df_filtered
    jams_3d = df_jams_raw if hist_3d else df_jams_filtered
    st.write("Alertas carregados:", len(base_3d), "· Congestionamentos carregados:", len(jams_3d))
    if not hist_3d and base_3d.empty and not df_alerts_raw.empty:
        st.info("Filtro de data vazio. Ative o histórico completo ou selecione uma data com registros.")
    city_view=st.segmented_control("Visualização",["2D","3D"],default="3D",key="city_2d3d")
    if city_view=="2D":
        city_layer='Congestionamentos' if modo_3d=="Fluxo de congestionamento" else 'Alertas'
        st_folium(overview_2d(base_3d,jams_3d,city_layer),height=620,width="100%",returned_objects=[],key="city_2d_map")
        st.caption("N ↑ · Norte no topo do mapa 2D com ruas OpenStreetMap.")
    else:
        st.caption("A seta N no mapa 3D acompanha a rotação configurada na barra lateral.")
    if city_view=="3D" and st.button("🗺️ Exibir mapa 3D", key="open_3d"):
        st.session_state["show_city_3d"] = True
    if city_view=="3D" and st.session_state.get("show_city_3d", False):
        render_3d_map(base_3d, jams_3d, modo_3d, deck_map_style_label,
                      deck_zoom, deck_pitch, deck_bearing, deck_hex_radius,
                      deck_elevation_scale, element_key="city3d_main")
    elif city_view=="3D":
        st.info("Clique em Exibir mapa 3D para carregar esta visualização.")
    st.divider()
    st.subheader("⏱️ Linha do tempo 3D")
    if city_view=="3D" and st.toggle("Mostrar linha do tempo", value=False, key="show_3d_timeline"):
        data_anim = prepare_points_for_deck(base_3d)
        if data_anim.empty or "timestamp" not in data_anim:
            st.info("Sem dados com coordenadas e tempo nesta seleção.")
        else:
            data_anim["timestamp"] = pd.to_datetime(data_anim["timestamp"], errors="coerce")
            data_anim = data_anim.dropna(subset=["timestamp"])
            gran = st.selectbox("Granularidade", ["Hora", "Dia", "Semana"], key="gran_3d")
            if gran == "Semana":
                data_anim["bucket"] = data_anim["timestamp"].dt.to_period("W").dt.start_time
            else:
                data_anim["bucket"] = data_anim["timestamp"].dt.floor("h" if gran == "Hora" else "D")
            buckets = sorted(data_anim["bucket"].unique())
            if len(buckets) < 2:
                st.info("Selecione um período maior para ter pelo menos dois intervalos.")
            else:
                index = st.slider("Momento", 0, len(buckets)-1, 0, key="moment_3d")
                moment = data_anim[data_anim["bucket"].eq(buckets[index])]
                st.caption(f"{pd.Timestamp(buckets[index]).strftime('%d/%m/%Y %H:%M')} · {len(moment)} registros")
                render_3d_map(moment, jams_3d, "Densidade hexagonal", deck_map_style_label,
                              deck_zoom, deck_pitch, deck_bearing, deck_hex_radius,
                              deck_elevation_scale, element_key="city3d_timeline", height=510)
                serie = data_anim.groupby("bucket").size().reset_index(name="Ocorrências")
                st.plotly_chart(px.area(serie, x="bucket", y="Ocorrências", title="Ocorrências no tempo"),
                                width="stretch")

with tab_temporal_danos:
    st.subheader("📅 Análise Temporal de Patologias Viárias")
    st.markdown("""
    Esta seção exibe o perfil de distribuição e reincidência de anomalias viárias nos arquivos ativos carregados atualmente.
    """)
    if not df_alerts_raw.empty:
        subtipos = get_clean_unique_values(df_alerts_raw["subtype"], invalid_values=["nan", ""])
        subtipo_sel = st.selectbox("Selecione a natureza do dano:", subtipos or ["(Sem dados)"], key="sel_dano_temporal")

        df_sub = df_alerts_raw[df_alerts_raw["subtype"] == subtipo_sel]
        if not df_sub.empty:
            fig_temp = px.histogram(
                df_sub,
                x="hour",
                nbins=24,
                color_discrete_sequence=['#dc2626'],
                title=f"Distribuição Horária Total de: {subtipo_sel}",
                labels={"hour": "Hora do Dia (Recorte Atual)", "count": "Volume de Alertas"}
            )
            st.plotly_chart(fig_temp, width="stretch")
        else:
            st.info("Sem registros para a patologia selecionada na data ativa.")
    else:
        st.warning("Base de dados de alertas vazia ou indisponível.")

with tab_temporal_anual:
    st.subheader("🗺️ Análisis Temporal Anual — Top ruas com mais buracos")
    st.caption(
        "Esta aba usa somente a planilha histórica de alertas para identificar, por ano, "
        "as ruas com maior número de reportes de BURACO NA VIA e exibi-las em mapa com geometrias."
    )

    annual_maps_enabled = st.toggle("Gerar mapas anuais (Nominatim)", value=False, key="annual_maps_enabled")
    st.info("O resumo apresenta 2026 de janeiro a agosto; totais anuais dependem da fonte CSV selecionada.")
    col_anual_1, col_anual_2 = st.columns([1, 1])

    with col_anual_1:
        anos_selecionados = st.multiselect(
            "Selecione os anos para análise",
            options=ANNUAL_YEARS_DEFAULT,
            default=ANNUAL_YEARS_DEFAULT,
            key="annual_pothole_years"
        )

    with col_anual_2:
        top_n_ruas = st.slider(
            "Número de ruas por ano",
            min_value=3,
            max_value=10,
            value=5,
            step=1,
            key="annual_top_streets_slider"
        )

    try:
        df_alertas_planilha_anual = load_alert_spreadsheet_for_annual_analysis(LOCAL_ALERT_CSV_PATH)
    except FileNotFoundError:
        st.error(
            f"Não foi possível localizar a planilha local em: `{LOCAL_ALERT_CSV_PATH}`. "
            "Ajuste o caminho do arquivo CSV no código."
        )
        df_alertas_planilha_anual = pd.DataFrame()
    except Exception as erro_planilha:
        st.error(f"Erro ao carregar a planilha histórica: {erro_planilha}")
        df_alertas_planilha_anual = pd.DataFrame()

    if df_alertas_planilha_anual.empty:
        st.warning("A planilha foi carregada, mas não há dados válidos para análise anual.")
    else:
        df_buracos_historico = df_alertas_planilha_anual.copy()

        if "subtype" not in df_buracos_historico.columns:
            st.warning("A planilha não possui a coluna `subtype/Subtype`, necessária para identificar buracos.")
        else:
            df_buracos_historico = df_buracos_historico[
                df_buracos_historico["subtype"].astype(str).str.upper().isin(POTHOLE_SUBTYPE_VALUES)
            ].copy()

            if df_buracos_historico.empty:
                st.info("Não foram encontrados registros de 'BURACO NA VIA' na planilha histórica.")
            else:
                df_buracos_historico = df_buracos_historico[
                    df_buracos_historico["year"].isin([2024, 2025, 2026])
                    & ~((df_buracos_historico["year"].eq(2026))
                        & (df_buracos_historico["timestamp"].dt.month > 8))
                ].copy()
                df_buracos_historico["month"] = df_buracos_historico["timestamp"].dt.month
                mensal = df_buracos_historico.groupby(["year", "month"]).size().reset_index(name="Ocorrências")
                if not mensal.empty:
                    mensal["Ano"] = mensal["year"].astype(int).astype(str)
                    fig_mensal = px.line(mensal, x="month", y="Ocorrências", color="Ano",
                                         markers=True, title="Buracos por mês — 2024–2026")
                    fig_mensal.update_xaxes(tickvals=list(range(1, 13)), ticktext=[
                        "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
                    st.plotly_chart(fig_mensal, width="stretch")
                with st.expander("🔎 Auditoria frente ao resumo"):
                    reference = {
                        2024: (7296, 5, 1460, "Avenida Paraná", 581),
                        2025: (17608, 8, 3166, "Avenida das Cataratas", 1206),
                        2026: (6168, 3, 1175, "Avenida Felipe Wandscheer", 936),
                    }
                    audit = []
                    for year, (total_ref, peak_month, peak_ref, road_ref, road_ref_n) in reference.items():
                        year_frame = df_buracos_historico[df_buracos_historico["year"].eq(year)]
                        counts = year_frame["street"].fillna("N/D").astype(str).str.strip().value_counts()
                        actual_road = int(counts[counts.index.str.casefold() == road_ref.casefold()].sum())
                        peak_actual = int(year_frame["month"].eq(peak_month).sum())
                        audit.append({"Ano": year, "Total resumo": total_ref, "Total calculado": len(year_frame),
                                      "Pico resumo": peak_ref, "Pico calculado": peak_actual,
                                      "Via": road_ref, "Via resumo": road_ref_n, "Via calculada": actual_road,
                                      "Status": "OK" if (len(year_frame), peak_actual, actual_road)
                                               == (total_ref, peak_ref, road_ref_n) else "REVISAR"})
                    st.dataframe(pd.DataFrame(audit), hide_index=True, width="stretch")
                    st.caption("Se houver divergências, confira arquivo-fonte, datas, duplicatas e grafias das vias.")

                anos_disponiveis_historico = sorted(
                    df_buracos_historico["year"].dropna().astype(int).unique().tolist()
                )

                if not anos_disponiveis_historico:
                    st.info("Não há anos válidos na planilha para análise.")
                else:
                    anos_para_renderizar = [
                        ano for ano in anos_selecionados
                        if ano in anos_disponiveis_historico
                    ]

                    if not anos_para_renderizar:
                        st.info("Nenhum dos anos selecionados possui dados de buracos na planilha.")
                    else:
                        for ano_analise in anos_para_renderizar:
                            st.markdown("---")
                            st.markdown(f"### Ano {ano_analise}")

                            top_ruas_ano = build_top_streets_by_year(
                                df_buracos_historico, ano_analise, top_n=top_n_ruas
                            )
                            mapa_anual = None
                            if annual_maps_enabled:
                                mapa_anual, _ = build_annual_pothole_map(
                                    df_buracos_historico, ano_analise, top_n=top_n_ruas
                                )

                            col_resumo_1, col_resumo_2 = st.columns([2, 1])

                            with col_resumo_1:
                                if top_ruas_ano.empty:
                                    st.info(f"Sem ruas classificadas para {ano_analise}.")
                                else:
                                    top_ruas_ano_exibir = top_ruas_ano.copy()
                                    top_ruas_ano_exibir.columns = ["Rua", "Cidade", "Contagem de Buracos"]

                                    st.dataframe(
                                        top_ruas_ano_exibir,
                                        hide_index=True,
                                        width="stretch"
                                    )

                                    fig_top_ruas_ano = px.bar(
                                        top_ruas_ano_exibir.sort_values("Contagem de Buracos", ascending=True),
                                        x="Contagem de Buracos",
                                        y="Rua",
                                        orientation="h",
                                        color="Contagem de Buracos",
                                        color_continuous_scale="magma",
                                        title=f"Top {top_n_ruas} ruas com mais reportes de buracos — {ano_analise}"
                                    )
                                    fig_top_ruas_ano.update_layout(height=360, coloraxis_showscale=False)
                                    st.plotly_chart(fig_top_ruas_ano, width="stretch")

                            with col_resumo_2:
                                total_buracos_ano = int(
                                    df_buracos_historico[df_buracos_historico["year"] == ano_analise].shape[0]
                                )
                                total_representado_top = int(
                                    top_ruas_ano["pothole_count"].sum()
                                ) if not top_ruas_ano.empty else 0

                                st.metric("Ano analisado", ano_analise)
                                st.metric("Buracos no ano", total_buracos_ano)
                                st.metric("Top ruas somadas", total_representado_top)

                            if mapa_anual is not None:
                                st_folium(
                                    mapa_anual,
                                    width="100%",
                                    height=560,
                                    key=f"annual_pothole_map_{ano_analise}"
                                )
                            elif annual_maps_enabled:
                                st.warning(
                                    f"Não foi possível montar o mapa de {ano_analise}. "
                                    "Talvez faltem geometrias do Nominatim ou coordenadas válidas na planilha."
                                )

with tab_graficos:
    if not df_filtered.empty:
        st.markdown(
            f"**{len(df_filtered)} registros analisados** para "
            f"**{selected_date.strftime('%d/%m/%Y')}** no intervalo "
            f"**{hora_range[0]:02d}:00–{hora_range[1]:02d}:59**"
        )
        st.markdown("---")

        df_hist = df_alerts_raw.copy()

        if filtro_tipo and "type" in df_hist.columns:
            df_hist = df_hist[df_hist["type"].isin(filtro_tipo)]
        if filtro_natureza and "subtype" in df_hist.columns:
            df_hist = df_hist[df_hist["subtype"].isin(filtro_natureza)]
        if filtro_rua and "street" in df_hist.columns:
            df_hist = df_hist[df_hist["street"] == filtro_rua]

        DIAS_PT = {
            "Monday": "Segunda",
            "Tuesday": "Terça",
            "Wednesday": "Quarta",
            "Thursday": "Quinta",
            "Friday": "Sexta",
            "Saturday": "Sábado",
            "Sunday": "Domingo",
        }

        CORES_TIPO = {
            "ACIDENTE": "#e74c3c",
            "VIA FECHADA": "#c0392b",
            "PERIGO": "#e67e22",
            "PERIGO CLIMÁTICO": "#3498db",
            "CONGESTIONAMENTO": "#f39c12",
            "ALERTA": "#9b59b6",
        }

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("Incidentes por Hora do Dia")
            hora_counts = (
                df_filtered["hour"]
                .value_counts()
                .reindex(range(24), fill_value=0)
                .reset_index()
            )
            hora_counts.columns = ["Hora", "Quantidade"]
            hora_pico = int(hora_counts.loc[hora_counts["Quantidade"].idxmax(), "Hora"])

            fig_hora = px.bar(
                hora_counts,
                x="Hora",
                y="Quantidade",
                color="Quantidade",
                color_continuous_scale="Reds",
                text="Quantidade",
                labels={"Hora": "Hora (UTC-3 / Foz)", "Quantidade": "Nº Incidentes"}
            )
            fig_hora.update_traces(textposition="outside")
            fig_hora.add_vline(
                x=hora_pico,
                line_dash="dash",
                line_color="darkred",
                annotation_text=f"Pico {hora_pico:02d}h"
            )
            fig_hora.update_layout(coloraxis_showscale=False, height=360)
            st.plotly_chart(fig_hora, width="stretch")

        with col_g2:
            st.subheader("Natureza das Ocorrências")

            tem_subtipo = (
                "subtype" in df_filtered.columns and
                df_filtered["subtype"].notna().any() and
                (~df_filtered["subtype"].isin(["nan", ""])).any()
            )

            if tem_subtipo:
                df_sub = df_filtered[
                    df_filtered["subtype"].notna() &
                    (~df_filtered["subtype"].isin(["nan", ""]))
                ].copy()
                df_sub["label"] = df_sub.apply(
                    lambda r: r["subtype"] if r["subtype"] != "" else r["type"],
                    axis=1
                )
                sub_counts = df_sub["label"].value_counts().reset_index()
            else:
                sub_counts = df_filtered["type"].value_counts().reset_index()

            sub_counts.columns = ["Natureza", "Quantidade"]

            fig_pie = px.pie(sub_counts, names="Natureza", values="Quantidade", hole=0.38)
            fig_pie.update_layout(height=380)
            st.plotly_chart(fig_pie, width="stretch")

        st.markdown("---")

        if "day_of_week" in df_hist.columns and not df_hist.empty:
            st.subheader("Incidentes por Dia da Semana")
            df_dow = df_hist.copy()
            df_dow["Dia"] = df_dow["day_of_week"].map(DIAS_PT)

            dow_tipo = df_dow.groupby(["Dia", "type"]).size().reset_index(name="Quantidade")
            ordem_dias = list(DIAS_PT.values())

            fig_dow = px.bar(
                dow_tipo,
                x="Dia",
                y="Quantidade",
                color="type",
                color_discrete_map=CORES_TIPO,
                category_orders={"Dia": ordem_dias},
                barmode="stack",
                text_auto=True
            )
            fig_dow.update_layout(height=420)
            st.plotly_chart(fig_dow, width="stretch")

        st.markdown("---")
        st.subheader("Vias Críticas — Incidentes por Natureza")
        top_ruas_lista = []

        if "street" in df_hist.columns:
            top_ruas_lista = (
                df_hist[
                    df_hist["street"].notna() &
                    (~df_hist["street"].isin(["NA", "nan", ""]))
                ]["street"]
                .value_counts()
                .head(10)
                .index
                .tolist()
            )

        if top_ruas_lista and "subtype" in df_hist.columns:
            df_rua = df_hist[
                df_hist["street"].isin(top_ruas_lista) &
                df_hist["subtype"].notna() &
                (~df_hist["subtype"].isin(["nan", ""]))
            ].copy()

            rua_sub = df_rua.groupby(["street", "subtype"]).size().reset_index(name="Quantidade")
            ordem_ruas = (
                rua_sub.groupby("street")["Quantidade"]
                .sum()
                .sort_values(ascending=True)
                .index
                .tolist()
            )

            fig_rua = px.bar(
                rua_sub,
                x="Quantidade",
                y="street",
                color="subtype",
                orientation="h",
                barmode="stack",
                category_orders={"street": ordem_ruas}
            )
            fig_rua.update_layout(height=460)
            st.plotly_chart(fig_rua, width="stretch")

        st.markdown("---")
        st.subheader("Quais dias cada rua tem mais problemas?")

        if top_ruas_lista and "day_of_week" in df_hist.columns:
            df_hm = df_hist[df_hist["street"].isin(top_ruas_lista)].copy()
            df_hm["Dia"] = df_hm["day_of_week"].map(DIAS_PT)

            bubble_dow = df_hm.groupby(["street", "Dia"]).size().reset_index(name="Qtd")
            total_dow = bubble_dow.groupby(["street", "Dia"])["Qtd"].sum().reset_index(name="Total")
            vmax_dow = total_dow["Total"].max() if not total_dow.empty else 1

            def nivel_label(v, vmax):
                if v == 0:
                    return "Nenhum"
                elif v <= vmax * 0.25:
                    return "Baixo"
                elif v <= vmax * 0.60:
                    return "Médio"
                return "Alto"

            total_dow["Nível"] = total_dow["Total"].apply(lambda v: nivel_label(v, vmax_dow))

            fig_b1 = px.scatter(
                total_dow,
                x="Dia",
                y="street",
                size="Total",
                color="Nível",
                text="Total",
                size_max=55,
                category_orders={"Dia": list(DIAS_PT.values())}
            )
            fig_b1.update_layout(height=460)
            st.plotly_chart(fig_b1, width="stretch")
    else:
        st.info("Sem incidentes para gerar gráficos no recorte atual.")

with tab_criticidade:
    st.subheader("📊 Classificação Hierárquica de Infraestrutura Viária Crítica")
    st.markdown("""
    Análise multicritério ponderando **volume de congestionamentos** e **atraso médio (s)**.
    Permite à **Foztrans** priorizar envio de agentes ou investimentos nas vias de maior peso operacional.
    """)

    if not df_criticidade_vias.empty:
        col_t1, col_t2 = st.columns([3, 2])

        with col_t1:
            fig_crit = px.bar(
                df_criticidade_vias.head(10),
                x="Criticidade_Index",
                y="street",
                orientation="h",
                title="Top 10 Vias Críticas — Intervenção Prioritária",
                labels={"Criticidade_Index": "Índice de Criticidade (0–100)", "street": "Logradouro"},
                color="Criticidade_Index",
                color_continuous_scale="Oranges"
            )
            fig_crit.update_layout(height=400)
            st.plotly_chart(fig_crit, width="stretch")

        with col_t2:
            st.markdown("#### Ranking de Prioridade Viária")
            st.dataframe(
                df_criticidade_vias[["street", "Volume_Jams", "Atraso_Medio_Seg", "Criticidade_Index"]].head(10),
                hide_index=True,
                column_config={
                    "street": "Logradouro",
                    "Volume_Jams": "Qtd Retenções",
                    "Atraso_Medio_Seg": "Atraso Médio (s)",
                    "Criticidade_Index": "Índice Geral (0–100)"
                }
            )
    else:
        st.info("Dados insuficientes para o ranking multicritério.")

with tab_dados:
    st.subheader("Tabela de Incidentes")

    if not df_filtered.empty:
        colunas_exibir = [
            c for c in [
                "timestamp", "type", "subtype", "street", "lat", "lon",
                "confidence", "reportRating"
            ] if c in df_filtered.columns
        ]
        st.dataframe(
            df_filtered[colunas_exibir].sort_values("timestamp", ascending=False),
            width="stretch"
        )
        csv = df_filtered[colunas_exibir].to_csv(index=False).encode("utf-8")
        st.download_button(
            "Baixar CSV — Incidentes",
            data=csv,
            file_name=f"incidentes_{selected_date}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum dado de incidente disponível.")

    st.subheader("Tabela de Congestionamentos")

    if not df_jams_filtered.empty:
        colunas_jams = [
            c for c in [
                "timestamp", "street", "speed", "length", "delay",
                "type", "subtype", "lat", "lon"
            ] if c in df_jams_filtered.columns
        ]

        df_jams_show = df_jams_filtered[colunas_jams].copy()
        if "speed" in df_jams_show.columns:
            df_jams_show["speed_kmh"] = (df_jams_show["speed"] * 3.6).round(1)

        st.dataframe(
            df_jams_show.sort_values("timestamp", ascending=False),
            width="stretch"
        )
        csv_jams = df_jams_show.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Baixar CSV — Congestionamentos",
            data=csv_jams,
            file_name=f"jams_{selected_date}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum dado de congestionamento disponível.")


# =========================================================
# BLOCO 7 — RODAPÉ
# =========================================================

st.markdown("---")

footer_html = f"""
<div style="
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
    text-align: center;
    font-family: 'Inter', sans-serif;
    box-shadow: 0 2px 12px rgba(15,23,42,0.07);
">
  <div style="font-size:1.4rem;font-weight:800;color:#0F172A;margin-bottom:0.25rem;
              display:flex;align-items:center;justify-content:center;gap:10px;">
    <img src="https://cdn.simpleicons.org/waze/00C9D4" width="32" height="32" alt="Waze for Cities">
    GEO_IA — Monitoramento de Tráfego
  </div>
  <div style="font-size:0.82rem;color:#475569;margin-bottom:1.5rem;">
    Sistema de análise de incidentes e congestionamentos via dados Waze for Cities · Foz do Iguaçu, PR
  </div>

  <div style="border-top:1px solid #E2E8F0;margin-bottom:1.5rem;"></div>

  <div style="margin-bottom:1.2rem;">
    <div style="font-size:1rem;font-weight:700;color:#0F172A;margin-bottom:0.2rem;">
      🏛️ UNILA — Universidade Federal da Integração Latino-Americana
    </div>
    <div style="font-size:0.78rem;color:#64748B;">Foz do Iguaçu, Paraná · Brasil</div>
  </div>

  <div style="border-top:1px solid #E2E8F0;margin-bottom:1.5rem;"></div>

  <div style="font-size:0.75rem;color:#94A3B8;margin-bottom:0.9rem;
              text-transform:uppercase;letter-spacing:0.8px;font-weight:600;">
    Grupos &amp; Laboratórios de Pesquisa
  </div>

  <div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;margin-bottom:1.5rem;">
    <div style="text-align:center;">
      <div style="font-size:1rem;font-weight:700;color:#2563EB;margin-bottom:0.2rem;">🔬 GPMME</div>
      <div style="font-size:0.78rem;color:#475569;max-width:200px;line-height:1.5;">
        Grupo de Pesquisa em Mobilidade<br>e Matriz Energética
      </div>
    </div>
    <div style="width:1px;background:#E2E8F0;align-self:stretch;margin:0 0.25rem;"></div>
    <div style="text-align:center;">
      <div style="font-size:1rem;font-weight:700;color:#059669;margin-bottom:0.2rem;">🧪 LAGGRA</div>
      <div style="font-size:0.78rem;color:#475569;max-width:220px;line-height:1.5;">
        Lab. de Geologia, Geotecnia<br>e Recuperação Ambiental
      </div>
    </div>
    <div style="width:1px;background:#E2E8F0;align-self:stretch;margin:0 0.25rem;"></div>
    <div style="text-align:center;">
      <div style="font-size:1rem;font-weight:700;color:#7C3AED;margin-bottom:0.2rem;">💻 LACA</div>
      <div style="font-size:0.78rem;color:#475569;max-width:200px;line-height:1.5;">
        Laboratório de<br>Computação Aplicada
      </div>
    </div>
  </div>

  <div style="border-top:1px solid #E2E8F0;margin-bottom:1.2rem;"></div>

  <div style="font-size:0.75rem;color:#94A3B8;margin-bottom:0.9rem;
              text-transform:uppercase;letter-spacing:0.8px;font-weight:600;">
    Equipe de Desenvolvimento
  </div>
  <div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;margin-bottom:1.2rem;">
    <span style="font-size:0.82rem;color:#334155;">👨‍💻 Luis Enrique Santacruz Alvarez</span>
    <span style="font-size:0.82rem;color:#334155;">🎓 Dr. Diego Moraes Flores — ILATIT · UNILA</span>
  </div>

  <div style="border-top:1px solid #E2E8F0;margin-bottom:1rem;"></div>

  <div style="display:flex;justify-content:center;align-items:center;gap:1.5rem;
              flex-wrap:wrap;font-size:0.73rem;color:#64748B;">
    <span>📡 Fonte:
      <img src="https://cdn.simpleicons.org/waze/00C9D4" width="14" height="14"
           style="vertical-align:middle;margin:0 2px;">
      <strong style="color:#0F172A;">Waze for Cities</strong>
    </span>
    <span>·</span>
    <span>🐍 Python · Streamlit · Folium · Plotly</span>
    <span>·</span>
    <span>☁️ Google Drive API</span>
    <span>·</span>
    <span>Local: Foz do Iguaçu (UTC-3)</span>
  </div>
  <div style="margin-top:0.75rem;font-size:0.68rem;color:#94A3B8;">
    © {current_foz_datetime.year} GPMME / LAGGRA / LACA — UNILA · Foz do Iguaçu · Uso acadêmico e de pesquisa
  </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
