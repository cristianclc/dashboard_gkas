"""Preparación de los datos obtenidos desde Metabase."""
from src.transformations import (
    transformar_aula_aula,
    transformar_notas_gk,
    transformar_notas_as,
    transformar_retirados,
    transformar_k2k,
)
from src.metabase import cargar_datos_crudos


def preparar_datos(semana=None):
    """Descarga y transforma los datos; semana=None selecciona la semana máxima del 01."""
    datos = cargar_datos_crudos(semana=semana)

    df = transformar_aula_aula(datos["df"])
    df_gk = transformar_notas_gk(datos["df_gk"])
    df_as = transformar_notas_as(datos["df_as"])
    df_ret = transformar_retirados(datos["df_ret"])
    df_k2k = transformar_k2k(datos["df_k2k"], df_gk, df_as)

    resultado = {
        "df": df,
        "df_gk": df_gk,
        "df_as": df_as,
        "df_ret": df_ret,
        "df_k2k": df_k2k,
    }
    if "df_k2k_complementario" in datos:
        resultado["df_k2k_complementario"] = datos["df_k2k_complementario"]
    if "_semana_consultada" in datos:
        resultado["semana_consultada"] = int(datos["_semana_consultada"]["semana"].iloc[0])
    if "_aviso_07" in datos:
        resultado["aviso_07"] = datos["_aviso_07"]["aviso"].iloc[0]
    return resultado
