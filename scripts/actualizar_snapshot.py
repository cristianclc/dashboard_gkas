"""Descarga los datos de Metabase, los transforma y guarda la copia en la base de datos.

Uso (desde la raíz del proyecto):
    python scripts/actualizar_snapshot.py

En Railway se ejecuta como un servicio con Cron Schedule (por ejemplo `0 * * * *`).
Termina con código distinto de 0 si algo falla, para que Railway lo marque como error
y la app siga mostrando la última copia buena.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dashboard import crear_tabla_aprovechamiento  # noqa: E402
from src.data import preparar_datos  # noqa: E402
from src.snapshot import guardar_snapshot  # noqa: E402


def main():
    inicio = time.time()
    print("Descargando y transformando datos de Metabase...")
    datos = preparar_datos()
    datos["tabla_aprovechamiento"] = crear_tabla_aprovechamiento(datos["df"])

    print(f"Descarga lista en {time.time() - inicio:.0f} s. Guardando copia...")
    guardar_snapshot(datos)
    print(f"Copia guardada. Total: {time.time() - inicio:.0f} s.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR al actualizar la copia: {exc}", file=sys.stderr)
        sys.exit(1)
