import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, StAggridTheme
import re
import math

tema = StAggridTheme(base="quartz").withParams(
    autoHeightMinBodyHeight=0,
    fontSize=10,
    headerFontSize=14,
    cellHorizontalPadding=6
)


#CSS PARA TABLAs

ESTILO_AGGRID = {
    ".ag-cell.sesion-ejecutada": {
        "background-color": "#C6EFCE !important",
        "color": "#006100 !important",
    },

    ".ag-cell.sesion-programada": {
        "background-color": "#FFEB9C !important",
        "color": "#9C6500 !important",
    },

    ".ag-cell.sesion-cancelada": {
        "background-color": "#FFC7CE !important",
        "color": "#9C0006 !important",
    },

    ".ag-cell.horas-por-migrar": {
        "background-color": "#FFC7CE !important",
        "color": "#9C0006 !important",
        "font-weight": "700 !important",
    },
    ".aprovechamiento-rojo": {
        "background-color": "#F8D7DA !important"
    },
    ".aprovechamiento-amarillo": {
        "background-color": "#FFF3CD !important"
    },
    ".ag-cell.celda-cero": {
        "background-color": "#F4CCCC !important",
        "color": "#A61B1B !important",
        "font-weight": "700 !important",
    },
        ".periodo-1-cell": {
        "background-color": "#D9EAD3 !important",
        "color": "#274E13 !important",
    },

    ".periodo-2-cell": {
        "background-color": "#FFF2CC !important",
        "color": "#7F6000 !important",
    },

    ".periodo-3-cell": {
        "background-color": "#CFE2F3 !important",
        "color": "#1155CC !important",
    },

    ".periodo-4-cell": {
        "background-color": "#FCE5CD !important",
        "color": "#E69138 !important",
},
    ".periodo-1-header": {
        "background-color": "#A9D18E !important",
        "color": "#1F1F1F !important",
        "font-weight": "700 !important"
    },

    ".periodo-2-header": {
        "background-color": "#FFD966 !important",
        "color": "#1F1F1F !important",
        "font-weight": "700 !important"
    },

    ".periodo-3-header": {
        "background-color": "#9DC3E6 !important",
        "color": "#1F1F1F !important",
        "font-weight": "700 !important"
    },

    ".periodo-4-header": {
        "background-color": "#F4B183 !important",
        "color": "#1F1F1F !important",
        "font-weight": "700 !important"
    },
    ".ag-header": {
        "background-color": "#0F3D4C !important",
        "border-bottom": "2px solid #0F3D4C !important",
    },

    ".ag-header-cell": {
        "background-color": "#0F3D4C !important",
        "color": "white !important",
        "font-weight": "600 !important",
        "border-right": "1px solid #285765 !important",
    },

    ".ag-header-cell-label": {
        "color": "white !important",
    },

    ".ag-header-cell-text": {
        "color": "white !important",
        "font-weight": "600 !important",
    },

    ".ag-row": {
        "border-bottom": "1px solid #E5E7EB !important",
    },

    ".ag-row-even": {
        "background-color": "#FFFFFF !important",
    },

    ".ag-row-odd": {
        "background-color": "#F7F9FA !important",
    },

    ".ag-row-hover": {
        "background-color": "#EAF2F5 !important",
    },

    ".ag-cell": {
        "border-right": "1px solid #EEF1F2 !important",
        "color": "#1F2937 !important",
        "font-size": "13px !important",
    },

    ".ag-row-pinned": {
        "background-color": "#DCEAF0 !important",
        "color": "#0F3D4C !important",
        "font-weight": "700 !important",
        "border-top": "2px solid #0F3D4C !important",
    },

    ".ag-row-pinned .ag-cell": {
        "background-color": "#DCEAF0 !important",
        "color": "#0F3D4C !important",
        "font-weight": "700 !important",
    },

    ".ag-floating-filter": {
        "background-color": "#F4F7F8 !important",
    },

    ".grupo-informacion": {
        "background-color": "#0F3D4C !important",
        "color": "white !important",
        "font-weight": "700 !important",
        "text-align": "center !important",
    },

    ".grupo-horas": {
        "background-color": "#3F7FE5 !important",
        "color": "white !important",
        "font-weight": "700 !important",
        "text-align": "center !important",
    },

    ".grupo-estudiantes": {
        "background-color": "#0F3D4C !important",
        "color": "white !important",
        "font-weight": "700 !important",
        "text-align": "center !important",
    },

    ".grupo-aprovechamiento": {
        "background-color": "#2E9F57 !important",
        "color": "white !important",
        "font-weight": "700 !important",
        "text-align": "center !important",
    },

    ".grupo-grupos": {
    "background-color": "#0F3D4C !important",
    "color": "white !important",
    "font-weight": "700 !important",
    "text-align": "center !important",
    },

    ".grupo-proyeccion": {
        "background-color": "#3F7FE5 !important",
        "color": "white !important",
        "font-weight": "700 !important",
        "text-align": "center !important",
    },

    ".grupo-proyeccion-sin": {
        "background-color": "#2E9F57 !important",
        "color": "white !important",
        "font-weight": "700 !important",
        "text-align": "center !important",
    },
    
    ".glocal-kids": {
        "background-color": "#4472C4",
        "color": "white",
        "font-weight": "700",
        "text-align": "center",
    },

    ".after-school": {
        "background-color": "#C65911",
        "color": "white",
        "font-weight": "700",
        "text-align": "center",

    },

    ".grupo-reposiciones": {
        "background-color": "#2E9F57 !important",
        "color": "white !important",
        "font-weight": "700 !important",
        "text-align": "center !important",
    },

    ".grupo-estudiantes": {
        "background-color": "#0F3D4C !important",
        "color": "white !important",
        "font-weight": "700 !important",
        "text-align": "center !important",
    },
    ".ag-layout-auto-height .ag-center-cols-clipper": {"min-height": "0 !important"},
    ".ag-layout-auto-height .ag-center-cols-viewport": {"min-height": "0 !important"},
    ".ag-layout-auto-height .ag-center-cols-container": {"min-height": "0 !important"}
}

