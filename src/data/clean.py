from __future__ import annotations

import re

import pandas as pd

from src.utils.validators import normalize_country

NUMERIC_COLUMNS = (
    "life_expectancy",
    "gdp_per_capita_ppp",
    "population",
    "fertility_rate",
    "land_area",
)


def to_numeric(series: pd.Series) -> pd.Series:
    def parse(value):
        if pd.isna(value):
            return float("nan")
        text = str(value).replace(",", "").replace("\u00a0", " ").strip()
        text = re.sub(r"\[[^\]]*\]", "", text)
        match = re.search(r"-?\d+(?:\.\d+)?", text)
        return float(match.group()) if match else float("nan")

    return series.map(parse)


def clean_dataset(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    cleaned = frame.copy()
    original_rows = len(cleaned)
    if "country" not in cleaned.columns:
        raise ValueError("El dataset requiere la columna country")
    cleaned["country"] = cleaned["country"].map(normalize_country)
    cleaned = cleaned.dropna(subset=["country"])
    for column in NUMERIC_COLUMNS:
        if column in cleaned:
            cleaned[column] = to_numeric(cleaned[column])
    before_dedup = len(cleaned)
    cleaned = cleaned.drop_duplicates("country", keep="first")
    duplicates = before_dedup - len(cleaned)
    impossible = {}
    bounds = {
        "life_expectancy": (20, 110),
        "gdp_per_capita_ppp": (0, 1_000_000),
        "population": (1, 10_000_000_000),
        "fertility_rate": (0, 15),
        "land_area": (0.01, 20_000_000),
    }
    for column, (low, high) in bounds.items():
        if column in cleaned:
            invalid = cleaned[column].notna() & ((cleaned[column] < low) | (cleaned[column] > high))
            impossible[column] = int(invalid.sum())
            cleaned.loc[invalid, column] = float("nan")
    target_missing = int(cleaned.get("life_expectancy", pd.Series(index=cleaned.index, dtype=float)).isna().sum())
    report = {
        "rows_original": int(original_rows),
        "rows_after_country_validation": int(before_dedup),
        "duplicate_countries_removed": int(duplicates),
        "rows_final": int(len(cleaned)),
        "missing_by_column": {key: int(value) for key, value in cleaned.isna().sum().items()},
        "implausible_values_set_missing": impossible,
        "missing_target_rows_not_imputed": target_missing,
    }
    return cleaned.reset_index(drop=True), report
