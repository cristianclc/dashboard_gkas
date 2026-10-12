"""Copia (snapshot) de los datos de Metabase guardada en la base de datos.

Un proceso aparte (scripts/actualizar_snapshot.py, programado cada hora en Railway)
descarga y transforma los datos y los guarda aquí. La app solo lee esta copia,
por lo que abre al instante aunque Metabase tarde.
Cada DataFrame se guarda como parquet en una tabla propia (no se mezcla con las
tablas de reposiciones/horarios, así que cargar_excel_a_db.py no la borra).
"""
import io
import json
import time

import pandas as pd
import pyarrow as pa
from sqlalchemy import Column, Float, LargeBinary, MetaData, Table, Text, delete, insert, select

from src.db import get_engine

_metadata = MetaData()

snapshots = Table(
    "snapshots", _metadata,
    Column("nombre", Text, primary_key=True),
    Column("contenido", LargeBinary, nullable=False),
    Column("actualizado_en", Float, nullable=False),
)

META = "_meta"  # semana consultada, avisos, etc. en JSON


def _a_parquet(df):
    """DataFrame -> bytes. Las columnas de tipos mezclados se pasan a texto."""
    df = df.copy()
    for col in df.columns[df.dtypes == object]:
        try:
            pa.array(df[col])
        except (pa.ArrowInvalid, pa.ArrowTypeError):
            df[col] = df[col].where(df[col].isna(), df[col].astype(str))
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    return buffer.getvalue()


def _de_parquet(contenido):
    return pd.read_parquet(io.BytesIO(contenido))


def guardar_snapshot(datos):
    """Reemplaza la copia completa en una sola transacción (nadie ve datos a medias)."""
    ahora = time.time()
    meta = {}
    filas = []

    for nombre, valor in datos.items():
        if isinstance(valor, pd.DataFrame):
            filas.append({"nombre": nombre, "contenido": _a_parquet(valor), "actualizado_en": ahora})
        else:
            meta[nombre] = valor

    filas.append({
        "nombre": META,
        "contenido": json.dumps(meta, default=str).encode("utf-8"),
        "actualizado_en": ahora,
    })

    engine = get_engine()
    _metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(delete(snapshots))
        conn.execute(insert(snapshots), filas)
    return ahora


def fecha_snapshot():
    """Marca de tiempo de la última copia (consulta liviana), o None si no hay."""
    engine = get_engine()
    _metadata.create_all(engine)
    with engine.connect() as conn:
        return conn.execute(
            select(snapshots.c.actualizado_en).where(snapshots.c.nombre == META)
        ).scalar()


def leer_snapshot():
    """Devuelve el mismo diccionario que preparar_datos() más 'actualizado_en'."""
    engine = get_engine()
    _metadata.create_all(engine)
    with engine.connect() as conn:
        filas = conn.execute(
            select(snapshots.c.nombre, snapshots.c.contenido, snapshots.c.actualizado_en)
        ).all()

    if not filas:
        return None

    datos = {}
    for nombre, contenido, actualizado_en in filas:
        if nombre == META:
            datos.update(json.loads(bytes(contenido).decode("utf-8")))
            datos["actualizado_en"] = actualizado_en
        else:
            datos[nombre] = _de_parquet(bytes(contenido))
    return datos
