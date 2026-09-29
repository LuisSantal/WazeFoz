from __future__ import annotations

import ast
import io
import re
import tempfile
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium

try:
    import pydeck as pdk
except ImportError:
    pdk = None

ROOT = Path(__file__).resolve().parent
FOZ_TZ = ZoneInfo("America/Sao_Paulo")
BBOX = (-25.70, -25.40, -54.75, -54.45)
CENTER = (-25.545, -54.585)
PRIMARY_CSV = "Waze for Cities Data _ tabelas alertas_20240101_20260306.csv"
CSV_FILES = [
    PRIMARY_CSV,
    "Waze for Cities Data _ buracos na via maio 2025 a maio 2026.csv",
    "Waze for Cities Data _ todos os alertas maio 2025 a maio 2026.csv",
    "Waze for Cities Data _Dashboard_Traffic Alerts_Tabela_2025-01-01-2026-07-04.csv",
]
FOLDERS_ALERTS = ["1xKkqLEusWuNoGzy5-UYuevUbMHAvc-bL", "1kQfYRJz0-EwY4gcsjTTVBCgK9zO5BAR0"]
FOLDERS_JAMS = ["192MCefe9vQwYhQcu-uZXekMbgdslTcgC", "16bblUG7NQmLMZM7BQUGAa3-GZIFYMka0"]
EXPECTED = {
    2024: {"total": 7296, "month": 5, "peak": 1460, "street": "Avenida Paraná", "street_count": 581},
    2025: {"total": 17608, "month": 8, "peak": 3166, "street": "Avenida das Cataratas", "street_count": 1206},
    2026: {"total": 6168, "month": 3, "peak": 1175, "street": "Avenida Felipe Wandscheer", "street_count": 936},
}
MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
ALIASES = {
    "latitude": "lat", "longitude": "lon", "lng": "lon", "long": "lon", "rua": "street",
    "logradouro": "street", "tipo": "type", "subtipo": "subtype", "natureza": "subtype",
    "data_hora": "timestamp", "datahora": "timestamp", "datetime": "timestamp",
    "velocidade_kmh": "speedkmh", "velocidade_km_h": "speedkmh",
}

st.set_page_config(page_title="WazeFoz | Mobilidade urbana", page_icon="🚦", layout="wide")
st.markdown("""<style>.block-container{max-width:1500px;padding-top:1.4rem}div[data-testid='stMetric']{background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:12px}</style>""", unsafe_allow_html=True)


def read_csv_robust(path: Path) -> pd.DataFrame:
    for encoding in ("utf-8-sig", "utf-8", "latin1", "cp1252"):
        for delimiter in (",", ";", "\t"):
            try:
                df = pd.read_csv(path, encoding=encoding, sep=delimiter, low_memory=False)
                if df.shape[1] > 1:
                    return df
            except (UnicodeError, pd.errors.ParserError, ValueError):
                pass
    raise ValueError(f"Não foi possível interpretar {path.name}")


def parse_location(value):
    if isinstance(value, dict):
        try:
            return float(value.get("y")), float(value.get("x"))
        except (ValueError, TypeError):
            return np.nan, np.nan
    if isinstance(value, str):
        point = re.search(r"POINT\s*\(\s*([-+\d.]+)\s+([-+\d.]+)\s*\)", value, re.I)
        if point:
            return float(point.group(2)), float(point.group(1))
        try:
            return parse_location(ast.literal_eval(value))
        except (ValueError, SyntaxError, TypeError, RecursionError):
            pass
    return np.nan, np.nan


