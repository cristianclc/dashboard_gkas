import numpy as np
import pandas as pd


def transformar_aula_aula(df): # ======================================================= 01 AULA - AULA

    df = df.copy()

    # 1. Total horas

    df["Total horas"] = (
        df["Hora Instruccion Directa Asistio"]
        + df["Hora Instruccion Directa No Asistio"]
        + df["Hora Instruccion Directa No Reportada"]
    )

    # 2. Motivo de inasistencia

    df["Motivo de inasistencia"] = np.where(
        (df["Estado Del Horario"] == 1) &
        (df["Hora Instruccion Directa No Reportada"] > 0) &
        (df["Festivo"] == "SI"),
        "DÍA FESTIVO",
        df["Descripcion Motivo"]
    )

    # 3. Tipificación

    mapeo_tipificacion = {

        "ACTIVIDAD DEPORTIVA": "RAZONES ACADÉMICAS IED",
        "ACTO CÍVICO": "RAZONES ACADÉMICAS IED",
        "AUSENCIA DEL TITULAR DEL GRUPO/SIN EL DOCENTE ACOMPAÑANTE DE REEMPLAZO": "RAZONES ACADÉMICAS IED",
        "CAMBIO DE HORARIO": "RAZONES ACADÉMICAS IED",
        "CELEBRACIÓN INSTITUCIONAL": "RAZONES ACADÉMICAS IED",
        "DÍA CÍVICO EN LA CIUDAD": "FECHAS CÍVICAS",
        "DÍA FESTIVO": "FESTIVIDADES",
        "ELECCIÓN DE PERSONERO ESTUDIANTIL": "RAZONES ACADÉMICAS IED",
        "ENTREGA DE BOLETINES": "RAZONES ACADÉMICAS IED",
        "ESTUDIANTES NO NOTIFICADOS": "RAZONES ACADÉMICAS IED",
        "FALTA DE AGUA": "RAZONES DE LA IED",
        "FALTA DE ELECTRICIDAD": "RAZONES DE LA IED",
        "FALTA DE PAE": "RAZONES DE LA SED",
        "FALTA DE TRANSPORTE ESCOLAR": "RAZONES DE LA SED",
        "FUERTES LLUVIAS": "RAZONES DE LA IED",
        "INCAPACIDAD MÉDICA DEL TUTOR": "RAZONES ADMINISTRATIVAS UN",
        "INCONVENIENTES CON LA INFRAESTRUCTURA DEL IED": "RAZONES DE LA IED",
        "INCONVENIENTES DE ACCESO A LA IED": "RAZONES DE LA IED",
        "NO FOCALIZADO INICIALMENTE": "RAZONES DE LA SED",
        "NO HAY JORNADA EXTENDIDA": "RAZONES ACADÉMICAS IED",
        "PARO": "RAZONES DE LA IED",
        "PARTIDO DE LA SELECCIÓN COLOMBIA": "FECHAS CÍVICAS",
        "REUNIÓN DE DOCENTES": "RAZONES ACADÉMICAS IED",
        "REUNIÓN DE PADRES DE FAMILIA": "RAZONES ACADÉMICAS IED",
        "SALIDA DE CONVIVENCIA": "RAZONES ACADÉMICAS IED",
        "SEDE DE VOTACIÓN": "FECHAS CÍVICAS",
        "SE RETIRA DE LA ESTRATEGIA": "RAZONES DE LA SED",
        "SIMULACROS/PRUEBAS INSTITUCIONALES": "RAZONES ACADÉMICAS IED",
        "SIN TUTOR ASIGNADO": "RAZONES ADMINISTRATIVAS UN",
        "VACACIONES ANTICIPADAS": "RAZONES ACADÉMICAS IED"
    }

    df["Tipificacion"] = (
        df["Motivo de inasistencia"]
        .map(mapeo_tipificacion)
    )

    # 4. Asistencia pendiente

    df["Asistencia pendiente"] = np.where(
        (df["Festivo"] == "NO") &
        (df["Hora Instruccion Directa No Reportada"] > 0),
        1,
        np.nan
    )

    df["Total horas"] = df["Total horas"].round(2)

    return df

