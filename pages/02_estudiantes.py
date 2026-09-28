import streamlit as st
import pandas as pd

from src.dashboard import (crear_tabla_estudiantes_semana, crear_retirados_por_grado, crear_rangos_asistencia_k2k)
from src.components import mostrar_tabla_interactiva

st.title("Detalle estudiantes")

if "datos" not in st.session_state:

    st.warning(
        "Primero debes cargar los archivos desde la página principal."
    )

else:

    #carga de los datos ===========================================================

    datos = st.session_state["datos"]

    df = datos["df"]
    df_k2k = datos["df_k2k"]
    df_ret = datos["df_ret"]

    
    tabla_estudiantes = crear_tabla_estudiantes_semana(
        df,
        df_k2k
    )

    retirados = crear_retirados_por_grado(
        df_ret
    )

    tabla_rangos = crear_rangos_asistencia_k2k(
        df_k2k
    )

    #estudiantes por semana ==================================================
    
    mostrar_tabla_interactiva(
            tabla_estudiantes,
            titulo="Estudiantes por semana",
            mostrar_total=True
    )

    #RANGOS ASISTENCIA ESTUDIANTES  ==================================================
    
    mostrar_tabla_interactiva(
            tabla_rangos,
            titulo="Rangos asistencia de estudiantes",
            mostrar_total=True
    )

    #retirados  ==================================================

    mostrar_tabla_interactiva(
            retirados,
            titulo="Estudiantes retirados",
            mostrar_total=True
    )