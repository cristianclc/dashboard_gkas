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

from src.db import (
    cargar_reposiciones,
    cargar_horarios,
    cargar_lt,
    cargar_tutores,
    crear_reposicion,
    actualizar_reposicion,
    eliminar_reposicion,
    marcar_ejecutadas
)

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

df_reposiciones = cargar_reposiciones()
df_horarios = cargar_horarios()
df_lt = cargar_lt()
df_tutores = cargar_tutores()



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
# CREAR REPOSICIÓN
# ============================================================

st.divider()
st.subheader("Crear reposición")

# --------------------------------
# 1. Seleccionar institución
# --------------------------------
instituciones_nuevas = sorted(
    df_horarios["ied"].dropna().unique().tolist()
)

ied_nueva = st.selectbox(
    "Institución",
    options=instituciones_nuevas,
    index=None,
    placeholder="Seleccione una institución",
    key="ied_nueva"
)

# --------------------------------
# 2. Seleccionar grupo, aula y horario
# --------------------------------
if ied_nueva:

    df_grupos_nuevos = df_horarios[
        df_horarios["ied"] == ied_nueva
    ].copy()

    # Eliminar únicamente duplicados de la misma aula y grupo
    df_grupos_nuevos = df_grupos_nuevos.drop_duplicates(
        subset=["ied", "grupo", "aula"]
    )

    # Crear opciones únicas por aula y grupo
    opciones_grupos = df_grupos_nuevos.to_dict("records")

else:
    df_grupos_nuevos = df_horarios.iloc[0:0]
    opciones_grupos = []

opcion_grupo_nueva = st.selectbox(
    "Grupo",
    options=opciones_grupos,
    index=None,
    placeholder="Seleccione un grupo",
    disabled=not ied_nueva,
    format_func=lambda fila: (
        f"Grupo {fila['grupo']} | "
        f"Aula {fila['aula']} | "
        f"{fila['horario']}"
    ),
    key="grupo_nuevo"
)

if opcion_grupo_nueva is not None:

    grupo_nuevo = opcion_grupo_nueva["grupo"]
    aula_nueva = opcion_grupo_nueva["aula"]
    horario_nuevo = opcion_grupo_nueva["horario"]

else:
    grupo_nuevo = None
    aula_nueva = None
    horario_nuevo = None

# --------------------------------
# 3. Mostrar aula y horario
# --------------------------------
aula_nueva = None
horario_nuevo = None

if opcion_grupo_nueva is not None:

    grupo_nuevo = opcion_grupo_nueva["grupo"]
    aula_nueva = opcion_grupo_nueva["aula"]
    horario_nuevo = opcion_grupo_nueva["horario"]

    col_aula, col_horario = st.columns(2)

    with col_aula:
        st.text_input(
            "Aula",
            value=str(aula_nueva),
            disabled=True
        )

    with col_horario:
        st.text_input(
            "Horario",
            value=str(horario_nuevo),
            disabled=True
        )
else:
    grupo_nuevo = None

# --------------------------------
# 4. Fecha y horas
# --------------------------------
col1, col2 = st.columns(2)

with col1:
    fecha_nueva = st.date_input(
        "Fecha de reposición",
        value=None
    )

with col2:
    horas_nuevas = st.number_input(
        "Horas",
        min_value=1,
        step=1,
        value=1
    )

# --------------------------------
# Seleccionar tutor (Tutores y LT)
# --------------------------------
tutores_disponibles = sorted(
    set(
        df_tutores["tutor"].dropna().tolist()
        + df_lt["lt"].dropna().tolist()
    )
)

tutor_nuevo = st.selectbox(
    "Tutor",
    options=tutores_disponibles,
    index=None,
    placeholder="Seleccione un tutor",
    key="tutor_nuevo"
)



