# Auditoría de licencias y procedencia

**Fecha de revisión:** 17 de noviembre de 2026.
**Alcance:** fuentes y artefactos existentes en el proyecto. No se ejecutó scraping. Esta matriz documenta evidencia pública de términos; no constituye asesoría legal.

## Alcance de `LICENSE`

El MIT de la raíz cubre **solo el código original del proyecto**: `main.py`, `app.py`, `src/` y las pruebas escritas para este código. No concede MIT sobre datos, tablas de Wikipedia, datos de terceros, imágenes, reportes estadísticos ni el modelo derivado. El titular no pudo verificarse en el proyecto; `[NOMBRE DEL TITULAR]` debe sustituirse por el titular real antes de publicar.

Los artefactos de terceros conservan sus propios términos. Una figura o modelo no queda automáticamente libre por no contener el CSV original.

## Fuentes y condiciones verificadas

| Indicador utilizado | URL de la página/tabla HTML | Fuente estadística y evidencia de términos |
|---|---|---|
| Esperanza de vida, tabla ONU 2023 | [Wikipedia: List of countries by life expectancy](https://en.wikipedia.org/wiki/List_of_countries_by_life_expectancy) | El reporte de extracción selecciona “Life expectancy overall at birth”, sección ONU 2023. UN DESA, Population Division, [World Population Prospects 2024: Data Sources](https://population.un.org/wpp/assets/Files/WPP2024_Data_Sources.pdf) indica CC BY 3.0 IGO para las tablas/figuras de WPP 2024. La tabla de Wikipedia tiene además sus términos editoriales. |
| PIB per cápita PPP, 2023 | [Wikipedia: List of countries by past and projected GDP (PPP) per capita](https://en.wikipedia.org/wiki/List_of_countries_by_past_and_projected_GDP_(PPP)_per_capita) | El encabezado de la tabla extraída identifica estimaciones IMF/WEO. Los [términos IMF](https://www.imf.org/en/about/copyright-and-terms) permiten copiar, crear derivados, publicar y distribuir datos IMF con atribución, exactitud y descripción de transformaciones; para reutilización comercial se debe solicitar permiso. La página de Wikipedia tiene términos separados. |
| Población ONU a 1 de julio de 2023 | [Wikipedia: List of countries by population (United Nations)](https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)) | La columna extraída es “Population (1 July 2023)”. Procedencia UN WPP 2024, CC BY 3.0 IGO; también se reutiliza una tabla de Wikipedia. |
| Fertilidad, 2023 | [Wikipedia: List of countries by fertility rate](https://en.wikipedia.org/wiki/List_of_countries_by_fertility_rate) | El caption de la tabla seleccionada dice “2023 list by OWID” y “based on Gapminder estimates”. Gapminder [Download the data](https://www.gapminder.org/data/) permite reutilización con atribución a Gapminder y a la fuente original cuando corresponda. OWID [Fertility Rate](https://ourworldindata.org/fertility-rate) indica que los datos de terceros mantienen los términos de sus autores originales. |
| Superficie terrestre, km² | [Wikipedia: List of countries and dependencies by area](https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_area) | Se seleccionó “Land in km2”. El reporte detecta marcadores de cita en 109 de 265 filas; las referencias varían por país. La declaración de dominio público del [World Factbook de CIA](https://www.cia.gov/llibrary/publications/the-world-factbook/docs/contributor_copyright.html) no verifica que todas las filas de esta tabla provengan de CIA. Derechos de todas las fuentes de fila no quedaron aclarados. |
| Tabla de Wikipedia reutilizada | [Wikipedia: Reusing Wikipedia content](https://en.wikipedia.org/wiki/Wikipedia:Reusing_Wikipedia_content) | Wikipedia señala CC BY-SA 4.0 para su contenido reutilizable. Exige atribución/enlace, indicar cambios y ShareAlike para adaptaciones. La licencia de Wikipedia no reemplaza los términos de las fuentes estadísticas citadas en una tabla. |

## Matriz de artefactos

“Incluible con condiciones” no significa que el archivo esté cubierto por MIT. Los archivos indicados como excluidos se conservan localmente y están protegidos por `.gitignore`.

| Artefacto | Fuentes que intervienen | Reutilización/atribución requerida | Decisión de publicación |
|---|---|---|---|
| Código propio (`main.py`, `app.py`, `src/**/*.py`, `tests/**/*.py`) | Autoría del proyecto | Aviso MIT y titular verdadero. | **Incluir bajo MIT**, solo este código. |
| `data/raw/life_expectancy.csv` | UN WPP 2024; tabla Wikipedia de esperanza de vida | UN DESA/Population Division, WPP 2024, CC BY 3.0 IGO; enlazar la página Wikipedia, CC BY-SA 4.0; indicar extracción y normalización. | **Excluido por ahora.** Las licencias de los componentes se identificaron, pero no se aprobó un aviso de datos con atribución/ShareAlike para el CSV derivado. |
| `data/raw/population.csv` | UN WPP 2024; tabla Wikipedia de población | Atribuir UN DESA/Population Division y la página; CC BY 3.0 IGO y CC BY-SA 4.0; indicar extracción. | **Excluido por ahora** por la misma falta de aviso/decisión de licencia para el archivo combinado. |
| `data/raw/fertility_rate.csv` | Gapminder/OWID; tabla Wikipedia | Atribuir Gapminder y la fuente original identificada; atribuir Wikipedia y CC BY-SA 4.0; indicar extracción/normalización. | **Excluido por ahora.** La página Gapminder permite reutilización atribuida, pero la cadena de fuente original y el aviso de distribución del CSV no están preparados. |
| `data/raw/gdp_per_capita_ppp.csv` | IMF WEO; tabla Wikipedia | Atribuir IMF WEO, indicar transformaciones, mantener exactitud; el uso comercial de IMF Data requiere permiso. | **Excluir.** El repositorio MIT no puede conceder esos derechos ni controlar reutilización comercial. |
| `data/raw/land_area.csv` | Fuentes heterogéneas, por fila, a través de tabla Wikipedia | Se requiere identificar fuente y términos por fila; la página general de CIA no basta para atribuir toda la tabla. | **Excluir.** Derechos de varias fuentes de fila no están suficientemente verificados. |
| `data/interim/country_indicators_long.csv`, `country_indicators_unchecked.csv`; `data/processed/country_indicators.csv` | Combinación de los cinco indicadores | Incluye IMF y superficie de derechos no aclarados, además de adaptaciones de tablas. | **Excluir.** |
| `models/life_expectancy_model.joblib` | Modelo entrenado con los cinco indicadores | Artefacto derivado de IMF y superficie, entre otras fuentes. No se considera libre por ser un modelo. | **Excluir.** Requiere autorización para toda la combinación de entrenamiento. |
| `outputs/figures/life_expectancy_histogram.png` | UN WPP y tabla Wikipedia | Atribuir WPP 2024 y la tabla; indicar que la visualización es una transformación; CC BY 3.0 IGO y términos CC BY-SA aplicables. | **Excluido por ahora** hasta distribuirlo con aviso de atribución/ShareAlike adjunto al artefacto. |
| `outputs/figures/population_vs_life_expectancy.png` | UN WPP (población y esperanza de vida), Wikipedia | Atribuir ambas páginas/tablas, WPP 2024 y transformación; respetar CC BY 3.0 IGO y CC BY-SA. | **Excluido por ahora** hasta adjuntar aviso de atribución/ShareAlike. |
| `outputs/figures/life_expectancy_by_continent.png` | UN WPP y región continental de tabla ONU/Wikipedia | Atribuir WPP y las tablas utilizadas; indicar transformación y ShareAlike aplicable. | **Excluido por ahora** hasta adjuntar aviso de atribución/ShareAlike. |
| `outputs/figures/fertility_rate_vs_life_expectancy.png` | Gapminder/OWID, UN WPP y Wikipedia | Atribuir Gapminder, fuente original, UN/WPP y páginas; indicar cambios y cumplir ShareAlike de la tabla. | **Excluido por ahora** hasta adjuntar aviso completo. |
| `outputs/figures/gdp_per_capita_ppp_vs_life_expectancy.png` | IMF WEO, UN WPP y Wikipedia | Atribución IMF/UN/Wikipedia, transformación declarada; la reutilización comercial IMF requiere permiso. | **Excluir** hasta resolver permiso/condiciones IMF y agregar aviso de fuente. |
| `outputs/figures/correlation_matrix.png` | Los cinco indicadores | Mezcla IMF y superficie no aclarada; además adaptación de tablas. | **Excluir.** |
| `outputs/tables/correlations.csv`, `descriptive_statistics.csv` | Todos los indicadores, incluido área e IMF | Estadísticas derivadas; derechos de área y términos IMF aún limitan la redistribución. | **Excluir.** |
| `outputs/tables/indicator_extremes.csv`, `country_match_audit.csv` | Filas y valores por país de varias fuentes | Datos derivados a nivel de país, incluyen fuentes con términos no aclarados. | **Excluir.** |
| `outputs/reports/extraction_report.json` | URLs, encabezados/tablas seleccionados, años y conteos; no incluye valores de indicadores | Atribuir las páginas enlazadas y reconocer IMF donde se reportan conteos; no está cubierto por MIT. | **Incluible con atribución** como metadatos de procedencia. |
| `outputs/reports/data_quality.json` | Conteos, cobertura y emparejamientos de todas las fuentes | Agregado derivado que involucra IMF y área. | **Excluir por ahora.** |
| `outputs/reports/analysis_summary.json`, `analysis_report.md` | EDA de todos los indicadores | Incluye asociaciones con IMF y superficie. | **Excluir.** |
| `outputs/reports/model_metrics.json`, `model_report.md` | Modelo y prueba sobre datos mixtos | Métricas derivadas del modelo; no se redistribuyen independientemente de los derechos del modelo/datos. | **Excluir con el modelo.** |
| `docs/resultados.md`, `conclusiones.md`, `auditoria_final.md`, `bitacora.md` | Narrativa de resultados y métricas del análisis | Contienen resultados derivados de varias fuentes; el MIT no se aplica a esos datos. | **Excluidos por ahora** del repositorio mediante `.gitignore`; permanecen en el directorio local. |
| `docs/fuentes_y_terminos.md`, `metodologia.md`, `diccionario_datos.md`, `auditoria_licencias.md` | Descripciones, metodología, esquemas y avisos | Texto de proyecto con enlaces/atribuciones; no concede licencias sobre datos terceros. | **Incluir**, manteniendo las atribuciones y avisos. |
| `README.md`, `requirements.txt`, `.gitignore`, `.gitkeep` | Proyecto propio/metadatos de ejecución | README separa MIT de datos y explica artefactos excluidos. | **Incluir.** |
| `outputs/reports/project.log`, cachés, temporales y entornos | Trazas locales o artefactos reproducibles | No son entregables; el log puede revelar rutas locales. | **Excluir** mediante `.gitignore`. |

## Estado de `app.py` y regeneración local

`app.py` necesita `models/life_expectancy_model.joblib`, `outputs/reports/model_metrics.json` y figuras. El modelo y los reportes estadísticos se mantienen fuera del repositorio mientras sus derechos no estén aclarados. Para regenerarlos localmente, y solo si el acceso y la licencia de cada fuente lo permiten:

```bash
python main.py --all
streamlit run app.py
```

No se documenta descarga de un modelo desde terceros: no existe un modelo remoto aprobado para redistribución. `LICENSE` no cubre ninguno de esos artefactos.
