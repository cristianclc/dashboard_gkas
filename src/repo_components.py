import streamlit as st
import pandas as pd
from pathlib import Path

#CARAGR DATOS
@st.cache_data
def cargar_datos_excel(ruta):
    """Carga las tres hojas del archivo Excel."""

    df_reposiciones = pd.read_excel(
        ruta, sheet_name="Reposiciones"
    )

    df_lt = pd.read_excel(
        ruta, sheet_name="LT"
    )

    df_horarios = pd.read_excel(
        ruta, sheet_name="Horarios_sedes"
    )

    df_tutores = pd.read_excel(
            ruta, sheet_name="Tutores"
        )

    return df_reposiciones, df_lt, df_horarios, df_tutores

#PREPARAR DATOS DE LAS REPOSICIONEs
@st.cache_data
def preparar_datos(df_reposiciones, df_lt, df_horarios, df_tutores):

    # 1. Estandarizar columnas
    df_reposiciones = df_reposiciones.rename(columns={
        "AULA": "aula",
        "IED": "ied",
        "GRUPO": "grupo",
        "SESION": "sesion",
        "FECHA REPO": "fecha_reposicion",
        "HORAS": "horas",
        "ESTADO": "estado",
        "TUTOR": "tutor",
        "LT": "lt",
        "MOTIVO DE CANCELACIÓN": "motivo_cancelacion"
    })

    df_lt = df_lt.rename(columns={
        "IED": "ied",
        "LEAD TEACHER": "lt"
    })

    df_horarios = df_horarios.rename(columns={
        "IED": "ied",
        "AULA": "aula",
        "GRUPO": "grupo",
        "GRADO": "grado",
        "HORARIO": "horario",
        "AUXILIAR": "auxiliar"
    })

    df_tutores = df_tutores.rename(columns={
        "TUTOR": "tutor",
    })

    # 1.5 Limpiar espacios en columnas de texto clave
    df_reposiciones["ied"] = df_reposiciones["ied"].str.strip()
    df_lt["ied"] = df_lt["ied"].str.strip()
    df_horarios["ied"] = df_horarios["ied"].str.strip()

    # 2. Convertir AULA a valor numérico
    df_reposiciones["aula"] = pd.to_numeric(
        df_reposiciones["aula"], errors="coerce"
    )

    df_horarios["aula"] = pd.to_numeric(
        df_horarios["aula"], errors="coerce"
    )

    # 3. Conectar con horarios
    df_reposiciones = df_reposiciones.merge(
        df_horarios[["aula", "horario", "auxiliar"]],
        on="aula",
        how="left",
        validate="many_to_one"
    )

    # 4. Conectar con Lead Teacher
    df_reposiciones = df_reposiciones.merge(
        df_lt[["ied", "lt"]],
        on="ied",
        how="left",
        suffixes=("", "_lookup"),
        validate="many_to_one"
    )

    df_reposiciones["lt"] = df_reposiciones["lt_lookup"]

    df_reposiciones = df_reposiciones.drop(
        columns=["lt_lookup"]
    )

    # 5. Convertir tipos de datos
    df_reposiciones["fecha_reposicion"] = pd.to_datetime(
        df_reposiciones["fecha_reposicion"],
        dayfirst=True,
        errors="coerce"
    )

    df_reposiciones["horas"] = pd.to_numeric(
        df_reposiciones["horas"],
        errors="coerce"
    )

    # 6. Crear identificador
    df_reposiciones = df_reposiciones.reset_index(drop=True)

    df_reposiciones["id_reposicion"] = (
        df_reposiciones.index + 1
    )

    # 7. Ordenar
    df_reposiciones = df_reposiciones.sort_values(
        ["aula", "fecha_reposicion"]
    ).reset_index(drop=True)

    return df_reposiciones, df_horarios, df_lt, df_tutores

#INDICADORES DE PROG, EJE, CANC
def calcular_indicadores(df):

    return {
        "Total programadas II semestre": df["horas"].sum(),
        "Ejecutadas": df.loc[
            df["estado"] == "Ejecutada", "horas"
        ].sum(),
        "Programadas": df.loc[
            df["estado"] == "Programada", "horas"
        ].sum(),
        "Canceladas": df.loc[
            df["estado"] == "Cancelada", "horas"
        ].sum()
    }
