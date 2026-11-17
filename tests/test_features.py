import pandas as pd

from src.features.build_features import select_model_data


def test_feature_selection_excludes_future_or_missing_rows():
    frame = pd.DataFrame(
        {
            "life_expectancy": [70, 80, 90],
            "gdp_per_capita_ppp": [1000, 2000, 3000],
            "population": [10, 20, 30],
            "fertility_rate": [2, 3, None],
            "land_area": [100, 200, 300],
            "temporal_compatible": [True, False, True],
        }
    )
    selected, features = select_model_data(frame)
    assert len(selected) == 1
    assert "log_population" in features
    assert "life_expectancy" not in features
