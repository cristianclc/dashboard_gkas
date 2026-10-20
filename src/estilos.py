"""Estilos visuales del dashboard (barra lateral fija, menú y encabezados)."""
import base64
import io
from pathlib import Path

import streamlit as st

CARPETA_IMG = Path(__file__).resolve().parents[1] / "img"
NOMBRES_LOGOS = ["01", "02", "03"]
EXTENSIONES = [".png", ".jpg", ".jpeg", ".webp"]

ANCHO_BARRA = 270  # px

_CSS = f"""
<style>
:root {{ color-scheme: light; }}

/* ---------- Barra lateral: ancho fijo (se puede ocultar, no redimensionar) ---------- */
section[data-testid="stSidebar"][aria-expanded="true"] {{
    width: {ANCHO_BARRA}px !important;
    min-width: {ANCHO_BARRA}px !important;
    max-width: {ANCHO_BARRA}px !important;
}}
section[data-testid="stSidebar"][aria-expanded="true"] > div:first-child {{
    width: {ANCHO_BARRA}px !important;
}}
[data-testid="stSidebarResizeHandle"],
[data-testid="stSidebar"] [class*="resize"] {{
    display: none !important;
}}

/* ---------- Menú de páginas ---------- */
[data-testid="stSidebarNav"] {{ padding-top: .5rem; }}

[data-testid="stSidebarNavSeparator"],
[data-testid="stNavSectionHeader"],
[data-testid="stSidebarNav"] span[class*="Header"] {{
    color: #8FC1DB !important;
    font-size: .9rem !important;
    letter-spacing: .12em;
    text-transform: uppercase;
    font-weight: 700;
}}

[data-testid="stSidebarNavLink"] {{
    border-radius: 12px;
    margin: 4px 8px;
    padding: 1.2rem 1rem;
    gap: .7rem;
    color: #EAF4F8 !important;
    font-weight: 500;
    transition: background .15s ease, transform .15s ease;
}}
[data-testid="stSidebarNavLink"]:hover {{
    background: rgba(61, 220, 151, .18);
    transform: translateX(3px);
}}
[data-testid="stSidebarNavLink"][aria-current="page"] {{
    background: linear-gradient(90deg, #1F9D74 0%, #1B7FB3 100%);
    color: #FFFFFF !important;
    font-weight: 700;
    box-shadow: 0 3px 10px rgba(0, 0, 0, .25);
}}
[data-testid="stSidebarNavLink"] span[data-testid="stIconMaterial"] {{
    font-size: 1.6rem;
}}
[data-testid="stSidebarNavLink"] > div, [data-testid="stSidebarNavLink"] > span {{ gap: .7rem !important; }}
/* Solo el texto del menú de la izquierda, más grande */
[data-testid="stSidebarNavLink"] span:not([data-testid="stIconMaterial"]),
[data-testid="stSidebarNavLink"] p {{
    font-size: 1.3rem !important;
    line-height: 1.25;
}}

/* ---------- Contenido ---------- */
h1 {{
    color: #0B3C5D;
    font-weight: 800;
    border-bottom: 4px solid;
    border-image: linear-gradient(90deg, #1F9D74, #1B7FB3) 1;
    padding-bottom: .35rem;
}}
h2, h3 {{ color: #124C73; }}

[data-testid="stMetric"] {{
    background: #FFFFFF;
    border: 1px solid #D5E5EE;
    border-left: 5px solid #1F9D74;
    border-radius: 12px;
    padding: .8rem 1rem;
    box-shadow: 0 2px 8px rgba(11, 60, 93, .08);
}}

.stButton > button {{
    border-radius: 10px;
    border: 1px solid #1F9D74;
    font-weight: 600;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(90deg, #1F9D74, #1B7FB3);
    border: none;
    color: #FFFFFF;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    color: #1F9D74 !important;
    font-weight: 700;
}}
</style>
"""


def _imagen_logos():
    """Apila img/01, 02 y 03 (una debajo de otra) en una sola imagen PNG, como data-URI."""
    from PIL import Image

    imagenes = []
    for nombre in NOMBRES_LOGOS:
        for ext in EXTENSIONES:
            ruta = CARPETA_IMG / f"{nombre}{ext}"
            if ruta.exists():
                imagenes.append(Image.open(ruta).convert("RGBA"))
                break
    if not imagenes:
        return None

    ancho, margen, separacion = 600, 40, 36
    piezas = []
    for im in imagenes:
        # Cada logo ocupa a lo sumo 80% del ancho y 150 px de alto
        escala = min((ancho * 0.8) / im.width, 150 / im.height)
        piezas.append(im.resize((max(1, int(im.width * escala)), max(1, int(im.height * escala)))))

    alto = margen * 2 + sum(p.height for p in piezas) + separacion * (len(piezas) - 1)
    lienzo = Image.new("RGBA", (ancho, alto), (255, 255, 255, 255))
    y = margen
    for p in piezas:
        lienzo.alpha_composite(p, ((ancho - p.width) // 2, y))
        y += p.height + separacion

    buffer = io.BytesIO()
    lienzo.convert("RGB").save(buffer, "PNG", optimize=True)
    codigo = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{codigo}", ancho, alto


@st.cache_resource(show_spinner=False)
def _css_logos():
    resultado = _imagen_logos()
    if resultado is None:
        return ""
    uri, ancho, alto = resultado
    return f"""
<style>
[data-testid="stSidebarNav"]::before {{
    content: "";
    display: block;
    margin: .6rem 14px 1rem 14px;
    border-radius: 14px;
    background: #FFFFFF url("{uri}") center / contain no-repeat;
    aspect-ratio: {ancho} / {alto};
    box-shadow: 0 3px 10px rgba(0, 0, 0, .25);
}}
</style>
"""


def _css_barra_titulo(titulo):
    texto = str(titulo).replace("\\", "").replace('"', "").replace("\n", " ")
    return f"""
<style>
header[data-testid="stHeader"] {{
    background: #FFFFFF !important;
    border-bottom: 1px solid #D5E5EE;
    box-shadow: 0 2px 8px rgba(11, 60, 93, .10);
    height: 4rem;
    display: flex;
    align-items: center;
}}
header[data-testid="stHeader"]::before {{
    content: "{texto}";
    color: #0B3C5D;
    font-size: 1.8rem;
    font-weight: 700;
    padding-left: 1.2rem;
    white-space: nowrap;
}}
</style>
"""


def aplicar_estilos(titulo_pagina=None):
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(_css_logos(), unsafe_allow_html=True)
    if titulo_pagina:
        st.markdown(_css_barra_titulo(titulo_pagina), unsafe_allow_html=True)