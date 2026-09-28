import streamlit as st
import pandas as pd

from src.components import mostrar_tabla_interactiva
from src.dashboard import (crear_tabla_tipificacion, crear_tabla_razones_agrupadas, crear_horas_prioritarias, crear_grafica_razones_agrupadas, crear_grafica_motivos_desagregados)


st.title("Detalle de motivos")

if "datos" not in st.session_state:

    st.warning(
        "Primero debes cargar los archivos desde la página principal."
    )

else:

    #carga de los datos ===========================================================

    df = st.session_state["datos"]["df"]
    tabla_tipificacion = crear_tabla_tipificacion(df)

    #horas por tipificacion ==================================================

    respuesta_desagregada = mostrar_tabla_interactiva(
        tabla_tipificacion,
        titulo="Horas por motivos desagregados",
        sin_total=["Tipificación", "Motivo de inasistencia"],
        mostrar_total=True
    )

    # Obtener el estado de las columnas
    estado_columnas = respuesta_desagregada.columns_state

    if estado_columnas is None:

        # Si todavía no existe estado,
        # todas las columnas están visibles
        columnas_visibles_desagregadas = [
            "4", "5", "9", "10"
        ]

    else:

        columnas_visibles_desagregadas = [
            str(col["colId"])
            for col in estado_columnas
            if not col.get("hide", False)
        ]

    # Crear gráfica según columnas visibles
    fig_desagregada = crear_grafica_motivos_desagregados(
        pd.DataFrame(respuesta_desagregada.data),
        columnas_visibles=columnas_visibles_desagregadas
    )

    if fig_desagregada is not None:

        st.plotly_chart(
            fig_desagregada,
            use_container_width=True
        )

    #razones agrupadas  ==================================================

    tabla_final = crear_tabla_razones_agrupadas(df)

    respuesta_razones = mostrar_tabla_interactiva(
        tabla_final,
        titulo="Horas por razones agrupadas",
        mostrar_total=True
    )

    # Obtener el estado de las columnas
    estado_columnas = respuesta_razones.columns_state

    if estado_columnas is None:
        # Si todavía no existe estado, todas las columnas están visibles
        columnas_visibles = ["4", "5", "9", "10"]
    else:
        columnas_visibles = [
            str(col["colId"])
            for col in estado_columnas
            if not col.get("hide", False)
        ]
        
    # Crear gráfica usando únicamente los grados visibles
    fig_razones = crear_grafica_razones_agrupadas(
        pd.DataFrame(respuesta_razones.data),
        columnas_visibles=columnas_visibles
    )

    if fig_razones is not None:
        st.plotly_chart(
            fig_razones,
            use_container_width=True
        )

    #horas prioritarias ==============================================
    
    tabla_prioritarias = crear_horas_prioritarias(df)
    
    mostrar_tabla_interactiva(
        tabla_prioritarias,
        titulo="Horas de reposición prioritarias",
        mostrar_total=True
    )