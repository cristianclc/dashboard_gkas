import pandas as pd

PREFIJOS_ARCHIVOS = {
    "01": "df",
    "03": "df_gk",
    "04": "df_as",
    "05": "df_ret",
    "06": "df_k2k",
    "07": "df_k2k_complementario"
}

PREFIJOS_OBLIGATORIOS = {
    "01",
    "03",
    "04",
    "05",
    "06"
}


def cargar_archivos(archivos):
    #lee los archivos XLSX y los identifica según sus dos primeros caracteres


    archivos_cargados = {}

    for archivo in archivos:

        prefijo = archivo.name[:2]

        # verificar si el prefijo corresponde a un archivo conocido
        if prefijo in PREFIJOS_ARCHIVOS:

            nombre_variable = PREFIJOS_ARCHIVOS[prefijo]

            archivos_cargados[nombre_variable] = pd.read_excel(
                archivo
            )

    return archivos_cargados


def validar_archivos(archivos):
    #verifica que estén presentes todos los archivos obligatorios, el archivo 07 es opcional.


    prefijos_cargados = {
        archivo.name[:2]
        for archivo in archivos
        if archivo.name[:2] in PREFIJOS_ARCHIVOS
    }

    faltantes = PREFIJOS_OBLIGATORIOS - prefijos_cargados

    return faltantes

