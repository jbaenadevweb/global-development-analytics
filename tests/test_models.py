import numpy as np
import pandas as pd
import pytest
import joblib

from src.models.evaluate import regression_metrics
from src.models.tune import tune_model
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def test_metrics_and_five_fold_grid_search():
    x = np.arange(50, dtype=float).reshape(-1, 1)
    y = 2 * x.ravel() + 1
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    model, report = tune_model("LinearRegression", LinearRegression(), x, y, cv)
    assert len(list(cv.split(x))) == 5
    assert report["grid_candidates"] == 2
    assert regression_metrics(y, model.predict(x))["mae"] < 1e-8


def test_training_guard_rejects_fewer_than_thirty_rows(tmp_path, monkeypatch):
    from src.models import train

    frame = pd.DataFrame(
        {
            "life_expectancy": np.linspace(60, 80, 29),
            "gdp_per_capita_ppp": np.linspace(1000, 30000, 29),
            "population": np.linspace(10000, 2_000_000, 29),
            "fertility_rate": np.linspace(1, 5, 29),
            "land_area": np.linspace(10, 100000, 29),
            "temporal_compatible": True,
        }
    )
    processed = tmp_path / "data" / "processed"
    processed.mkdir(parents=True)
    frame.to_csv(processed / "country_indicators.csv", index=False)
    monkeypatch.setattr(train, "ROOT", tmp_path)
    with pytest.raises(RuntimeError, match="se requieren al menos 30"):
        train.run_training()


def test_pipeline_serialization_preserves_predictions(tmp_path):
    x = pd.DataFrame({"x": np.arange(20, dtype=float)})
    y = 3 * x["x"] + 2
    pipeline = Pipeline([("scale", StandardScaler()), ("model", LinearRegression())]).fit(x, y)
    expected = pipeline.predict(pd.DataFrame({"x": [4.5]}))
    path = tmp_path / "pipeline.joblib"
    joblib.dump(pipeline, path)
    restored = joblib.load(path)
    np.testing.assert_allclose(restored.predict(pd.DataFrame({"x": [4.5]})), expected)
