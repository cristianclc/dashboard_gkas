import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px


#TABULACION POR AULA =====================================================================

#aprovechamiento de clases
@st.cache_data
def crear_tabla_aprovechamiento(df):
    """
    Crea la tabla de aprovechamiento académico por Aula.
    """
    df = df.copy()

    semana_max = df["Semana Del Proyecto"].max() - 1

    # ============================================================
    # 1. Horas ejecutadas por Aula
    # ============================================================

    horas_ejecutadas = (
        df[
            (df["Aula"].notna()) &
            (df["Semana Del Proyecto"] <= semana_max)
        ]
        .groupby("Aula")["Hora Instruccion Directa Asistio"]
        .sum()
    )

    # ============================================================
    # 2. Horas de reposición ejecutadas por Aula
    # ============================================================

    horas_repo_ejecutadas = (
            df[
                (df["Aula"].notna()) &
                (df["ID Interna Tutor Repo"] > 0)
            ]
            .groupby("Aula")["Total horas"]
            .sum()
        )

    # IED, HORAS PROG, GRUPO

    nombre_institucion_por_aula = (
        df[df["Aula"].notna()]
        .groupby("Aula")["Nombre Institucion"]
        .first()
    )

    grupo_por_aula = (
        df[df["Aula"].notna()]
        .groupby("Aula")["Grupo"]
        .first()
    )

    # ============================================================
    # 3. Horas perdidas por motivo
    # ============================================================

    motivos_perdida = [
        "DÍA FESTIVO",
        "INCAPACIDAD MÉDICA DEL TUTOR",
        "SIN TUTOR ASIGNADO"
    ]

    horas_perdidas = (
        df[
            (df["Aula"].notna()) &
            (df["Motivo de inasistencia"].isin(motivos_perdida))
        ]
        .pivot_table(
            index="Aula",
            columns="Motivo de inasistencia",
            values="Total horas",
            aggfunc="sum",
            fill_value=0
        )
        .reindex(columns=motivos_perdida, fill_value=0)
    )

    # ============================================================
    # 4. Grado asociado a cada Aula
    # ============================================================

    grado_por_aula = (
        df[df["Aula"].notna()]
        .groupby("Aula")["Grado"]
        .first()
    )

    # ============================================================
    # 5. Estudiantes por Aula
    # ============================================================

    df_aulas = df[
        (df["Aula"].notna()) &
        (df["Cantidad Est Asiste"] > 0)
    ]

    estudiantes_promedio = (
        df_aulas
        .groupby("Aula")["Cantidad Est Asiste"]
        .mean()
        .apply(lambda x: np.floor(x + 0.5))
    )

    estudiantes_aula = (
        df_aulas
        .groupby("Aula")["Cantidad Est Aula"]
        .first()
    )

    # ============================================================
    # 6. Horas canceladas por Aula
    # ============================================================

    df_canceladas = df[df["Aula"].notna()].copy()

    df_canceladas["Horas_canceladas"] = (
        df_canceladas["Hora Instruccion Directa No Asistio"].fillna(0)
        +
        np.where(
            df_canceladas["Festivo"] == "SI",
            df_canceladas["Hora Instruccion Directa No Reportada"].fillna(0),
            0
        )
    )

    horas_canceladas = (
        df_canceladas
        .groupby("Aula")["Horas_canceladas"]
        .sum()
    )

    # ============================================================
    # 7. Horas de reposición primer semestre
    # ============================================================

    df_repos_primer_semestre = df[
        (df["Aula"].notna()) &
        (df["ID Interna Tutor Repo"] > 0) &
        (
            pd.to_datetime(
                df["Fecha Reposicion"],
                errors="coerce"
            ) < "2026-07-01"
        )
    ]

    repos_primer_semestre = (
        df_repos_primer_semestre
        .groupby("Aula")["Total horas"]
        .sum()
    )

    # ============================================================
    # Crear DataFrame final
    # ============================================================

    tabla_aprovechamiento = pd.DataFrame({
        "Grado": grado_por_aula,
        "IED": nombre_institucion_por_aula,
        "Grupo": grupo_por_aula,
        "Horas canceladas": horas_canceladas,
        "Horas ejecutadas": horas_ejecutadas,
        "Horas de reposición ejecutadas": horas_repo_ejecutadas,
        "Horas de reposición primer semestre": repos_primer_semestre,
        "Número promedio de estudiantes asistentes": estudiantes_promedio,
        "Número de estudiantes del Aula": estudiantes_aula
    }).fillna(0)

    tabla_aprovechamiento["Horas programadas"] = semana_max * 2

    # Agregar horas perdidas
    tabla_aprovechamiento = tabla_aprovechamiento.join(
        horas_perdidas,
        how="left"
    ).fillna(0)

    # ============================================================
    # 8. Horas de reposición segundo semestre
    # ============================================================

    tabla_aprovechamiento["Horas de reposición segundo semestre"] = (
        tabla_aprovechamiento["Horas de reposición ejecutadas"]
        - tabla_aprovechamiento["Horas de reposición primer semestre"]
    )

    # ============================================================
    # 9. % de aprovechamiento académico
    # ============================================================

    tabla_aprovechamiento["% de aprovechamiento académico"] = (
        (
            tabla_aprovechamiento["Horas ejecutadas"]
            + tabla_aprovechamiento["Horas de reposición ejecutadas"]
        )
        / (semana_max * 2)
        * 100
    ).astype(float).round(2)

    # ============================================================
    # 10. % de aprovechamiento de estudiantes
    # ============================================================

    tabla_aprovechamiento["% de aprovechamiento de estudiantes"] = (
        tabla_aprovechamiento["Número promedio de estudiantes asistentes"]
        / tabla_aprovechamiento["Número de estudiantes del Aula"]
        * 100
    ).replace(
        [float("inf"), -float("inf")],
        0
    ).fillna(0).round(2)

    # ============================================================
    # 11. Dejar Aula como columna
    # ============================================================

    tabla_aprovechamiento = tabla_aprovechamiento.reset_index()

    tabla_aprovechamiento = tabla_aprovechamiento[
        [
            "Aula",
            "IED",
            "Grupo",
            "Grado",
            "Horas programadas",
            "Horas canceladas",
            "Horas ejecutadas",
            "Horas de reposición ejecutadas",
            "Horas de reposición primer semestre",
            "Horas de reposición segundo semestre",
            "Número promedio de estudiantes asistentes",
            "Número de estudiantes del Aula",
            "% de aprovechamiento académico",
            "% de aprovechamiento de estudiantes"
        ]
    ]

    return tabla_aprovechamiento