#FILTROS REPOS

def filtrar_reposiciones(
    df,
    fecha_desde,
    fecha_hasta,
    estado="Todos",
    instituciones=None,
    grupo="Todos",
    sesion="Todas"
):

    df_filtrado = df.copy()

    # Filtro por fechas
    df_filtrado = df_filtrado[
        (df_filtrado["fecha_reposicion"].dt.date >= fecha_desde)
        &
        (df_filtrado["fecha_reposicion"].dt.date <= fecha_hasta)
    ]

    # Filtro por estado
    if estado != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["estado"] == estado
        ]

    # Filtro por institución
    if instituciones:
        df_filtrado = df_filtrado[
            df_filtrado["ied"].isin(instituciones)
        ]

    # Filtro por grupo
    if grupo != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["grupo"] == grupo
        ]

    # Filtro por sesión
    if sesion != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["sesion"] == sesion
        ]

    return df_filtrado

#CREAR REPOSICONS
def crear_registro_reposicion(
    df,
    ied,
    grupo,
    aula,
    horario,
    fecha,
    horas,
    tutor,
    auxiliar=None,
    lt=None
):
    
    nuevo_id = (
        df["id_reposicion"].max() + 1
        if not df.empty
        else 1
    )

    nueva_reposicion = pd.DataFrame([{
        "id_reposicion": nuevo_id,
        "aula": aula,
        "horario": horario,
        "sesion": None,
        "ied": ied,
        "grupo": grupo,
        "fecha_reposicion": pd.Timestamp(fecha),
        "horas": horas,
        "estado": "Programada",
        "tutor": tutor,
        "motivo_cancelacion": None,
        "auxiliar": auxiliar,
        "lt": lt
        
    }])

    df = pd.concat(
        [df, nueva_reposicion],
        ignore_index=True
    )

    return df

#MODIFICAR REPOSICIONS
def actualizar_registro_reposicion(
    df,
    id_reposicion,
    fecha,
    horas,
    estado,
    motivo,
    tutor
):

    indice = df.index[
        df["id_reposicion"] == id_reposicion
    ][0]

    df.loc[indice, "fecha_reposicion"] = pd.Timestamp(fecha)
    df.loc[indice, "horas"] = horas
    df.loc[indice, "estado"] = estado
    df.loc[indice, "motivo_cancelacion"] = motivo
    df.loc[indice, "tutor"] = tutor

    return df

