import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =========================================================
# 1. CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="MIMO | Monitor Operacional",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta (la misma que usa el CSS)
COLORES = {"Baja": "#36C995", "Media": "#F2B84B", "Alta": "#F16B75"}
AZUL, CIAN, MORADO = "#58A6FF", "#43D6D0", "#9B7BEA"
RUTA = "#3DF2C8"                      # verde turquesa del recorrido y la aceleración
GRILLA = "rgba(120,150,190,.14)"

# Alturas de los paneles (para que queden parejos)
ALTO_HEROE = 590
ALTO_INFERIOR = 400


# =========================================================
# 2. ESTILO VISUAL: PANEL INDUSTRIAL OSCURO
# =========================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
        --bg: #050D1A;
        --panel: #0B1A2E;
        --line: #16304F;
        --text: #EAF1FA;
        --muted: #8FA3BC;
    }

    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background:
            radial-gradient(ellipse at 80% -10%, rgba(30,120,160,.15), transparent 40%),
            linear-gradient(160deg, #050D1A 0%, #07111F 60%, #060F1C 100%);
        color: var(--text);
    }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1760px; padding: 1rem 2rem 1rem 2rem; }
    [data-testid="stVerticalBlock"] { gap: .75rem; }
    [data-testid="stHorizontalBlock"] { gap: .8rem; }
    #MainMenu, footer { visibility: hidden; }

    /* ---------- Radios: se oculta el círculo, solo queda el texto ---------- */
    [role="radiogroup"] label > :not(:has([data-testid="stMarkdownContainer"])) { display: none !important; }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #081426 0%, #060F1D 100%);
        border-right: 1px solid #12253F;
    }
    [data-testid="stSidebar"] * { color: #DCE7F5; }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] section {
        background: #0F2037; border: 1px dashed #2E4B70; border-radius: 10px;
    }
    .brand { display:flex; align-items:center; gap:.7rem; padding:.2rem 0 .6rem 0; }
    .brand-ico {
        width:42px; height:42px; border-radius:11px; display:flex; align-items:center; justify-content:center;
        background: linear-gradient(135deg, #1B9FD6, #3DF2C8); color:#04202B;
        box-shadow: 0 6px 18px rgba(40,200,200,.30);
    }
    .brand-name { font-size:1.45rem; font-weight:800; letter-spacing:-.02em; color:#F2F7FD; line-height:1.1; }
    .brand-sub { font-size:.62rem; font-weight:600; letter-spacing:.14em; color:#7E94B0; }
    .side-label { font-size:.66rem; font-weight:700; letter-spacing:.12em; color:#6F86A4; margin:.9rem 0 .35rem 0; }
    .side-card { background:#0C1B30; border:1px solid #16304F; border-radius:10px; padding:.65rem .8rem; }
    .side-row { display:flex; justify-content:space-between; align-items:center; padding:.18rem 0; font-size:.82rem; }
    .side-row span:first-child { color:#8FA3BC; }

    /* Navegación como menú */
    [data-testid="stSidebar"] [role="radiogroup"] { gap:.25rem; }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        width:100%; margin:0; padding:.62rem .85rem; border-radius:9px;
        border:1px solid transparent; transition: background .15s ease;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { background:#0F2440; }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, #12607A, #178A8C);
        border-color:#2FC7BD;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label p { font-size:.9rem; font-weight:500; }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p { color:#fff !important; font-weight:650; }

    /* Botones tipo "pastilla" (selector de ventana de tiempo) */
    [data-testid="stMain"] [role="radiogroup"] { gap:.4rem; justify-content:flex-end; flex-wrap:wrap; }
    [data-testid="stMain"] [role="radiogroup"] label {
        margin:0; padding:.34rem .9rem; border-radius:999px; border:1px solid #1B3556;
        background:#0C1B30; transition: all .15s ease;
    }
    [data-testid="stMain"] [role="radiogroup"] label:hover { border-color:#2FC7BD; }
    [data-testid="stMain"] [role="radiogroup"] label:has(input:checked) { background:#0F4B57; border-color:#3DF2C8; }
    [data-testid="stMain"] [role="radiogroup"] label p { font-size:.8rem; font-weight:600; color:#C9D8EA !important; }
    [data-testid="stMain"] [role="radiogroup"] label:has(input:checked) p { color:#fff !important; }

    /* ---------- Barra superior ---------- */
    .topbar {
        display:flex; align-items:center; justify-content:space-between; gap:1rem;
        padding:.55rem .4rem .85rem .4rem; margin-bottom:.35rem; border-bottom:1px solid #12253F;
    }
    .topbar-title { font-size:1.55rem; font-weight:700; letter-spacing:-.03em; color:#F2F7FD; margin-right:.9rem; }
    .topbar-sub { font-size:.82rem; color:var(--muted); }
    .topbar-right { display:flex; align-items:center; gap:1.4rem; }
    .tb-item { display:flex; align-items:center; gap:.6rem; color:#C9D8EA; font-size:.82rem; line-height:1.25; }
    .tb-sep { width:1px; height:34px; background:#16304F; }
    .tb-bell { position:relative; color:#C9D8EA; display:flex; }
    .tb-badge {
        position:absolute; top:-8px; right:-9px; min-width:19px; height:19px; padding:0 5px;
        border-radius:10px; background:#E5484D; color:#fff; font-size:.68rem; font-weight:700;
        display:flex; align-items:center; justify-content:center;
    }
    .pill { font-size:.7rem; font-weight:700; letter-spacing:.04em; padding:.32rem .75rem; border-radius:20px;
            border:1px solid; white-space:nowrap; }
    .pill-demo { color:#8FB4E6; background:#0F2340; border-color:#23406A; }
    .pill-csv  { color:#5FDDB0; background:#0E2E27; border-color:#1D5C4A; }

    /* ---------- Tarjetas KPI (compactas) ---------- */
    .kpi {
        background: linear-gradient(160deg, #0D1D33 0%, #0A182B 100%);
        border:1px solid #16304F; border-radius:12px; padding:.75rem .9rem .7rem .9rem;
        min-height:108px; display:flex; flex-direction:column; justify-content:space-between;
    }
    .kpi-top { display:flex; align-items:center; gap:.75rem; }
    .kpi-ico {
        width:44px; height:44px; border-radius:50%; flex:0 0 44px; border:1px solid;
        display:flex; align-items:center; justify-content:center;
    }
    .kpi-label { font-size:.72rem; font-weight:600; color:#A5B8CF; letter-spacing:.02em; }
    .kpi-val { font-size:1.55rem; font-weight:700; letter-spacing:-.03em; line-height:1.15; }
    .kpi-sub { font-size:.74rem; color:#9FB2CA; margin-top:.45rem; }
    .kpi-bar { height:5px; border-radius:4px; background:#16283F; margin-top:.35rem; overflow:hidden; }
    .kpi-bar span { display:block; height:100%; border-radius:4px; }

    /* ---------- Paneles ---------- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(160deg, rgba(13,29,51,.96), rgba(9,21,38,.96));
        border:1px solid #16304F; border-radius:13px; padding:.35rem .5rem;
    }
    .panel-title {
        font-size:.8rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:#E4EDF8;
        margin:.2rem 0 .1rem 0;
    }
    .panel-title small { font-size:.72rem; font-weight:500; letter-spacing:0; text-transform:none;
                         color:var(--muted); margin-left:.4rem; }
    .hero-title { font-size:1.05rem; font-weight:650; color:#F2F7FD; letter-spacing:-.01em; padding-top:.35rem; }
    .hero-title small { font-size:.78rem; font-weight:400; color:var(--muted); margin-left:.6rem; }

    [data-testid="stExpander"] { border:1px solid #16304F; border-radius:13px; background:rgba(10,24,43,.9); }
    [data-testid="stExpander"] summary p { font-weight:600; color:#E4EDF8; }

    /* ---------- Tablas ---------- */
    table.tbl { width:100%; border-collapse:collapse; font-size:.82rem; margin-top:.3rem; }
    table.tbl th { text-align:left; font-weight:600; font-size:.72rem; color:#8FA3BC; padding:.5rem .4rem;
                   border-bottom:1px solid #1B3556; }
    table.tbl td { padding:.5rem .4rem; border-bottom:1px solid #12243C; color:#E1EAF6; }
    table.tbl tr:last-child td { border-bottom:none; }
    .mono { font-family:'IBM Plex Mono', monospace; }
    .chip { display:inline-block; font-size:.72rem; font-weight:700; padding:.12rem .55rem; border-radius:6px; }
    .chip-baja  { color:#5FE0B4; background:#10382F; }
    .chip-media { color:#FFCF73; background:#463716; }
    .chip-alta  { color:#FF8F98; background:#4B2029; }
    .dot { display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:.5rem; }

    .leg-row { display:flex; justify-content:space-between; align-items:center; padding:.42rem 0; font-size:.86rem;
               border-bottom:1px solid #12243C; }
    .leg-row:last-child { border-bottom:none; }
    .leg-val { font-family:'IBM Plex Mono', monospace; color:#F2F7FD; }

    /* Ficha del evento */
    .ficha { display:grid; grid-template-columns:repeat(3, 1fr); gap:.6rem; margin-top:.4rem; }
    .ficha-item { background:#0C1B30; border:1px solid #16304F; border-radius:10px; padding:.6rem .75rem; }
    .ficha-item .l { font-size:.7rem; color:#8FA3BC; font-weight:600; }
    .ficha-item .v { font-family:'IBM Plex Mono', monospace; font-size:1.1rem; font-weight:600; color:#F2F7FD; margin-top:.15rem; }
    .ficha-foot { font-size:.78rem; color:#8FA3BC; margin-top:.7rem; line-height:1.6; }

    /* ---------- Controles ---------- */
    h1, h2, h3, h4 { color:#F0F5FC !important; letter-spacing:-.03em; }
    p, label { color:#D3DFED; }
    [data-testid="stCaptionContainer"] { color:var(--muted) !important; font-size:.76rem; }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        border-radius:8px; border:1px solid #28456B; background:#0F2037; color:#EAF1FA;
    }
    [data-testid="stSelectbox"] label, [data-testid="stNumberInput"] label, [data-testid="stFileUploader"] label {
        color:#AFC0D4 !important; font-size:.76rem; font-weight:600;
    }
    [data-testid="stAlert"] { background:#0F2037; border:1px solid #28456B; border-radius:9px; }
    .stButton button, .stDownloadButton button {
        background: linear-gradient(135deg, #1B8FA8, #166F85); color:white; border:1px solid #2FC7BD;
        border-radius:8px; font-weight:650; min-height:2.3rem; transition: all .18s ease;
    }
    .stButton button:hover, .stDownloadButton button:hover {
        background: linear-gradient(135deg, #24B0C7, #1B8CA5); color:white; border-color:#6FF0DC;
    }
    [data-testid="stMetric"] { background:#0C1B30; border:1px solid #16304F; border-radius:12px; padding:.8rem 1rem; }
    [data-testid="stMetricLabel"] { color:#9FB2CA !important; font-size:.74rem !important; font-weight:600 !important; }
    [data-testid="stMetricValue"] { color:#F3F7FD !important; font-family:'IBM Plex Mono', monospace !important; font-size:1.5rem !important; }
    [data-testid="stDataFrame"] { border:1px solid #16304F; border-radius:10px; overflow:hidden; }
    hr { border-color:#12253F; margin:.4rem 0; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. AYUDANTES DE INTERFAZ
# =========================================================

ICONOS = {
    "activity": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "gauge": '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
    "bell": '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
    "calendar": '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    "bars": '<path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
}


def icono(nombre, tam=22):
    return (
        f'<svg viewBox="0 0 24 24" width="{tam}" height="{tam}" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONOS[nombre]}</svg>'
    )


def html(contenido):
    """Renderiza HTML sin que Markdown lo interprete como bloque de código."""
    limpio = "\n".join(l.strip() for l in contenido.splitlines() if l.strip())
    st.markdown(limpio, unsafe_allow_html=True)


def titulo_panel(texto, detalle=""):
    extra = f"<small>{detalle}</small>" if detalle else ""
    html(f'<div class="panel-title">{texto}{extra}</div>')


def tarjeta_kpi(columna, icono_nombre, etiqueta, valor, color, detalle="", porcentaje=None):
    barra = ""
    if porcentaje is not None:
        ancho = max(0, min(100, porcentaje))
        barra = f'<div class="kpi-bar"><span style="width:{ancho:.0f}%;background:{color}"></span></div>'
    with columna:
        html(f"""
        <div class="kpi">
          <div class="kpi-top">
            <div class="kpi-ico" style="color:{color};background:{color}1F;border-color:{color}55">{icono(icono_nombre, 20)}</div>
            <div><div class="kpi-label">{etiqueta}</div><div class="kpi-val" style="color:{color}">{valor}</div></div>
          </div>
          <div><div class="kpi-sub">{detalle}</div>{barra}</div>
        </div>
        """)


def tabla_html(df, columna_nivel=None, columnas_mono=()):
    encabezado = "".join(f"<th>{c}</th>" for c in df.columns)
    filas = []
    for _, fila in df.iterrows():
        celdas = []
        for c in df.columns:
            v = fila[c]
            if c == columna_nivel:
                celdas.append(f'<td><span class="chip chip-{str(v).lower()}">{v}</span></td>')
            elif c in columnas_mono:
                celdas.append(f'<td class="mono">{v}</td>')
            else:
                celdas.append(f"<td>{v}</td>")
        filas.append("<tr>" + "".join(celdas) + "</tr>")
    return f'<table class="tbl"><thead><tr>{encabezado}</tr></thead><tbody>{"".join(filas)}</tbody></table>'


def hex_a_rgba(color, alfa):
    color = color.lstrip("#")
    r, g, b = (int(color[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alfa})"


def estilo_grafico(fig, altura):
    fig.update_layout(
        height=altura,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#A9BBD2", family="Inter, sans-serif", size=11),
        margin=dict(l=10, r=14, t=28, b=10),
        hoverlabel=dict(bgcolor="#142640", bordercolor="#3A6AA5", font=dict(color="#F4F8FE", family="Inter")),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRILLA, zeroline=False, linecolor="#1B3556", tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True, gridcolor=GRILLA, zeroline=False, tickfont=dict(size=10))
    return fig


# ---------------------------------------------------------
# Mapa
# ---------------------------------------------------------

# Compatibilidad entre versiones de Plotly (Scattermap en v6, Scattermapbox antes)
MAPA_NUEVO = hasattr(go, "Scattermap")

CAPA_SATELITE = [{
    "below": "traces",
    "sourcetype": "raster",
    "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"],
}]


def traza_mapa(**kwargs):
    return (go.Scattermap if MAPA_NUEVO else go.Scattermapbox)(**kwargs)


def zoom_ajustado(df, altura_px, ancho_px=760):
    """Calcula el zoom para que todo el recorrido quepa en el mapa."""
    lat_media = float(df["latitud"].mean())
    lat_m = max((df["latitud"].max() - df["latitud"].min()) * 111320, 60.0)
    lon_m = max((df["longitud"].max() - df["longitud"].min()) * 111320 * np.cos(np.radians(lat_media)), 60.0)
    escala = 156543.03 * np.cos(np.radians(lat_media))
    z_lat = np.log2(escala / (lat_m / (altura_px * 0.78)))
    z_lon = np.log2(escala / (lon_m / (ancho_px * 0.78)))
    return float(np.clip(min(z_lat, z_lon), 10, 18))


def crear_mapa(df, altura=490, estilo="Satélite"):
    fig = go.Figure()

    # Brillo suave bajo la línea y línea principal
    fig.add_trace(traza_mapa(
        lat=df["latitud"], lon=df["longitud"], mode="lines",
        line=dict(width=10, color=hex_a_rgba(RUTA, 0.22)), hoverinfo="skip", showlegend=False
    ))
    fig.add_trace(traza_mapa(
        lat=df["latitud"], lon=df["longitud"], mode="lines",
        line=dict(width=4, color=RUTA), hoverinfo="skip", name="Recorrido"
    ))

    tiene_vel = "velocidad" in df.columns
    for nivel, tam in [("Media", 11), ("Alta", 15)]:
        sub = df[df["intensidad"] == nivel]
        if len(sub) == 0:
            continue
        vel = sub["velocidad"].round(0) if tiene_vel else pd.Series(np.nan, index=sub.index)
        fig.add_trace(traza_mapa(
            lat=sub["latitud"], lon=sub["longitud"], mode="markers",
            marker=dict(size=tam, color=COLORES[nivel]), name=f"Evento {nivel.lower()}",
            customdata=np.stack([sub["timestamp"].dt.strftime("%H:%M:%S"),
                                 sub["aceleracion"].round(2), vel], axis=-1),
            hovertemplate="%{customdata[0]}<br>%{customdata[1]} g · %{customdata[2]} km/h<extra>"
                          + nivel + "</extra>"
        ))

    ultimo = df.iloc[-1]
    fig.add_trace(traza_mapa(
        lat=[ultimo["latitud"]], lon=[ultimo["longitud"]], mode="markers",
        marker=dict(size=22, color="rgba(255,255,255,.35)"), hoverinfo="skip", showlegend=False
    ))
    fig.add_trace(traza_mapa(
        lat=[ultimo["latitud"]], lon=[ultimo["longitud"]], mode="markers",
        marker=dict(size=12, color="#FFFFFF"), name="Última posición", hoverinfo="name"
    ))

    configuracion = dict(
        center=dict(lat=float(df["latitud"].mean()), lon=float(df["longitud"].mean())),
        zoom=zoom_ajustado(df, altura),
    )
    if estilo == "Satélite":
        configuracion.update(style="white-bg", layers=CAPA_SATELITE)
    else:
        configuracion.update(style="carto-darkmatter")

    # Tarjeta flotante con el estado de la última lectura
    vel_txt = f"{ultimo['velocidad']:.0f} km/h" if tiene_vel and pd.notna(ultimo["velocidad"]) else "sin dato"
    color_nivel = COLORES[ultimo["intensidad"]]
    tarjeta = (
        f"<b>Última lectura · {ultimo['timestamp']:%H:%M:%S}</b><br>"
        f"Nivel: <span style='color:{color_nivel}'><b>{ultimo['intensidad']}</b></span>"
        f" · {ultimo['aceleracion']:.2f} g<br>Velocidad: {vel_txt}"
    )
    anotaciones = [dict(
        text=tarjeta, xref="paper", yref="paper", x=0.99, y=0.97, xanchor="right", yanchor="top",
        align="left", showarrow=False, bgcolor="rgba(8,20,36,.88)", bordercolor="#2A4A70",
        borderwidth=1, borderpad=8, font=dict(size=11, color="#EAF1FA")
    )]
    if estilo == "Satélite":
        anotaciones.append(dict(
            text="Imágenes: Esri, Maxar, Earthstar Geographics", xref="paper", yref="paper",
            x=0.01, y=0.01, xanchor="left", yanchor="bottom", showarrow=False,
            bgcolor="rgba(8,20,36,.6)", font=dict(size=9, color="#C5D5E8")
        ))

    fig.update_layout(
        height=altura, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", x=0.01, y=0.99, bgcolor="rgba(8,20,36,.82)",
                    bordercolor="#1B3556", borderwidth=1, font=dict(size=10, color="#C5D5E8")),
        annotations=anotaciones,
        **{"map" if MAPA_NUEVO else "mapbox": configuracion}
    )
    return fig


# ---------------------------------------------------------
# Velocidad estimada a partir del GPS
# ---------------------------------------------------------

def calcular_velocidad(df, k=3):
    """Velocidad en km/h usando la distancia entre puntos separados por k muestras.
    Así el ruido típico del GPS no inventa movimiento cuando el camión está detenido."""
    if df["latitud"].isna().all() or df["longitud"].isna().all():
        return pd.Series(np.nan, index=df.index)
    lat, lon = df["latitud"], df["longitud"]
    dy = (lat.shift(-k) - lat.shift(k)) * 111320
    dx = (lon.shift(-k) - lon.shift(k)) * 111320 * np.cos(np.radians(lat))
    dt = (df["timestamp"].shift(-k) - df["timestamp"].shift(k)).dt.total_seconds().replace(0, np.nan)
    v = (np.hypot(dx, dy) / dt * 3.6).bfill().ffill()
    return v.where(v.isna() | (v >= 3.0), 0.0)


# =========================================================
# 4. DATOS DE DEMOSTRACIÓN
# =========================================================

def crear_datos_demo():

    np.random.seed(42)

    ahora = datetime.now().replace(second=0, microsecond=0)

    tiempos = [
        ahora - timedelta(minutes=2 * (59 - i))
        for i in range(60)
    ]

    ax = np.random.normal(0.05, 0.18, 60)
    ay = np.random.normal(0.02, 0.16, 60)
    az = np.random.normal(1.00, 0.12, 60)

    # Simulación de algunos impactos
    impactos = [8, 16, 25, 33, 42, 51, 57]

    for i in impactos:
        ax[i] += np.random.uniform(0.8, 1.5)
        ay[i] += np.random.uniform(0.5, 1.0)
        az[i] += np.random.uniform(0.5, 1.2)

    aceleracion = np.sqrt(ax**2 + ay**2 + az**2)

    intensidades = []

    for valor in aceleracion:
        if valor >= 2.0:
            intensidades.append("Alta")
        elif valor >= 1.4:
            intensidades.append("Media")
        else:
            intensidades.append("Baja")

    # Coordenadas ficticias para demostración
    latitudes = -33.45 + np.cumsum(np.random.normal(0, 0.00015, 60))
    longitudes = -70.66 + np.cumsum(np.random.normal(0, 0.00015, 60))

    datos = pd.DataFrame({
        "timestamp": tiempos,
        "ax": ax,
        "ay": ay,
        "az": az,
        "aceleracion": aceleracion,
        "intensidad": intensidades,
        "latitud": latitudes,
        "longitud": longitudes
    })

    return datos


# =========================================================
# 5. CARGA Y PREPARACIÓN DE DATOS
# =========================================================

def preparar_datos(archivo):

    datos = pd.read_csv(archivo)

    # Normalizar nombres de columnas
    datos.columns = [
        str(columna).strip().lower()
        for columna in datos.columns
    ]

    columnas_requeridas = [
        "timestamp", "ax", "ay", "az"
    ]

    faltantes = [
        columna for columna in columnas_requeridas
        if columna not in datos.columns
    ]

    if faltantes:
        raise ValueError(
            "Faltan columnas obligatorias: "
            + ", ".join(faltantes)
        )

    datos["timestamp"] = pd.to_datetime(
        datos["timestamp"],
        errors="coerce"
    )

    for columna in ["ax", "ay", "az"]:
        datos[columna] = pd.to_numeric(
            datos[columna],
            errors="coerce"
        )

    datos = datos.dropna(
        subset=["timestamp", "ax", "ay", "az"]
    )

    datos["aceleracion"] = np.sqrt(
        datos["ax"]**2
        + datos["ay"]**2
        + datos["az"]**2
    )

    if "intensidad" not in datos.columns:

        datos["intensidad"] = np.select(
            [
                datos["aceleracion"] >= 2.0,
                datos["aceleracion"] >= 1.4
            ],
            ["Alta", "Media"],
            default="Baja"
        )

    if "latitud" not in datos.columns:
        datos["latitud"] = np.nan

    if "longitud" not in datos.columns:
        datos["longitud"] = np.nan

    return datos


# =========================================================
# 6. ESTADO DE LA SESIÓN
# =========================================================

if "datos_mimo" not in st.session_state:
    st.session_state.datos_mimo = crear_datos_demo()

if "modo_demo" not in st.session_state:
    st.session_state.modo_demo = True


# =========================================================
# 7. BARRA LATERAL
# =========================================================

NAVEGACION = {
    "Dashboard": "▣",
    "Geolocalización": "◎",
    "Historial de eventos": "≣",
    "Datos y configuración": "⚙",
}

with st.sidebar:

    html(f"""
    <div class="brand">
      <div class="brand-ico">{icono("activity", 22)}</div>
      <div><div class="brand-name">MIMO</div><div class="brand-sub">MONITOR OPERACIONAL</div></div>
    </div>
    """)

    pagina = st.radio(
        "Seleccionar sección",
        list(NAVEGACION.keys()),
        format_func=lambda nombre: f"{NAVEGACION[nombre]}   {nombre}",
        label_visibility="collapsed"
    )

    html('<div class="side-label">VEHÍCULO</div>')
    html(f"""
    <div class="side-card">
      <div class="side-row"><span>Código</span><b class="mono">CA-742</b></div>
      <div class="side-row"><span>Fuente</span>
        <span class="chip {'chip-media' if st.session_state.modo_demo else 'chip-baja'}">
        {'Demostración' if st.session_state.modo_demo else 'Archivo CSV'}</span></div>
    </div>
    """)

    html('<div class="side-label">FUENTE DE DATOS</div>')

    archivo = st.file_uploader(
        "Cargar mediciones CSV",
        type=["csv"],
        help="Carga un archivo CSV con timestamp, ax, ay y az."
    )

    if archivo is not None:

        try:
            datos_cargados = preparar_datos(archivo)

            st.session_state.datos_mimo = datos_cargados
            st.session_state.modo_demo = False

            st.success("Archivo cargado correctamente.")

        except Exception as error:
            st.error(f"No se pudo cargar el archivo: {error}")

    if st.button("Restablecer datos de demostración"):
        st.session_state.datos_mimo = crear_datos_demo()
        st.session_state.modo_demo = True
        st.rerun()

    html('<div class="side-label">UMBRALES DE INTENSIDAD</div>')

    umbral_medio = st.number_input(
        "Referencia media (g)", min_value=0.1, max_value=10.0,
        value=1.4, step=0.1
    )
    umbral_alto = st.number_input(
        "Referencia alta (g)", min_value=0.2, max_value=20.0,
        value=2.0, step=0.1
    )
    if umbral_alto <= umbral_medio:
        st.error("El umbral alto debe ser mayor que el umbral medio.")


# =========================================================
# 8. VARIABLES GENERALES
# =========================================================

datos = st.session_state.datos_mimo.copy()
datos = datos.sort_values("timestamp").reset_index(drop=True)

if len(datos) == 0:
    st.warning("El archivo no contiene mediciones válidas.")
    st.stop()

# Clasificación recalculada según los umbrales configurados por el usuario.
if umbral_alto > umbral_medio:
    datos["intensidad"] = np.select(
        [datos["aceleracion"] >= umbral_alto,
         datos["aceleracion"] >= umbral_medio],
        ["Alta", "Media"],
        default="Baja"
    )

datos["velocidad"] = calcular_velocidad(datos)

eventos = datos[datos["intensidad"].isin(["Media", "Alta"])].copy()
n_alta = int((datos["intensidad"] == "Alta").sum())

if len(datos) > 1:
    duracion = datos["timestamp"].max() - datos["timestamp"].min()
    minutos = int(duracion.total_seconds() / 60)
    tiempo_operacion = f"{minutos // 60} h {minutos % 60:02d} min"
else:
    tiempo_operacion = "Sin datos"

ultimo = datos.iloc[-1]
acc_max = float(datos["aceleracion"].max())
pct_eventos = len(eventos) / len(datos) * 100

TITULOS = {
    "Dashboard": ("Resumen operacional", "Aceleración y ubicación del vehículo"),
    "Geolocalización": ("Geolocalización", "Recorrido y posición de cada registro"),
    "Historial de eventos": ("Historial de eventos", "Consulta, filtra y descarga los registros"),
    "Datos y configuración": ("Datos y configuración", "Fuente de datos, componentes y formato del archivo"),
}
titulo, subtitulo = TITULOS[pagina]
ahora = datetime.now()


# =========================================================
# 9. BARRA SUPERIOR
# =========================================================

html(f"""
<div class="topbar">
  <div><span class="topbar-title">{titulo}</span><span class="topbar-sub">{subtitulo}</span></div>
  <div class="topbar-right">
    <span class="pill {'pill-demo' if st.session_state.modo_demo else 'pill-csv'}">
      ● {'MODO DEMOSTRACIÓN' if st.session_state.modo_demo else 'CSV CONECTADO'}</span>
    <div class="tb-item">{icono("calendar", 26)}<div>{ahora:%d/%m/%Y}<br>{ahora:%H:%M:%S}</div></div>
    <div class="tb-sep"></div>
    <div class="tb-bell" title="Eventos de intensidad alta">{icono("bell", 26)}<span class="tb-badge">{n_alta}</span></div>
  </div>
</div>
""")


# =========================================================
# 10. DASHBOARD
# =========================================================

if pagina == "Dashboard":

    # ---- Indicadores compactos ----
    k = st.columns(6)

    if acc_max >= umbral_alto:
        color_max = COLORES["Alta"]
    elif acc_max >= umbral_medio:
        color_max = COLORES["Media"]
    else:
        color_max = AZUL

    vel_ult = ultimo["velocidad"]
    vel_max = datos["velocidad"].max()
    hay_vel = pd.notna(vel_ult)

    tarjeta_kpi(k[0], "gauge", "Aceleración máxima", f"{acc_max:.2f} g", color_max,
                f"Umbral alto: {umbral_alto:.1f} g", acc_max / umbral_alto * 100)
    tarjeta_kpi(k[1], "truck", "Velocidad estimada", f"{vel_ult:.0f} km/h" if hay_vel else "—", AZUL,
                f"Máx. {vel_max:.0f} km/h" if hay_vel else "Requiere coordenadas GPS",
                (vel_ult / vel_max * 100) if hay_vel and vel_max > 0 else None)
    tarjeta_kpi(k[2], "bars", "Eventos detectados", f"{len(eventos):02d}", COLORES["Media"],
                f"{pct_eventos:.1f}% de los registros", pct_eventos)
    tarjeta_kpi(k[3], "alert", "Eventos de nivel alto", f"{n_alta:02d}", COLORES["Alta"],
                f"Sobre {umbral_alto:.1f} g", (n_alta / len(eventos) * 100) if len(eventos) else 0)
    tarjeta_kpi(k[4], "clock", "Tiempo de registro", tiempo_operacion, MORADO,
                f"{len(datos)} mediciones")
    tarjeta_kpi(k[5], "shield", "Última intensidad", ultimo["intensidad"], COLORES[ultimo["intensidad"]],
                f"Lectura de las {ultimo['timestamp']:%H:%M:%S}")

    # ---- Ventana de tiempo compartida por el gráfico y el mapa ----
    c_titulo, c_ventana = st.columns([1, 1.5])
    with c_titulo:
        html('<div class="hero-title">Aceleración y recorrido'
             '<small>el gráfico y el mapa usan la misma ventana de tiempo</small></div>')
    with c_ventana:
        periodo = st.radio(
            "Ventana de tiempo",
            ["Todo el registro", "Últimos 30 min", "Últimos 15 min", "Últimos 5 min"],
            horizontal=True, label_visibility="collapsed", key="dashboard_periodo"
        )

    datos_vista = datos.copy()
    if periodo != "Todo el registro":
        minutos_periodo = {"Últimos 30 min": 30, "Últimos 15 min": 15, "Últimos 5 min": 5}[periodo]
        limite = datos_vista["timestamp"].max() - timedelta(minutes=minutos_periodo)
        datos_vista = datos_vista[datos_vista["timestamp"] >= limite]

    # ---- Protagonistas: aceleración + mapa ----
    col_acc, col_mapa = st.columns([1, 1.4])

    with col_acc:
        with st.container(border=True, height=ALTO_HEROE):
            titulo_panel("Comportamiento de aceleración")
            variable_grafico = st.selectbox(
                "Señal", ["Resultante", "Eje X", "Eje Y", "Eje Z", "Todos los ejes"],
                key="dashboard_senal"
            )

            if len(datos_vista) > 0:
                variables = {
                    "Eje X": ("ax", AZUL),
                    "Eje Y": ("ay", COLORES["Baja"]),
                    "Eje Z": ("az", COLORES["Media"]),
                    "Resultante": ("aceleracion", RUTA),
                }
                mostrar = list(variables) if variable_grafico == "Todos los ejes" else [variable_grafico]
                fig_acc = go.Figure()
                for nombre in mostrar:
                    columna, color = variables[nombre]
                    fig_acc.add_trace(go.Scatter(
                        x=datos_vista["timestamp"], y=datos_vista[columna],
                        mode="lines", name=nombre,
                        line=dict(color=color, width=2.2, shape="spline", smoothing=0.3),
                        fill="tozeroy" if len(mostrar) == 1 else None,
                        fillcolor=hex_a_rgba(color, 0.12) if len(mostrar) == 1 else None,
                        hovertemplate="%{y:.2f} g<extra>" + nombre + "</extra>"
                    ))

                ver_resultante = variable_grafico in ["Resultante", "Todos los ejes"]
                eventos_graf = datos_vista[datos_vista["intensidad"].isin(["Media", "Alta"])]
                if ver_resultante and len(eventos_graf):
                    fig_acc.add_trace(go.Scatter(
                        x=eventos_graf["timestamp"], y=eventos_graf["aceleracion"],
                        mode="markers", name="Eventos",
                        marker=dict(color=eventos_graf["intensidad"].map(COLORES), size=9,
                                    line=dict(color="#F4F8FE", width=1.4)),
                        customdata=eventos_graf[["intensidad"]],
                        hovertemplate="%{y:.2f} g · nivel %{customdata[0]}<extra>Evento</extra>"
                    ))
                if ver_resultante:
                    fig_acc.add_hline(y=umbral_medio, line_dash="dot", line_color=COLORES["Media"],
                                      annotation_text=f"Media ({umbral_medio:.1f} g)",
                                      annotation_position="top left",
                                      annotation_font=dict(color=COLORES["Media"], size=10))
                    fig_acc.add_hline(y=umbral_alto, line_dash="dot", line_color=COLORES["Alta"],
                                      annotation_text=f"Alta ({umbral_alto:.1f} g)",
                                      annotation_position="top left",
                                      annotation_font=dict(color=COLORES["Alta"], size=10))

                estilo_grafico(fig_acc, ALTO_HEROE - 200)
                fig_acc.update_layout(
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                                font=dict(size=10, color="#C5D5E8"), bgcolor="rgba(0,0,0,0)")
                )
                fig_acc.update_yaxes(ticksuffix=" g")
                st.plotly_chart(fig_acc, use_container_width=True, config={"displayModeBar": False})
                st.caption("Resultante = √(ax² + ay² + az²); incluye la gravedad (≈1 g en reposo). "
                           "Los umbrales son referencias configurables.")
            else:
                st.info("No hay mediciones dentro del intervalo seleccionado.")

    with col_mapa:
        with st.container(border=True, height=ALTO_HEROE):
            c_m1, c_m2 = st.columns([2.2, 1])
            with c_m1:
                titulo_panel("Recorrido GPS", "posición de cada registro")
            with c_m2:
                estilo_mapa = st.selectbox("Estilo de mapa", ["Satélite", "Oscuro"],
                                           label_visibility="collapsed", key="estilo_mapa_dash")
            ubicaciones = datos_vista.dropna(subset=["latitud", "longitud"])
            if len(ubicaciones) > 0:
                st.plotly_chart(crear_mapa(ubicaciones, altura=ALTO_HEROE - 100, estilo=estilo_mapa),
                                use_container_width=True,
                                config={"displayModeBar": False, "scrollZoom": True})
            else:
                st.info("No hay coordenadas GPS disponibles en este intervalo.")

    # ---- Fila inferior: eventos, línea de tiempo y ficha ----
    b1, b2, b3 = st.columns([1.1, 1, 1])

    with b1:
        with st.container(border=True, height=ALTO_INFERIOR):
            titulo_panel("Últimos eventos")
            if len(eventos) > 0:
                tabla = eventos.sort_values("timestamp", ascending=False).head(7).copy()
                tabla["Hora"] = tabla["timestamp"].dt.strftime("%H:%M:%S")
                tabla["Resultante"] = tabla["aceleracion"].map(lambda v: f"{v:.2f} g")
                tabla["Nivel"] = tabla["intensidad"]
                tabla["Velocidad"] = tabla["velocidad"].map(lambda v: f"{v:.0f} km/h" if pd.notna(v) else "—")
                html(tabla_html(tabla[["Hora", "Nivel", "Resultante", "Velocidad"]],
                                columna_nivel="Nivel", columnas_mono=("Hora", "Resultante", "Velocidad")))
            else:
                st.info("Todavía no hay eventos registrados.")

    with b2:
        with st.container(border=True, height=ALTO_INFERIOR):
            titulo_panel("Eventos en el tiempo")
            if len(eventos) > 0:
                span_min = (datos["timestamp"].max() - datos["timestamp"].min()).total_seconds() / 60
                frecuencia = "10min" if span_min <= 180 else ("1h" if span_min <= 2880 else "1D")
                ev = eventos.copy()
                ev["bloque"] = ev["timestamp"].dt.floor(frecuencia)
                agrupado = ev.groupby(["bloque", "intensidad"]).size().unstack(fill_value=0)
                fig_ev = go.Figure()
                for nivel in ["Media", "Alta"]:
                    if nivel in agrupado.columns:
                        fig_ev.add_trace(go.Bar(
                            x=agrupado.index, y=agrupado[nivel], name=nivel, marker_color=COLORES[nivel],
                            hovertemplate="%{x|%H:%M}<br>%{y} eventos<extra>" + nivel + "</extra>"
                        ))
                estilo_grafico(fig_ev, ALTO_INFERIOR - 110)
                fig_ev.update_layout(
                    barmode="stack", bargap=0.35,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                                font=dict(size=10, color="#C5D5E8"))
                )
                fig_ev.update_yaxes(nticks=5, rangemode="tozero")
                st.plotly_chart(fig_ev, use_container_width=True, config={"displayModeBar": False})
                st.caption(f"Eventos agrupados cada {'10 minutos' if frecuencia == '10min' else ('hora' if frecuencia == '1h' else 'día')}.")
            else:
                st.info("Todavía no hay eventos registrados.")

    with b3:
        with st.container(border=True, height=ALTO_INFERIOR):
            titulo_panel("Ficha del evento")
            if len(eventos) > 0:
                eventos_detalle = eventos.sort_values("timestamp", ascending=False).reset_index(drop=True)
                opciones = {
                    f"{fila['timestamp'].strftime('%d/%m %H:%M:%S')} · {fila['intensidad']}": i
                    for i, fila in eventos_detalle.iterrows()
                }
                elegido = st.selectbox("Seleccionar registro", list(opciones.keys()), key="dashboard_evento")
                ev = eventos_detalle.iloc[opciones[elegido]]
                gps = (f"{ev['latitud']:.6f}, {ev['longitud']:.6f}"
                       if pd.notna(ev["latitud"]) and pd.notna(ev["longitud"]) else "No disponible")
                vel_ev = f"{ev['velocidad']:.0f} km/h" if pd.notna(ev["velocidad"]) else "—"
                html(f"""
                <div class="ficha">
                  <div class="ficha-item"><div class="l">Intensidad</div><div class="v"><span class="chip chip-{ev['intensidad'].lower()}">{ev['intensidad']}</span></div></div>
                  <div class="ficha-item"><div class="l">Resultante</div><div class="v">{ev['aceleracion']:.2f} g</div></div>
                  <div class="ficha-item"><div class="l">Velocidad</div><div class="v">{vel_ev}</div></div>
                  <div class="ficha-item"><div class="l">Eje X</div><div class="v">{ev['ax']:.2f} g</div></div>
                  <div class="ficha-item"><div class="l">Eje Y</div><div class="v">{ev['ay']:.2f} g</div></div>
                  <div class="ficha-item"><div class="l">Eje Z</div><div class="v">{ev['az']:.2f} g</div></div>
                </div>
                <div class="ficha-foot">Fecha y hora: {ev['timestamp']:%d/%m/%Y %H:%M:%S}<br>GPS: {gps}</div>
                """)
            else:
                st.info("No hay eventos para consultar.")

    # ---- Detalle opcional ----
    with st.expander("Estadística por señal y distribución de registros"):
        e1, e2 = st.columns([1.2, 1])
        with e1:
            filas = []
            for nombre, columna in [("Eje X", "ax"), ("Eje Y", "ay"), ("Eje Z", "az"), ("Resultante", "aceleracion")]:
                serie = datos[columna]
                filas.append({
                    "Señal": nombre, "Prom. (g)": f"{serie.mean():.2f}", "Máx. (g)": f"{serie.max():.2f}",
                    "Mín. (g)": f"{serie.min():.2f}", "Desv.": f"{serie.std():.2f}"
                })
            html(tabla_html(pd.DataFrame(filas), columnas_mono=("Prom. (g)", "Máx. (g)", "Mín. (g)", "Desv.")))
        with e2:
            conteo = datos["intensidad"].value_counts().reindex(["Baja", "Media", "Alta"], fill_value=0)
            fig_dist = go.Figure()
            for nivel in ["Baja", "Media", "Alta"]:
                fig_dist.add_trace(go.Bar(
                    y=[""], x=[int(conteo[nivel])], name=nivel, orientation="h",
                    marker_color=COLORES[nivel], hovertemplate="%{x} registros<extra>" + nivel + "</extra>"
                ))
            fig_dist.update_layout(
                barmode="stack", height=70, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(visible=False), yaxis=dict(visible=False)
            )
            st.plotly_chart(fig_dist, use_container_width=True, config={"displayModeBar": False})
            html("".join(
                f'<div class="leg-row"><span><span class="dot" style="background:{COLORES[n]}"></span>{n}</span>'
                f'<span class="leg-val">{int(conteo[n])} · {conteo[n] / len(datos) * 100:.1f}%</span></div>'
                for n in ["Baja", "Media", "Alta"]
            ))


# =========================================================
# 11. GEOLOCALIZACIÓN
# =========================================================

elif pagina == "Geolocalización":

    ubicaciones = datos.dropna(subset=["latitud", "longitud"]).copy()

    if len(ubicaciones) > 0:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                titulo_panel("Mapa del recorrido", "usa la rueda del mouse para acercar")
            with c2:
                estilo_mapa = st.selectbox("Estilo de mapa", ["Satélite", "Oscuro"],
                                           label_visibility="collapsed", key="estilo_mapa_geo")
            st.plotly_chart(crear_mapa(ubicaciones, altura=600, estilo=estilo_mapa),
                            use_container_width=True,
                            config={"displayModeBar": False, "scrollZoom": True})

        with st.container(border=True):
            titulo_panel("Registros geolocalizados")
            tabla_mapa = ubicaciones[["timestamp", "latitud", "longitud", "intensidad", "aceleracion"]].copy()
            tabla_mapa["aceleracion"] = tabla_mapa["aceleracion"].round(2)
            st.dataframe(tabla_mapa.sort_values("timestamp", ascending=False),
                         use_container_width=True, hide_index=True, height=300)
    else:
        st.warning(
            "No hay coordenadas disponibles para mostrar en el mapa. "
            "El archivo debe incluir las columnas 'latitud' y 'longitud'."
        )

    st.info(
        "Las coordenadas de demostración son ficticias. En la versión conectada al GPS "
        "se utilizarán las posiciones reales registradas por el dispositivo."
    )


# =========================================================
# 12. HISTORIAL DE EVENTOS
# =========================================================

elif pagina == "Historial de eventos":

    with st.container(border=True):
        titulo_panel("Registros")
        filtro = st.selectbox("Filtrar por intensidad", ["Todas", "Baja", "Media", "Alta"])

        historial = datos.copy() if filtro == "Todas" else datos[datos["intensidad"] == filtro].copy()
        historial = historial.sort_values("timestamp", ascending=False)

        columnas_historial = ["timestamp", "intensidad", "aceleracion", "ax", "ay", "az", "latitud", "longitud"]
        st.dataframe(historial[columnas_historial].round(3), use_container_width=True,
                     hide_index=True, height=480)

        c1, c2 = st.columns([3, 1])
        with c1:
            st.caption(f"Registros mostrados: {len(historial)}")
        with c2:
            st.download_button(
                label="Descargar historial CSV",
                data=historial[columnas_historial].to_csv(index=False).encode("utf-8"),
                file_name="historial_mimo.csv",
                mime="text/csv"
            )


# =========================================================
# 13. DATOS Y CONFIGURACIÓN
# =========================================================

elif pagina == "Datos y configuración":

    k = st.columns(4)
    tarjeta_kpi(k[0], "bars", "Total de mediciones", f"{len(datos)}", AZUL)
    tarjeta_kpi(k[1], "alert", "Eventos media o alta", f"{len(eventos)}", COLORES["Media"])
    tarjeta_kpi(k[2], "activity", "Ejes registrados", "3", CIAN)
    tarjeta_kpi(k[3], "shield", "Fuente de información",
                "Demostración" if st.session_state.modo_demo else "Archivo CSV", MORADO)

    col_comp, col_csv = st.columns(2)

    with col_comp:
        with st.container(border=True):
            titulo_panel("Componentes considerados")
            componentes = pd.DataFrame({
                "Componente": ["Raspberry Pi Pico", "Sensor MPU6050", "Módulo GPS NEO-6M",
                               "Módulo microSD", "Batería"],
                "Función": ["Procesamiento y control", "Medición de aceleración",
                            "Registro de coordenadas", "Almacenamiento de datos",
                            "Alimentación del sistema"]
            })
            html(tabla_html(componentes))

    with col_csv:
        with st.container(border=True):
            titulo_panel("Formato esperado del archivo CSV")
            ejemplo = pd.DataFrame({
                "timestamp": ["2026-11-23 09:15:00", "2026-11-23 09:15:01"],
                "ax": [0.12, 0.35], "ay": [0.08, 0.14], "az": [1.02, 1.18],
                "latitud": [-33.45, -33.451], "longitud": [-70.66, -70.661]
            })
            html(tabla_html(ejemplo, columnas_mono=tuple(ejemplo.columns)))
            st.caption(
                "Obligatorias: timestamp, ax, ay y az. Las columnas latitud y longitud son opcionales: "
                "sin ellas se muestran las mediciones, pero no la ubicación."
            )


# =========================================================
# 14. PIE DE PÁGINA
# =========================================================

html("""
<div style="text-align:center;color:#6F86A4;padding:.6rem 0 .2rem 0;font-size:.76rem;">
MIMO · Monitor Integrado de Movimiento Operacional · Prototipo académico
</div>
""")