#reposiciones por grado
def crear_reposiciones_por_grupo(df):
    """
    Crea el total de horas de reposición por grado.
    """

    semana_max = df["Semana Del Proyecto"].max() - 1

    reposiciones_por_grupo = (
        df[
            (df["Fecha Reposicion"].notna()) &
            (df["Semana Del Proyecto"] <= semana_max)
        ]
        .groupby("Grado")["Total horas"]
        .sum()
        .reindex([4, 5, 9, 10], fill_value=0)
        .reset_index(name="Horas de reposicion")
    )

    fila_total = pd.DataFrame({
        "Grado": ["TOTAL"],
        "Horas de reposicion": [
            reposiciones_por_grupo["Horas de reposicion"].sum()
        ]
    })

    reposiciones_por_grupo = pd.concat(
        [reposiciones_por_grupo, fila_total],
        ignore_index=True
    )

    return reposiciones_por_grupo

#horas efectivas de clases
def crear_tabla_semanal(df):
    """
    Crea la tabla de horas ejecutadas por grado y semana.
    """

    semana_max = df["Semana Del Proyecto"].max() - 1

    tabla_semanal = pd.pivot_table(
        df[
            (df["Grado"].isin([4, 5, 9, 10])) &
            (df["Semana Del Proyecto"] <= semana_max)
        ],
        index="Grado",
        columns="Semana Del Proyecto",
        values="Hora Instruccion Directa Asistio",
        aggfunc="sum",
        fill_value=0,
        margins=True,
        margins_name="Total"
    )

    return tabla_semanal

#CONTROL DE MOTIVOS =====================================================================

