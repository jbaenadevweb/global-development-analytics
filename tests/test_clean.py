import pandas as pd

from src.data.clean import clean_dataset, to_numeric
from src.utils.validators import normalize_country


def test_country_aliases_and_conservative_normalization():
    assert normalize_country("United States of America") == "united states"
    assert normalize_country("Korea, Republic of") == "south korea"
    assert normalize_country("Réunion (France)") == "reunion"
    assert normalize_country("Europe") is None
    assert normalize_country("Oceania") is None
    assert normalize_country("Unknown territory") == "unknown territory"


def test_numeric_conversion_and_quality_report():
    assert to_numeric(pd.Series(["1,234", "3.5", "unknown"])).tolist()[:2] == [1234.0, 3.5]
    source = pd.DataFrame(
        {"country": ["A", "A", "B"], "life_expectancy": [80, 81, 200], "population": [100, 200, 300]}
    )
    cleaned, report = clean_dataset(source)
    assert len(cleaned) == 2
    assert report["duplicate_countries_removed"] == 1
    assert pd.isna(cleaned.loc[cleaned.country == "b", "life_expectancy"]).all()
