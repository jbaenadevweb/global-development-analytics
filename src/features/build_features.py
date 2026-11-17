import numpy as np
import pandas as pd

FEATURE_CANDIDATES = ["gdp_per_capita_ppp", "population", "fertility_rate", "land_area"]


def select_model_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    if "temporal_compatible" not in frame:
        raise ValueError("Falta temporal_compatible; ejecute la integración primero")
    features = [column for column in FEATURE_CANDIDATES if column in frame.columns]
    selected = frame.loc[frame["temporal_compatible"].fillna(False)].copy()
    selected = selected.dropna(subset=["life_expectancy"] + features)
    if "gdp_per_capita_ppp" in features:
        selected["log_gdp_per_capita_ppp"] = np.log1p(selected["gdp_per_capita_ppp"])
        features[features.index("gdp_per_capita_ppp")] = "log_gdp_per_capita_ppp"
    if "population" in features:
        selected["log_population"] = np.log1p(selected["population"])
        features[features.index("population")] = "log_population"
    return selected, features
