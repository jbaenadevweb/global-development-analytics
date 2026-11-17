from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

from src.features.build_features import select_model_data
from src.models.evaluate import regression_metrics

ROOT = Path(__file__).resolve().parents[2]
MINIMUM_SAMPLE = 30
RANDOM_STATE = 42


def run_training() -> dict:
    path = ROOT / "data" / "processed" / "country_indicators.csv"
    if not path.exists():
        raise FileNotFoundError("Ejecute primero: python main.py --stage clean")
    frame = pd.read_csv(path)
    data, features = select_model_data(frame)
    if len(data) < MINIMUM_SAMPLE:
        raise RuntimeError(
            f"Entrenamiento detenido: solo {len(data)} observaciones completas y temporalmente compatibles; "
            f"se requieren al menos {MINIMUM_SAMPLE}. No se generan filas artificiales."
        )
    X, y = data[features], data["life_expectancy"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )
    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    models = {
        "LinearRegression": Pipeline([("scale", StandardScaler()), ("model", LinearRegression())]),
        "DecisionTreeRegressor": Pipeline(
            [("model", DecisionTreeRegressor(random_state=RANDOM_STATE))]
        ),
        "RandomForestRegressor": Pipeline(
            [("model", RandomForestRegressor(random_state=RANDOM_STATE, n_estimators=200))]
        ),
    }
    if len(data) >= 80:
        models["HistGradientBoostingRegressor"] = Pipeline(
            [("model", HistGradientBoostingRegressor(random_state=RANDOM_STATE))]
        )
    cv_results = {}
    for name, model in models.items():
        scores = cross_validate(
            model, X_train, y_train, cv=cv,
            scoring={"mae": "neg_mean_absolute_error", "rmse": "neg_root_mean_squared_error", "r2": "r2"},
        )
        cv_results[name] = {
            "mae_mean": float(-scores["test_mae"].mean()),
            "rmse_mean": float(-scores["test_rmse"].mean()),
            "r2_mean": float(scores["test_r2"].mean()),
        }
    base_name = min(cv_results, key=lambda name: cv_results[name]["mae_mean"])
    from src.models.tune import tune_model

    tuned, tuning = tune_model(base_name, models[base_name], X_train, y_train, cv)
    base = models[base_name].fit(X_train, y_train)
    base_metrics = regression_metrics(y_test, base.predict(X_test))
    tuned_metrics = regression_metrics(y_test, tuned.predict(X_test))
    results = {
        "n_observations": int(len(data)),
        "features": features,
        "cv_folds": 5,
        "cv": cv_results,
        "selected_base_model": base_name,
        "base_test_metrics": base_metrics,
        "optimized_test_metrics": tuned_metrics,
        "tuning": tuning,
        "random_state": RANDOM_STATE,
        "interpretation": "Las métricas miden ajuste predictivo y no implican causalidad.",
    }
    (ROOT / "models").mkdir(exist_ok=True)
    (ROOT / "outputs" / "reports").mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": tuned, "features": features}, ROOT / "models" / "life_expectancy_model.joblib")
    (ROOT / "outputs" / "reports" / "model_metrics.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (ROOT / "outputs" / "reports" / "model_report.md").write_text(
        "# Evaluación del modelo\n\n"
        f"- Observaciones: {len(data)}\n- Predictores: {', '.join(features)}\n"
        "- Validación cruzada: 5 particiones\n\n"
        f"- Métricas del modelo base: `{base_metrics}`\n"
        f"- Métricas optimizadas: `{tuned_metrics}`\n"
        f"- Mejores parámetros: `{tuning['best_params']}`\n",
        encoding="utf-8",
    )
    return results
