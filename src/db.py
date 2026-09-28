"""Acceso a la base de datos de reposiciones (PostgreSQL en Railway, SQLite en local)."""
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import (
    Column, Date, Float, Integer, MetaData, Table, Text,
    create_engine, delete, insert, text, update,
)

load_dotenv()

metadata = MetaData()

lead_teachers = Table(
    "lead_teachers", metadata,
    Column("ied", Text, primary_key=True),
    Column("lt", Text),
)

horarios_sedes = Table(
    "horarios_sedes", metadata,
    Column("aula", Integer, primary_key=True),
    Column("ied", Text, nullable=False),
    Column("grupo", Text),
    Column("grado", Integer),
    Column("horario", Text),
    Column("auxiliar", Text),
)

tutores = Table(
    "tutores", metadata,
    Column("tutor", Text, primary_key=True),
)

reposiciones = Table(
    "reposiciones", metadata,
    Column("id_reposicion", Integer, primary_key=True, autoincrement=True),
    Column("aula", Integer),
    Column("ied", Text, nullable=False),
    Column("grupo", Text, nullable=False),
    Column("fecha_reposicion", Date),
    Column("horas", Float),
    Column("estado", Text),
    Column("tutor", Text),
    Column("motivo_cancelacion", Text),
)

_engine = None


def get_engine():
    """Engine único por proceso. Sin DATABASE_URL usa un SQLite local."""
    global _engine
    if _engine is None:
        url = os.getenv("DATABASE_URL", "sqlite:///datos/reposiciones.db")
        # Railway entrega postgres:// o postgresql://; SQLAlchemy necesita el driver.
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def crear_tablas():
    metadata.create_all(get_engine())


# ============================================================
# LECTURA (con caché; se invalida al escribir)
# ============================================================

_SQL_REPOSICIONES = """
SELECT
    r.id_reposicion, r.aula, r.ied, r.grupo,
    ROW_NUMBER() OVER (
        PARTITION BY r.ied, r.grupo, r.aula
        ORDER BY r.fecha_reposicion, r.id_reposicion
    ) AS sesion,
    r.fecha_reposicion, r.horas, r.estado, r.tutor, r.motivo_cancelacion,
    h.horario, h.auxiliar, l.lt
FROM reposiciones r
LEFT JOIN horarios_sedes h ON h.aula = r.aula
LEFT JOIN lead_teachers  l ON l.ied  = r.ied
ORDER BY r.aula, r.fecha_reposicion, r.id_reposicion
"""


@st.cache_data
def cargar_reposiciones():
    df = pd.read_sql(text(_SQL_REPOSICIONES), get_engine())
    df["fecha_reposicion"] = pd.to_datetime(df["fecha_reposicion"], errors="coerce")
    return df


@st.cache_data
def cargar_horarios():
    return pd.read_sql(text("SELECT ied, aula, grupo, grado, horario, auxiliar FROM horarios_sedes"), get_engine())


@st.cache_data
def cargar_lt():
    return pd.read_sql(text("SELECT ied, lt FROM lead_teachers"), get_engine())


@st.cache_data
def cargar_tutores():
    return pd.read_sql(text("SELECT tutor FROM tutores"), get_engine())


# ============================================================
# ESCRITURA
# ============================================================

def _py(valor):
    """Convierte NaN/NaT/numpy a tipos nativos que aceptan los drivers."""
    if valor is None or pd.isna(valor):
        return None
    return valor.item() if hasattr(valor, "item") else valor


def _fecha(valor):
    valor = _py(valor)
    return pd.Timestamp(valor).date() if valor is not None else None


def crear_reposicion(ied, grupo, aula, fecha, horas, tutor):
    """Inserta una reposición 'Programada' y devuelve su id."""
    with get_engine().begin() as conn:
        resultado = conn.execute(
            insert(reposiciones).values(
                aula=_py(aula), ied=ied, grupo=str(grupo),
                fecha_reposicion=_fecha(fecha), horas=_py(horas),
                estado="Programada", tutor=_py(tutor), motivo_cancelacion=None,
            )
        )
        nuevo_id = resultado.inserted_primary_key[0]
    cargar_reposiciones.clear()
    return nuevo_id


def actualizar_reposicion(id_reposicion, fecha, horas, estado, motivo, tutor):
    with get_engine().begin() as conn:
        conn.execute(
            update(reposiciones)
            .where(reposiciones.c.id_reposicion == int(id_reposicion))
            .values(
                fecha_reposicion=_fecha(fecha), horas=_py(horas),
                estado=estado, motivo_cancelacion=_py(motivo), tutor=_py(tutor),
            )
        )
    cargar_reposiciones.clear()


def eliminar_reposicion(id_reposicion):
    with get_engine().begin() as conn:
        conn.execute(
            delete(reposiciones).where(reposiciones.c.id_reposicion == int(id_reposicion))
        )
    cargar_reposiciones.clear()


def marcar_ejecutadas(ids):
    """Pasa a 'Ejecutada' las reposiciones 'Programada' con esos ids."""
    ids = [int(i) for i in ids]
    if not ids:
        return
    with get_engine().begin() as conn:
        conn.execute(
            update(reposiciones)
            .where(reposiciones.c.id_reposicion.in_(ids))
            .where(reposiciones.c.estado == "Programada")
            .values(estado="Ejecutada")
        )
    cargar_reposiciones.clear()