def normalize_frame(frame: pd.DataFrame, source: str, jams: bool = False) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame()
    df = frame.copy()
    df.columns = [re.sub(r"[\s/\-]+", "_", str(c).strip()).lower() for c in df.columns]
    df = df.rename(columns={c: ALIASES[c] for c in df.columns if c in ALIASES})
    df = df.loc[:, ~df.columns.duplicated()].copy()
    millis = next((c for c in ("pubmillis", "pub_millis") if c in df), None)
    if millis:
        ts = pd.to_datetime(pd.to_numeric(df[millis], errors="coerce"), unit="ms", utc=True, errors="coerce")
        df["timestamp"] = ts.dt.tz_convert(FOZ_TZ).dt.tz_localize(None)
    elif "timestamp" in df:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", dayfirst=True, format="mixed")
    else:
        date_col = next((c for c in ("date", "data", "pubdate", "pub_utc_date") if c in df), None)
        df["timestamp"] = (pd.to_datetime(df[date_col], errors="coerce", dayfirst=True, format="mixed")
                           if date_col else pd.NaT)
    for column in ("lat", "lon"):
        if column not in df:
            df[column] = np.nan
        df[column] = pd.to_numeric(df[column], errors="coerce")
    if "location" in df:
        missing = df["lat"].isna() | df["lon"].isna()
        if missing.any():
            coords = df.loc[missing, "location"].map(parse_location)
            df.loc[missing, "lat"] = df.loc[missing, "lat"].fillna(coords.map(lambda v: v[0]))
            df.loc[missing, "lon"] = df.loc[missing, "lon"].fillna(coords.map(lambda v: v[1]))
    for target, fallback in (("lat", "y"), ("lon", "x")):
        if fallback in df:
            df[target] = df[target].fillna(pd.to_numeric(df[fallback], errors="coerce"))
    if jams and "line" in df and (df["lat"].isna() | df["lon"].isna()).any():
        def middle(line):
            try:
                values = line if isinstance(line, list) else ast.literal_eval(str(line))
                return parse_location(values[len(values) // 2]) if values else (np.nan, np.nan)
            except (ValueError, SyntaxError, TypeError, KeyError):
                return np.nan, np.nan
        missing = df["lat"].isna() | df["lon"].isna()
        coords = df.loc[missing, "line"].map(middle)
        df.loc[missing, "lat"] = df.loc[missing, "lat"].fillna(coords.map(lambda v: v[0]))
        df.loc[missing, "lon"] = df.loc[missing, "lon"].fillna(coords.map(lambda v: v[1]))
    for col, default in (("type", "N/D"), ("subtype", "N/D"), ("street", "N/D")):
        if col not in df:
            df[col] = default
        df[col] = df[col].fillna(default).astype(str).str.strip()
    df["subtype"] = df["subtype"].str.upper().replace({"HAZARD_ON_ROAD_POT_HOLE": "BURACO NA VIA"})
    df["type"] = df["type"].str.upper().replace({"ACCIDENT": "ACIDENTE", "HAZARD": "PERIGO", "JAM": "CONGESTIONAMENTO"})
    if "speed" not in df:
        speed_col = next((c for c in ("speedkmh", "speed_kmh") if c in df), None)
        df["speed"] = pd.to_numeric(df[speed_col], errors="coerce") / 3.6 if speed_col else np.nan
    else:
        df["speed"] = pd.to_numeric(df["speed"], errors="coerce")
    df["speed_kmh"] = df["speed"] * 3.6
    if "delay" in df:
        df["delay"] = pd.to_numeric(df["delay"], errors="coerce")
    df["source"] = source
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    return df


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    if "uuid" in df and df["uuid"].notna().any():
        has_id = df["uuid"].notna() & df["uuid"].astype(str).str.strip().ne("")
        identified = df.loc[has_id].drop_duplicates(subset=["uuid"], keep="first")
        no_id = df.loc[~has_id]
        df = pd.concat([identified, no_id], ignore_index=True)
    keys = [c for c in ("timestamp", "street", "type", "subtype", "lat", "lon") if c in df]
    return df.drop_duplicates(subset=keys, keep="first").reset_index(drop=True) if keys else df


@st.cache_resource(show_spinner=False)
def drive_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    info = dict(st.secrets["gcp_service_account"])
    credentials = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def latest_h5(folder_id: str):
    service = drive_service()
    result = service.files().list(
        q=f"'{folder_id}' in parents and name contains '.h5' and trashed = false",
        fields="nextPageToken,files(id,name,modifiedTime)", orderBy="modifiedTime desc", pageSize=100,
    ).execute()
    return next((f["id"] for f in result.get("files", []) if f["name"].lower().endswith(".h5")), None)


@st.cache_data(ttl=600, show_spinner=False)
def load_h5(file_id: str) -> pd.DataFrame:
    from googleapiclient.http import MediaIoBaseDownload
    request = drive_service().files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    finished = False
    while not finished:
        _, finished = downloader.next_chunk()
    with tempfile.NamedTemporaryFile(suffix=".h5") as tmp:
        tmp.write(buf.getvalue())
        tmp.flush()
        return pd.read_hdf(tmp.name, key="s")


@st.cache_data(ttl=600, show_spinner="Carregando dados históricos...")
def load_local_file(path_text: str, modified: float):
    path = Path(path_text)
    return normalize_frame(read_csv_robust(path), path.name)


def load_local_collection(paths: list[Path]):
    frames, errors = [], []
    for path in paths:
        if not path.exists():
            errors.append(f"CSV ausente: {path.name}")
            continue
        try:
            frame = load_local_file(str(path), path.stat().st_mtime)
            if not frame.empty:
                frames.append(frame)
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")
    return (deduplicate(pd.concat(frames, ignore_index=True, sort=False)) if frames else pd.DataFrame(), errors)


def load_drive_collection(folder_ids: list[str], jams=False):
    frames, errors = [], []
    for folder in folder_ids:
        try:
            file_id = latest_h5(folder)
            if file_id:
                frame = normalize_frame(load_h5(file_id), f"hdf5:{file_id}", jams=jams)
                if not frame.empty:
                    frames.append(frame)
            else:
                errors.append(f"Sem HDF5 na pasta {folder}")
        except Exception as exc:
            errors.append(f"Drive {folder}: {exc}")
    return (deduplicate(pd.concat(frames, ignore_index=True, sort=False)) if frames else pd.DataFrame(), errors)


def within_foz(frame):
    if frame.empty:
        return frame
    return frame[frame["lat"].between(BBOX[0], BBOX[1]) & frame["lon"].between(BBOX[2], BBOX[3])].copy()


def pothole_scope(frame, through_august=True):
    if frame.empty:
        return frame
    scope = frame[frame["subtype"].eq("BURACO NA VIA") & frame["year"].isin([2024, 2025, 2026])].copy()
    if through_august:
        scope = scope[~((scope["year"] == 2026) & (scope["month"] > 8))]
    return scope


def make_map(frame, heat=False, paths=False, limit=1800):
    points = within_foz(frame)
    center = [float(points["lat"].mean()), float(points["lon"].mean())] if not points.empty else list(CENTER)
    map_obj = folium.Map(location=center, zoom_start=12, tiles="OpenStreetMap")
    if points.empty:
        return map_obj, 0
    points = points.sample(min(limit, len(points)), random_state=42) if len(points) > limit else points
    if heat:
        HeatMap(points[["lat", "lon"]].values.tolist(), radius=19, blur=14).add_to(map_obj)
    else:
        cluster = MarkerCluster().add_to(map_obj)
        for row in points.itertuples(index=False):
            street = str(getattr(row, "street", "N/D"))
            subtype = str(getattr(row, "subtype", "N/D"))
            timestamp = getattr(row, "timestamp", pd.NaT)
            label = timestamp.strftime("%d/%m/%Y %H:%M") if pd.notna(timestamp) else "N/D"
            from html import escape
            folium.CircleMarker(
                [row.lat, row.lon], radius=5, color="#dc2626", fill=True,
                tooltip=escape(street), popup=f"<b>{escape(street)}</b><br>{escape(subtype)}<br>{label}",
            ).add_to(cluster)
    if paths and "line" in frame:
        for item in frame["line"].head(150):
            try:
                line = item if isinstance(item, list) else ast.literal_eval(str(item))
                coords = [[float(p["y"]), float(p["x"])] for p in line if isinstance(p, dict)]
                if len(coords) > 1:
                    folium.PolyLine(coords, color="#7c3aed", weight=4).add_to(map_obj)
            except (ValueError, TypeError, SyntaxError, KeyError):
                continue
    return map_obj, len(points)


def render_3d(frame, mode="Hexágonos", radius=140, pitch=50):
    if pdk is None:
        st.warning("Instale pydeck para utilizar a visualização 3D.")
        return
    sample = within_foz(frame)
    if sample.empty:
        st.info("Sem pontos geográficos para esta seleção.")
        return
    if len(sample) > 40000:
        sample = sample.sample(40000, random_state=42)
        st.caption("Amostra de 40.000 registros para preservar o desempenho; totais e gráficos usam todos os registros.")
    if mode == "Hexágonos":
        layer = pdk.Layer("HexagonLayer", sample[["lon", "lat"]], get_position="[lon, lat]", radius=radius,
                          elevation_scale=28, extruded=True, pickable=True, auto_highlight=True,
                          color_range=[[255,255,178],[254,204,92],[253,141,60],[240,59,32],[189,0,38]])
        tooltip = {"html": "{elevationValue} registros no hexágono"}
    else:
        streets = (sample.groupby("street", dropna=False).agg(ocorrencias=("street", "size"),
                     lat=("lat", "mean"), lon=("lon", "mean")).reset_index().nlargest(40, "ocorrencias"))
        layer = pdk.Layer("ColumnLayer", streets, get_position="[lon, lat]", get_elevation="ocorrencias",
                          elevation_scale=35, radius=95, get_fill_color=[220, 70, 50, 190],
                          extruded=True, pickable=True)
        tooltip = {"html": "<b>{street}</b><br>{ocorrencias} registros"}
    deck = pdk.Deck(layers=[layer], initial_view_state=pdk.ViewState(
        latitude=CENTER[0], longitude=CENTER[1], zoom=12.2, pitch=pitch, bearing=0),
        map_style="dark", tooltip=tooltip)
    st.pydeck_chart(deck, use_container_width=True, height=610)
    st.caption("Alturas representam volume de registros; não representam altura real de edifícios nem fluxos observados.")


with st.sidebar:
    st.title("🚦 WazeFoz")
    st.caption("Foz do Iguaçu · Pesquisa em mobilidade urbana")
    st.subheader("Fonte da análise anual")
    annual_source = st.radio("Base de buracos", ["CSV principal", "Todos os CSVs (deduplicados)"], index=0)
    use_drive = st.toggle("Complementar painel operacional com HDF5 do Drive", value=False)
    if st.button("🔄 Atualizar cache"):
        st.cache_data.clear()
        st.rerun()

paths = [ROOT / PRIMARY_CSV] if annual_source == "CSV principal" else [ROOT / name for name in CSV_FILES]
historical, local_errors = load_local_collection(paths)
alerts, jams, drive_errors = historical, pd.DataFrame(), []
if use_drive:
    drive_alerts, err_a = load_drive_collection(FOLDERS_ALERTS)
    jams, err_j = load_drive_collection(FOLDERS_JAMS, jams=True)
    drive_errors = err_a + err_j
    if not drive_alerts.empty:
        alerts = deduplicate(pd.concat([drive_alerts, historical], ignore_index=True, sort=False)) if not historical.empty else drive_alerts

st.title("🚦 WazeFoz — análise da mobilidade urbana")
st.caption("Registros colaborativos Waze · análise temporal, espacial e apoio exploratório à decisão")
if historical.empty:
    st.error("Não foi possível carregar a base CSV histórica. Confira os arquivos na mesma pasta de streamlit_app.py.")
    for message in local_errors:
        st.warning(message)
    st.stop()

buracos = pothole_scope(historical)
with st.sidebar:
    st.divider()
    available_years = sorted(buracos["year"].dropna().astype(int).unique().tolist()) if not buracos.empty else []
    selected_year = st.selectbox("Ano de análise", available_years or [2026], index=max(0, len(available_years) - 1))
    selected_months = st.multiselect("Meses (mapas e tabela)", list(range(1, 13)), default=list(range(1, 13)), format_func=lambda m: MONTHS[m - 1])
    roads = sorted(buracos.loc[buracos["year"].eq(selected_year), "street"].dropna().unique().tolist()) if not buracos.empty else []
    selected_road = st.selectbox("Via", ["Todas"] + roads)
    st.caption("Os filtros de mês e via alteram mapas e registros; o gráfico histórico e a auditoria permanecem globais.")

scope = buracos[buracos["year"].eq(selected_year) & buracos["month"].isin(selected_months)].copy()
if selected_road != "Todas":
    scope = scope[scope["street"].eq(selected_road)].copy()

annual = buracos.groupby("year").size().reindex([2024, 2025, 2026], fill_value=0)
cols = st.columns(4)
for idx, year in enumerate((2024, 2025, 2026)):
    cols[idx].metric(f"Buracos {year}", f"{int(annual[year]):,}".replace(",", "."))
cols[3].metric("Vias no recorte", int(scope["street"].nunique()))
st.info("2026: recorte de janeiro a agosto. Contagens são registros da fonte selecionada, não uma medição física completa das vias.")

(tab_annual, tab_maps, tab_incidents, tab_jams, tab_3d, tab_audit) = st.tabs([
    "🕳️ Buracos 2024–2026", "🗺️ Mapa espacial", "🚨 Incidentes", "🚗 Congestionamentos",
    "🧊 Cidade 3D", "🧾 Auditoria e dados",
])

with tab_annual:
    st.subheader("Série mensal de buracos")
    monthly = buracos.groupby(["year", "month"]).size().reset_index(name="Registros")
    if monthly.empty:
        st.warning("Não há registros de buracos no período.")
    else:
        monthly["Ano"] = monthly["year"].astype(int).astype(str)
        fig = px.line(monthly, x="month", y="Registros", color="Ano", markers=True,
                      title="Comparação mensal — 2024, 2025 e 2026")
        fig.update_xaxes(tickvals=list(range(1,13)), ticktext=MONTHS, title="Mês")
        fig.update_layout(hovermode="x unified", height=470)
        st.plotly_chart(fig, use_container_width=True)
    st.subheader(f"Cinco vias com mais registros — {selected_year}")
    ranked = (buracos[buracos["year"].eq(selected_year)].groupby("street").size()
              .reset_index(name="Registros").sort_values("Registros", ascending=False).head(5))
    if ranked.empty:
        st.info("Sem vias disponíveis para o ano.")
    else:
        st.plotly_chart(px.bar(ranked.iloc[::-1], x="Registros", y="street", orientation="h", text="Registros",
                                labels={"street": "Via"}, title="Ranking anual; independente dos filtros de mês e via"),
                        use_container_width=True)
        st.dataframe(ranked.rename(columns={"street": "Via"}), hide_index=True, use_container_width=True)
    st.caption("O ranking representa frequência de registros, não severidade constatada em vistoria.")

with tab_maps:
    st.subheader(f"Distribuição geográfica — {selected_year}")
    mode = st.radio("Exibição", ["Calor", "Pontos"], horizontal=True)
    map_obj, rendered = make_map(scope, heat=mode == "Calor")
    st_folium(map_obj, height=590, use_container_width=True, key=f"potholes_{mode}_{selected_year}_{selected_road}")
    st.caption(f"{rendered} pontos exibidos; mapa limita a 1.800 pontos por desempenho. O total anual usa todos os registros.")
    st.caption("Sem coordenadas ou fora da caixa geográfica de Foz: omitidos apenas dos mapas, não dos totais.")

with tab_incidents:
    st.subheader("Outros tipos de ocorrência")
    available_types = sorted(alerts["type"].dropna().unique().tolist()) if not alerts.empty else []
    categories = st.multiselect("Tipos", available_types, default=available_types)
    incident_period = alerts[alerts["year"].eq(selected_year) & alerts["type"].isin(categories)].copy() if not alerts.empty else pd.DataFrame()
    if incident_period.empty:
        st.info("Nenhum incidente encontrado neste recorte.")
    else:
        st.plotly_chart(px.bar(incident_period.groupby("type").size().reset_index(name="Registros"),
                                x="type", y="Registros", title="Ocorrências por tipo"), use_container_width=True)
        st_folium(make_map(incident_period)[0], height=520, use_container_width=True, key="incidents_map")

with tab_jams:
    st.subheader("Congestionamentos HDF5")
    if jams.empty:
        st.info("Ative a leitura HDF5 na barra lateral e configure gcp_service_account para explorar congestionamentos.")
    else:
        jams_period = jams[jams["year"].eq(selected_year)].copy()
        valid_speeds = jams_period["speed_kmh"].dropna() if not jams_period.empty else pd.Series(dtype=float)
        a, b, c = st.columns(3)
        a.metric("Registros", len(jams_period))
        b.metric("Velocidade média", f"{valid_speeds.mean():.1f} km/h" if not valid_speeds.empty else "N/D")
        c.metric("Atraso médio", f"{jams_period['delay'].mean():.0f} s" if "delay" in jams_period and jams_period["delay"].notna().any() else "N/D")
        if not jams_period.empty:
            jam_map, count = make_map(jams_period, paths=True)
            st_folium(jam_map, height=520, use_container_width=True, key="jams_map")
            st.caption(f"Até {count} pontos exibidos; até 150 trajetos com geometria válida.")

with tab_3d:
    st.subheader("Visualização tridimensional exploratória")
    mode3d = st.radio("Camada", ["Hexágonos", "Colunas por via"], horizontal=True)
    radius = st.slider("Raio dos hexágonos (m)", 60, 400, 140, 20)
    pitch = st.slider("Inclinação", 0, 70, 50, 5)
    render_3d(scope, mode3d, radius, pitch)
    st.subheader("Linha do tempo interativa")
    timeline = scope.dropna(subset=["timestamp"]).copy()
    if not timeline.empty:
        timeline["bucket"] = timeline["timestamp"].dt.to_period("M").dt.to_timestamp()
        buckets = sorted(timeline["bucket"].unique())
        if buckets:
            step = st.slider("Mês exibido", 0, len(buckets)-1, 0)
            current = timeline[timeline["bucket"].eq(buckets[step])]
            st.caption(f"{pd.Timestamp(buckets[step]).strftime('%m/%Y')} · {len(current)} registros")
            render_3d(current, mode3d, radius, pitch)

with tab_audit:
    st.subheader("Validação frente ao resumo EICTI")
    st.caption("Os valores do resumo são referências de conferência, não substituem os dados calculados.")
    checks = []
    for year, reference in EXPECTED.items():
        yr = buracos[buracos["year"].eq(year)]
        monthly_counts = yr.groupby("month").size()
        streets = yr.groupby("street").size()
        calculated_total = len(yr)
        calculated_peak = int(monthly_counts.get(reference["month"], 0))
        matching_street = streets[streets.index.astype(str).str.casefold() == reference["street"].casefold()]
        calculated_street = int(matching_street.sum())
        checks.append({
            "Ano": year, "Total resumo": reference["total"], "Total calculado": calculated_total,
            "Mês pico esperado": MONTHS[reference["month"] - 1], "Pico resumo": reference["peak"],
            "Mês calculado": calculated_peak, "Via resumo": reference["street"],
            "Via resumo (registros)": reference["street_count"], "Via calculada": calculated_street,
            "Status": "OK" if (calculated_total, calculated_peak, calculated_street) == (
                reference["total"], reference["peak"], reference["street_count"]) else "REVISAR",
        })
    st.dataframe(pd.DataFrame(checks), hide_index=True, use_container_width=True)
    if any(item["Status"] == "REVISAR" for item in checks):
        st.warning("Divergências podem indicar base distinta, cobertura diferente, duplicidade, parse de data ou padronização de nomes. Não ajuste números manualmente.")
    st.write("**Fonte anual selecionada:**", annual_source)
    st.write("**Registros do CSV:**", len(historical))
    st.write("**Datas válidas:**", int(historical["timestamp"].notna().sum()))
    st.write("**Coordenadas válidas:**", int(historical[["lat", "lon"]].notna().all(axis=1).sum()))
    st.write("**Buracos após filtros anuais:**", len(buracos))
    for message in local_errors + drive_errors:
        st.warning(message)
    st.dataframe(scope[[c for c in ("timestamp", "street", "type", "subtype", "lat", "lon", "source") if c in scope]],
                 hide_index=True, use_container_width=True)
    st.download_button("Baixar recorte CSV", scope.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"wazefoz_buracos_{selected_year}.csv", mime="text/csv")

st.markdown("---")
st.caption(f"WazeFoz · UNILA · {datetime.now(FOZ_TZ).year} · Registros colaborativos sujeitos a subnotificação e validação em campo.")

