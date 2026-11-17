from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.clean import clean_dataset
from src.scraping.sources import SOURCES
from src.utils.validators import normalize_country


ROOT = Path(__file__).resolve().parents[2]
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"


def build_dataset() -> tuple[pd.DataFrame, dict]:
    """Stack indicators in long form, then pivot them to one exact country row."""
    frames = []
    long_frames = []
    source_counts = {}
    normalized_duplicates = {}
    for source in SOURCES:
        path = ROOT / "data" / "raw" / f"{source.key}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Falta el resultado de scraping: {path}")
        frame = pd.read_csv(path)
        if "country" not in frame:
            raise ValueError(f"{path} no contiene columna country")
        if source.output_column not in frame:
            raise ValueError(f"{path} no contiene el indicador {source.output_column}")
        if "country_raw" not in frame:
            frame["country_raw"] = frame["country"]
        frame["country"] = frame["country"].map(normalize_country)
        frame = frame.dropna(subset=["country"])
        normalized_duplicates[source.key] = int(frame["country"].duplicated().sum())
        frame = frame.drop_duplicates("country", keep="first")
        frames.append(frame)
        source_counts[source.key] = len(frame)

        def values_or_default(column: str, default):
            if column in frame:
                return frame[column].to_numpy()
            return [default] * len(frame)

        years = (
            pd.to_numeric(frame[source.year_column], errors="coerce").to_numpy()
            if source.year_column in frame and not source.static_indicator
            else [pd.NA] * len(frame)
        )
        long_frames.append(
            pd.DataFrame(
                {
                    "country": frame["country"].to_numpy(),
                    "indicator": source.output_column,
                    "value": pd.to_numeric(frame[source.output_column], errors="coerce").to_numpy(),
                    "year": years,
                    "source": values_or_default("statistic_source", source.statistic_source),
                    "source_url": values_or_default("source_url", source.url),
                    "country_raw": values_or_default("country_raw", ""),
                    "extracted_at_utc": values_or_default("extracted_at_utc", pd.NA),
                    "table_citations": values_or_default("table_citations", pd.NA),
                    "continent": values_or_default("continent", pd.NA),
                }
            )
        )

    # A real vertical union: each source contributes one row per country-indicator.
    long_dataset = pd.concat(long_frames, ignore_index=True, sort=False)
    long_dataset["year"] = pd.to_numeric(long_dataset["year"], errors="coerce")
    expected_indicators = {source.output_column for source in SOURCES}
    if long_dataset["indicator"].isna().any() or not set(long_dataset["indicator"]).issubset(expected_indicators):
        raise ValueError("Formato largo contiene indicadores vacíos o no configurados")
    if long_dataset["country"].isna().any():
        raise ValueError("Formato largo contiene países sin llave normalizada")
    duplicate_keys = long_dataset.duplicated(["country", "indicator"], keep=False)
    if duplicate_keys.any():
        examples = long_dataset.loc[duplicate_keys, ["country", "indicator"]].head().to_dict("records")
        raise ValueError(f"Claves country/indicator duplicadas en formato largo: {examples}")

    # Pivot the measured values to the model's one-row-per-country schema.
    indicator_order = [source.output_column for source in SOURCES]
    country_order = sorted(long_dataset["country"].unique())
    dataset = (
        long_dataset.pivot(index="country", columns="indicator", values="value")
        .reindex(index=country_order, columns=indicator_order)
    )
    dataset.columns.name = None

    # Keep year and provenance as indicator-specific columns alongside the wide values.
    for source in SOURCES:
        indicator_rows = long_dataset.loc[long_dataset["indicator"] == source.output_column]
        indicator_rows = indicator_rows.drop_duplicates("country").set_index("country")
        dataset[source.year_column] = indicator_rows["year"].reindex(dataset.index)
        dataset[f"country_raw_{source.key}"] = indicator_rows["country_raw"].reindex(dataset.index)
        dataset[f"extracted_at_{source.key}"] = indicator_rows["extracted_at_utc"].reindex(dataset.index)
        dataset[f"source_url_{source.key}"] = indicator_rows["source_url"].reindex(dataset.index)
        dataset[f"statistic_source_{source.key}"] = indicator_rows["source"].reindex(dataset.index)
        dataset[f"table_citations_{source.key}"] = indicator_rows["table_citations"].reindex(dataset.index)
        if source.key == "population":
            dataset["continent"] = indicator_rows["continent"].reindex(dataset.index)

    dataset = dataset.reset_index()
    column_order = ["country"]
    for source in SOURCES:
        column_order.extend(
            [
                f"country_raw_{source.key}",
                source.output_column,
                source.year_column,
                f"extracted_at_{source.key}",
                f"source_url_{source.key}",
            ]
        )
        if source.key == "population":
            column_order.append("continent")
        column_order.extend(
            [f"statistic_source_{source.key}", f"table_citations_{source.key}"]
        )
    dataset = dataset[column_order]
    country_raw_cols = [column for column in dataset if column.startswith("country_raw_")]
    dataset["country"] = dataset["country"].astype(str)
    dataset["country_match_method"] = "normalized exact match; no fuzzy matching"
    dataset["temporal_compatible"] = _temporal_compatibility(dataset)
    cleaned, quality = clean_dataset(dataset)
    quality["source_record_counts"] = source_counts
    quality["normalized_duplicate_countries_removed_by_source"] = normalized_duplicates
    quality["long_format_rows"] = int(len(long_dataset))
    quality["long_format_unique_country_indicator_keys"] = int(
        long_dataset[["country", "indicator"]].drop_duplicates().shape[0]
    )
    quality["long_format_missing_values_by_indicator"] = {
        key: int(value)
        for key, value in long_dataset.groupby("indicator")["value"].apply(lambda values: values.isna().sum()).items()
    }
    quality["countries_in_union"] = int(dataset["country"].nunique())
    quality["countries_with_all_five_indicators"] = int(
        dataset[[source.output_column for source in SOURCES]].notna().all(axis=1).sum()
    )
    quality["countries_temporally_compatible"] = int(dataset["temporal_compatible"].sum())
    target_countries = set(frames[0]["country"])
    quality["countries_with_target"] = int(dataset["life_expectancy"].notna().sum())
    quality["countries_without_target"] = int(dataset["life_expectancy"].isna().sum())
    quality["exact_country_overlap_with_target"] = {
        source.key: int(len(target_countries.intersection(set(frame["country"]))))
        for source, frame in zip(SOURCES, frames)
    }
    quality["country_matching"] = "explicit alias normalization followed by exact equality; no fuzzy matches"
    quality["country_raw_columns"] = country_raw_cols
    INTERIM.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs" / "tables").mkdir(parents=True, exist_ok=True)
    audit = dataset[["country"] + [source.output_column for source in SOURCES]].copy()
    audit["sources_present"] = audit[[source.output_column for source in SOURCES]].notna().sum(axis=1)
    audit.to_csv(ROOT / "outputs" / "tables" / "country_match_audit.csv", index=False)
    long_dataset.to_csv(INTERIM / "country_indicators_long.csv", index=False)
    dataset.to_csv(INTERIM / "country_indicators_unchecked.csv", index=False)
    cleaned.to_csv(PROCESSED / "country_indicators.csv", index=False)
    return cleaned, quality


def _temporal_compatibility(frame: pd.DataFrame) -> pd.Series:
    years = [
        "reference_year_life_expectancy",
        "reference_year_gdp",
        "reference_year_population",
        "reference_year_fertility",
    ]
    existing = [column for column in years if column in frame]
    if "reference_year_life_expectancy" not in existing:
        return pd.Series(False, index=frame.index)
    life_year = pd.to_numeric(frame["reference_year_life_expectancy"], errors="coerce")
    valid = life_year.notna()
    for column in existing:
        if column == "reference_year_life_expectancy":
            continue
        year = pd.to_numeric(frame[column], errors="coerce")
        # Inputs must not come from after the target year; tolerate at most five years.
        valid &= year.notna() & (year <= life_year) & ((life_year - year) <= 5)
    # Area is a static geographic attribute and is not treated as a dated annual observation.
    return valid
