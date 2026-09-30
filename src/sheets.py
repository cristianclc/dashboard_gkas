"""Lectura de las reposiciones desde Google Sheets (solo lectura).

Lee las hojas "Reposiciones canceladas GK" y "Reposiciones canceladas AS"
(columnas B a K, encabezados en la fila 1) y las une en una sola tabla.
La hoja debe estar compartida como "Cualquiera con el enlace: lector".

Configuración (variable de entorno o .env):
    REPOSICIONES_SHEET_ID -> el texto entre /d/ y /edit en la URL de la hoja

Los datos se capturan una vez al abrir el dashboard (por sesión) y quedan
guardados en st.session_state; recargar_reposiciones() fuerza una nueva captura.
"""
import os
from urllib.parse import quote

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.db import cargar_horarios, cargar_lt

load_dotenv()

CLAVE_SESION = "_captura_reposiciones"

HOJAS = ["Reposiciones canceladas GK", "Reposiciones canceladas AS"]

# Columnas B a K de la hoja, en orden (la A se ignora)
COLUMNAS_HOJA = [
    "sesion", "aula", "ied", "grupo", "fecha_reposicion",
    "horas", "estado", "tutor", "lt", "motivo_cancelacion",
]

ESTADOS_VALIDOS = ["Cancelada", "Ejecutada", "Programada"]


def _url_hoja(nombre):
    hoja = os.getenv("REPOSICIONES_SHEET_ID")
    if not hoja:
        raise RuntimeError("Falta la variable REPOSICIONES_SHEET_ID (id de la hoja de Google Sheets).")
    return (
        f"https://docs.google.com/spreadsheets/d/{hoja}/gviz/tq"
        f"?tqx=out:csv&sheet={quote(nombre)}"
    )


def _leer_hoja(nombre, origen=None):
    """Lee una pestaña (columnas B a K) y la deja con los nombres del dashboard.
    `origen` permite probar con un archivo local."""
    df = pd.read_csv(origen or _url_hoja(nombre), dtype=str)

    if df.shape[1] < 11:
        raise ValueError(f"La hoja '{nombre}' tiene {df.shape[1]} columnas; se esperaban al menos 11 (A a K).")

    df = df.iloc[:, 1:11].copy()
    df.columns = COLUMNAS_HOJA

    for c in ["ied", "grupo", "estado", "tutor", "lt", "motivo_cancelacion"]:
        df[c] = df[c].astype("string").str.strip().replace("", pd.NA)

    # Solo los estados válidos, sin importar mayúsculas
    estado = df["estado"].str.capitalize()
    df = df[estado.isin(ESTADOS_VALIDOS)].copy()
    df["estado"] = estado[df.index]

    df["sesion"] = pd.to_numeric(df["sesion"], errors="coerce").astype("Int64")
    df["aula"] = pd.to_numeric(df["aula"], errors="coerce").astype("Int64")
    df["horas"] = pd.to_numeric(df["horas"].str.replace(",", ".", regex=False), errors="coerce")
    df["fecha_reposicion"] = pd.to_datetime(df["fecha_reposicion"], errors="coerce", dayfirst=True)

    return df.reset_index(drop=True)


def _construir_reposiciones(origenes=None):
    """`origenes` (opcional): {nombre_hoja: archivo_local} para pruebas."""
    origenes = origenes or {}
    df = pd.concat(
        [_leer_hoja(h, origenes.get(h)) for h in HOJAS], ignore_index=True
    )
    df["id_reposicion"] = range(1, len(df) + 1)

    horarios = cargar_horarios()[["aula", "horario", "auxiliar"]].drop_duplicates("aula")
    df = df.merge(horarios, on="aula", how="left")

    # LT: el de la hoja; si viene vacío, el de la tabla de lead teachers
    lt_db = cargar_lt().assign(ied=lambda d: d["ied"].str.strip()).drop_duplicates("ied")
    df = df.merge(lt_db.rename(columns={"lt": "lt_db"}), on="ied", how="left")
    df["lt"] = df["lt"].fillna(df["lt_db"])

    df = df.sort_values(["aula", "fecha_reposicion", "id_reposicion"], kind="stable")

    return df[[
        "id_reposicion", "aula", "ied", "grupo", "sesion", "fecha_reposicion",
        "horas", "estado", "tutor", "motivo_cancelacion", "horario", "auxiliar", "lt",
    ]].reset_index(drop=True)


def cargar_reposiciones():
    """Devuelve la captura de la sesión; solo lee la hoja la primera vez."""
    if CLAVE_SESION not in st.session_state:
        st.session_state[CLAVE_SESION] = _construir_reposiciones()
    return st.session_state[CLAVE_SESION].copy()


def recargar_reposiciones():
    """Descarta la captura para que la próxima lectura vuelva a la hoja."""
    st.session_state.pop(CLAVE_SESION, None)