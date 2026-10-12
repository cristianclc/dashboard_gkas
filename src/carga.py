"""Lectura de los datos de Metabase desde la copia guardada en la base de datos.

- asegurar_datos(): se llama al inicio de cada página; deja los datos en
  st.session_state["datos"] / ["tabla_aprovechamiento"] y vigila si hay una copia nueva.
- boton_actualizar(): vuelve a leer la copia (y la hoja de reposiciones) de inmediato.
- texto_actualizacion(datos): línea informativa con la fecha de la copia.
"""
import time

import streamlit as st

from src.sheets import CLAVE_SESION
from src.snapshot import fecha_snapshot, leer_snapshot

REVISION_SEGUNDOS = 5 * 60  # cada cuánto una página abierta revisa si hay datos nuevos


@st.cache_data(max_entries=2, show_spinner="Cargando datos...")
def _cargar(version):
    """`version` (fecha de la copia) es la llave: solo se vuelve a leer si cambió."""
    return leer_snapshot()


@st.fragment(run_every=REVISION_SEGUNDOS)
def _vigilar_cambios():
    if fecha_snapshot() != st.session_state.get("_version_datos"):
        st.session_state.pop(CLAVE_SESION, None)  # también recarga la hoja de reposiciones
        st.rerun()


def asegurar_datos():
    """Deja los datos en session_state; detiene la página si aún no hay copia."""
    try:
        version = fecha_snapshot()
    except Exception as exc:
        st.error(f"No se pudo consultar la base de datos: {exc}")
        st.stop()

    if version is None:
        st.warning(
            "Todavía no hay datos de Metabase guardados. "
            "Ejecuta scripts/actualizar_snapshot.py (o espera a la próxima tarea programada)."
        )
        st.stop()

    datos = _cargar(version)
    st.session_state["datos"] = datos
    st.session_state["tabla_aprovechamiento"] = datos["tabla_aprovechamiento"]
    st.session_state["_version_datos"] = version

    _vigilar_cambios()
    return datos


def texto_actualizacion(datos):
    hora = time.strftime("%d/%m/%Y %H:%M", time.localtime(datos["actualizado_en"]))
    return (
        f"Datos de Metabase actualizados el {hora} "
        f"(se renuevan solos cada hora). "
        f"Semana K2K consultada: {datos.get('semana_consultada', 'N/D')}."
    )


def boton_actualizar(clave="actualizar_ahora"):
    if st.button("Volver a leer los datos", key=clave):
        _cargar.clear()
        st.session_state.pop(CLAVE_SESION, None)
        st.rerun()
