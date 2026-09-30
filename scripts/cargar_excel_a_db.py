"""Carga única del Excel de reposiciones a la base de datos.

Uso (desde la raíz del proyecto):
    python scripts/cargar_excel_a_db.py --reset

--reset borra y recrea las tablas antes de cargar (evita duplicar datos).
"""
import argparse
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.db import (  # noqa: E402
    crear_tablas, get_engine, metadata,
    horarios_sedes, lead_teachers, reposiciones, tutores,
)

RUTA_EXCEL = Path(__file__).resolve().parents[1] / "datos" / "reposiciones.xlsx"
url = os.getenv("DATABASE_URL", "sqlite:///datos/reposiciones.db")

def texto(serie):
    """Texto limpio; 401.0 -> '401'."""
    return (
        serie.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
    )


def main(reset):
    if not reset:
        sys.exit("Agrega --reset para confirmar que se borren y recreen las tablas.")

    hojas = pd.read_excel(RUTA_EXCEL, sheet_name=None)

    # --- Lead teachers
    lt = hojas["LT"].rename(columns={"IED": "ied", "LEAD TEACHER": "lt"})
    lt["ied"] = texto(lt["ied"])
    lt = lt.dropna(subset=["ied"]).drop_duplicates(subset=["ied"])[["ied", "lt"]]

    # --- Horarios
    h = hojas["Horarios_sedes"].rename(columns={
        "IED": "ied", "AULA": "aula", "GRUPO": "grupo",
        "GRADO": "grado", "HORARIO": "horario", "AUXILIAR": "auxiliar",
    })
    h["ied"] = texto(h["ied"])
    h["aula"] = pd.to_numeric(h["aula"], errors="coerce")
    h["grado"] = pd.to_numeric(h["grado"], errors="coerce")
    h["grupo"] = texto(h["grupo"])
    antes = len(h)
    h = h.dropna(subset=["aula"]).drop_duplicates(subset=["aula"])
    h["aula"] = h["aula"].astype(int)
    h = h[["aula", "ied", "grupo", "grado", "horario", "auxiliar"]]
    if len(h) < antes:
        print(f"Aviso: horarios_sedes descartó {antes - len(h)} filas (aula vacía o repetida).")

    # --- Tutores
    t = hojas["Tutores"].rename(columns={"TUTOR": "tutor"})
    t["tutor"] = texto(t["tutor"])
    t = t.dropna(subset=["tutor"]).drop_duplicates(subset=["tutor"])[["tutor"]]

    # --- Reposiciones (horario, auxiliar, lt y sesion se calculan al leer)
    r = hojas["Reposiciones"].rename(columns={
        "AULA": "aula", "IED": "ied", "GRUPO": "grupo",
        "FECHA REPO": "fecha_reposicion", "HORAS": "horas",
        "ESTADO": "estado", "TUTOR": "tutor",
        "MOTIVO DE CANCELACIÓN": "motivo_cancelacion",
    })
    r["ied"] = texto(r["ied"])
    r["grupo"] = texto(r["grupo"])
    r["aula"] = pd.to_numeric(r["aula"], errors="coerce").astype("Int64")
    r["fecha_reposicion"] = pd.to_datetime(
        r["fecha_reposicion"], dayfirst=True, errors="coerce"
    ).dt.date
    r["horas"] = pd.to_numeric(r["horas"], errors="coerce")
    r = r.sort_values(["aula", "fecha_reposicion"])[
        ["aula", "ied", "grupo", "fecha_reposicion", "horas",
        "estado", "tutor", "motivo_cancelacion"]
    ]
    r = r.astype(object).where(r.notna(), None)  # NaN/NA/NaT -> NULL

    engine = get_engine()
    metadata.drop_all(engine)
    crear_tablas()

    with engine.begin() as conn:
        conn.execute(lead_teachers.insert(), lt.to_dict("records"))
        conn.execute(horarios_sedes.insert(), h.astype(object).where(h.notna(), None).to_dict("records"))
        conn.execute(tutores.insert(), t.to_dict("records"))
        conn.execute(reposiciones.insert(), r.to_dict("records"))

    print(f"Cargado: {len(lt)} LT, {len(h)} horarios, {len(t)} tutores, {len(r)} reposiciones.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    main(parser.parse_args().reset)
