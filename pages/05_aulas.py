import streamlit as st
from src.components import mostrar_tabla_interactiva, mostrar_reporte_alertas, obtener_aulas_filtradas

from src.dashboard import (crear_tabla_aprovechamiento,crear_reposiciones_por_grupo,
    crear_tabla_semanal, crear_rangos_aprovechamiento_academico, crear_rangos_aprovechamiento_estudiantes, crear_reporte_alertas)


st.title("Detalle de Aulas")

if "datos" not in st.session_state:

    st.warning(
        "Primero debes cargar los archivos desde la página principal."
    )

else:

    #carga de los datos ===========================================================
    datos = st.session_state["datos"]
    df = datos["df"]

    
    #aprovechamiento por aula ==================================================
    
    tabla_aprovechamiento = crear_tabla_aprovechamiento(df)

    st.session_state["tabla_aprovechamiento"] = tabla_aprovechamiento

    tabla_filtrada = obtener_aulas_filtradas(
        tabla_aprovechamiento,
        sin_total=[
            "Aula",
            "IED",
            "Grupo",
            "Grado"
        ],
        promedios=[
            "Número promedio de estudiantes asistentes"
        ],
        porcentajes={
            "% de aprovechamiento académico": {
                "numerador": [
                    "Horas ejecutadas",
                    "Horas de reposición ejecutadas"
                ],
                "denominador": "Horas programadas"
            },
            "% de aprovechamiento de estudiantes": {
                "numerador": [
                    "Número promedio de estudiantes asistentes"
                ],
                "denominador": "Número de estudiantes del Aula"
            }
        },
        mostrar_total=True,
        altura=900
    )
        
    aulas_filtradas = tabla_filtrada["Aula"].dropna().unique()
    
    df_filtrado = df[
        df["Aula"].isin(aulas_filtradas)
    ].copy()
        
    #resumen proyeccion horas ==================================================
    
    reporte_alertas = crear_reporte_alertas(
        df_filtrado
    )
    
    mostrar_reporte_alertas(
        reporte_alertas,
        titulo="Reporte GK - AS"
    )
    
    #reposiciones  ==================================================

    reposiciones = crear_reposiciones_por_grupo(df)

    mostrar_tabla_interactiva(
            reposiciones,
            titulo="Reposiciones",
            mostrar_total=True
        )

    # HORAS EJECUTADAS POR SEMANA ==================================================

    semanal = crear_tabla_semanal(df)

    mostrar_tabla_interactiva(
        semanal,
        titulo="Horas ejecutadas por semana",
        mostrar_total=True
    )


    # CREACION TABLAS CON RANGOS ====================================================

    tabla_aprovechamiento_aula_poc = crear_rangos_aprovechamiento_academico(
        tabla_aprovechamiento
    )

    tabla_asistencia_prom = crear_rangos_aprovechamiento_estudiantes(
        tabla_aprovechamiento
    )


    # APROVECHAMIENTO ACADÉMICO AULA ===============================================

    mostrar_tabla_interactiva(
        tabla_aprovechamiento_aula_poc,
        titulo="Horas efectivas vs programación académica",
        mostrar_total=True,
        sin_total=[
                    "Rango aprovechamiento"
                ]
    )


    # ASISTENCIA ESTUDIANTES AULA ===================================================

    mostrar_tabla_interactiva(
        tabla_asistencia_prom,
        titulo="% de asistencia promedio de los estudiantes",
        mostrar_total=True
        
    )