## TABLA DE SESIIONES EJECUTADAS, PROGRAMAS, CANCELADAS
@st.cache_data
def crear_vista_sesiones(
    df_filt,
    df_reposiciones,
    df_horarios,
    tabla_aprovechamiento
):

    if df_filt.empty:
        return pd.DataFrame()

    # ========================================================
    # 1. ORDENAR REGISTROS
    # ========================================================

    df_filt = df_filt.sort_values(
        ["ied", "grupo", "aula", "sesion"]
    ).copy()

    identificadores = ["ied", "grupo", "aula"]

    # ========================================================
    # 2. PREPARAR INFORMACIÓN DE HORARIOS
    # ========================================================

    if not df_horarios.empty:
        df_horarios = (
            df_horarios
            .drop_duplicates(subset=["aula"])
            .set_index("aula")
        )

    # ========================================================
    # 3. PREPARAR INFORMACIÓN DE APROVECHAMIENTO
    # ========================================================

    if not tabla_aprovechamiento.empty:
        tabla_aprovechamiento = (
            tabla_aprovechamiento
            .drop_duplicates(subset=["Aula"])
            .set_index("Aula")
        )

    # ========================================================
    # 4. IDENTIFICAR NÚMERO MÁXIMO DE SESIONES
    # ========================================================

    if not df_reposiciones.empty:
        max_sesion = int(
            pd.to_numeric(
                df_reposiciones["sesion"],
                errors="coerce"
            ).max()
        )
    else:
        max_sesion = 0

    filas = []

    # ========================================================
    # 5. CONSTRUIR UNA FILA POR AULA
    # ========================================================

    for claves, grupo_df in df_filt.groupby(
        identificadores,
        sort=False,
        dropna=False
    ):

        ied, grupo, aula = claves

        fila = {
            "Aula": aula,
            "IED": ied,
            "Grado": "—",
            "Grupo": grupo,
            "Horario": "—",
            "Total horas ejecutadas": 0,
            "Horas de reposición segundo semestre": 0,
            "Horas de reposición por migrar": 0,
            "Auxiliar": "—"
        }

        # ----------------------------------------------------
        # DATOS DE HORARIO, GRADO Y AUXILIAR
        # ----------------------------------------------------

        if (
            not df_horarios.empty
            and aula in df_horarios.index
        ):

            datos_horario = df_horarios.loc[aula]

            fila["Grado"] = datos_horario["grado"]
            fila["Horario"] = datos_horario["horario"]
            fila["Auxiliar"] = datos_horario["auxiliar"]

        # ----------------------------------------------------
        # HORAS DE REPOSICIÓN DEL SEGUNDO SEMESTRE
        # ----------------------------------------------------

        horas_segundo_semestre = 0

        if (
            not tabla_aprovechamiento.empty
            and aula in tabla_aprovechamiento.index
        ):

            datos_aprovechamiento = (
                tabla_aprovechamiento.loc[aula]
            )

            horas_segundo_semestre = pd.to_numeric(
                datos_aprovechamiento[
                    "Horas de reposición segundo semestre"
                ],
                errors="coerce"
            )

            if pd.isna(horas_segundo_semestre):
                horas_segundo_semestre = 0

        fila["Horas de reposición segundo semestre"] = (
            float(horas_segundo_semestre)
        )

        # ----------------------------------------------------
        # SESIONES Y TOTAL DE HORAS EJECUTADAS
        # ----------------------------------------------------

        total_horas_ejecutadas = 0

        # Preparar las sesiones del aula una sola vez
        sesiones_aula = (
            grupo_df
            .drop_duplicates(subset=["sesion"], keep="first")
            .set_index("sesion")
        )

        for sesion in range(1, max_sesion + 1):

            if sesion not in sesiones_aula.index:
                fila[f"Sesión {sesion}"] = "—"
                continue

            registro = sesiones_aula.loc[sesion]

            # FECHA
            fecha = registro["fecha_reposicion"]

            if pd.notna(fecha):
                fecha = pd.to_datetime(
                    fecha,
                    errors="coerce"
                )

                fecha = (
                    fecha.strftime("%d/%m/%Y")
                    if pd.notna(fecha)
                    else "Sin fecha"
                )
            else:
                fecha = "Sin fecha"

            # HORAS
            horas = registro["horas"]

            if pd.isna(horas):
                horas = 0

            # ESTADO
            estado = registro["estado"]

            if estado == "Ejecutada":
                icono = "🟢"
            elif estado == "Programada":
                icono = "🟡"
            elif estado == "Cancelada":
                icono = "🔴"
            else:
                icono = "⚪"

            # TUTOR
            tutor = registro["tutor"]

            if pd.isna(tutor):
                tutor = "Sin tutor"

            # TOTAL DE HORAS EJECUTADAS
            if estado == "Ejecutada":
                total_horas_ejecutadas += float(horas)

            # CELDA DE SESIÓN
            fila[f"Sesión {sesion}"] = (
                f"{fecha} | {horas} h | "
                f"{icono} {estado} | {tutor}"
            )

        # ----------------------------------------------------
        # TOTALES
        # ----------------------------------------------------

        fila["Total horas ejecutadas"] = (
            total_horas_ejecutadas
        )

        fila["Horas de reposición por migrar"] = max(
            0,
            total_horas_ejecutadas
            - fila["Horas de reposición segundo semestre"]
        )

        filas.append(fila)

    # ========================================================
    # 6. ORGANIZAR COLUMNAS
    # ========================================================

    columnas_fijas = [
        "Aula",
        "IED",
        "Grado",
        "Grupo",
        "Horario"
    ]

    columnas_sesiones = [
        f"Sesión {sesion}"
        for sesion in range(1, max_sesion + 1)
    ]

    columnas_finales = columnas_fijas + columnas_sesiones + [
        "Total horas ejecutadas",
        "Horas de reposición segundo semestre",
        "Horas de reposición por migrar",
        "Auxiliar"
    ]

    return pd.DataFrame(
        filas,
        columns=columnas_finales
    )

