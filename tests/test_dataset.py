import pandas as pd

from src.data import make_dataset
from src.scraping.sources import SOURCES


def test_dataset_concat_and_pivot_use_exact_normalized_country_keys(tmp_path, monkeypatch):
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    source_values = {
        "life_expectancy": [70.0, 80.0],
        "gdp_per_capita_ppp": [1000.0, 2000.0],
        "population": [10000.0, 20000.0],
        "fertility_rate": [2.0, 3.0],
        "land_area": [100.0, 200.0],
    }
    for source in SOURCES:
        pd.DataFrame(
            {
                "country": ["United States", "Exampleland"],
                "country_raw": ["United States", "Exampleland"],
                source.output_column: source_values[source.output_column],
                source.year_column: [2023, 2023],
            }
        ).to_csv(raw / f"{source.key}.csv", index=False)
    monkeypatch.setattr(make_dataset, "ROOT", tmp_path)
    monkeypatch.setattr(make_dataset, "INTERIM", tmp_path / "data" / "interim")
    monkeypatch.setattr(make_dataset, "PROCESSED", tmp_path / "data" / "processed")
    original_concat = pd.concat
    concatenated_indicator_frames = []

    def track_concat(objects, *args, **kwargs):
        result = original_concat(objects, *args, **kwargs)
        if {"country", "indicator", "value", "year", "source"}.issubset(result.columns):
            concatenated_indicator_frames.append(result.copy())
        return result

    monkeypatch.setattr(make_dataset.pd, "concat", track_concat)
    dataset, report = make_dataset.build_dataset()
    long_data = pd.read_csv(tmp_path / "data" / "interim" / "country_indicators_long.csv")
    assert set(dataset.country) == {"united states", "exampleland"}
    assert report["countries_with_all_five_indicators"] == 2
    assert set(dataset["temporal_compatible"]) == {True}
    assert len(concatenated_indicator_frames) == 1
    assert len(long_data) == 10
    assert not long_data.duplicated(["country", "indicator"]).any()
    assert set(long_data["indicator"]) == {source.output_column for source in SOURCES}
    assert long_data["value"].notna().all()
    assert long_data["source"].notna().all()
    assert long_data.loc[long_data["indicator"] != "land_area", "year"].eq(2023).all()
    assert long_data.loc[long_data["indicator"] == "land_area", "year"].isna().all()
    indexed_dataset = dataset.set_index("country")
    for source in SOURCES:
        expected = (
            long_data.loc[long_data["indicator"] == source.output_column]
            .set_index("country")["value"]
            .sort_index()
        )
        actual = indexed_dataset[source.output_column].dropna().sort_index()
        pd.testing.assert_series_equal(
            actual.rename("value"), expected, check_dtype=False, check_exact=True
        )
    gdp_row = long_data.loc[long_data["indicator"] == "gdp_per_capita_ppp"].iloc[0]
    assert gdp_row["year"] == 2023
    gdp_source = next(source for source in SOURCES if source.key == "gdp_per_capita_ppp")
    assert gdp_row["source"] == gdp_source.statistic_source
    assert gdp_row["source_url"] == gdp_source.url
    assert report["long_format_rows"] == 10
    assert report["long_format_unique_country_indicator_keys"] == 10
