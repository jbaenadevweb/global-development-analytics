"""Configuración de fuentes HTML documentadas."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    key: str
    url: str
    country_terms: tuple[str, ...]
    value_terms: tuple[str, ...]
    output_column: str
    year_column: str
    statistic_source: str
    preferred_column_terms: tuple[str, ...] = ()
    preferred_year: int | None = None
    static_indicator: bool = False


SOURCES = (
    Source(
        "life_expectancy",
        "https://en.wikipedia.org/wiki/List_of_countries_by_life_expectancy",
        ("country", "countries", "location", "entity"),
        ("overall", "total", "life expectancy", "estimate", "years"),
        "life_expectancy",
        "reference_year_life_expectancy",
        "United Nations, World Bank Group, WHO or CIA, as indicated in table",
        ("life expectancy overall", "at birth"),
        2023,
    ),
    Source(
        "gdp_per_capita_ppp",
        "https://en.wikipedia.org/wiki/List_of_countries_by_past_and_projected_GDP_(PPP)_per_capita",
        ("country", "countries", "economy", "territory", "entity"),
        ("2023",),
        "gdp_per_capita_ppp",
        "reference_year_gdp",
        "International Monetary Fund, World Economic Outlook",
        ("2023",),
        2023,
    ),
    Source(
        "population",
        "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)",
        ("country", "countries", "location", "entity", "state"),
        ("population", "2023"),
        "population",
        "reference_year_population",
        "United Nations World Population Prospects (2024 revision)",
        ("population", "2023"),
        2023,
    ),
    Source(
        "fertility_rate",
        "https://en.wikipedia.org/wiki/List_of_countries_by_fertility_rate",
        ("country", "countries", "location", "entity"),
        ("fertility", "births", "rate", "2023"),
        "fertility_rate",
        "reference_year_fertility",
        "Source cited in the fertility table",
        ("2023",),
        2023,
    ),
    Source(
        "land_area",
        "https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_area",
        ("country", "countries", "location", "entity", "state"),
        ("area", "land", "km2", "km²"),
        "land_area",
        "reference_year_area",
        "Country-specific citations in the Wikipedia area table; source varies by row",
        ("land in km2",),
        None,
        True,
    ),
)