##TABLA DE CANCELADAs

def crear_tabla_cancelaciones(df_filt):

    if df_filt.empty:
        return pd.DataFrame()

    df_canceladas = df_filt[
        df_filt["estado"] == "Cancelada"
    ].copy()

    if df_canceladas.empty:
        return pd.DataFrame()

    tabla = df_canceladas[
        [
            "ied",
            "grupo",
            "fecha_reposicion",
            "horas",
            "motivo_cancelacion"
        ]
    ].copy()

    # Renombrar columnas para presentación
    tabla = tabla.rename(
        columns={
            "ied": "IED",
            "grupo": "Grupo",
            "fecha_reposicion": "Fecha",
            "horas": "N° de horas",
            "motivo_cancelacion": "Motivo"
        }
    )

    # Formato de fecha
    tabla["Fecha"] = tabla["Fecha"].dt.strftime(
        "%d/%m/%Y"
    )

    # Orden
    tabla = tabla.sort_values(
        ["IED", "Grupo", "Fecha"]
    )

    return tabla.reset_index(drop=True)

#ACTUALIZAR NUMERO DE SESION

def actualizar_sesiones(df, ied, grupo, aula):

    df = df.copy()

    # Normalizar valores para comparar
    mask = (
        df["ied"].astype("string").str.strip()
        == str(ied).strip()
    ) & (
        pd.to_numeric(df["grupo"], errors="coerce")
        == pd.to_numeric(grupo, errors="coerce")
    ) & (
        pd.to_numeric(df["aula"], errors="coerce")
        == pd.to_numeric(aula, errors="coerce")
    )

    indices = (
        df.loc[mask]
        .sort_values(
            ["fecha_reposicion", "id_reposicion"]
        )
        .index
    )

    for numero_sesion, indice in enumerate(indices, start=1):
        df.loc[indice, "sesion"] = numero_sesion

    return df


#ELIMIANR REPOSICION
def eliminar_reposicion(df, id_reposicion):

    df = df[
        df["id_reposicion"] != id_reposicion
    ].copy()

    return df

## reportes migracion

def generar_reporte_migracion(df_reposiciones):
    df = df_reposiciones.copy()

    columna_horas = "Horas de reposición por migrar"

    df[columna_horas] = pd.to_numeric(
        df[columna_horas], errors="coerce"
    ).fillna(0)

    # Obtener grado desde el grupo
    df["grado_migracion"] = (
        df["Grupo"]
        .astype(str)
        .str[0]
        .map({"4": 4, "5": 5, "9": 9, "1": 10})
    )

    df_gk = df[
        df["grado_migracion"].isin([4, 5])
        & (df[columna_horas] > 0)
    ].copy()

    df_as = df[
        df["grado_migracion"].isin([9, 10])
        & (df[columna_horas] > 1)
    ].copy()

    def construir_texto(datos):
        lineas = []

        for ied, grupo_ied in datos.groupby("IED", sort=False):
            grupos = (
                grupo_ied["Grupo"]
                .drop_duplicates()
                .astype(str)
                .tolist()
            )

            auxiliares = (
                grupo_ied["Auxiliar"]
                .dropna()
                .astype(str)
                .drop_duplicates()
                .tolist()
            )

            horas_por_grupo = (
                grupo_ied.groupby("Grupo")[columna_horas]
                .sum()
            )

            detalle_horas = []

            for grupo, horas in horas_por_grupo.items():
                detalle_horas.append(
                    f"{horas:g} ({grupo})"
                )

            linea = (
                f"{ied}: {', '.join(grupos)} "
                f"({', '.join(auxiliares)}). "
                f"Horas por grupo: {', '.join(detalle_horas)}"
            )

            lineas.append(linea)

        return "\n".join(lineas)

    return (
        "GK:\n"
        + construir_texto(df_gk)
        + "\n\nAS:\n"
        + construir_texto(df_as)
    )

##