#tabla con todas las tipificaciones
def crear_tabla_tipificacion(df):
    """
    Crea la tabla de horas por tipificación y motivo de inasistencia,
    incluyendo los totales de GK (grados 4 y 5) y AS (grados 9 y 10).
    """

    semana_max = df["Semana Del Proyecto"].max() - 1

    tabla_tipificacion = pd.pivot_table(
        df[
            (df["Grado"].isin([4, 5, 9, 10])) &
            (df["Semana Del Proyecto"] <= semana_max)
        ],
        index=["Tipificacion", "Motivo de inasistencia"],
        columns="Grado",
        values="Total horas",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    # Asegurar que existan las cuatro columnas de grado
    for grado in [4, 5, 9, 10]:
        if grado not in tabla_tipificacion.columns:
            tabla_tipificacion[grado] = 0

    # Totales por programa
    tabla_tipificacion["Total GK"] = (
        tabla_tipificacion[4] +
        tabla_tipificacion[5]
    )

    tabla_tipificacion["Total AS"] = (
        tabla_tipificacion[9] +
        tabla_tipificacion[10]
    )

    # Ordenar columnas
    tabla_tipificacion = tabla_tipificacion[
        [
            "Tipificacion",
            "Motivo de inasistencia",
            4,
            5,
            "Total GK",
            9,
            10,
            "Total AS"
        ]
    ]

    tabla_tipificacion = (
        tabla_tipificacion
        .sort_values("Motivo de inasistencia")
        .reset_index(drop=True)
    )

    return tabla_tipificacion

#tabla de razones agrupadas
@st.cache_data
def crear_tabla_razones_agrupadas(df):
    """
    Crea la tabla consolidada de horas por tipificación y grado.
    """

    grados = [4, 5, 9, 10]

    tipificaciones = [
        "RAZONES ACADÉMICAS IED",
        "RAZONES ADMINISTRATIVAS UN",
        "RAZONES DE LA IED"
    ]

    # ============================================================
    # HORAS DE CLASE
    # ============================================================

    tabla_semanal = crear_tabla_semanal(df)

    horas_clase = tabla_semanal.loc[grados, "Total"]

    # ============================================================
    # HORAS DE REPOSICIÓN
    # ============================================================

    reposiciones_por_grupo = crear_reposiciones_por_grupo(df)

    horas_reposicion = (
        reposiciones_por_grupo
        .groupby("Grado")["Horas de reposicion"]
        .sum()
    )

    horas_disponibles = (
        horas_clase
        .add(horas_reposicion, fill_value=0)
    )

    # ============================================================
    # HORAS DE INASISTENCIA POR TIPIFICACIÓN
    # ============================================================

    tabla_tipificacion = crear_tabla_tipificacion(df)

    tabla_inasistencia = (
        tabla_tipificacion[
            tabla_tipificacion["Tipificacion"].isin(tipificaciones)
        ]
        .groupby("Tipificacion")[grados]
        .sum()
    )

    # ============================================================
    # TABLA FINAL
    # ============================================================

    tabla_final = pd.DataFrame(
        index=[
            "Si hubo clase + Reposiciones",
            *tipificaciones
        ],
        columns=grados
    )

    # Horas disponibles
    for grado in grados:

        tabla_final.loc[
            "Si hubo clase + Reposiciones",
            grado
        ] = horas_disponibles.get(grado, 0)

    # Horas de inasistencia
    for tipificacion in tipificaciones:

        for grado in grados:

            if tipificacion in tabla_inasistencia.index:

                tabla_final.loc[
                    tipificacion,
                    grado
                ] = tabla_inasistencia.loc[
                    tipificacion,
                    grado
                ]

            else:

                tabla_final.loc[
                    tipificacion,
                    grado
                ] = 0

    tabla_final[grados] = tabla_final[grados].astype(int)

    # ============================================================
    # PORCENTAJES GK
    # ============================================================

    tabla_final["% General de GK"] = (
        (tabla_final[4] + tabla_final[5])
        / (tabla_final[4].sum() + tabla_final[5].sum())
        * 100
    ).round(2)

    # ============================================================
    # PORCENTAJES AS
    # ============================================================

    tabla_final["% General de AS"] = (
        (tabla_final[9] + tabla_final[10])
        / (tabla_final[9].sum() + tabla_final[10].sum())
        * 100
    ).round(2)

    # ============================================================
    # DEJAR TIPIFICACIÓN COMO COLUMNA
    # ============================================================

    tabla_final = tabla_final.reset_index()

    tabla_final = tabla_final.rename(
        columns={"index": "Tipificación"}
    )

    # ============================================================
    # TOTAL
    # ============================================================

    fila_total = pd.DataFrame({
        "Tipificación": ["TOTAL"],
        4: [tabla_final[4].sum()],
        5: [tabla_final[5].sum()],
        9: [tabla_final[9].sum()],
        10: [tabla_final[10].sum()],
        "% General de GK": [
            tabla_final["% General de GK"].sum()
        ],
        "% General de AS": [
            tabla_final["% General de AS"].sum()
        ]
    })

    tabla_final = pd.concat(
        [tabla_final, fila_total],
        ignore_index=True
    )

    return tabla_final

#cancelaciones prioritarias
def crear_horas_prioritarias(df):
    """
    Crea el total de horas afectadas por inasistencias
    específicas para cada grado.
    """

    grados = [4, 5, 9, 10]

    motivos = [
        "DÍA FESTIVO",
        "INCAPACIDAD MÉDICA DEL TUTOR",
        "SIN TUTOR ASIGNADO"
    ]

    horas_por_grado = (
        df[
            (df["Grado"].isin(grados)) &
            (df["Motivo de inasistencia"].isin(motivos))
        ]
        .groupby("Grado")["Total horas"]
        .sum()
        .reindex(grados, fill_value=0)
        .reset_index(name="Total horas")
    )

    return horas_por_grado

#ESTUDIANTES  ===========================================================================

#asistencia promedio de estudiantes
def crear_tabla_estudiantes_semana(df, df_k2k):
    """
    Crea la tabla de estudiantes asistentes por grado y semana.
    """

    grados = [4, 5, 9, 10]

    semana_max = int(
        df["Semana Del Proyecto"].max() - 1
    )

    tabla_estudiantes_semana = pd.DataFrame(
        index=pd.Index(grados, name="Grado")
    )

    for semana in range(1, semana_max + 1):

        columna = f"tf_sem{semana:02d}_cha"

        conteo = (
            df_k2k[
                df_k2k["tf_grado"].isin(grados)
            ]
            .groupby("tf_grado")[columna]
            .apply(lambda x: (x > 0).sum())
        )

        tabla_estudiantes_semana[semana] = (
            conteo.reindex(
                grados,
                fill_value=0
            )
        )

    # Promedio de estudiantes asistentes por semana
    tabla_estudiantes_semana["Promedio"] = (
        tabla_estudiantes_semana.mean(axis=1)
    )

    # Redondeo convencional: 2.5 → 3, 2.4 → 2
    tabla_estudiantes_semana = tabla_estudiantes_semana.apply(
        lambda col: np.floor(col + 0.5)
    )

    return tabla_estudiantes_semana

#estudiantes retirados
def crear_retirados_por_grado(df_ret):
    """
    Crea el total de estudiantes retirados por grado.
    """

    grados = [4, 5, 9, 10]

    retirados_por_grado = (
        df_ret[
            df_ret["Gradonum"].isin(grados)
        ]
        .groupby("Gradonum")
        .size()
        .reindex(grados, fill_value=0)
        .reset_index(name="Total retirados")
        .rename(columns={"Gradonum": "Grado"})
    )

    return retirados_por_grado

#RESUMEN ===========================================================================

#ppt arribe
def crear_tabla_civicos(df):
    """
    Crea la tabla de horas afectadas por motivos cívicos,
    festivos, PAE, transporte y no focalización.
    """

    # Primero obtenemos la tabla de tipificación
    tabla_tipificacion = crear_tabla_tipificacion(df)

    motivos_agrupados = {
        "DÍA CÍVICO + PARTIDO + SEDE DE VOTACIÓN": [
            "DÍA CÍVICO EN LA CIUDAD",
            "PARTIDO DE LA SELECCIÓN COLOMBIA",
            "SEDE DE VOTACIÓN"
        ],

        "DÍA FESTIVO": [
            "DÍA FESTIVO"
        ],

        "FALTA PAE + TRANSPORTE + NO FOCALIZADO": [
            "FALTA DE PAE",
            "FALTA DE TRANSPORTE ESCOLAR",
            "NO FOCALIZADO INICIALMENTE"
        ]
    }

    grados = [4, 5, 9, 10]

    tabla_civicos = pd.DataFrame(index=grados)

    for nombre, motivos in motivos_agrupados.items():

        filtro = tabla_tipificacion[
            tabla_tipificacion["Motivo de inasistencia"].isin(motivos)
        ]

        tabla_civicos[nombre] = (
            filtro[grados]
            .sum(axis=0)
        )

    # Total por fila
    tabla_civicos["Total"] = tabla_civicos.sum(axis=1)

    # Total por columna
    tabla_civicos.loc["TOTAL"] = tabla_civicos.sum(axis=0)

    # Dejar Grado como columna
    tabla_civicos = tabla_civicos.reset_index()

    tabla_civicos = tabla_civicos.rename(
        columns={"index": "Grado"}
    )

    return tabla_civicos

#resumen 1
@st.cache_data
def crear_tabla_resultado(df, df_k2k, df_ret):
    """
    Crea la tabla resumen de indicadores por grado.
    """

    grados = [4, 5, 9, 10]

    # ============================================================
    # TABLAS NECESARIAS
    # ============================================================

    tabla_semanal = crear_tabla_semanal(df)

    reposiciones_por_grupo = crear_reposiciones_por_grupo(df)

    tabla_tipificacion = crear_tabla_tipificacion(df)

    tabla_final = crear_tabla_razones_agrupadas(df)

    tabla_estudiantes_semana = crear_tabla_estudiantes_semana(
        df,
        df_k2k
    )

    retirados_por_grado = crear_retirados_por_grado(
        df_ret
    )

    tabla_civicos = crear_tabla_civicos(df)

    # ============================================================
    # AULAS ÚNICAS
    # ============================================================

    resultado = (
        df[
            df["Grado"].isin(grados)
        ]
        .groupby("Grado")["Aula"]
        .nunique()
        .reindex(grados, fill_value=0)
        .reset_index(name="Aulas únicas")
    )

    # ============================================================
    # HORAS PROGRAMADAS
    # ============================================================

    semana_max = df["Semana Del Proyecto"].max() - 1

    resultado["N de horas programadas"] = (
        resultado["Aulas únicas"]
        * 2
        * semana_max
    )

    # ============================================================
    # HORAS EFECTIVAS + REPOSICIONES
    # ============================================================

    horas_efectivas_reposiciones = (
        tabla_final
        .loc[
            tabla_final["Tipificación"] == "Si hubo clase + Reposiciones",
            grados
        ]
        .iloc[0]
    )

    resultado["N de horas efectivas + Reposiciones"] = (
        resultado["Grado"]
        .map(horas_efectivas_reposiciones)
        .fillna(0)
    )

    resultado["N de horas efectivas + Reposiciones (sin sedes de votación, festivos, PAE)"] = (
            resultado["Grado"]
            .map(horas_efectivas_reposiciones)
            .fillna(0)
    )

    # ============================================================
    # % HORAS EFECTIVAS
    # ============================================================

    resultado["% de Horas efectivas"] = (
        resultado["N de horas efectivas + Reposiciones"]
        / resultado["N de horas programadas"]
        * 100
    ).round(2)

    # ============================================================
    # HORAS PROGRAMADAS SIN CÍVICOS, FESTIVOS Y PAE
    # ============================================================

    total_civicos_por_grado = (
        tabla_civicos
        .set_index("Grado")["Total"]
    )

    resultado[
        "N de horas programadas "
        "(sin sedes de votación, festivos, PAE)"
    ] = (
        resultado["N de horas programadas"]
        - resultado["Grado"].map(
            total_civicos_por_grado
        ).fillna(0)
    )

    # ============================================================
    # HORAS EFECTIVAS SIN CÍVICOS, FESTIVOS Y PAE
    # ============================================================

    resultado[
        "N de horas efectivas + Reposiciones "
        "(sin sedes de votación, festivos, PAE)"
    ] = (
        resultado["Grado"]
        .map(horas_efectivas_reposiciones)
        .fillna(0)
    )

    # ============================================================
    # % HORAS EFECTIVAS SIN CÍVICOS, FESTIVOS Y PAE
    # ============================================================

    resultado[
        "% de Horas efectivas "
        "(sin sedes de votación, festivos, PAE)"
    ] = (
        resultado[
            "N de horas efectivas + Reposiciones (sin sedes de votación, festivos, PAE)"
        ]
        /
        resultado[
            "N de horas programadas "
            "(sin sedes de votación, festivos, PAE)"
        ]
        * 100
    ).round(2)

    # ============================================================
    # HORAS DE REPOSICIÓN EJECUTADAS
    # ============================================================

    horas_reposicion_por_grado = (
        reposiciones_por_grupo
        .set_index("Grado")["Horas de reposicion"]
    )

    resultado["N de Horas de reposición ejecutadas"] = (
        resultado["Grado"]
        .map(horas_reposicion_por_grado)
        .fillna(0)
    )

    # ============================================================
    # PROMEDIO DE ESTUDIANTES ASISTENTES
    # ============================================================

    resultado[
        "Promedio de estudiantes asistentes por semana"
    ] = (
        resultado["Grado"]
        .map(tabla_estudiantes_semana["Promedio"])
    ).round(2)

    # ============================================================
    # RETIRADOS
    # ============================================================

    retirados_por_grado = (
        retirados_por_grado
        .set_index("Grado")["Total retirados"]
    )

    resultado["Retirados"] = (
        resultado["Grado"]
        .map(retirados_por_grado)
        .fillna(0)
    )

    # ============================================================
    # FILA TOTAL
    # ============================================================

    resultado_sin_total = resultado.copy()

    fila_total = pd.DataFrame({
        "Grado": ["TOTAL"],

        "Aulas únicas": [
            resultado_sin_total["Aulas únicas"].sum()
        ],

        "N de horas programadas": [
            resultado_sin_total[
                "N de horas programadas"
            ].sum()
        ],

        "N de horas efectivas + Reposiciones": [
            resultado_sin_total[
                "N de horas efectivas + Reposiciones"
            ].sum()
        ],

        "% de Horas efectivas": [
            resultado_sin_total[
                "N de horas efectivas + Reposiciones"
            ].sum()
            /
            resultado_sin_total[
                "N de horas programadas"
            ].sum()
            * 100
        ],

        "N de horas programadas "
        "(sin sedes de votación, festivos, PAE)": [
            resultado_sin_total[
                "N de horas programadas "
                "(sin sedes de votación, festivos, PAE)"
            ].sum()
        ],

        "N de horas efectivas + Reposiciones "
        "(sin sedes de votación, festivos, PAE)": [
            resultado_sin_total[
                "N de horas efectivas + Reposiciones "
                "(sin sedes de votación, festivos, PAE)"
            ].sum()
        ],

        "% de Horas efectivas "
        "(sin sedes de votación, festivos, PAE)": [
            resultado_sin_total[
                "N de horas efectivas + Reposiciones "
                "(sin sedes de votación, festivos, PAE)"
            ].sum()
            /
            resultado_sin_total[
                "N de horas programadas "
                "(sin sedes de votación, festivos, PAE)"
            ].sum()
            * 100
        ],

        "N de Horas de reposición ejecutadas": [
            resultado_sin_total[
                "N de Horas de reposición ejecutadas"
            ].sum()
        ],

        "Promedio de estudiantes asistentes por semana": [
            resultado_sin_total[
                "Promedio de estudiantes asistentes por semana"
            ].sum()
        ],

        "Retirados": [
            resultado_sin_total["Retirados"].sum()
        ]
    })

    resultado = pd.concat(
        [resultado_sin_total, fila_total],
        ignore_index=True
    )

    return resultado

#resumen reposiciones
@st.cache_data
def crear_tabla_reposiciones(df, df_reposiciones):
    """
    Crea la tabla de seguimiento de horas de reposición por grado,
    incluyendo los indicadores del segundo semestre.
    """

    grados = [4, 5, 9, 10]

    # ============================================================
    # TABLAS NECESARIAS
    # ============================================================

    tabla_tipificacion = crear_tabla_tipificacion(df)
    reposiciones_por_grupo = crear_reposiciones_por_grupo(df)
    horas_por_grado = crear_horas_prioritarias(df)

    # ============================================================
    # HORAS CANCELADAS ACUMULADAS
    # ============================================================

    horas_canceladas = (
        tabla_tipificacion[grados]
        .sum()
    )

    # ============================================================
    # HORAS DE REPOSICIÓN EJECUTADAS ACUMULADAS
    # ============================================================

    horas_reposicion_ejecutadas = (
        reposiciones_por_grupo
        .set_index("Grado")["Horas de reposicion"]
        .reindex(grados, fill_value=0)
    )

    # ============================================================
    # OBTENER GRADO DESDE EL GRUPO
    # ============================================================

    df_rep = df_reposiciones.copy()

    df_rep["Grado"] = (
        df_rep["grupo"]
        .astype(str)
        .str[0]
        .map({
            "4": 4,
            "5": 5,
            "9": 9,
            "1": 10
        })
    )

    # ============================================================
    # AGRUPAR HORAS DEL SEGUNDO SEMESTRE POR GRADO Y ESTADO
    # ============================================================

    tabla_estados = (
        df_rep
        .groupby(["Grado", "estado"])["horas"]
        .sum()
        .unstack(fill_value=0)
        .reindex(grados, fill_value=0)
    )

    # Asegurar que existan todas las columnas de estados
    for estado in ["Programada", "Cancelada", "Ejecutada"]:
        if estado not in tabla_estados.columns:
            tabla_estados[estado] = 0

    # ============================================================
    # TABLA FINAL
    # ============================================================

    tabla_reposiciones = pd.DataFrame({
        "Grado": grados,

        "Acumulado total horas canceladas": (
            horas_canceladas.values
        ),

        "Acumulado total horas priorizadas para reposición": (
            horas_por_grado["Total horas"].values
        ),

        "Acumulado total horas de reposición ejecutadas": (
            horas_reposicion_ejecutadas.values
        ),

        # Segundo semestre
        "Total horas reposición programadas II semestre": (
            tabla_estados["Ejecutada"].values
            + tabla_estados["Cancelada"].values
        ),

        "Total horas reposición canceladas II semestre": (
            tabla_estados["Cancelada"].values
        ),

        "Total horas reposición ejecutadas II semestre": (
            tabla_estados["Ejecutada"].values
        )
    })

    # ============================================================
    # % CUMPLIMIENTO ACUMULADO
    # ============================================================

    tabla_reposiciones[
        "% cumplimiento total de reposición vs horas priorizadas"
    ] = (
        tabla_reposiciones[
            "Acumulado total horas de reposición ejecutadas"
        ]
        / tabla_reposiciones[
            "Acumulado total horas priorizadas para reposición"
        ]
        * 100
    ).replace(
        [float("inf"), -float("inf")],
        0
    ).fillna(0).round(2)

    # ============================================================
    # PLAN DE REPOSICIÓN ACORDADO II SEMESTRE
    # ============================================================

    tabla_reposiciones[
        "Plan de reposición acordado II semestre"
    ] = (
        tabla_reposiciones[
            "Total horas reposición programadas II semestre"
        ]
        + tabla_reposiciones[
            "Total horas reposición canceladas II semestre"
        ]
        + tabla_reposiciones[
            "Total horas reposición ejecutadas II semestre"
        ]
    )

    # ============================================================
    # % CUMPLIMIENTO II SEMESTRE
    # ============================================================

    tabla_reposiciones[
        "% cumplimiento II semestre total de reposición vs horas priorizadas"
    ] = (
        tabla_reposiciones[
            "Total horas reposición ejecutadas II semestre"
        ]
        / tabla_reposiciones[
            "Acumulado total horas priorizadas para reposición"
        ]
        * 100
    ).replace(
        [float("inf"), -float("inf")],
        0
    ).fillna(0).round(2)

    # ============================================================
    # FILA TOTAL
    # ============================================================

    columnas_sumar = [
        "Acumulado total horas canceladas",
        "Acumulado total horas priorizadas para reposición",
        "Acumulado total horas de reposición ejecutadas",
        "Total horas reposición programadas II semestre",
        "Total horas reposición canceladas II semestre",
        "Total horas reposición ejecutadas II semestre",
        "Plan de reposición acordado II semestre"
    ]

    fila_total = {
        "Grado": "TOTAL"
    }

    for columna in columnas_sumar:
        fila_total[columna] = tabla_reposiciones[columna].sum()

    fila_total = pd.DataFrame([fila_total])

    # % cumplimiento acumulado total
    fila_total[
        "% cumplimiento total de reposición vs horas priorizadas"
    ] = (
        fila_total[
            "Acumulado total horas de reposición ejecutadas"
        ]
        / fila_total[
            "Acumulado total horas priorizadas para reposición"
        ]
        * 100
    ).replace(
        [float("inf"), -float("inf")],
        0
    ).fillna(0).round(2)

    # % cumplimiento segundo semestre total
    fila_total[
        "% cumplimiento II semestre total de reposición vs horas priorizadas"
    ] = (
        fila_total[
            "Total horas reposición ejecutadas II semestre"
        ]
        / fila_total[
            "Acumulado total horas priorizadas para reposición"
        ]
        * 100
    ).replace(
        [float("inf"), -float("inf")],
        0
    ).fillna(0).round(2)

    # ============================================================
    # UNIR FILA TOTAL
    # ============================================================

    tabla_reposiciones = pd.concat(
        [tabla_reposiciones, fila_total],
        ignore_index=True
    )

    return tabla_reposiciones

#grupos en alerta y todos los grupos
def crear_reporte_alertas(df):
    """
    Crea el reporte de aulas afectadas y reposiciones
    para los grupos GK y AS.
    """

    motivos = {
        "FESTIVOS": "DÍA FESTIVO",
        "SIN TUTOR ASIGNADO": "SIN TUTOR ASIGNADO",
        "INCAPACIDAD MÉDICA": "INCAPACIDAD MÉDICA DEL TUTOR"
    }

    grupos = {
        "GK": [4, 5],
        "AS": [9, 10]
    }

    filas = []

    for nombre_grupo, grados in grupos.items():

        datos_grupo = df[
            df["Grado"].isin(grados)
        ]

        # Si el filtro no contiene este grupo, no generar filas
        if datos_grupo.empty:
            continue

        total_horas_afectadas = 0

        # ========================================================
        # Una fila por motivo
        # ========================================================

        for nombre_motivo, motivo in motivos.items():

            datos_motivo = datos_grupo[
                datos_grupo["Motivo de inasistencia"] == motivo
            ]

            grupos_afectados = datos_motivo["Aula"].nunique()

            horas_afectadas = datos_motivo["Total horas"].sum()

            total_horas_afectadas += horas_afectadas

            filas.append({
                "Grupo": nombre_grupo,
                "Motivo": nombre_motivo,
                "# Grupos afectados": grupos_afectados,
                "# de horas afectadas": horas_afectadas,
                "# de horas de reposición ejecutadas": None,
                "% de horas de reposición vs horas afectadas": None
            })

        # ========================================================
        # Horas de reposición ejecutadas
        # ========================================================

        horas_reposicion = datos_grupo[
            datos_grupo["ID Interna Tutor Repo"] > 0
        ]["Total horas"].sum()

        porcentaje = (
            horas_reposicion / total_horas_afectadas * 100
            if total_horas_afectadas > 0
            else 0
        ).round(2)

        # ========================================================
        # Fila Total
        # ========================================================

        filas.append({
            "Grupo": nombre_grupo,
            "Motivo": "Total",
            "# Grupos afectados": None,
            "# de horas afectadas": total_horas_afectadas,
            "# de horas de reposición ejecutadas": horas_reposicion,
            "% de horas de reposición vs horas afectadas": porcentaje
        })

    reporte_alertas = pd.DataFrame(filas)

    return reporte_alertas

#TABLAS DE RANGOS =============================================================================

#aprovehcamiento de aulas (sobre programa academico)
def crear_rangos_aprovechamiento_academico(tabla_aprovechamiento):

    grados = [4, 5, 9, 10]

    bins = [
        -float("inf"), 1, 10, 20, 30, 40, 50,
        60, 70, 80, 90, 101
    ]

    labels = [
        "0",
        "1 - 9",
        "10 - 19",
        "20 - 29",
        "30 - 39",
        "40 - 49",
        "50 - 59",
        "60 - 69",
        "70 - 79",
        "80 - 89",
        "90 - 100"
    ]

    tabla = tabla_aprovechamiento.copy()

    tabla["Rango aprovechamiento"] = pd.cut(
        tabla["% de aprovechamiento académico"],
        bins=bins,
        labels=labels,
        right=False
    )

    tabla_rangos = pd.crosstab(
        tabla["Rango aprovechamiento"],
        tabla["Grado"]
    )

    # Asegurar que existan todos los grados
    tabla_rangos = (
        tabla_rangos
        .reindex(index=labels, fill_value=0)
        .reindex(columns=grados, fill_value=0)
    )

    # Totales por programa
    tabla_rangos["Total GK"] = (
        tabla_rangos[4] +
        tabla_rangos[5]
    )

    tabla_rangos["Total AS"] = (
        tabla_rangos[9] +
        tabla_rangos[10]
    )

    # Ordenar columnas
    tabla_rangos = tabla_rangos[
        [
            4,
            5,
            "Total GK",
            9,
            10,
            "Total AS"
        ]
    ]

    # Total general por grado y programa
    tabla_rangos.loc["TOTAL"] = tabla_rangos.sum(axis=0)

    return tabla_rangos

#aprovechamiento de estudiantes (procentaje que asistena l aula)
def crear_rangos_aprovechamiento_estudiantes(tabla_aprovechamiento):

    grados = [4, 5, 9, 10]

    bins = [
        -0.001, 1, 10, 20, 30, 40, 50,
        60, 70, 80, 90, 200.001
    ]

    labels = [
        "0",
        "1 - 9",
        "10 - 19",
        "20 - 29",
        "30 - 39",
        "40 - 49",
        "50 - 59",
        "60 - 69",
        "70 - 79",
        "80 - 89",
        "90 - 100"
    ]

    tabla = tabla_aprovechamiento.copy()

    tabla["Rango aprovechamiento"] = pd.cut(
        tabla["% de aprovechamiento de estudiantes"],
        bins=bins,
        labels=labels,
        right=False
    )

    tabla_rangos = pd.crosstab(
        tabla["Rango aprovechamiento"],
        tabla["Grado"]
    )

    # Asegurar que existan todos los grados
    tabla_rangos = (
        tabla_rangos
        .reindex(index=labels, fill_value=0)
        .reindex(columns=grados, fill_value=0)
    )

    # Total GK = grados 4 + 5
    tabla_rangos["Total GK"] = (
        tabla_rangos[4] +
        tabla_rangos[5]
    )

    # Total AS = grados 9 + 10
    tabla_rangos["Total AS"] = (
        tabla_rangos[9] +
        tabla_rangos[10]
    )

    # Orden de las columnas
    tabla_rangos = tabla_rangos[
        [
            4,
            5,
            "Total GK",
            9,
            10,
            "Total AS"
        ]
    ]

    # Fila TOTAL
    tabla_rangos.loc["TOTAL"] = tabla_rangos.sum(axis=0)

    return tabla_rangos

#asistencias de estudiantes (asistencia por estudiante)
def crear_rangos_asistencia_k2k(df_k2k):

    grados = [4, 5, 9, 10]

    bins = [
        -0.001, 1, 10, 20, 30, 40, 50,
        60, 70, 80, 90, 200.001
    ]

    labels = [
        "0",
        "1 - 9",
        "10 - 19",
        "20 - 29",
        "30 - 39",
        "40 - 49",
        "50 - 59",
        "60 - 69",
        "70 - 79",
        "80 - 89",
        "90 - 100"
    ]

    tabla = df_k2k.copy()

    tabla["Rango asistencia"] = pd.cut(
        tabla["tf_porcentaje"],
        bins=bins,
        labels=labels,
        right=False
    )

    tabla_asistencia = pd.crosstab(
        tabla["Rango asistencia"],
        tabla["tf_grado"]
    )

    # Asegurar que existan todos los grados
    tabla_asistencia = (
        tabla_asistencia
        .reindex(index=labels, fill_value=0)
        .reindex(columns=grados, fill_value=0)
    )

    # Total GK = grados 4 + 5
    tabla_asistencia["Total GK"] = (
        tabla_asistencia[4] +
        tabla_asistencia[5]
    )

    # Total AS = grados 9 + 10
    tabla_asistencia["Total AS"] = (
        tabla_asistencia[9] +
        tabla_asistencia[10]
    )

    # Orden de las columnas
    tabla_asistencia = tabla_asistencia[
        [
            4,
            5,
            "Total GK",
            9,
            10,
            "Total AS"
        ]
    ]

    # Fila TOTAL
    tabla_asistencia.loc["TOTAL"] = tabla_asistencia.sum(axis=0)

    return tabla_asistencia

#GRAFICAS ===========================================================================================================================================================

def crear_grafica_razones_agrupadas(tabla, columnas_visibles=None):

    import plotly.express as px

    tabla = tabla.copy()

    # Eliminar fila TOTAL
    mascara_total = tabla.astype(str).apply(
        lambda x: x.str.strip().str.upper().eq("TOTAL")
    ).any(axis=1)

    tabla = tabla.loc[~mascara_total].copy()

    # Grados disponibles
    grados = ["4", "5", "9", "10"]

    # Filtrar según las columnas visibles
    if columnas_visibles is not None:
        grados = [
            grado
            for grado in grados
            if grado in columnas_visibles
        ]

    # Si no queda ningún grado visible
    if not grados:
        return None

    # Asegurar que las columnas existan
    grados = [
        grado
        for grado in grados
        if grado in tabla.columns
    ]

    # Pasar a formato largo
    tabla_larga = tabla.melt(
        id_vars=["Tipificación"],
        value_vars=grados,
        var_name="Grado",
        value_name="Horas"
    )

    # COLORES FIJOS POR GRADO
    colores_grados = {
        "4": "#636EFA",
        "5": "#EF553B",
        "9": "#00CC96",
        "10": "#AB63FA"
    }

    fig = px.bar(
        tabla_larga,
        x="Tipificación",
        y="Horas",
        color="Grado",
        barmode="group",
        text_auto=True,
        color_discrete_map=colores_grados
    )

    fig.update_layout(
        xaxis_title="Motivo",
        yaxis_title="Horas",
        legend_title="Grado",
        xaxis_tickangle=-45
    )

    return fig

def crear_grafica_motivos_desagregados(tabla, columnas_visibles=None):

    import plotly.express as px

    tabla = tabla.copy()

    # Eliminar fila TOTAL
    mascara_total = tabla.astype(str).apply(
        lambda x: x.str.strip().str.upper().eq("TOTAL")
    ).any(axis=1)

    tabla = tabla.loc[~mascara_total].copy()

    # Grados disponibles
    grados = ["4", "5", "9", "10"]

    # Filtrar según las columnas visibles
    if columnas_visibles is not None:
        grados = [
            grado
            for grado in grados
            if grado in columnas_visibles
        ]

    # Si no queda ningún grado visible
    if not grados:
        return None

    # Asegurar que las columnas existan
    grados = [
        grado
        for grado in grados
        if grado in tabla.columns
    ]

    # Crear nombre completo del motivo
    tabla["Motivo completo"] = (
        tabla["Tipificacion"].astype(str)
        + " - "
        + tabla["Motivo de inasistencia"].astype(str)
    )

    # Crear etiqueta corta para mostrar en la gráfica
    max_caracteres = 35

    tabla["Motivo"] = tabla["Motivo completo"].apply(
        lambda x: (
            x[:max_caracteres] + "..."
            if len(x) > max_caracteres
            else x
        )
    )

    # Pasar a formato largo
    tabla_larga = tabla.melt(
        id_vars=["Motivo", "Motivo completo"],
        value_vars=grados,
        var_name="Grado",
        value_name="Horas"
    )

    # Colores fijos por grado
    colores_grados = {
        "4": "#636EFA",
        "5": "#EF553B",
        "9": "#00CC96",
        "10": "#AB63FA"
    }

    fig = px.bar(
        tabla_larga,
        x="Motivo",
        y="Horas",
        color="Grado",
        barmode="group",
        text="Horas",
        color_discrete_map=colores_grados,
        custom_data=["Motivo completo"]
    )

    fig.update_traces(
        textposition="outside",
        textfont=dict(size=14),
        texttemplate="%{y}",
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Grado: %{fullData.name}<br>"
            "Horas: %{y}<extra></extra>"
        ),
        cliponaxis=False
    )

    fig.update_layout(
        xaxis_title="Motivo de inasistencia",
        yaxis_title="Horas",
        legend_title="Grado",
        xaxis_tickangle=-45,
        height=650,
        margin=dict(
            l=50,
            r=30,
            t=50,
            b=180
        )
    )

    return fig