#TAMAÑO INICIAL DE COLUMNAS
def calcular_anchos_por_contenido(df, ancho_min=100, ancho_max=400, ancho_caracter=8, padding=24):
    anchos = {}
    for columna in df.columns:
        valores = df[columna].astype(str)
        max_len = valores.map(lambda x: len(str(x))).max() if not valores.empty else 0
        ancho = max_len * ancho_caracter + padding
        anchos[columna] = int(min(max(ancho, ancho_min), ancho_max))
    return anchos

# TABLA CON TOTAL DINÁMICO

def mostrar_tabla_interactiva(
    df,
    titulo=None,
    sin_total=None,
    porcentajes=None,
    promedios=None,
    mostrar_total=True,
    grupos_columnas=None,
    contar_ceros=False,
    altura_maxima=None
):

    """
    Muestra un DataFrame como una tabla interactiva de AgGrid.

    Funcionalidades:
    - Filtros de texto y numéricos.
    - Filtros por rango para columnas numéricas.
    - Ordenamiento.
    - Redimensionamiento de columnas.
    - Reordenamiento de columnas.
    - Ocultar columnas desde el menú de cada columna.
    - Fila TOTAL/SUBTOTAL dinámica.
    """

    tabla = df.copy()
    tabla.columns = tabla.columns.map(str)

    # ============================================================
    # TÍTULO
    # ============================================================

    if titulo:
        st.subheader(titulo)

    # ============================================================
    # PREPARAR ÍNDICE
    # ============================================================

    # Si la tabla tiene un índice diferente al RangeIndex,
    # lo convertimos en una columna para mostrarlo en AgGrid.
    if not isinstance(tabla.index, pd.RangeIndex):
        nombre_indice = tabla.index.name or "Índice"
        tabla = tabla.reset_index()
        tabla = tabla.rename(columns={nombre_indice: nombre_indice})

    # ============================================================
    # ELIMINAR COLUMNA INDEX
    # ============================================================

    if "index" in tabla.columns:
        tabla = tabla.drop(columns=["index"])

    # ============================================================
    # ELIMINAR FILAS TOTAL EXISTENTES
    # ============================================================

    # Las funciones de dashboard ya generan una fila TOTAL.
    # La quitamos aquí porque AgGrid generará un TOTAL dinámico
    # según las filas que queden después de aplicar filtros.

    mascara_total = pd.Series(False, index=tabla.index)

    for columna in tabla.columns:
        mascara_total |= (
            tabla[columna]
            .astype(str)
            .str.strip()
            .str.upper()
            .eq("TOTAL")
        )

    tabla = tabla.loc[~mascara_total].copy()

    # ============================================================
    # CÓDIGO JAVASCRIPT PARA EL TOTAL DINÁMICO
    # ============================================================

    actualizar_total = JsCode(
        """
        function(params) {

            const api = params.api;
            const columnas = api.getColumns();

            if (!columnas) {
                return;
            }

            const total = {};

            // ========================================================
            // CONTAR CEROS
            // ========================================================

            const contarCeros = (
                params.context &&
                params.context.contar_ceros === true
            );

            // ========================================================
            // SUMA / CEROS
            // ========================================================

            columnas.forEach(function(columna) {

                const campo = columna.getColDef().field;

                if (!campo) {
                    return;
                }

                let suma = 0;
                let cantidadCeros = 0;

                api.forEachNodeAfterFilter(function(rowNode) {

                    if (!rowNode.data) {
                        return;
                    }

                    const valor = rowNode.data[campo];

                    if (
                        typeof valor === "number" &&
                        Number.isFinite(valor)
                    ) {

                        if (contarCeros) {

                            if (valor === 0) {
                                cantidadCeros += 1;
                            }

                        } else {

                            suma += valor;

                        }

                    }

                });

                if (contarCeros) {
                    total[campo] = cantidadCeros;
                } else {
                    total[campo] = Math.round(suma);
                }

            });


            // ========================================================
            // ETIQUETA TOTAL
            // ========================================================

            const primeraColumna =
                columnas.length > 0
                    ? columnas[0].getColDef().field
                    : null;

            if (primeraColumna) {
                total[primeraColumna] = "TOTAL";
            }


            // ========================================================
            // COLUMNAS SIN TOTAL
            // ========================================================

            const sinTotal = (
                params.context &&
                Array.isArray(params.context.sin_total)
            )
                ? params.context.sin_total
                : [];

            sinTotal.forEach(function(nombre) {

                if (total.hasOwnProperty(nombre)) {
                    total[nombre] = null;
                }

            });


            // ========================================================
            // PROMEDIOS
            // ========================================================

            const promedios = (
                params.context &&
                Array.isArray(params.context.promedios)
            )
                ? params.context.promedios
                : [];

            promedios.forEach(function(nombre) {

                let suma = 0;
                let cantidad = 0;

                api.forEachNodeAfterFilter(function(rowNode) {

                    if (!rowNode.data) {
                        return;
                    }

                    const valor = rowNode.data[nombre];

                    if (
                        typeof valor === "number" &&
                        Number.isFinite(valor)
                    ) {
                        suma += valor;
                        cantidad += 1;
                    }

                });

                if (cantidad > 0) {

                    total[nombre] =
                        Math.round((suma / cantidad) * 100) / 100;

                } else {

                    total[nombre] = 0;

                }

            });


            // ========================================================
            // PORCENTAJES SOBRE EL TOTAL
            // ========================================================

            const porcentajes = (
                params.context &&
                params.context.porcentajes
            )
                ? params.context.porcentajes
                : {};

            Object.keys(porcentajes).forEach(function(nombre) {

                const configuracion = porcentajes[nombre];

                let numerador = 0;
                let denominador = 0;


                // ----------------------------------------------------
                // RECORRER FILAS FILTRADAS
                // ----------------------------------------------------

                api.forEachNodeAfterFilter(function(rowNode) {

                    if (!rowNode.data) {
                        return;
                    }


                    // ------------------------------------------------
                    // NUMERADOR
                    // ------------------------------------------------

                    if (Array.isArray(configuracion.numerador)) {

                        configuracion.numerador.forEach(function(campo) {

                            const valor = rowNode.data[campo];

                            if (
                                typeof valor === "number" &&
                                Number.isFinite(valor)
                            ) {
                                numerador += valor;
                            }

                        });

                    } else {

                        const valor =
                            rowNode.data[configuracion.numerador];

                        if (
                            typeof valor === "number" &&
                            Number.isFinite(valor)
                        ) {
                            numerador += valor;
                        }

                    }


                    // ------------------------------------------------
                    // DENOMINADOR
                    // ------------------------------------------------

                    const valorDenominador =
                        rowNode.data[configuracion.denominador];

                    if (
                        typeof valorDenominador === "number" &&
                        Number.isFinite(valorDenominador)
                    ) {
                        denominador += valorDenominador;
                    }

                });


                // ----------------------------------------------------
                // CALCULAR PORCENTAJE
                // ----------------------------------------------------

                if (denominador !== 0) {

                    total[nombre] =
                        Math.round(
                            ((numerador / denominador) * 100) * 100
                        ) / 100;

                } else {

                    total[nombre] = 0;

                }

            });


            // ========================================================
            // MOSTRAR TOTAL
            // ========================================================

            api.setGridOption(
                "pinnedBottomRowData",
                [total]
            );

        }
        """
    )

    # ============================================================
    # CONFIGURACIÓN DE AGGRID
    # ============================================================

    anchos_columnas = calcular_anchos_por_contenido(tabla)

    gb = GridOptionsBuilder.from_dataframe(tabla)
    
    gb.configure_column(
        tabla.columns[0],
        cellRenderer=JsCode(
            """
            function(params) {
                if (params.node && params.node.rowPinned) {
                    return "TOTAL";
                }

                return params.value;
            }
            """
        )
    )

    gb.configure_default_column(
        sortable=True,
        filter=True,
        resizable=True,
        floatingFilter=True,
        minWidth=100,
        wrapHeaderText=True,
        autoHeaderHeight=True
        
    )

    for columna in tabla.columns:
        gb.configure_column(
            str(columna),
            width=anchos_columnas.get(str(columna), 100)
        )
        
    # Menú de columnas:
    # permite ocultar columnas, ordenar, etc.
    dom_layout = "normal" if altura_maxima else "autoHeight"
    
    gb.configure_grid_options(
        onColumnVisible=JsCode("function(p){ p.api.sizeColumnsToFit(); }"),
        onColumnResized=JsCode("""
        function(p) {
            if (!p.finished || p.source !== "uiColumnResized") return;
            const limites = (p.columns || []).map(function(c) {
                const w = c.getActualWidth();
                return {key: c.getColId(), minWidth: w, maxWidth: w};
            });
            p.api.sizeColumnsToFit({columnLimits: limites});
        }
        """),
        onColumnMoved=JsCode("""
            function(p) {
                if (!p.finished) return;
                p.api.sizeColumnsToFit();
            }
            """),
        onGridSizeChanged=JsCode("function(p){ p.api.sizeColumnsToFit(); }"),
        domLayout=dom_layout,
        suppressMenuHide=False,
        onFirstDataRendered=actualizar_total if mostrar_total else None,
        onFilterChanged=actualizar_total if mostrar_total else None,
        onSortChanged=actualizar_total if mostrar_total else None
    )


    # ============================================================
    # MOSTRAR TABLA
    # ============================================================
    
    grid_options = gb.build()

    # ============================================================
    # ENCABEZADOS AGRUPADOS
    # ============================================================

    if grupos_columnas:

        columnas = {
            str(col["field"]): col
            for col in grid_options["columnDefs"]
            if "field" in col
        }

        column_defs_agrupadas = []

        for grupo in grupos_columnas:

            children = []

            for nombre_columna in grupo["columnas"]:

                if nombre_columna in columnas:

                    columna = columnas[nombre_columna].copy()

                    if "cellClass" in grupo:

                        columna["cellClass"] = grupo["cellClass"]

                        columna["cellClassRules"] = {
                            "celda-cero": JsCode("""
                                function(params) {
                                    return params.value === 0;
                                }
                            """)
                        }

                    children.append(columna)

            if children:

                column_defs_agrupadas.append({
                    "headerName": grupo["nombre"],
                    "headerClass": grupo.get(
                        "headerClass",
                        "grupo-header"
                    ),
                    "children": children
                })

        grid_options["columnDefs"] = column_defs_agrupadas

    grid_options["context"] = {
        "sin_total": sin_total,
        "porcentajes": porcentajes or {},
        "promedios": promedios or [],
        "mostrar_total": mostrar_total,
        "contar_ceros": contar_ceros
    }

    respuesta = AgGrid(
        tabla,
        gridOptions=grid_options,
        height=altura_maxima if altura_maxima else None,
        theme=tema,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        update_on=["filterChanged", "sortChanged", "columnVisible", "cellClicked"],
        data_return_mode="FILTERED_AND_SORTED",
        custom_css=ESTILO_AGGRID
    )

    return respuesta

