import streamlit as st

from src.data import preparar_datos
from src.metabase import MetabaseError
from src.dashboard import crear_tabla_aprovechamiento
from src.components import mostrar_tabla_interactiva

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

    claves_pestanas = [
        clave
        for clave in nombres
        if datos.get(clave) is not None and not datos[clave].empty
    ]

    pestanas = st.tabs([nombres[clave] for clave in claves_pestanas])

    for clave, pestana in zip(claves_pestanas, pestanas):
        with pestana:
            df_pestana = datos[clave].copy()

            # Las columnas categóricas (ej. Desempeño) dejan la tabla en blanco
            for columna in df_pestana.select_dtypes("category").columns:
                df_pestana[columna] = df_pestana[columna].astype("object")

            st.caption(
                f"{df_pestana.shape[0]:,} filas × "
                f"{df_pestana.shape[1]:,} columnas"
            )

            mostrar_tabla_interactiva(
                df_pestana,
                mostrar_total=False,
                altura_maxima=800
            )

    st.session_state["tabla_aprovechamiento"] = crear_tabla_aprovechamiento(datos["df"])