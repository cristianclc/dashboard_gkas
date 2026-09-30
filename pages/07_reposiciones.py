import streamlit as st
import pandas as pd
from pathlib import Path


from src.repo_components import (
    calcular_indicadores,
    filtrar_reposiciones,
    crear_vista_sesiones,
    crear_tabla_cancelaciones,
    generar_reporte_migracion
)

from src.db import cargar_horarios
from src.sheets import cargar_reposiciones, recargar_reposiciones

from src.components import mostrar_tabla_interactiva, mostrar_tabla_reposiciones

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.title("Reporte de reposiciones")

st.caption(
    "Consulta y seguimiento de las sesiones de reposición."
)

# ============================================================
# CARGA E INICIALIZACIÓN DE DATOS
# ============================================================

if st.button("Recargar datos desde Google Sheets"):
    recargar_reposiciones()
    st.rerun()

df_reposiciones = cargar_reposiciones()
df_horarios = cargar_horarios()



# ============================================================
# VERIFICAR DATOS
# ============================================================

with st.expander("Verificar datos conectados"):

    st.write("Reposiciones:", len(df_reposiciones))

    st.write(
        "Reposiciones sin horario:",
        df_reposiciones["horario"].isna().sum()
    )

    st.write(
        "Reposiciones sin LT:",
        df_reposiciones["lt"].isna().sum()
    )

    st.dataframe(
        df_reposiciones[
            [
                "id_reposicion",
                "aula",
                "ied",
                "grupo",
                "horario",
                "auxiliar",
                "fecha_reposicion",
                "horas",
                "estado",
                "tutor",
                "lt"
            ]
        ],
        use_container_width=True
    )


# ============================================================
# INDICADORES
# ============================================================

indicadores = calcular_indicadores(df_reposiciones)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total programadas II semestre", indicadores["Total programadas II semestre"])

with col2:
    st.metric("Ejecutadas", indicadores["Ejecutadas"])

with col3:
    st.metric("Programadas", indicadores["Programadas"])

with col4:
    st.metric("Canceladas", indicadores["Canceladas"])


st.divider()


# ============================================================
# FILTROS
# ============================================================

st.subheader("Filtros")

col1, col2, col3 = st.columns(3)

fecha_minima = df_reposiciones["fecha_reposicion"].min()
fecha_maxima = df_reposiciones["fecha_reposicion"].max()

with col1:
    fecha_desde = st.date_input(
        "Fecha desde",
        value=fecha_minima.date() if pd.notna(fecha_minima) else None
    )

with col2:
    fecha_hasta = st.date_input(
        "Fecha hasta",
        value=fecha_maxima.date() if pd.notna(fecha_maxima) else None
    )

with col3:
    estados = ["Todos"] + sorted(
        df_reposiciones["estado"].dropna().unique().tolist()
    )

    estado_seleccionado = st.selectbox(
        "Estado",
        estados
    )


col1, col2, col3 = st.columns(3)

with col1:

    df_reposiciones["ied"] = (
        df_reposiciones["ied"]
        .astype("string")
        .str.strip()
    )

    instituciones = sorted(
        df_reposiciones["ied"]
        .dropna()
        .unique()
        .tolist()
    )

    instituciones_filtro = st.multiselect(
        "Institución",
        options=instituciones,
        placeholder="Seleccione una o varias instituciones"
    )

with col2:
    grupos = ["Todos"] + sorted(
        df_reposiciones["grupo"].dropna().unique().tolist()
    )

    grupo_seleccionado = st.selectbox(
        "Grupo",
        grupos
    )

with col3:
    sesiones = ["Todas"] + sorted(
        df_reposiciones["sesion"].dropna().unique().tolist()
    )

    sesion_seleccionada = st.selectbox(
        "Sesión",
        sesiones
    )

# ============================================================
# FILTRAR DATOS
# ============================================================

df_filtrado = filtrar_reposiciones(
    df=df_reposiciones,
    fecha_desde=fecha_desde,
    fecha_hasta=fecha_hasta,
    estado=estado_seleccionado,
    instituciones=instituciones_filtro,
    grupo=grupo_seleccionado,
    sesion=sesion_seleccionada
)

# ============================================================
# VISTA DE REPOSICIONES
# ============================================================

st.subheader("Reposiciones")