# TABLA DE REPORTES PRIORITARIAS

def mostrar_reporte_alertas(df, titulo=None, altura=None):
    """
    Muestra el reporte de alertas de GK y AS
    en una única tabla.
    """

    tabla = df.copy()
    tabla.columns = tabla.columns.map(str)

    # --------------------------------------------------------
    # Título
    # --------------------------------------------------------

    if titulo:
        st.subheader(titulo)

    # --------------------------------------------------------
    # Configuración AgGrid
    # --------------------------------------------------------

    gb = GridOptionsBuilder.from_dataframe(tabla)

    gb.configure_default_column(
        sortable=True,
        filter=True,
        resizable=True,
        floatingFilter=True,
        minWidth=100,
        wrapHeaderText=True,
        autoHeaderHeight=True
    )

    gb.configure_grid_options(
        domLayout="autoHeight",
        onGridReady=JsCode("""
            function(p) {
                setTimeout(function() {
                    p.api.sizeColumnsToFit();
                    window.dispatchEvent(new Event('resize'));
                }, 1000);
            }
            """),
        onGridSizeChanged=JsCode(
            "function(p){ p.api.sizeColumnsToFit(); }"
        ),
        onColumnVisible=JsCode(
            "function(p){ p.api.sizeColumnsToFit(); }"
        ),
        onColumnResized=JsCode(
            """
            function(p) {
                if (!p.finished || p.source !== "uiColumnResized") return;
                const limites = (p.columns || []).map(function(c) {
                    const w = c.getActualWidth();
                    return {key: c.getColId(), minWidth: w, maxWidth: w};
                });
                p.api.sizeColumnsToFit({columnLimits: limites});
            }
            """
        )
    )

    for col in tabla.columns[1:]:
        gb.configure_column(col, flex=max(1, len(col) / 12))

    # --------------------------------------------------------
    # Ancho de columnas
    # --------------------------------------------------------

    gb.configure_column(
        "Grupo",
        width=90
    )

    gb.configure_column(
        "Motivo",
        width=220
    )

    gb.configure_column(
        "# Grupos afectados",
        type=["numericColumn"]
    )

    gb.configure_column(
        "# de horas afectadas",
        type=["numericColumn"]
    )

    gb.configure_column(
        "# de horas de reposición ejecutadas",
        type=["numericColumn"]
    )

    gb.configure_column(
        "% de horas de reposición vs horas afectadas",
        type=["numericColumn"]
    )

    # --------------------------------------------------------
    # Estilo fila TOTAL
    # --------------------------------------------------------

    grid_options = gb.build()

    grid_options["getRowStyle"] = JsCode(
        """
        function(params) {

            if (
                params.data &&
                params.data.Motivo &&
                params.data.Motivo.toString().trim().toUpperCase() === "TOTAL"
            ) {
                return {
                    'background-color': '#DCEAF0',
                    'color': '#0F3D4C',
                    'font-weight': 'bold',
                    'border-top': '2px solid #0F3D4C'
                };
            }

            return null;
        }
        """
    )

    # --------------------------------------------------------
    # Estilo Grupo GK / AS
    # --------------------------------------------------------

    grid_options["columnDefs"] = [
        {
            **col,
            "cellStyle": JsCode(
                """
                function(params) {

                    if (params.value === "GK") {
                        return {
                            'font-weight': '600',
                            'color': '#3F7FE5'
                        };
                    }

                    if (params.value === "AS") {
                        return {
                            'font-weight': '600',
                            'color': '#2E9F57'
                        };
                    }

                    return null;
                }
                """
            )
        }
        if col.get("field") == "Grupo"
        else col
        for col in grid_options["columnDefs"]
    ]

    # --------------------------------------------------------
    # Mostrar tabla
    # --------------------------------------------------------

    AgGrid(
        tabla,
        gridOptions=grid_options,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        data_return_mode="FILTERED_AND_SORTED",
        theme=tema,
        height=500,
        custom_css=ESTILO_AGGRID,
        key="reporte_alertas"
    )

