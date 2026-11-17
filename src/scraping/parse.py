"""Selección auditable de tablas HTML y extracción de una variable."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from io import StringIO
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup

from src.scraping.sources import Source
from src.utils.validators import normalize_country


def _flat(value: Any) -> str:
    if isinstance(value, tuple):
        parts = [str(part).strip() for part in value if str(part).strip() and not str(part).startswith("Unnamed")]
        return " ".join(parts).strip()
    return str(value).strip()


def _clean_columns(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result.columns = [_flat(column) for column in result.columns]
    return result


def _match_column(columns: list[str], terms: tuple[str, ...], exclude: set[str] | None = None) -> str | None:
    exclude = exclude or set()
    ranked = []
    for column in columns:
        normalized = column.casefold()
        if column in exclude:
            continue
        score = sum(term in normalized for term in terms)
        if score:
            ranked.append((score, -len(column), column))
    return sorted(ranked, reverse=True)[0][2] if ranked else None


def _extract_year(text: str) -> int | None:
    years = [int(year) for year in re.findall(r"\b(?:19|20)\d{2}\b", text)]
    return years[-1] if years else None


def _row_year(value: object) -> int | None:
    if pd.isna(value):
        return None
    parsed = pd.to_datetime(str(value), errors="coerce")
    if pd.notna(parsed):
        return int(parsed.year)
    return _extract_year(str(value))


def _number(value: object) -> float | None:
    if pd.isna(value):
        return None
    text = str(value).replace(",", "").replace("\u00a0", " ").strip()
    text = re.sub(r"\[[^\]]*\]", "", text)
    text = re.sub(r"(?i)(?:years?|km(?:²|2)|international dollars?|usd|\$)", "", text)
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


def parse_source(html: str, source: Source, extracted_at: str | None = None) -> tuple[pd.DataFrame, dict]:
    """Parse the best matching actual HTML table into one canonical source frame."""
    soup = BeautifulSoup(html, "lxml")
    html_tables = soup.find_all("table")
    if not html_tables:
        raise ValueError(f"{source.key}: no HTML tables found")
    tables = pd.read_html(StringIO(html))
    if not tables:
        raise ValueError(f"{source.key}: pandas.read_html found no tables")
    candidates = []
    for index, raw_frame in enumerate(tables):
        frame = _clean_columns(raw_frame)
        columns = list(frame.columns)
        country_col = _match_column(columns, source.country_terms)
        if country_col is None and len(columns):
            first = columns[0]
            if any(word in first.casefold() for word in ("country", "location", "entity", "state")):
                country_col = first
        if country_col is None:
            continue
        value_col = _match_column(columns, source.preferred_column_terms, {country_col})
        if value_col is None:
            value_col = _match_column(columns, source.value_terms, {country_col})
        # If headers are generic (e.g. "2023"), use the first numeric-looking data column.
        if value_col is None:
            value_col = next((column for column in columns if column != country_col), None)
        if value_col is None:
            continue
        score = sum(term in " ".join(columns).casefold() for term in source.value_terms)
        if source.preferred_year and str(source.preferred_year) in str(value_col):
            score += 100
        if source.key == "life_expectancy" and "overall" in value_col.casefold() and "at birth" in value_col.casefold():
            score += 100
        candidates.append((score, len(frame), -index, frame, country_col, value_col, index))
    if not candidates:
        raise ValueError(f"{source.key}: no table with recognizable country and value columns")
    _, _, _, frame, country_col, value_col, table_index = max(candidates, key=lambda item: item[:3])
    table_element = html_tables[table_index]
    section = table_element.find_previous(["h2", "h3", "h4"])
    section_text = section.get_text(" ", strip=True) if section else ""
    caption = table_element.find("caption")
    caption_text = caption.get_text(" ", strip=True) if caption else ""
    local_context = " ".join([section_text, caption_text, value_col])
    reference_year = _extract_year(local_context)
    if source.preferred_year and (
        str(source.preferred_year) in value_col or source.key == "life_expectancy"
    ):
        reference_year = source.preferred_year
    date_col = _match_column(list(frame.columns), ("date", "year"))
    source_col = _match_column(list(frame.columns), ("source", "reference"))
    if source_col == country_col or source_col == value_col:
        source_col = None
    row_years = frame[date_col].map(_row_year) if date_col else pd.Series(reference_year, index=frame.index)
    source_context_is_specific = any(
        token in section_text.casefold()
        for token in ("united nations", "world health organization", "world bank", "imf", "cia", "who", "un:")
    )
    row_sources = frame[source_col].astype(str) if source_col else pd.Series(
        section_text if source_context_is_specific else source.statistic_source, index=frame.index
    )
    if caption_text and any(
        token in caption_text.casefold()
        for token in ("our world in data", "gapminder", "world population prospects", "world bank", "imf", "who", "united nations")
    ):
        row_sources = pd.Series(caption_text, index=frame.index)
    known_countries = set(frame[country_col].map(normalize_country).dropna())
    citation_map: dict[str, list[str]] = {}
    for html_row in table_element.find_all("tr"):
        cells = html_row.find_all(["th", "td"])
        row_country = next(
            (
                normalized
                for cell in cells
                if (normalized := normalize_country(cell.get_text(" ", strip=True))) in known_countries
            ),
            None,
        )
        if not row_country:
            continue
        references = []
        for reference in html_row.select("sup.reference a"):
            label = reference.get_text(" ", strip=True)
            if not label and reference.get("href"):
                label = reference["href"].rsplit("#", 1)[-1]
            if label:
                references.append(label)
        if references:
            citation_map[row_country] = list(dict.fromkeys(references))
    data = pd.DataFrame(
        {
            "country_raw": frame[country_col].astype(str).str.replace(r"\[.*?\]", "", regex=True).str.strip(),
            "country": frame[country_col].map(normalize_country),
            source.output_column: frame[value_col].map(_number),
            source.year_column: row_years,
            "statistic_source": row_sources,
            "source_url": source.url,
            "extracted_at_utc": extracted_at or datetime.now(timezone.utc).isoformat(),
        }
    )
    continent_col = _match_column(list(frame.columns), ("continental region", "continent"))
    if continent_col and continent_col not in {country_col, value_col}:
        data["continent"] = frame[continent_col].astype(str).str.strip()
        data.loc[data["continent"].str.casefold().isin({"nan", "", "none"}), "continent"] = pd.NA
    data["table_citations"] = data["country"].map(
        lambda key: "; ".join(citation_map.get(key, [])) if key in citation_map else pd.NA
    )
    has_citations = data["table_citations"].notna()
    data.loc[has_citations, "statistic_source"] = (
        data.loc[has_citations, "statistic_source"].astype(str)
        + " | table citations: "
        + data.loc[has_citations, "table_citations"].astype(str)
    )
    before_dedup = len(data)
    data = data.dropna(subset=["country", source.output_column]).drop_duplicates("country", keep="first")
    if source.static_indicator:
        data[source.year_column] = pd.NA
    if data.empty:
        raise ValueError(f"{source.key}: selected table produced no usable records")
    report = {
        "source": source.key,
        "url": source.url,
        "html_table_count": len(html_tables),
        "pandas_table_count": len(tables),
        "selected_table_index": table_index,
        "selected_columns": {"country": country_col, "value": value_col},
        "records": int(len(data)),
        "duplicates_removed": int(before_dedup - len(data)),
        "reference_year": reference_year,
        "year_source": "row date column" if date_col else ("selected column/section" if reference_year else "not declared"),
        "observed_year_counts": {
            str(year): int(count)
            for year, count in data[source.year_column].dropna().value_counts().sort_index().items()
        },
        "statistic_source_column": source_col,
        "rows_with_table_citations": int(has_citations.sum()),
    }
    return data.reset_index(drop=True), report
