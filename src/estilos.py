"""Estilos visuales del dashboard (barra lateral fija, menú y encabezados)."""
import streamlit as st

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
    font-size: .72rem !important;
    letter-spacing: .12em;
    text-transform: uppercase;
    font-weight: 700;
}}

[data-testid="stSidebarNavLink"] {{
    border-radius: 12px;
    margin: 3px 10px;
    padding: .55rem .8rem;
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
    font-size: 1.35rem;
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


def aplicar_estilos():
    st.markdown(_CSS, unsafe_allow_html=True)