#AULAS FILTRADAS PARA REPORTE GK

def obtener_aulas_filtradas(
    tabla_aprovechamiento,
    sin_total=None,
    porcentajes=None,
    promedios=None,
    mostrar_total=True,
    altura=None
):
    """
    Muestra la tabla de aprovechamiento por aula y retorna
    las filas que quedan después de aplicar los filtros de AgGrid.
    """

    tabla = tabla_aprovechamiento.copy()
    tabla.columns = tabla.columns.map(str)

    # --------------------------------------------------------
    # Altura
    # --------------------------------------------------------

    if altura is None:
        numero_filas = len(tabla)

        altura = min(
            (numero_filas + 2) * 35,
            500
        )

    # --------------------------------------------------------
    # JavaScript para actualizar el TOTAL dinámico
    # --------------------------------------------------------

    actualizar_total = JsCode(
        """
        function(params) {

            const api = params.api;
            const columnas = api.getColumns();

            if (!columnas) {
                return;
            }

            const total = {};
            const contarCeros = (
                params.context &&
                params.context.contar_ceros === true
            );

            columnas.forEach(function(columna) {

                const campo = columna.getColDef().field;

                if (!campo) {
                    return;
                }

                let suma = 0;

                api.forEachNodeAfterFilter(function(rowNode) {

                    if (!rowNode.data) {
                        return;
                    }

                    const valor = rowNode.data[campo];

                    if (
                        typeof valor === "number" &&
                        Number.isFinite(valor)
                    ) {
                        suma += valor;
                    }

                });

                total[campo] = Math.round(suma);

            });

            const primeraColumna =
                columnas.length > 0
                    ? columnas[0].getColDef().field
                    : null;

            if (primeraColumna) {
                total[primeraColumna] = "TOTAL";
            }

            const sinTotal = (
                params.context &&
                Array.isArray(params.context.sin_total)
            )
                ? params.context.sin_total
                : [];

            sinTotal.forEach(function(nombre) {
                if (total.hasOwnProperty(nombre)) {
                    total[nombre] = null;
                }
            });

            const promedios = (
                params.context &&
                Array.isArray(params.context.promedios)
            )
                ? params.context.promedios
                : [];

            promedios.forEach(function(nombre) {

                let suma = 0;
                let cantidad = 0;

                api.forEachNodeAfterFilter(function(rowNode) {

                    if (!rowNode.data) {
                        return;
                    }

                    const valor = rowNode.data[nombre];

                    if (
                        typeof valor === "number" &&
                        Number.isFinite(valor)
                    ) {
                        suma += valor;
                        cantidad += 1;
                    }

                });

                if (cantidad > 0) {
                    total[nombre] =
                        Math.round((suma / cantidad) * 100) / 100;
                } else {
                    total[nombre] = 0;
                }

            });

            const porcentajes = (
                params.context &&
                params.context.porcentajes
            )
                ? params.context.porcentajes
                : {};

            Object.keys(porcentajes).forEach(function(nombre) {

                const configuracion = porcentajes[nombre];

                let numerador = 0;
                let denominador = 0;

                api.forEachNodeAfterFilter(function(rowNode) {

                    if (!rowNode.data) {
                        return;
                    }

                    // NUMERADOR
                    if (Array.isArray(configuracion.numerador)) {

                        configuracion.numerador.forEach(function(campo) {

                            const valor = rowNode.data[campo];

                            if (
                                typeof valor === "number" &&
                                Number.isFinite(valor)
                            ) {
                                numerador += valor;
                            }

                        });

                    } else {

                        const valor =
                            rowNode.data[configuracion.numerador];

                        if (
                            typeof valor === "number" &&
                            Number.isFinite(valor)
                        ) {
                            numerador += valor;
                        }

                    }

                    // DENOMINADOR
                    const valorDenominador =
                        rowNode.data[configuracion.denominador];

                    if (
                        typeof valorDenominador === "number" &&
                        Number.isFinite(valorDenominador)
                    ) {
                        denominador += valorDenominador;
                    }

                });

                if (denominador !== 0) {

                    total[nombre] =
                        Math.round(
                            ((numerador / denominador) * 100) * 100
                        ) / 100;

                } else {

                    total[nombre] = 0;

                }

            });

            if (
                params.context &&
                params.context.mostrar_total === false
            ) {
                return;
            }

            api.setGridOption(
                "pinnedBottomRowData",
                [total]
            );
        }
        """
    )

    # --------------------------------------------------------
    # Configuración de AgGrid
    # --------------------------------------------------------

    gb = GridOptionsBuilder.from_dataframe(tabla)
    
    gb.configure_default_column(
        sortable=True,
        filter=True,
        resizable=True,
        floatingFilter=True,
        minWidth=100,
        wrapHeaderText=True,
        autoHeaderHeight=True
    )
    
    gb.configure_grid_options(
        height=altura,

        onFirstDataRendered=JsCode("""
            function(p) {
                p.api.sizeColumnsToFit();
            }
        """),

        onGridSizeChanged=JsCode("""
            function(p) {
                p.api.sizeColumnsToFit();
            }
        """),

        onColumnMoved=JsCode("""
            function(p) {
                if (!p.finished) return;
                p.api.sizeColumnsToFit();
            }
        """),
        onColumnVisible=JsCode("function(p){ p.api.sizeColumnsToFit(); }"),
        

        suppressMenuHide=False,
        groupHeaderHeight=32,
        headerHeight=55,

        onFilterChanged=actualizar_total,
        onSortChanged=actualizar_total
    )

    grid_options = gb.build()

    # --------------------------------------------------------
    # Color de celdas según aprovechamiento académico
    # --------------------------------------------------------

    estilo_aprovechamiento = JsCode("""
        function(params) {

            if (params.node.rowPinned) {
                return null;
            }

            const valor = params.data["% de aprovechamiento académico"];

            if (
                typeof valor !== "number" ||
                !Number.isFinite(valor)
            ) {
                return null;
            }

            // Menor a 50 → rojo
            if (valor < 50) {
                return {
                    backgroundColor: "#F8D7DA"
                };
            }

            // 50 hasta menor de 70 → amarillo
            if (valor < 70) {
                return {
                    backgroundColor: "#FFF3CD"
                };
            }

            return null;
        }
    """)

    # Aplicar el estilo a todas las columnas
    for columna in grid_options["columnDefs"]:
        columna["cellStyle"] = estilo_aprovechamiento

        

    # ============================================================
    # ENCABEZADOS AGRUPADOS
    # ============================================================

    column_defs = grid_options["columnDefs"]

    # Guardar las definiciones originales por nombre de columna
    columnas = {
        str(col["field"]): col
        for col in column_defs
        if "field" in col
    }

    column_defs_agrupadas = [
        {
            "headerName": "INFORMACIÓN DEL AULA",
            "headerClass": "grupo-informacion",
            "children": [
                columnas["Aula"],
                columnas["IED"],
                columnas["Grupo"],
                columnas["Grado"]
            ]
        },
        {
            "headerName": "HORAS",
            "headerClass": "grupo-horas",
            "children": [
                columnas["Horas programadas"],
                columnas["Horas canceladas"],
                columnas["Horas ejecutadas"],
                columnas["Horas de reposición ejecutadas"],
                columnas["Horas de reposición primer semestre"],
                columnas["Horas de reposición segundo semestre"]
            ]
        },
        {
            "headerName": "ESTUDIANTES",
            "headerClass": "grupo-estudiantes",
            "children": [
                columnas["Número promedio de estudiantes asistentes"],
                columnas["Número de estudiantes del Aula"]
            ]
        },
        {
            "headerName": "APROVECHAMIENTO",
            "headerClass": "grupo-aprovechamiento",
            "children": [
                columnas["% de aprovechamiento académico"],
                columnas["% de aprovechamiento de estudiantes"]
            ]
        }
    ]

    grid_options["columnDefs"] = column_defs_agrupadas

    grid_options["context"] = {
        "sin_total": sin_total or [],
        "porcentajes": porcentajes or {},
        "promedios": promedios or [],
        "mostrar_total": mostrar_total
    }

    # --------------------------------------------------------
    # AgGrid
    # --------------------------------------------------------

    respuesta = AgGrid(
        tabla,
        gridOptions=grid_options,
        height=altura,
        theme=tema,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        update_on=["filterChanged", "sortChanged", "columnVisible"],
        data_return_mode="FILTERED_AND_SORTED",
        custom_css=ESTILO_AGGRID,
        key="aprovechamiento_filtro"
    )

    
    # --------------------------------------------------------
    # Filas filtradas
    # --------------------------------------------------------

    tabla_filtrada = pd.DataFrame(
        respuesta["data"]
    )

    return tabla_filtrada

