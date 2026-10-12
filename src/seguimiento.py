"""Lectura del seguimiento de avance desde un Google Sheet con cuatro pestañas (solo lectura).

Un solo Google Sheet con una pestaña por grado: "GK Grado 4", "GK Grado 5",
"AS Grado 9" y "AS Grado 10". Se descarga completo como .xlsx (sirve si está
compartido como "Cualquiera con el enlace: Lector") y se leen esas cuatro pestañas.

Configuración (variable de entorno o .env): el ID del Google Sheet, que es el
texto entre /d/ y /edit en su URL.
    SEGUIMIENTO_SHEET_ID
"""
import os
import unicodedata
from io import BytesIO

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

CLAVE_SESION = "_captura_seguimiento"

# nombre de la pestaña -> grado
PESTANAS = {
    "GK Grado 4": 4,
    "GK Grado 5": 5,
    "AS Grado 9": 9,
    "AS Grado 10": 10,
}

# Columnas que se leen (encabezado normalizado -> nombre final).
# "aula z" es un error de escritura que existe en una de las hojas.
COLUMNAS = {
    "aula": "aula",
    "aula z": "aula",
    "tutor": "tutor",
    "ied": "ied",
    "grupo": "grupo",
    "avance p1": "avance_p1",
    "avance p2": "avance_p2",
    "avance p3": "avance_p3",
    "avance p4": "avance_p4",
}

# Hay 4 columnas con este encabezado en cada pestaña: la 1.ª es del P1, la 2.ª del P2...
COMENTARIO = "comentarios de cancelacion / ajuste de clases (dd/mm)"
COMENTARIOS = ["comentario_p1", "comentario_p2", "comentario_p3", "comentario_p4"]

# Nombres con los que se muestran las columnas
NOMBRES_FINALES = {
    "grado": "Grado", "aula": "Aula", "tutor": "Tutor", "ied": "IED", "grupo": "Grupo",
    **{f"comentario_p{n}": f"Comentarios P{n}" for n in range(1, 5)},
    **{f"avance_p{n}": f"Avance P{n}" for n in range(1, 5)},
}

OBLIGATORIAS = ["aula", "tutor", "ied", "grupo"]
SALIDA = (
    ["grado"]
    + ["aula", "tutor", "ied", "grupo"]
    + ["avance_p1", "avance_p2", "avance_p3", "avance_p4"]
    + COMENTARIOS
)


def _normalizar(texto):
    if pd.isna(texto):
        return ""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(texto.lower().split())


def _descargar(sheet_id):
    """Descarga el Google Sheet completo como .xlsx (bytes)."""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    respuesta = requests.get(url, timeout=(15, 120))
    respuesta.raise_for_status()
    if not respuesta.content.startswith(b"PK"):  # un .xlsx es un zip
        raise RuntimeError(
            "El Google Sheet no se pudo descargar como Excel. "
            "Revisa el ID y que esté compartido como 'Cualquiera con el enlace: Lector'."
        )
    return respuesta.content


def _leer_pestana(bruta, grado, nombre_pestana):
    """Devuelve el DataFrame de una pestaña, o None si no tiene las columnas."""
    # La fila de encabezados es la primera (entre las 15 primeras) que trae Aula e IED
    fila_encabezado = None
    for i in range(min(15, len(bruta))):
        celdas = {_normalizar(v) for v in bruta.iloc[i].tolist()}
        if "ied" in celdas and ({"aula", "aula z"} & celdas):
            fila_encabezado = i
            break
    if fila_encabezado is None:
        return None

    encabezados = [_normalizar(v) for v in bruta.iloc[fila_encabezado].tolist()]
    datos = bruta.iloc[fila_encabezado + 1:]

    columnas = {}   # nombre final -> posición
    n_comentario = 0
    for pos, encabezado in enumerate(encabezados):
        if encabezado == COMENTARIO and n_comentario < len(COMENTARIOS):
            columnas[COMENTARIOS[n_comentario]] = pos
            n_comentario += 1
        elif encabezado in COLUMNAS and COLUMNAS[encabezado] not in columnas:
            columnas[COLUMNAS[encabezado]] = pos

    if any(c not in columnas for c in OBLIGATORIAS):
        return None

    df = pd.DataFrame({nombre: datos.iloc[:, pos].to_numpy() for nombre, pos in columnas.items()})
    for nombre in SALIDA:
        if nombre not in df.columns and nombre != "grado":
            df[nombre] = pd.NA

    # Filas sin ningún dato de identificación
    df = df.dropna(subset=OBLIGATORIAS, how="all")

    for c in ["tutor", "ied", "grupo"] + COMENTARIOS:
        df[c] = df[c].astype("string").str.strip().replace("", pd.NA)
    df["aula"] = pd.to_numeric(df["aula"], errors="coerce").astype("Int64")
    df = df[df["aula"].notna() | df["ied"].notna()]

    for c in ["avance_p1", "avance_p2", "avance_p3", "avance_p4"]:
        df[c] = _a_numero(df[c])

    df.insert(0, "grado", grado)
    return df[SALIDA].rename(columns=NOMBRES_FINALES).reset_index(drop=True)


def _a_numero(serie):
    """Números tal cual vienen; textos como '50%' pasan a 0.5 (igual que en Excel)."""
    texto = serie.astype("string").str.strip()
    con_porcentaje = texto.str.endswith("%", na=False)
    limpio = texto.str.rstrip("%").str.replace(",", ".", regex=False)
    numero = pd.to_numeric(limpio, errors="coerce").astype("Float64")
    return numero.where(~con_porcentaje, numero)


def _construir(contenido=None):
    """`contenido` (opcional): bytes del .xlsx para pruebas."""
    if contenido is None:
        sheet_id = os.getenv("SEGUIMIENTO_SHEET_ID")
        if not sheet_id:
            raise RuntimeError("Falta la variable SEGUIMIENTO_SHEET_ID (ID del Google Sheet).")
        contenido = _descargar(sheet_id)

    hojas = pd.read_excel(BytesIO(contenido), sheet_name=None, header=None, engine="openpyxl")
    por_nombre = {_normalizar(nombre): nombre for nombre in hojas}

    tablas, resumen = [], []
    for pestana, grado in PESTANAS.items():
        real = por_nombre.get(_normalizar(pestana))
        if real is None:
            raise RuntimeError(
                f"No se encontró la pestaña '{pestana}'. Pestañas del Sheet: {list(hojas)}"
            )
        df = _leer_pestana(hojas[real], grado, real)
        if df is None:
            raise RuntimeError(
                f"La pestaña '{real}' no tiene las columnas Aula, Tutor, IED y Grupo."
            )
        tablas.append(df)
        resumen.append({"pestaña": real, "grado": grado, "filas": len(df)})

    return pd.concat(tablas, ignore_index=True), pd.DataFrame(resumen)


def cargar_seguimiento():
    """(tabla, resumen) de la sesión; solo descarga el Sheet la primera vez."""
    if CLAVE_SESION not in st.session_state:
        st.session_state[CLAVE_SESION] = _construir()
    tabla, resumen = st.session_state[CLAVE_SESION]
    return tabla.copy(), resumen.copy()


def recargar_seguimiento():
    st.session_state.pop(CLAVE_SESION, None)