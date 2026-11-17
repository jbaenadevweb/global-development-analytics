# Diccionario de datos

Los campos se crean solo después de extraer y validar tablas HTML reales.

| Campo | Tipo | Unidad / descripción |
|---|---|---|
| `country` | texto | Nombre de país normalizado a minúsculas; llave exacta conservadora, no identificador oficial. |
| `life_expectancy` | decimal | Variable objetivo, años. No se imputa. |
| `gdp_per_capita_ppp` | decimal | PIB per cápita ajustado por PPA, dólares internacionales corrientes según la tabla histórica IMF/WEO, año 2023. |
| `population` | entero/decimal | Estimación de personas. |
| `fertility_rate` | decimal | Nacimientos por mujer, según tabla fuente. |
| `land_area` | decimal | Superficie terrestre en km², según encabezado de tabla. |
| `reference_year_life_expectancy` | entero | Año de observación objetivo identificado en el encabezado/sección. |
| `reference_year_gdp` | entero | Año de observación del PIB. |
| `reference_year_population` | entero | Año de observación de población. |
| `reference_year_fertility` | entero | Año de observación de fertilidad. |
| `reference_year_area` | entero | Año declarado para la superficie (puede no existir; superficie suele tener periodo de referencia no comparable). |
| `country_raw_<fuente>` | texto | Etiqueta original usada para revisar emparejamiento. |
| `source_url_<fuente>` | URL | Procedencia directa de la variable. |
| `statistic_source_<fuente>` | texto | Productor o descripción de la tabla, más referencias de fila cuando el HTML las expone. |
| `table_citations_<fuente>` | texto | Marcadores de cita HTML asociados a la fila; consultar las notas enlazadas en la página fuente. |
| `extracted_at_<fuente>` | fecha ISO UTC | Momento de extracción. |
| `temporal_compatible` | booleano | Año de esperanza de vida disponible, y años de predictores incluidos no futuros y con diferencia máxima de cinco años. |
| `country_match_method` | texto | Método de unión documentado; coincidencia exacta tras normalización. |
| `continent` | texto | Región continental ONU de la tabla de población UN, cuando está indicada; no se infiere. |

La disponibilidad depende de encabezados y calidad real de las páginas. No se supone que una celda vacía signifique cero. La ausencia de año o fuente se conserva como faltante y no se inventa.