#PENDIENTES POR ASISTENCIA

def crear_asistencias_pendientes_gk(df):
    """
    Crea el total de asistencias pendientes por tutor para AS
    (grados 4 y 5), excluyendo la semana actual.
    """

    semana_max = df["Semana Del Proyecto"].max() - 1

    tabla_gk = (
        df[
            (df["Grado"].isin([4, 5])) &
            (df["Semana Del Proyecto"] <= semana_max)
        ]
        .groupby("Nombre Tutor Del Aula")["Asistencia pendiente"]
        .sum()
        .reset_index(name="Total asistencias pendientes")
        .sort_values(
            "Total asistencias pendientes",
            ascending=False
        )
    )

    tabla_gk["Total asistencias pendientes"] = (
        tabla_gk["Total asistencias pendientes"]
        .astype(int)
    )

    tabla_gk = tabla_gk.reset_index(drop=True)

    return tabla_gk

def crear_asistencias_pendientes_as(df):
    """
    Crea el total de asistencias pendientes por tutor para AS
    (grados 9 y 10), excluyendo la semana actual.
    """

    semana_max = df["Semana Del Proyecto"].max() - 1

    tabla_as = (
        df[
            (df["Grado"].isin([9, 10])) &
            (df["Semana Del Proyecto"] <= semana_max)
        ]
        .groupby("Nombre Tutor Del Aula")["Asistencia pendiente"]
        .sum()
        .reset_index(name="Total asistencias pendientes")
        .sort_values(
            "Total asistencias pendientes",
            ascending=False
        )
    )

    tabla_as["Total asistencias pendientes"] = (
        tabla_as["Total asistencias pendientes"]
        .astype(int)
    )

    tabla_as = tabla_as.reset_index(drop=True)

    return tabla_as

#SEGUIMIENTO NOTAS Y TUTORES

def crear_notas_por_aula(df, actividades):
    """
    Cuenta, por aula, cuántos estudiantes tienen nota
    registrada en cada actividad.

    Cada fila del DataFrame representa un estudiante.
    """

    columnas_base = [
        "Aula",
        "Ied",
        "Grupo",
        "Gradonum",
        "Nombre Tutor"
    ]

    tabla = (
        df.groupby(columnas_base, dropna=False)[actividades]
        .count()
        .reset_index()
    )

    tabla = tabla.rename(columns={
        "Gradonum": "Grado",
        "Ied": "IED"
    })

    return tabla
