import streamlit as st
import pandas as pd
from pathlib import Path

from src.dashboard import (crear_tabla_civicos, crear_tabla_resultado, crear_tabla_civicos, crear_tabla_reposiciones, crear_asistencias_pendientes_gk, crear_asistencias_pendientes_as)
from src.components import mostrar_tabla_interactiva

from src.db import cargar_reposiciones

st.title("Detalle resumen - PPT")

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

    
    tabla_civicos = crear_tabla_civicos(
        df
    )

    resumen_1 = crear_tabla_resultado(
        df, df_k2k, df_ret
    )
    
    #MODIFICAR CUANDO ESTE BASE DE DATOS DE REPOSICIONES

    df_reposiciones = cargar_reposiciones()
    
    #MODIFICAR CUANDO ESTE BASE DE DATOS DE REPOSICIONES

    df_reposiciones["grado"] = (
        df_reposiciones["grupo"]
        .astype(str)
        .str[0]
        .replace({
            "1": 10,
            "4": 4,
            "5": 5,
            "9": 9
        })
    )

    resumen_reposiciones = crear_tabla_reposiciones(
        df,
        df_reposiciones
    )
    
    pendientes_gk = crear_asistencias_pendientes_gk(
        df
    )
    
    pendientes_as = crear_asistencias_pendientes_as(
        df
    )

    #resumen 1  ==================================================
    
    mostrar_tabla_interactiva(
            resumen_1,
            titulo="Resumen proyección de horas",
            mostrar_total=True,
            grupos_columnas=[
                {
                    "nombre": "GRUPOS",
                    "headerClass": "grupo-grupos",
                    "columnas": [
                        "Grado",
                        "Aulas únicas"
                    ]
                },

                {
                    "nombre": "PROYECCIÓN DE HORAS",
                    "headerClass": "grupo-proyeccion",
                    "columnas": [
                        "N de horas programadas",
                        "N de horas efectivas + Reposiciones",
                        "% de Horas efectivas"
                    ]
                },

                {
                    "nombre": "PROYECCIÓN DE HORAS SIN CONTAR SEDES DE VOTACIÓN, FESTIVOS, PAE",
                    "headerClass": "grupo-proyeccion-sin",
                    "columnas": [
                        "N de horas programadas (sin sedes de votación, festivos, PAE)",
                        "N de horas efectivas + Reposiciones (sin sedes de votación, festivos, PAE)",
                        "% de Horas efectivas (sin sedes de votación, festivos, PAE)"
                    ]
                },

                {
                    "nombre": "REPOSICIONES",
                    "headerClass": "grupo-reposiciones",
                    "columnas": [
                        "N de Horas de reposición ejecutadas"
                    ]
                },

                {
                    "nombre": "ESTUDIANTES",
                    "headerClass": "grupo-estudiantes",
                    "columnas": [
                        "Promedio de estudiantes asistentes por semana",
                        "Retirados"
                    ]
                }
            ]
    )

    #resumen reposiciones ==================================================

    mostrar_tabla_interactiva(
            resumen_reposiciones,
            titulo="Resumen reposiciones",
            mostrar_total=True,
            grupos_columnas=[
                {
                    "nombre": "GRUPOS",
                    "headerClass": "grupo-grupos",
                    "columnas": [
                        "Grado"
                    ]
                },
                {
                    "nombre": "ACUMULADO TOTAL AÑO",
                    "headerClass": "grupo-proyeccion",
                    "columnas": [
                        "Acumulado total horas canceladas",
                        "Acumulado total horas priorizadas para reposición",
                        "Acumulado total horas de reposición ejecutadas",
                        "% cumplimiento total de reposición vs horas priorizadas"
                    ]
                },
                {
                    "nombre": "PLAN DE REPOSICIÓN SEGUNDO SEMESTRE",
                    "headerClass": "grupo-proyeccion-sin",
                    "columnas": [
                        "Total horas reposición programadas II semestre",
                        "Total horas reposición canceladas II semestre",
                        "Total horas reposición ejecutadas II semestre",
                        "% cumplimiento II semestre total de reposición vs horas priorizadas",
                        "Plan de reposición acordado II semestre"
                    ]
                }
            ]
    )

    #motivos excluidos de resumen ==================================================

    mostrar_tabla_interactiva(
            tabla_civicos,
            titulo="SEDES DE VOTACIÓN / DÍAS CÍVICOS + FESTIVOS + PAE / INICIO TARDE",
            mostrar_total=True
    )
    
    #pendientes
    
    col_gk, col_as = st.columns(2)

    with col_gk:

        mostrar_tabla_interactiva(
            pendientes_gk,
            mostrar_total=True,
            titulo="Asistencias pendientes GK",
            grupos_columnas=[
                            {
                                "nombre": "GLOCAL KIDS",
                                "headerClass": "glocal-kids",
                                "columnas": [
                                    "Nombre Tutor Del Aula",
                                    "Total asistencias pendientes"
                                ]
                            }
            ]
            
        )

    with col_as:

        mostrar_tabla_interactiva(
            pendientes_as,
            mostrar_total=True,
            titulo="Asistencias pendientes AS",
            grupos_columnas=[
                                        {
                                            "nombre": "AFTER SCHOOL",
                                            "headerClass": "after-school",
                                            "columnas": [
                                                "Nombre Tutor Del Aula",
                                                "Total asistencias pendientes"
                                            ]
                                        }
                        ]
        )

