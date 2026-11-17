# Global Development Analytics

**Título:** Análisis de indicadores económicos y demográficos para la estimación de la esperanza de vida mediante técnicas de Ciencia de Datos y Machine Learning.

Proyecto académico que obtiene tablas HTML públicas, integra indicadores por país, analiza su cobertura y, únicamente cuando la muestra y los años lo permiten, estima esperanza de vida con regresión. No utiliza APIs ni datasets descargados como fuente.

## Estado actual

El proyecto implementa scraping responsable de tablas HTML, limpieza, EDA, regresión y una interfaz Streamlit. Los productos que dependen de IMF o de superficie terrestre no se incluyen hasta aclarar sus condiciones. La extracción se detiene si `robots.txt` no se puede validar o no autoriza el acceso.

## Instalación

Se recomienda Python 3.11–3.13 y un entorno virtual local:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Dependencias

Las dependencias directas están declaradas en `requirements.txt`:

- Scraping de tablas HTML: `requests`, `beautifulsoup4`, `lxml`, `pandas`.
- Datos y visualización: `numpy`, `matplotlib`, `seaborn`.
- Modelado y serialización: `scikit-learn`, `joblib`.
- Pruebas e interfaz local: `pytest`, `streamlit`.

La instalación usa versiones compatibles por rango; no hay lockfile de versiones exactas.

## Ejecución

Desde la raíz:

```bash
python main.py --stage scrape
python main.py --stage clean
python main.py --stage analyze
python main.py --stage train
python main.py --all
python -m pytest -q
```

Para abrir la interfaz local después del entrenamiento:

```bash
streamlit run app.py
```

`--all` detiene el flujo al primer error y no marca etapas posteriores como completadas. Scraping hace una pausa entre solicitudes, declara un user-agent, aplica timeout y reintentos limitados, valida `robots.txt` y no reintenta respuestas HTTP 401/403/404/429.

## Artefactos

- `data/raw/`: las extracciones permanecen locales y se excluyen hasta cerrar la revisión de términos de redistribución de las tablas extraídas y sus fuentes subyacentes.
- `data/interim/` y `data/processed/`: se generan localmente; los CSV por país se excluyen del repositorio.
- `outputs/figures/`: los PNG derivados se generan localmente y se excluyen hasta cerrar la revisión de licencias y atribuciones por figura.
- `outputs/reports/extraction_report.json`: metadatos de procedencia. Reportes estadísticos y tablas derivados quedan excluidos.
- `models/`: el modelo `joblib` se conserva localmente pero no se incluye hasta aclarar los derechos de todas las fuentes de entrenamiento.

Para generar localmente los datos completos, el modelo, las figuras y los reportes de la aplicación, ejecuta `python main.py --all` cuando las páginas permitan acceso. El comando descarga las tablas HTML, valida `robots.txt` y no usa APIs. Después puedes lanzar Streamlit; si el modelo no está presente, la interfaz solicita ejecutar primero el entrenamiento.

## Metodología y cautelas

Los países se emparejan mediante normalización explícita de alias y comparación exacta; no se usa fuzzy matching. Se conserva año de referencia por indicador. Para ML, cada predictor debe ser del año objetivo o de hasta cinco años anteriores; se rechazan datos futuros. Se aplican transformaciones logarítmicas a PIB y población. Un mínimo de 30 filas completas es condición de parada, no garantía de generalización. La correlación no implica causalidad.

Fuentes, términos, limitaciones y decisiones: [`docs/fuentes_y_terminos.md`](docs/fuentes_y_terminos.md), [`docs/metodologia.md`](docs/metodologia.md), [`docs/diccionario_datos.md`](docs/diccionario_datos.md).

## Licencia y atribución

`LICENSE` aplica MIT únicamente al código propio. No aplica a datasets, contenido de terceros, figuras ni al modelo. El titular de copyright está pendiente de confirmación; reemplaza `[NOMBRE DEL TITULAR]` antes de publicar. Consulta [`docs/auditoria_licencias.md`](docs/auditoria_licencias.md) para fuentes, atribuciones, condiciones y artefactos excluidos.

## Interfaz local

La interfaz carga el artefacto entrenado existente, enseña métricas/gráficos y permite consultar una estimación estadística.
