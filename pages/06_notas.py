import streamlit as st
from src.components import mostrar_tabla_interactiva, mostrar_reporte_alertas, obtener_aulas_filtradas

from src.dashboard import (crear_notas_por_aula)


ACTIVIDADES_GK = [
    "C1 Class Activity 80%",
    "C1 Class Performance 20%",
    "C2 Class Activity 30%",
    "C2 Oral Evaluation 30%",
    "C2 Final Exam 30%",
    "C2 Class Performance 10%",
    "C3 Class Activity 30%",
    "C3 Oral Evaluation 30%",
    "C3 Final Exam 30%",
    "C3 Class Performance 10%",
    "C4 Class Activity 30%",
    "C4 Oral Evaluation 30%",
    "C4 Final Exam 30%",
    "C4 Class Performance 10%"
]

ACTIVIDADES_AS = [
    "C1 Oral Activity 40%",
    "C1 Final Oral Activity 50%",
    "C1 Class Performance 10%",
    "C2 Oral Activity1 30%",
    "C2 Oral Activity2 30%",
    "C2 Final Project 30%",
    "C2 Class Performance 10%",
    "C3 Oral Activity1 30%",
    "C3 Oral Activity2 30%",
    "C3 Final Project 30%",
    "C3 Class Performance 10%",
    "C4 Oral Activity 40%",
    "C4 Final Oral Activity 50%",
    "C4 Class Performance 10%"
]

st.title("Seguimiento de Notas")

if "datos" not in st.session_state:

    st.warning(
        "Primero debes cargar los archivos desde la página principal."
    )

else:

    #carga de los datos ===========================================================
    
    datos = st.session_state["datos"]
    df = datos["df"]
    df_gk = datos["df_gk"]
    df_as = datos["df_as"]

    tabla_gk = crear_notas_por_aula(
        df_gk,
        ACTIVIDADES_GK
    )

    tabla_as = crear_notas_por_aula(
        df_as,
        ACTIVIDADES_AS
    )
    
    #estudiantes con nota por aula GK ==================================================
    
    mostrar_tabla_interactiva(
        tabla_gk,
        mostrar_total=True,
        #contar_ceros=True,
        titulo="Seguimiento notas GK",
        sin_total=[
                "Aula",
                "IED",
                "Grupo",
                "Grado",
                "Nombre Tutor"
            ],
        contar_ceros=True,
        grupos_columnas=[
            {
                "nombre": "SEGUIMIENTO",
                "headerClass": "grupo-grupos",
                "columnas": [
                    "Aula",
                    "IED",
                    "Grupo",
                    "Grado",
                    "Nombre Tutor"
                ]
            },
            {
                "nombre": "PRIMER PERIODO",
                "headerClass": "periodo-1-header",
                "cellClass": "periodo-1-cell",
                "columnas": [
                    "C1 Class Activity 80%",
                    "C1 Class Performance 20%"
                ]
            },
            {
                "nombre": "SEGUNDO PERIODO",
                "headerClass": "periodo-2-header",
                "cellClass": "periodo-2-cell",
                "columnas": [
                    "C2 Class Activity 30%",
                    "C2 Oral Evaluation 30%",
                    "C2 Final Exam 30%",
                    "C2 Class Performance 10%"
                ]
            },
            {
                "nombre": "TERCER PERIODO",
                "headerClass": "periodo-3-header",
                "cellClass": "periodo-3-cell",
                "columnas": [
                    "C3 Class Activity 30%",
                    "C3 Oral Evaluation 30%",
                    "C3 Final Exam 30%",
                    "C3 Class Performance 10%"
                ]
            },
            {
                "nombre": "CUARTO PERIODO",
                "headerClass": "periodo-4-header",
                "cellClass": "periodo-4-cell",
                "columnas": [
                    "C4 Class Activity 30%",
                    "C4 Oral Evaluation 30%",
                    "C4 Final Exam 30%",
                    "C4 Class Performance 10%"
                ]
            }
        ],
        altura_maxima=700
    )
    
    #AS
    
    mostrar_tabla_interactiva(
        tabla_as,
        mostrar_total=True,
        #contar_ceros=True,
        titulo="Seguimiento notas AS",
        sin_total=[
                "Aula",
                "IED",
                "Grupo",
                "Grado",
                "Nombre Tutor"
            ],
        contar_ceros=True,
        grupos_columnas=[
            {
                "nombre": "SEGUIMIENTO",
                "headerClass": "grupo-grupos",
                "columnas": [
                    "Aula",
                    "IED",
                    "Grupo",
                    "Grado",
                    "Nombre Tutor"
                ]
            },
            {
                "nombre": "PRIMER PERIODO",
                "headerClass": "periodo-1-header",
                "cellClass": "periodo-1-cell",
                "columnas": [
                    "C1 Oral Activity 40%",
                    "C1 Final Oral Activity 50%",
                    "C1 Class Performance 10%"
                ]
            },
            {
                "nombre": "SEGUNDO PERIODO",
                "headerClass": "periodo-2-header",
                "cellClass": "periodo-2-cell",
                "columnas": [
                    "C2 Oral Activity1 30%",
                    "C2 Oral Activity2 30%",
                    "C2 Final Project 30%",
                    "C2 Class Performance 10%"
                ]
            },
            {
                "nombre": "TERCER PERIODO",
                "headerClass": "periodo-3-header",
                "cellClass": "periodo-3-cell",
                "columnas": [
                    "C3 Oral Activity1 30%",
                    "C3 Oral Activity2 30%",
                    "C3 Final Project 30%",
                    "C3 Class Performance 10%"
                ]
            },
            {
                "nombre": "CUARTO PERIODO",
                "headerClass": "periodo-4-header",
                "cellClass": "periodo-4-cell",
                "columnas": [
                    "C4 Oral Activity 40%",
                    "C4 Final Oral Activity 50%",
                    "C4 Class Performance 10%"
                ]
            }
        ],
        altura_maxima=700
    )