# --------------------------------
# 5. Crear reposición
# --------------------------------
if st.button("Crear reposición", type="primary"):

    if ied_nueva is None:
        st.error("Debe seleccionar una institución.")

    elif grupo_nuevo is None:
        st.error("Debe seleccionar un grupo.")

    elif fecha_nueva is None:
        st.error("Debe seleccionar una fecha.")

    elif aula_nueva is None:
        st.error("No se encontró el aula asociada al grupo.")

    elif tutor_nuevo is None:
        st.error("Debe seleccionar el tutor encargado de la reposición.")

    else:

        # 1. Buscar AUXILIAR según IED y AULA
        auxiliar_nuevo = None

        auxiliar_aula = df_horarios.loc[
            (df_horarios["ied"] == ied_nueva) &
            (df_horarios["aula"] == aula_nueva),
            "auxiliar"
        ].dropna()

        if not auxiliar_aula.empty:
            auxiliar_nuevo = auxiliar_aula.iloc[0]

        # 2. Buscar LT según IED
        lt_nuevo = None

        lt_ied = df_lt.loc[
            df_lt["ied"].str.strip() == ied_nueva.strip(), "lt"
        ].dropna()

        if not lt_ied.empty:
            lt_nuevo = lt_ied.iloc[0]

        # 3. Mostrar información de la reposición
        st.write("Grupo:", grupo_nuevo)
        st.write("Aula:", aula_nueva)
        st.write("Horario:", horario_nuevo)
        st.write("Tutor:", tutor_nuevo)
        st.write("Auxiliar:", auxiliar_nuevo)
        st.write("LT:", lt_nuevo)

        print(repr(ied_nueva), type(ied_nueva), "IED NUEVA")
        print(df_lt["ied"].unique()[:10]) #BORRAR
        print(df_lt["ied"].apply(type).unique())


        # 4. Crear el registro en la base de datos
        crear_reposicion(
            ied=ied_nueva,
            grupo=grupo_nuevo,
            aula=aula_nueva,
            fecha=fecha_nueva,
            horas=horas_nuevas,
            tutor=tutor_nuevo
        )

        # 5. Confirmar y actualizar la interfaz
        st.success("La reposición fue creada correctamente.")
        st.rerun()

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

    # ========================================================
    # IDENTIFICAR LA TABLA QUE GENERÓ LA SELECCIÓN
    # ========================================================

    evento_celda = None
    df_seleccionado = None

    if evento_4_5 is not None:

        evento = getattr(evento_4_5, "event_data", None)

        if evento and evento.get("type") == "cellClicked":
            evento_celda = evento
            df_seleccionado = df_vista_4_5

    if evento_9_10 is not None:

        evento = getattr(evento_9_10, "event_data", None)

        if evento and evento.get("type") == "cellClicked":
            evento_celda = evento
            df_seleccionado = df_vista_9_10


    # ========================================================
    # PROCESAR LA SELECCIÓN
    # ========================================================

    if evento_celda is not None:

        # ----------------------------------------------------
        # OBTENER COLUMNA Y FILA SELECCIONADAS
        # ----------------------------------------------------

        nombre_columna = evento_celda.get(
            "column", {}
        ).get("colId")

        fila = evento_celda.get("data")

        # ----------------------------------------------------
        # VERIFICAR SI ES UNA SESIÓN
        # ----------------------------------------------------

        if (
            nombre_columna
            and nombre_columna.startswith("Sesión ")
            and fila is not None
        ):

            sesion_seleccionada_tabla = int(
                nombre_columna.replace("Sesión ", "")
            )

            # ------------------------------------------------
            # DATOS DEL AULA
            # ------------------------------------------------

            aula = fila["Aula"]
            ied = fila["IED"]
            grupo = fila["Grupo"]

            # ------------------------------------------------
            # BUSCAR LA REPOSICIÓN
            # ------------------------------------------------

            reposicion = df_reposiciones[
                (df_reposiciones["aula"] == aula)
                &
                (df_reposiciones["ied"] == ied)
                &
                (df_reposiciones["grupo"] == grupo)
                &
                (
                    df_reposiciones["sesion"]
                    == sesion_seleccionada_tabla
                )
            ]

            # ------------------------------------------------
            # GUARDAR REPOSICIÓN SELECCIONADA
            # ------------------------------------------------

            if not reposicion.empty:

                reposicion_seleccionada = reposicion.iloc[0]

    # ========================================================
    # FORMULARIO DE EDICIÓN
    # ========================================================

    if reposicion_seleccionada is not None:

        st.divider()
        st.subheader("Editar reposición")

        registro = reposicion_seleccionada

        st.caption(
            f"{registro['ied']} · "
            f"Grupo {registro['grupo']} · "
            f"Sesión {registro['sesion']}"
        )

        estados_disponibles = [
            "Programada",
            "Ejecutada",
            "Cancelada"
        ]

        estado_actual = registro["estado"]

        indice_estado = (
            estados_disponibles.index(estado_actual)
            if estado_actual in estados_disponibles
            else 0
        )

        nuevo_estado = st.selectbox(
            "Estado",
            estados_disponibles,
            index=indice_estado,
            key=f"estado_{registro['id_reposicion']}"
        )

        with st.form(
            f"form_editar_reposicion_{registro['id_reposicion']}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                st.text_input(
                    "Institución",
                    value=str(registro["ied"]),
                    disabled=True
                )

                st.text_input(
                    "Grupo",
                    value=str(registro["grupo"]),
                    disabled=True
                )

                st.number_input(
                    "Sesión",
                    min_value=1,
                    value=max(1, int(registro["sesion"]))
                    if pd.notna(registro["sesion"]) else 1,
                    disabled=True
                )

                # --------------------------------
                # Seleccionar tutor o LT
                # --------------------------------

            with col2:

                opciones_tutor = list(tutores_disponibles)

                tutor_actual = registro["tutor"]

                if (
                    pd.notna(tutor_actual)
                    and tutor_actual not in opciones_tutor
                ):
                    opciones_tutor.append(tutor_actual)

                indice_tutor = (
                    opciones_tutor.index(tutor_actual)
                    if tutor_actual in opciones_tutor
                    else None
                )

                nuevo_tutor = st.selectbox(
                    "Tutor",
                    options=opciones_tutor,
                    index=indice_tutor,
                    placeholder="Seleccione un tutor o LT"
                )

            with col2:

                nueva_fecha = st.date_input(
                    "Fecha de reposición",
                    value=registro["fecha_reposicion"].date()
                )

                nuevas_horas = st.number_input(
                    "Horas",
                    min_value=1,
                    value=int(registro["horas"])
                    if pd.notna(registro["horas"]) else 1,
                    step=1
                )

            if nuevo_estado == "Cancelada":

                nuevo_motivo = st.text_input(
                    "Motivo de cancelación",
                    value=registro["motivo_cancelacion"]
                    if pd.notna(registro["motivo_cancelacion"])
                    else "",
                    placeholder="Escriba el motivo de cancelación..."
                )

            else:
                nuevo_motivo = None

            guardar = st.form_submit_button(
                "Guardar cambios",
                type="primary"
            )

            if guardar:

                actualizar_reposicion(
                    id_reposicion=registro["id_reposicion"],
                    fecha=nueva_fecha,
                    horas=nuevas_horas,
                    estado=nuevo_estado,
                    motivo=nuevo_motivo,
                    tutor=nuevo_tutor
                )

                st.success(
                    "La reposición fue actualizada correctamente."
                )

                st.rerun()

        # ========================================================
        # BORRAR REPOSICIÓN
        # ========================================================

        id_reposicion = registro["id_reposicion"]

        if st.button(
            "Borrar reposición",
            key=f"borrar_{id_reposicion}",
            type="secondary",
            use_container_width=True
        ):
            st.session_state[f"confirmar_borrado_{id_reposicion}"] = True

        if st.session_state.get(f"confirmar_borrado_{id_reposicion}", False):

            st.warning(
                "¿Estás seguro de que deseas borrar esta reposición? "
                "Esta acción no se puede deshacer."
            )

            col_confirmar, col_cancelar = st.columns(2)

            with col_confirmar:
                if st.button(
                    "Sí, borrar",
                    key=f"confirmar_{id_reposicion}",
                    type="primary",
                    use_container_width=True
                ):
                    eliminar_reposicion(id_reposicion)

                    st.session_state.pop(
                        f"confirmar_borrado_{id_reposicion}",
                        None
                    )

                    st.rerun()

            with col_cancelar:
                if st.button(
                    "Cancelar",
                    key=f"cancelar_{id_reposicion}",
                    use_container_width=True
                ):
                    st.session_state.pop(
                        f"confirmar_borrado_{id_reposicion}",
                        None
                    )
                    st.rerun()

# ============================================================
# ACTUALIZACIÓN SEMANAL DE REPORTES
# ============================================================

st.subheader("Actualización masiva de reposiciones")

fecha_limite = st.date_input(
    "Cambiar a ejecutadas las reposiciones programadas hasta:",
    value=None,
    key="fecha_limite_ejecucion",
)

if fecha_limite:
    df = df_reposiciones

    fechas = pd.to_datetime(
        df["fecha_reposicion"],
        errors="coerce"
    ).dt.date

    mascara = (
        (df["estado"] == "Programada")
        & (fechas <= fecha_limite)
    )

    cantidad = int(mascara.sum())
    horas = df.loc[mascara, "horas"].sum()

    st.write(f"Reposiciones por actualizar: **{cantidad}**")
    st.write(f"Horas involucradas: **{horas}**")

    if cantidad > 0:
        if st.button("Confirmar actualización masiva"):
            marcar_ejecutadas(
                df.loc[mascara, "id_reposicion"].tolist()
            )

            st.success(
                f"Se actualizaron {cantidad} reposiciones."
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