#MOSTRAR TABLA REPOSICIONES
def mostrar_tabla_reposiciones(
    df,
    sin_total=None,
    mostrar_total=True,
    altura_maxima=600,
    columnas_fijas=None
):
    """
    Muestra una tabla interactiva de reposiciones en AgGrid.

    Funcionalidades:
    - Filtros y ordenamiento.
    - Redimensionamiento de columnas.
    - Fila TOTAL dinámica según los filtros aplicados.
    - Exclusión de columnas del cálculo del TOTAL.
    - Colores según el estado de las sesiones.
    - Resaltado de horas de reposición por migrar.
    """

    # ============================================================
    # PREPARAR TABLA
    # ============================================================

    tabla = df.copy()
    tabla.columns = tabla.columns.map(str)

    if not isinstance(tabla.index, pd.RangeIndex):
        nombre_indice = tabla.index.name or "Índice"
        tabla = tabla.reset_index()

    if "index" in tabla.columns:
        tabla = tabla.drop(columns=["index"])

    # Eliminar filas TOTAL existentes
    mascara_total = pd.Series(False, index=tabla.index)

    for columna in tabla.columns:
        mascara_total |= (
            tabla[columna]
            .astype(str)
            .str.strip()
            .str.upper()
            .eq("TOTAL")
        )

    tabla = tabla.loc[~mascara_total].copy()

    # ============================================================
    # TOTAL DINÁMICO
    # ============================================================

    actualizar_total = JsCode("""
        function(params) {

            const api = params.api;
            const columnas = api.getColumns();

            if (!columnas) return;

            const total = {};

            columnas.forEach(function(columna) {

                const campo = columna.getColDef().field;

                if (!campo) return;

                let suma = 0;

                api.forEachNodeAfterFilter(function(rowNode) {

                    if (!rowNode.data) return;

                    const valor = rowNode.data[campo];

                    if (
                        typeof valor === "number" &&
                        Number.isFinite(valor)
                    ) {
                        suma += valor;
                    }
                });

                total[campo] = Math.round(suma);
            });

            // Etiqueta TOTAL en la primera columna
            const primeraColumna =
                columnas.length > 0
                    ? columnas[0].getColDef().field
                    : null;

            if (primeraColumna) {
                total[primeraColumna] = "TOTAL";
            }

            // Columnas que no deben sumar
            const sinTotal = (
                params.context &&
                Array.isArray(params.context.sin_total)
            ) ? params.context.sin_total : [];

            sinTotal.forEach(function(nombre) {
                if (total.hasOwnProperty(nombre)) {
                    total[nombre] = null;
                }
            });

            api.setGridOption(
                "pinnedBottomRowData",
                [total]
            );
        }
    """)

    # ============================================================
    # CONFIGURACIÓN DE AGGRID
    # ============================================================

    gb = GridOptionsBuilder.from_dataframe(tabla)

    # Renderizar la etiqueta TOTAL en la primera columna
    if len(tabla.columns) > 0:

        gb.configure_column(
            tabla.columns[0],
            cellRenderer=JsCode("""
                function(params) {
                    if (params.node && params.node.rowPinned) {
                        return "TOTAL";
                    }
                    return params.value;
                }
            """)
        )

    gb.configure_default_column(
        sortable=True,
        filter=True,
        resizable=True,
        floatingFilter=True,
        minWidth=100,
        flex=1,
        wrapHeaderText=True,
        autoHeaderHeight=True,
        wrapText=True,
        autoHeight=True,
    )

    # ============================================================
    # ANCHO DE COLUMNAS INFORMATIVAS
    # ============================================================

    if "IED" in tabla.columns:
        gb.configure_column(
            "IED",
            minWidth=300,
            flex=2,
            wrapText=False,
            autoHeight=False,
        )

    if "Horario" in tabla.columns:
        gb.configure_column(
            "Horario",
            minWidth=250,
            flex=2,
            wrapText=False,
        autoHeight=False,
    )

    # ============================================================
    # FIJAR COLUMNAS A LA IZQUIERDA
    # ============================================================

    if columnas_fijas:

        for columna in columnas_fijas:

            if columna in tabla.columns:

                gb.configure_column(
                    columna,
                    pinned="left"
                )

    # ============================================================
    # COLORES DE LAS SESIONES
    # ============================================================

    for columna in tabla.columns:

        if columna.startswith("Sesión "):

            gb.configure_column(
                columna,
                minWidth=300,
                flex=2,
                wrapText=False,
                autoHeight=False,
                cellClassRules={

                    "sesion-ejecutada": JsCode("""
                        function(params) {
                            if (params.node && params.node.rowPinned) {
                                return false;
                            }

                            return String(params.value || "")
                                .includes("Ejecutada");
                        }
                    """),

                    "sesion-programada": JsCode("""
                        function(params) {
                            if (params.node && params.node.rowPinned) {
                                return false;
                            }

                            return String(params.value || "")
                                .includes("Programada");
                        }
                    """),

                    "sesion-cancelada": JsCode("""
                        function(params) {
                            if (params.node && params.node.rowPinned) {
                                return false;
                            }

                            return String(params.value || "")
                                .includes("Cancelada");
                        }
                    """)
                }
            )

            

        # ========================================================
        # HORAS POR MIGRAR
        # ========================================================

        elif columna == "Horas de reposición por migrar":

            gb.configure_column(
                columna,
                cellClassRules={
                    "horas-por-migrar": JsCode("""
                        function(params) {
                            if (params.node && params.node.rowPinned) {
                                return false;
                            }

                            const valor = Number(params.value);

                            return Number.isFinite(valor) && valor > 0;
                        }
                    """)
                }
            )

    # ============================================================
    # OPCIONES DE LA TABLA
    # ============================================================

    dom_layout = "normal" if altura_maxima else "autoHeight"

    gb.configure_grid_options(
        resetRowHeights=True,
        onColumnVisible=JsCode(
            "function(p){ p.api.sizeColumnsToFit(); }"
        ),

        onColumnResized=JsCode("""
            function(p) {
                if (!p.finished || p.source !== "uiColumnResized") return;

                const limites = (p.columns || []).map(function(c) {
                    const w = c.getActualWidth();
                    return {
                        key: c.getColId(),
                        minWidth: w,
                        maxWidth: w
                    };
                });

                p.api.sizeColumnsToFit({
                    columnLimits: limites
                });
            }
        """),

        onColumnMoved=JsCode("""
            function(p) {
                if (!p.finished) return;
                p.api.sizeColumnsToFit();
            }
        """),

        onGridSizeChanged=JsCode(
            "function(p){ p.api.sizeColumnsToFit(); }"
        ),

        domLayout=dom_layout,
        suppressMenuHide=False,

        onFirstDataRendered=actualizar_total if mostrar_total else None,
        onFilterChanged=actualizar_total if mostrar_total else None,
        onSortChanged=actualizar_total if mostrar_total else None,
    )

    # ============================================================
    # CONSTRUIR OPCIONES Y CONTEXTO
    # ============================================================

    grid_options = gb.build()

    grid_options["context"] = {
        "sin_total": sin_total or [],
    }

    if not mostrar_total:
        grid_options["pinnedBottomRowData"] = []

    # ============================================================
    # MOSTRAR TABLA
    # ============================================================

    respuesta = AgGrid(
        tabla,
        gridOptions=grid_options,
        height=altura_maxima if altura_maxima else None,
        theme=tema,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        update_on=[
            "filterChanged",
            "sortChanged",
            "columnVisible",
            "cellClicked"
        ],
        data_return_mode="FILTERED_AND_SORTED",
        custom_css=ESTILO_AGGRID
    )

    return respuesta