def transformar_notas_gk(df_gk):  # ======================================================= 03 NOTAS GK
    """
    Transformaciones correspondientes al archivo 03 - Notas GK.
    """

    df_gk = df_gk.copy()

    # 1. Definitiva C1

    df_gk["C1 Definitiva (1-5)"] = (
        df_gk["C1 Class Activity 80%"].fillna(0) * 0.8
        + df_gk["C1 Class Performance 20%"].fillna(0) * 0.2
    )

    df_gk["C1 Definitiva (1-100)"] = (
        df_gk["C1 Definitiva (1-5)"] * 20
    )

    # 2. Definitiva C2

    df_gk["C2 Definitiva (1-5)"] = (
        df_gk["C2 Class Activity 30%"].fillna(0) * 0.3
        + df_gk["C2 Oral Evaluation 30%"].fillna(0) * 0.3
        + df_gk["C2 Final Exam 30%"].fillna(0) * 0.3
        + df_gk["C2 Class Performance 10%"].fillna(0) * 0.1
    )

    df_gk["C2 Definitiva (1-100)"] = (
        df_gk["C2 Definitiva (1-5)"] * 20
    )

    # 3. Definitiva C3

    df_gk["C3 Definitiva (1-5)"] = (
        df_gk["C3 Class Activity 30%"].fillna(0) * 0.3
        + df_gk["C3 Oral Evaluation 30%"].fillna(0) * 0.3
        + df_gk["C3 Final Exam 30%"].fillna(0) * 0.3
        + df_gk["C3 Class Performance 10%"].fillna(0) * 0.1
    )

    df_gk["C3 Definitiva (1-100)"] = (
        df_gk["C3 Definitiva (1-5)"] * 20
    )

    # 4. Definitiva C4

    df_gk["C4 Definitiva (1-5)"] = (
        df_gk["C4 Class Activity 30%"].fillna(0) * 0.3
        + df_gk["C4 Oral Evaluation 30%"].fillna(0) * 0.3
        + df_gk["C4 Final Exam 30%"].fillna(0) * 0.3
        + df_gk["C4 Class Performance 10%"].fillna(0) * 0.1
    )

    df_gk["C4 Definitiva (1-100)"] = (
        df_gk["C4 Definitiva (1-5)"] * 20
    )

    # 5. Promedio C1 - C2

    df_gk["Definitiva Promedio C1 - C2"] = (
        df_gk[
            [
                "C1 Definitiva (1-5)",
                "C2 Definitiva (1-5)"
            ]
        ]
        .fillna(0)
        .sum(axis=1) / 2
    )

    # 6. Desempeño Periodo 1

    df_gk["Desempeño Periodo 1"] = pd.cut(
        df_gk["C1 Definitiva (1-5)"],
        bins=[
            -float("inf"),
            3,
            4,
            4.5,
            float("inf")
        ],
        labels=[
            "BAJO",
            "BÁSICO",
            "ALTO",
            "SUPERIOR"
        ],
        right=False
    )

    # 7. Desempeño Periodo 2

    df_gk["Desempeño Periodo 2"] = pd.cut(
        df_gk["C2 Definitiva (1-5)"],
        bins=[
            -float("inf"),
            3,
            4,
            4.5,
            float("inf")
        ],
        labels=[
            "BAJO",
            "BÁSICO",
            "ALTO",
            "SUPERIOR"
        ],
        right=False
    )

    # Redondeo al final: los desempeños se calculan con el valor sin redondear
    columnas_calculadas = [
        f"C{n} Definitiva ({escala})"
        for n in range(1, 5)
        for escala in ("1-5", "1-100")
    ] + ["Definitiva Promedio C1 - C2"]

    df_gk[columnas_calculadas] = df_gk[columnas_calculadas].round(2)

    return df_gk

def transformar_notas_as(df_as):  # ======================================================= 04 NOTAS AS
    """
    Transformaciones correspondientes al archivo 04 - Notas AS.
    """
    df_as = df_as.copy()

    # DEFINITIVA C1

    df_as["C1 Definitiva (1-5)"] = (
        df_as["C1 Oral Activity 40%"].fillna(0) * 0.4
        + df_as["C1 Final Oral Activity 50%"].fillna(0) * 0.5
        + df_as["C1 Class Performance 10%"].fillna(0) * 0.1
    )

    df_as["C1 Definitiva (1-100)"] = (
        df_as["C1 Definitiva (1-5)"] * 20
    )

    # DEFINITIVA C2

    df_as["C2 Definitiva (1-5)"] = (
        df_as["C2 Oral Activity1 30%"].fillna(0) * 0.3
        + df_as["C2 Oral Activity2 30%"].fillna(0) * 0.3
        + df_as["C2 Final Project 30%"].fillna(0) * 0.3
        + df_as["C2 Class Performance 10%"].fillna(0) * 0.1
    )

    df_as["C2 Definitiva (1-100)"] = (
        df_as["C2 Definitiva (1-5)"] * 20
    )

    # DEFINITIVA C3

    df_as["C3 Definitiva (1-5)"] = (
        df_as["C3 Oral Activity1 30%"].fillna(0) * 0.3
        + df_as["C3 Oral Activity2 30%"].fillna(0) * 0.3
        + df_as["C3 Final Project 30%"].fillna(0) * 0.3
        + df_as["C3 Class Performance 10%"].fillna(0) * 0.1
    )

    df_as["C3 Definitiva (1-100)"] = (
        df_as["C3 Definitiva (1-5)"] * 20
    )

    # DEFINITIVA C4

    df_as["C4 Definitiva (1-5)"] = (
        df_as["C4 Oral Activity 40%"].fillna(0) * 0.4
        + df_as["C4 Final Oral Activity 50%"].fillna(0) * 0.5
        + df_as["C4 Class Performance 10%"].fillna(0) * 0.1
    )

    df_as["C4 Definitiva (1-100)"] = (
        df_as["C4 Definitiva (1-5)"] * 20
    )

    # PROMEDIO C1 - C2

    df_as["Definitiva Promedio C1 - C2"] = (
        df_as[
            [
                "C1 Definitiva (1-5)",
                "C2 Definitiva (1-5)"
            ]
        ]
        .fillna(0)
        .sum(axis=1) / 2
    )

    # DESEMPEÑO PERIODO 1

    df_as["Desempeño Periodo 1"] = pd.cut(
        df_as["C1 Definitiva (1-5)"],
        bins=[
            -float("inf"),
            3,
            4,
            4.5,
            float("inf")
        ],
        labels=[
            "BAJO",
            "BÁSICO",
            "ALTO",
            "SUPERIOR"
        ],
        right=False
    )

    # DESEMPEÑO PERIODO 2

    df_as["Desempeño Periodo 2"] = pd.cut(
        df_as["C2 Definitiva (1-5)"],
        bins=[
            -float("inf"),
            3,
            4,
            4.5,
            float("inf")
        ],
        labels=[
            "BAJO",
            "BÁSICO",
            "ALTO",
            "SUPERIOR"
        ],
        right=False
    )

    # Redondeo al final: los desempeños se calculan con el valor sin redondear
    columnas_calculadas = [
        f"C{n} Definitiva ({escala})"
        for n in range(1, 5)
        for escala in ("1-5", "1-100")
    ] + ["Definitiva Promedio C1 - C2"]

    df_as[columnas_calculadas] = df_as[columnas_calculadas].round(2)

    return df_as

