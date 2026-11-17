"""Interfaz Streamlit local para el modelo entrenado y validado."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "life_expectancy_model.joblib"
METRICS_PATH = ROOT / "outputs" / "reports" / "model_metrics.json"

st.set_page_config(page_title="Global Development Analytics", page_icon="🌍", layout="wide")
st.title("Global Development Analytics")
st.subheader("Estimación estadística de esperanza de vida")
st.write(
    "Proyecto académico de análisis de indicadores económicos y demográficos. "
    "La predicción no es un dato oficial ni sustituye estadísticas nacionales."
)

if not MODEL_PATH.exists() or not METRICS_PATH.exists():
    st.error("No existe un modelo entrenado válido. Ejecute primero `python main.py --stage train`.")
    st.stop()

artifact = joblib.load(MODEL_PATH)
pipeline = artifact["pipeline"]
features = artifact["features"]
metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

st.markdown("### Variables empleadas")
st.write(", ".join(features))
st.caption("El PIB per cápita PPP y la población se transforman con log(1 + x) en el preprocesamiento.")

st.markdown("### Métricas del modelo")
left, middle, right = st.columns(3)
left.metric("MAE (años)", f"{metrics['optimized_test_metrics']['mae']:.2f}")
middle.metric("RMSE (años)", f"{metrics['optimized_test_metrics']['rmse']:.2f}")
right.metric("R²", f"{metrics['optimized_test_metrics']['r2']:.3f}")
st.caption(
    f"Prueba reservada; validación cruzada de {metrics['cv_folds']} folds. "
    "Las métricas describen esta muestra y no garantizan rendimiento fuera de ella."
)

with st.expander("Gráficos del análisis exploratorio", expanded=True):
    figure_paths = sorted((ROOT / "outputs" / "figures").glob("*.png"))
    for path in figure_paths:
        st.image(str(path), caption=path.stem.replace("_", " ").title(), width="stretch")

st.markdown("### Estimar para un conjunto de indicadores")
with st.form("prediction_form"):
    gdp = st.number_input("PIB per cápita PPP (dólares internacionales)", min_value=0.0, value=15000.0, step=1000.0)
    population = st.number_input("Población (personas)", min_value=1.0, value=1_000_000.0, step=100_000.0)
    fertility = st.number_input("Tasa de fertilidad (nacimientos por mujer)", min_value=0.0, max_value=15.0, value=2.0, step=0.1)
    area = st.number_input("Superficie terrestre (km²)", min_value=1.0, value=100_000.0, step=10_000.0)
    submitted = st.form_submit_button("Calcular estimación")

if submitted:
    values = {
        "gdp_per_capita_ppp": gdp,
        "population": population,
        "fertility_rate": fertility,
        "land_area": area,
        "log_gdp_per_capita_ppp": float(np.log1p(gdp)),
        "log_population": float(np.log1p(population)),
    }
    input_frame = pd.DataFrame([{feature: values[feature] for feature in features}])
    prediction = float(pipeline.predict(input_frame)[0])
    st.success(f"Esperanza de vida estimada: **{prediction:.1f} años**")
    st.warning(
        "Estimación estadística no oficial. Las fuentes son transversales y pueden diferir en "
        "definiciones; no interpretar como causalidad ni como predicción individual."
    )
