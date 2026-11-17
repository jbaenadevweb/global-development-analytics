# Metodología

## Problema y objetivos

La esperanza de vida varía junto con condiciones económicas, demográficas y geográficas. El objetivo académico es estudiar esas asociaciones con datos públicos recolectados exclusivamente de tablas HTML y evaluar, si la cobertura lo permite, un modelo de regresión de esperanza de vida.

Objetivos específicos: (1) extraer tablas HTML de forma responsable; (2) limpiar e integrar con Pandas; (3) explorar distribuciones y asociaciones; (4) comparar regresores; (5) ajustar hiperparámetros con GridSearchCV y validación cruzada de cinco particiones; (6) interpretar métricas y límites.

## Obtención y unión

Se hace GET de páginas HTTPS, después de comprobar robots.txt, y se verifica existencia de `<table>` con BeautifulSoup. `pandas.read_html` obtiene tablas. El selector usa encabezados identificables y conserva nombre de tabla/columnas elegidos en un reporte de extracción. Cada fuente produce CSV separado en `data/raw/`; la fecha de extracción se registra en UTC.

Nombres de países: Unicode y anotaciones de referencia se normalizan, se aplica un diccionario explícito de alias y luego se hace unión exacta. No se aplican coincidencias aproximadas. Las dependencias y territorios solo se conservan si los nombres coinciden; se documentan conteos de cobertura.

## Limpieza y temporalidad

Se convierten separadores de miles y valores numéricos, se eliminan duplicados por clave de país y se aplican rangos plausibles amplios. Observaciones fuera de rango se convierten a faltantes y se reportan, no se eliminan silenciosamente. El objetivo faltante no se imputa.

Cada variable mantiene un año individual. La tabla histórica de PIB permite seleccionar 2023; la tabla de fertilidad contiene explícitamente 2023; la tabla de población ONU permite seleccionar el 1 de julio de 2023. La elegibilidad temporal para ML exige que los predictores variables tengan año identificable, no posterior al objetivo y a no más de cinco años anteriores. Área es una característica geográfica estática y no se interpreta como indicador anual. Esta regla es pragmática y no elimina sesgos de diferencias de fuente.

## Análisis exploratorio

Se generan histograma del objetivo, dispersiones de PIB, fertilidad y población, matriz de correlación y boxplot por continente solo si existe una columna continental verificada. Población se grafica en escala logarítmica. Se entregan estadísticas descriptivas y correlaciones; no se interpretan como causalidad.

## Machine Learning

Objetivo `life_expectancy`; identificadores nunca son predictores. Features candidatas: GDP PPP per capita, población, fertilidad y área, limitadas a las disponibles, completas y temporalmente admisibles. PIB y población usan `log1p` por asimetría; escalado estándar solo para regresión lineal.

Separación test 80/20 con random_state 42. Modelos: regresión lineal, árbol, bosque aleatorio; HistGradientBoosting se contempla desde 80 casos. Modelos se comparan con KFold de cinco folds sobre entrenamiento. El de menor MAE CV pasa a GridSearchCV; métricas MAE, RMSE, R² se calculan en test. El flujo se detiene con menos de 30 observaciones; no se fabrican datos.

## Limitaciones

Las listas agregan fuentes estadísticas diferentes, pueden variar en definiciones, cobertura, unidades y años. Hay errores de correspondencia, territorios no soberanos, valores estimados y cambios entre ediciones. La restricción de cinco años no garantiza comparabilidad. Un split aleatorio por país no mide extrapolación temporal. La cantidad de países y la selección de países completos pueden sesgar los resultados. Una predicción no reemplaza una estadística oficial ni permite inferir causalidad.