def transformar_k2k(df_k2k): # ======================================================= 06 NIÑO A NIÑO K2K

    df_k2k = df_k2k.copy()

    # =========================
    # TOTAL HORAS ASISTIDAS
    # =========================

    df_k2k["Total horas asistidas por el estudiante"] = (
        df_k2k.loc[:, "tf_sem01_cha":"tf_sem32_cha"]
        .sum(axis=1)
    )

    # =========================
    # % ASISTENCIA TOTAL
    # =========================

    df_k2k["% de horas asistidas por estudiante vs horas efectivas de clase"] = (
        df_k2k["Total horas asistidas por el estudiante"]
        / df_k2k["tf_cant_horas_dictadas"]
        * 100
    ).clip(upper=100).round(2)

    # =========================
    # ALERTA DEL ESTUDIANTE
    # =========================

    condiciones = [
        (
            df_k2k["tf_grado_en_letras"].isin(["NOVENO", "DÉCIMO"])
            & (
                df_k2k[
                    "% de horas asistidas por estudiante vs horas efectivas de clase"
                ] < 70
            )
        ),
        (
            df_k2k["tf_grado_en_letras"].isin(["NOVENO", "DÉCIMO"])
            & (df_k2k["tf_estudiante_en_riesgo"] == "ALERTA")
        ),
        (
            df_k2k["tf_grado_en_letras"].isin(["CUARTO", "QUINTO"])
            & (df_k2k["tf_estudiante_en_riesgo"] == "ALERTA")
        )
    ]

    valores = [
        "ALERTA POR CONSTANCIA",
        "ALERTA POR ASISTENCIA",
        "ALERTA POR ASISTENCIA"
    ]

    df_k2k["Alerta del estudiante"] = np.select(
        condiciones,
        valores,
        default=""
    )

    # =========================
    # ASISTENCIA PERIODO 1
    # =========================

    df_k2k["% Asistencia Periodo 1"] = (
        df_k2k.loc[:, "tf_sem01_cha":"tf_sem05_cha"]
        .sum(axis=1)
        / 10
        * 100
    )

    # =========================
    # ASISTENCIA PERIODO 2
    # =========================

    df_k2k["% Asistencia Periodo 2"] = (
        df_k2k.loc[:, "tf_sem06_cha":"tf_sem15_cha"]
        .sum(axis=1)
        / 20
        * 100
    )

    # =========================
    # ASISTENCIA PERIODO 3
    # =========================

    df_k2k["% Asistencia Periodo 3"] = (
            df_k2k.loc[:, "tf_sem16_cha":"tf_sem25_cha"]
            .sum(axis=1)
            / 20
            * 100
        )

    # =========================
    # ASISTENCIA PERIODO 4
    # =========================

    df_k2k["% Asistencia Periodo 4"] = (
                df_k2k.loc[:, "tf_sem26_cha":"tf_sem32_cha"]
                .sum(axis=1)
                / 20
                * 100
            )

    columnas_calculadas = [
        "Total horas asistidas por el estudiante",
        "% de horas asistidas por estudiante vs horas efectivas de clase",
        "% Asistencia Periodo 1",
        "% Asistencia Periodo 2"
    ]

    df_k2k[columnas_calculadas] = df_k2k[columnas_calculadas].round(2)

    return df_k2k

def transformar_retirados(df_ret): #=========================================== 05 -RETIRADOS, REQUIERE MÁS TRASNFORMACIONES DEL MOTIVO
    """ 
    Transformaciones correspondientes al archivo 05 - Retirados.
    """
    df_ret = df_ret.copy()

    df_ret["NombreEst"] = (
        df_ret["Nombre Est"]
        .str.replace(" ", "", regex=False)
    )

    return df_ret