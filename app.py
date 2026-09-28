import streamlit as st

from src.data import preparar_datos
from src.metabase import MetabaseError
from src.dashboard import crear_tabla_aprovechamiento

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Dashboard de seguimiento GKAS")
st.markdown("Consulta los datos directamente desde Metabase.")

if st.button("Cargar / actualizar datos desde Metabase", type="primary"):
    with st.spinner("Conectando con Metabase y descargando los resultados..."):
        try:
            datos = preparar_datos()
            st.session_state["datos"] = datos
            st.success(
                f"Datos actualizados. Semana K2K consultada: {datos.get('semana_consultada', 'N/D')}"
            )
        except MetabaseError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Ocurrió un error al preparar los datos: {exc}")

if "datos" in st.session_state:
    datos = st.session_state["datos"]

    if datos.get("aviso_07"):
        st.warning(f"La consulta complementaria 07 no se cargó: {datos['aviso_07']}")

    nombres = {
        "df": "01 - Aula a Aula",
        "df_gk": "03 - Notas GK",
        "df_as": "04 - Notas AS",
        "df_ret": "05 - Retirados",
        "df_k2k": "06 - Niño a Niño / K2K",
        "df_k2k_complementario": "07 - Complementario K2K",
    }

    st.subheader("Archivos identificados")
    for nombre, df_temp in datos.items():
        if nombre in nombres and df_temp is not None:
            st.write(
                f"**{nombres[nombre]}** — {df_temp.shape[0]:,} filas × "
                f"{df_temp.shape[1]:,} columnas"
            )

    st.subheader("DataFrames transformados")
    for clave in ("df", "df_gk", "df_as", "df_ret", "df_k2k"):
        st.write(nombres[clave])
        st.dataframe(datos[clave], use_container_width=True)

    st.session_state["tabla_aprovechamiento"] = crear_tabla_aprovechamiento(datos["df"])