tabla_aprovechamiento = st.session_state.get(
    "tabla_aprovechamiento",
    pd.DataFrame()
)

df_vista = crear_vista_sesiones(
    df_filtrado,
    df_reposiciones,
    df_horarios,
    tabla_aprovechamiento
)

# ========================================================
# TABLA 1: GRADOS 4 Y 5
# ========================================================

df_vista_4_5 = df_vista[
    pd.to_numeric(df_vista["Grado"], errors="coerce").isin([4, 5])
].copy()

df_vista_4_5 = df_vista_4_5[
    [
        "Aula",
        "IED",
        "Horario",
        "Grupo",
        "Grado",
        "Horas de reposición segundo semestre"
    ]
    + [
        col for col in df_vista_4_5.columns
        if col not in [
            "Aula", "IED", "Grupo", 
            "Horario", "Horas de reposición segundo semestre", "Grado"
        ]
    ]
]

columnas_sin_total_gk = [
    columna
    for columna in df_vista_4_5.columns
    if columna.startswith("Sesión ")
]


# ========================================================
# TABLA 2: GRADOS 9 Y 10
# ========================================================

df_vista_9_10 = df_vista[
    pd.to_numeric(df_vista["Grado"], errors="coerce").isin([9, 10])
].copy()

df_vista_9_10 = df_vista_9_10[
    [
        "Aula",
        "IED",
        "Horario",
        "Grupo",
        "Grado",
        "Horas de reposición segundo semestre"
    ]
    + [
        col for col in df_vista_9_10.columns
        if col not in [
            "Aula", "IED", "Grupo", 
            "Horario", "Horas de reposición segundo semestre", "Grado"
        ]
    ]
]

columnas_sin_total_as = [
    columna
    for columna in df_vista_9_10.columns
    if columna.startswith("Sesión ")
]


if df_vista.empty:

    st.info(
        "No hay reposiciones que coincidan con los filtros seleccionados."
    )

else:

    # ========================================================
    # INICIALIZAR VARIABLES
    # ========================================================

    evento_4_5 = None
    evento_9_10 = None
    reposicion_seleccionada = None

    # ========================================================
    # TABLA 1: GRADOS 4 Y 5
    # ========================================================

    st.subheader("Reposiciones - Grados GK")

    if df_vista_4_5.empty:

        st.info("No hay reposiciones para los grados 4 y 5.")

    else:

        evento_4_5 = mostrar_tabla_reposiciones(
            df_vista_4_5,
            mostrar_total=True,
            altura_maxima=600,
            sin_total=[
                "Aula",
                "IED",
                "Grupo",
                "Grado",
                "Horario",
                "Auxiliar",
            ] + columnas_sin_total_gk,
            columnas_fijas=["Aula", "IED","Horario","Grupo"]
        )

    # ========================================================
    # TABLA 2: GRADOS 9 Y 10
    # ========================================================

    st.subheader("Reposiciones - Grados AS")

    if df_vista_9_10.empty:

        st.info("No hay reposiciones para los grados 9 y 10.")

    else:

        evento_9_10 = mostrar_tabla_reposiciones(
            df_vista_9_10,
            mostrar_total=True,
            altura_maxima=600,
            sin_total=[
                "Aula",
                "IED",
                "Grupo",
                "Grado",
                "Horario",
                "Auxiliar"
            ] + columnas_sin_total_as,
            columnas_fijas=["Aula", "IED","Horario","Grupo"]
        )

# ============================================================
# TABLA DE REPOSICIONES POR MIGRAR
# ============================================================

reporte_migracion = generar_reporte_migracion(
    df_vista
)

st.subheader("Reposiciones pendientes por migrar")

st.text_area(
    "Reporte para copiar y pegar",
    value=reporte_migracion,
    height=400
)

# ============================================================
# TABLA DE CANCELACIONES
# ============================================================

st.divider()
st.subheader("Reposiciones canceladas")

df_cancelaciones = crear_tabla_cancelaciones(df_filtrado)

if df_cancelaciones.empty:

    st.info(
        "No hay reposiciones canceladas para los filtros seleccionados."
    )

else:


    mostrar_tabla_interactiva(
            df_cancelaciones,
            titulo="Cancelaciones",
            mostrar_total=True,
            altura_maxima=600,
            sin_total=["Grupo",
                    "Fecha",
                    "Motivo"]
    )