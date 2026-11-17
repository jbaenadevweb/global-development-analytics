# Fuentes, términos y procedencia

## Verificación realizada

Las páginas utilizadas contestaron en la inspección HTML y el proceso Python final pudo consultar robots.txt y leer las tablas. Una consulta preliminar aislada devolvió **403**; esa respuesta no se trató como autorización y no se intentó evadirla. La extracción solo se ejecutó después de que las verificaciones posteriores permitieron el acceso. `src/scraping/fetch.py` aborta antes de solicitar la página si no puede leer o validar robots.txt.

Las páginas contienen diferentes fuentes estadísticas y años. Wikipedia es el agregador/página de scraping, no necesariamente el productor estadístico. La columna `statistic_source` identifica la fuente descrita por la tabla cuando la página lo permite; el informe captura tabla seleccionada, encabezados, URL, filas y año encontrado.

| Indicador | Página HTML inicial | Observación |
|---|---|---|
| Esperanza de vida (usada) | https://en.wikipedia.org/wiki/List_of_countries_by_life_expectancy | Se extrajo tabla ONU de esperanza de vida general al nacer, año 2023. |
| PIB per cápita PPP (página inicial inspeccionada, no usada) | https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(PPP)_per_capita | Distintas fuentes/estimaciones actuales, incluyendo años posteriores al objetivo; reemplazada por tabla histórica 2023. |
| Población (verificada, usada) | https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations) | La página inicial de población variaba entre países; se cambió a tabla ONU con columna explícita del 1 de julio de 2023 y región continental. |
| Fertilidad | https://en.wikipedia.org/wiki/List_of_countries_by_fertility_rate | La URL redirige al título actual `/wiki/List_of_countries_by_total_fertility_rate`; se selecciona la tabla 2023 identificada por Wikipedia como OWID, basada en estimaciones Gapminder. |
| Superficie terrestre (usada) | https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_area | Se eligió explícitamente la columna “Land in km2”; el sitio no declara año de observación para el valor. |

La primera lista de PIB por PPP per cápita ofrece ediciones de distintos años (en la inspección, 2026 y 2025/2024). Para evitar mezclar años posteriores al objetivo, se sustituyó por la tabla histórica por año: https://en.wikipedia.org/wiki/List_of_countries_by_past_and_projected_GDP_(PPP)_per_capita. En ella se selecciona la columna 2023, dejando explícito que los años posteriores en la tabla están clasificados como proyecciones.

La lista más reciente de población mezclaba fechas por país de 2020 a 2026. Para comparar con el objetivo 2023, se sustituyó por https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations), que contiene columnas HTML explícitas “Population (1 July 2023)” y región/subregión ONU. Así, la población y el continente se obtienen con fecha y clasificación indicadas en la tabla.

**Estado de uso efectivo:** el proceso local logró validar robots.txt y extraer efectivamente cinco páginas, documentadas en `outputs/reports/extraction_report.json`. La URL de PIB empleada fue la página histórica alternativa. No se usó la tabla actual de PIB con estimaciones posteriores.

## Condiciones de reutilización y scraping

- Respetar robots.txt, términos del sitio y atribución/licencia CC BY-SA 4.0.
- Solicitudes HTTPS, user-agent identificable, pausas de 2 segundos por host, timeout de 20 segundos y máximo de dos reintentos ante errores transitorios.
- Un error de robots.txt, 403, 429 o falta de permiso detiene la petición.
- Extraer solo tablas presentes en el HTML público; no usar API, exportaciones tabulares del sitio ni fuentes de dataset alternativas.
- Antes de reactivar una fuente bloqueada, revisar manualmente los términos aplicables y obtener permiso/resolver el acceso legítimamente. No cambiar headers ni usar proxies para eludir controles.

## Cambios de fuente inicial

Se sustituyeron las páginas actuales de PIB PPP y población por páginas HTML históricas/ONU con campos 2023 explícitos para compatibilidad temporal. No se utilizaron APIs ni archivos tabulares descargados. Las fuentes estadísticas originales y sus licencias/atribuciones deben consultarse en notas y citas de cada página; los registros y tablas seleccionadas se detallan en el reporte de extracción.
