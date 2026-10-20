import streamlit as st

from src.components import mostrar_tabla_interactiva
from src.seguimiento import cargar_seguimiento, recargar_seguimiento

st.title("Seguimiento de avance")
st.caption("Avance por periodo y comentarios de cancelación, leídos del Google Sheet (pestañas GK Grado 4 y 5, AS Grado 9 y 10).")

if st.button("Volver a leer el Google Sheet"):
    recargar_seguimiento()
    st.session_state["_seguimiento_recargado"] = True
    st.rerun()

try:
    with st.spinner("Leyendo el Google Sheet…"):
        tabla, resumen = cargar_seguimiento()
    if st.session_state.pop("_seguimiento_recargado", False):
        st.toast("Datos actualizados desde el Google Sheet", icon="✅")
except Exception as exc:
    st.error(f"No se pudo leer el Google Sheet: {exc}")
    st.stop()

with st.expander("Verificar lectura", expanded=False):
    st.dataframe(resumen, use_container_width=True, hide_index=True)

st.markdown(
    """
    <style>
    [class*="st-key-seg_p"] [data-testid="stCheckbox"] label { gap: 0.6rem; }
    [class*="st-key-seg_p"] [data-testid="stCheckbox"] label > div:first-of-type {
        width: 1.7rem; height: 1.7rem;
    }
    [class*="st-key-seg_p"] [data-testid="stCheckbox"] label > div:first-of-type svg {
        width: 1.1rem; height: 1.1rem;
    }
    [class*="st-key-seg_p"] [data-testid="stCheckbox"] label p {
        font-size: 1.25rem; font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.write("Periodos a mostrar")
casillas = st.columns(4)
periodos = [
    p for p, casilla in zip([1, 2, 3, 4], casillas)
    if casilla.checkbox(f"P{p}", value=True, key=f"seg_p{p}")
]

base = ["Grado", "Aula", "Tutor", "IED", "Grupo"]
por_periodo = [c for p in periodos for c in (f"Comentarios P{p}", f"Avance P{p}")]
# Se respeta el orden original de la tabla
visibles = [c for c in tabla.columns if c in base or c in por_periodo]
tabla = tabla[visibles]

NOMBRES_PERIODO = {1: "PRIMER PERIODO", 2: "SEGUNDO PERIODO", 3: "TERCER PERIODO", 4: "CUARTO PERIODO"}
grupos = [{"nombre": "SEGUIMIENTO", "headerClass": "grupo-grupos", "columnas": base}]
for p in periodos:
    grupos.append({
        "nombre": NOMBRES_PERIODO[p],
        "headerClass": f"periodo-{p}-header",
        "columnas": [f"Comentarios P{p}", f"Avance P{p}"],
    })

if tabla.empty:
    st.info("No se encontraron filas en el Google Sheet.")
else:
    mostrar_tabla_interactiva(
        tabla,
        mostrar_total=False,
        altura_maxima=600,
        columnas_porcentaje=[f"Avance P{p}" for p in periodos],
        grupos_columnas=grupos,
        tamano_fuente=11,
    )