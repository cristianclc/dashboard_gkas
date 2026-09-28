"""Conexión con Metabase y descarga de resultados de preguntas guardadas."""
from __future__ import annotations

import os
from io import BytesIO
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv(
    "METABASE_URL", "https://glocalkids-reportes.uninorte.edu.co"
).rstrip("/")
USERNAME = os.getenv("METABASE_USERNAME")
PASSWORD = os.getenv("METABASE_PASSWORD")

# ID de pregunta -> nombre lógico que utiliza el tablero.
CONSULTAS = {
    "df": 51,
    "df_gk": 53,
    "df_as": 54,
    "df_ret": 55,
    "df_k2k": 56,
    "df_k2k_complementario": 57,
}


class MetabaseError(RuntimeError):
    """Error de autenticación o descarga desde Metabase."""


def _crear_sesion() -> requests.Session:
    if not USERNAME or not PASSWORD:
        raise MetabaseError(
            "Faltan METABASE_USERNAME o METABASE_PASSWORD en las variables de entorno."
        )

    session = requests.Session()
    session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})

    try:
        response = session.post(
            f"{BASE_URL}/api/session",
            json={"username": USERNAME, "password": PASSWORD},
            timeout=30,
        )
        response.raise_for_status()
        token = response.json().get("id")
        if not token:
            raise MetabaseError("Metabase no devolvió un token de sesión.")
        session.headers.update({"X-Metabase-Session": token})
        return session
    except requests.RequestException as exc:
        session.close()
        raise MetabaseError(
            "No fue posible iniciar sesión en Metabase. Verifica la URL, las credenciales "
            "y que el método de autenticación permita acceso por API."
        ) from exc


def _descargar_xlsx(
    session: requests.Session,
    card_id: int,
    semana: int | None = None,
) -> pd.DataFrame:
    payload: dict[str, Any] = {}
    if semana is not None:
        payload["parameters"] = [
            {
                "type": "text",
                "target": ["variable", ["template-tag", "SEMANA"]],
                "value": str(semana),
            }
        ]

    try:
        response = session.post(
            f"{BASE_URL}/api/card/{card_id}/query/xlsx",
            json=payload,
            timeout=(30, 300),
        )
        if not response.ok:
            detalle = response.text[:1000]
            raise MetabaseError(
                f"Error descargando la pregunta {card_id} (HTTP {response.status_code}). "
                f"Respuesta de Metabase: {detalle}"
            )
        return pd.read_excel(BytesIO(response.content), engine="openpyxl")
    except requests.RequestException as exc:
        raise MetabaseError(f"No se pudo descargar la pregunta {card_id}.") from exc
    except Exception as exc:
        if isinstance(exc, MetabaseError):
            raise
        raise MetabaseError(
            f"La respuesta de la pregunta {card_id} no pudo leerse como Excel. "
            "Comprueba el formato de exportación y los parámetros."
        ) from exc


def cargar_datos_crudos(semana: int | None = None) -> dict[str, pd.DataFrame]:
    """Descarga las preguntas; si semana=None, la deduce de la pregunta 51."""
    session = _crear_sesion()
    try:
        # La consulta 51 se obtiene primero para calcular la semana por defecto.
        df = _descargar_xlsx(session, CONSULTAS["df"])

        if semana is None:
            if "Semana Del Proyecto" not in df.columns:
                raise MetabaseError(
                    "La consulta 51 no contiene la columna 'Semana Del Proyecto'. "
                    f"Columnas recibidas: {list(df.columns)}"
                )
            semanas = pd.to_numeric(df["Semana Del Proyecto"], errors="coerce").dropna()
            if semanas.empty:
                raise MetabaseError(
                    "No se encontró una semana válida en 'Semana Del Proyecto' de la consulta 51."
                )
            semana = int(semanas.max()) - 1

        datos = {"df": df}
        for clave in ("df_gk", "df_as", "df_ret"):
            datos[clave] = _descargar_xlsx(session, CONSULTAS[clave])

        datos["df_k2k"] = _descargar_xlsx(
            session, CONSULTAS["df_k2k"], semana=semana
        )
        # La consulta 07 es complementaria; si falla, no interrumpe la carga principal.
        try:
            datos["df_k2k_complementario"] = _descargar_xlsx(
                session, CONSULTAS["df_k2k_complementario"], semana=semana
            )
        except MetabaseError as exc:
            datos["df_k2k_complementario"] = pd.DataFrame()
            datos["_aviso_07"] = pd.DataFrame({"aviso": [str(exc)]})

        datos["_semana_consultada"] = pd.DataFrame({"semana": [semana]})
        return datos
    finally:
        session.close()