#TEXTO NOTAS

def crear_texto_notas(tabla, actividades, periodo):
    """
    Una línea por actividad del periodo, con el % de aulas que ya
    subieron notas (aulas con la celda en 0 = sin notas).
    Si faltan 10 aulas o menos, agrega el tutor de cada una.
    """

    tabla = pd.DataFrame(tabla)
    lineas = []

    for actividad in actividades:

        if not actividad.startswith(f"{periodo} "):
            continue

        # "C3 Oral Activity1 30%" -> "C3 Oral Activity 1"
        nombre = re.sub(r"\s*\d+%$", "", actividad)
        nombre = re.sub(r"(?<=[a-z])(\d)", r" \1", nombre)

        if tabla.empty:
            lineas.append(f"{nombre} (sin aulas)")
            continue

        valores = pd.to_numeric(tabla[actividad], errors="coerce")
        sin_nota = int((valores == 0).sum())

        # Hacia abajo: solo dice 100% si no falta ninguna aula
        porcentaje = math.floor((len(tabla) - sin_nota) / len(tabla) * 100)

        linea = f"{nombre} ({porcentaje}%)"

        if 0 < sin_nota <= 10:
            tutores = (
                tabla.loc[valores == 0, "Nombre Tutor"]
                .dropna()
                .astype(str)
                .drop_duplicates()
                .tolist()
            )
            linea += f" - Tutores faltantes: {', '.join(tutores)}"

        lineas.append(linea)

    return "\n".join(lineas)

#COSAS