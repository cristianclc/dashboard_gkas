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

if tabla.empty:
    st.info("No se encontraron filas en el Google Sheet.")
else:
    mostrar_tabla_interactiva(
        tabla,
        mostrar_total=False,
        altura_maxima=600,
        columnas_porcentaje=[f"Avance P{i}" for i in range(1, 5)],
    )