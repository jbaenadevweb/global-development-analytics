from __future__ import annotations

import re
import unicodedata

import pandas as pd


ALIASES = {
    "united states": "united states",
    "united states of america": "united states",
    "usa": "united states",
    "russian federation": "russia",
    "russia": "russia",
    "iran, islamic republic of": "iran",
    "iran": "iran",
    "viet nam": "vietnam",
    "vietnam": "vietnam",
    "bolivia (plurinational state of)": "bolivia",
    "bolivia": "bolivia",
    "venezuela (bolivarian republic of)": "venezuela",
    "venezuela": "venezuela",
    "republic of korea": "south korea",
    "south korea": "south korea",
    "korea, republic of": "south korea",
    "democratic people's republic of korea": "north korea",
    "north korea": "north korea",
    "taiwan, province of china": "taiwan",
    "taiwan": "taiwan",
    "czech republic": "czechia",
    "czechia": "czechia",
    "ivory coast": "côte d'ivoire",
    "cote d'ivoire": "côte d'ivoire",
    "côte d'ivoire": "côte d'ivoire",
    "dr congo": "democratic republic of the congo",
    "democratic republic of congo": "democratic republic of the congo",
    "congo, democratic republic of the": "democratic republic of the congo",
    "congo": "republic of the congo",
    "republic of congo": "republic of the congo",
    "eswatini": "eswatini",
    "swaziland": "eswatini",
    "turkiye": "turkey",
    "türkiye": "turkey",
    "turkey": "turkey",
    "micronesia": "micronesia",
    "micronesia, federated states of": "micronesia",
    "palestine": "palestine",
    "state of palestine": "palestine",
    "the gambia": "gambia",
    "reunion (france)": "reunion",
    "hong kong sar, china": "hong kong",
    "hong kong": "hong kong",
    "macau": "macau",
    "macao": "macau",
}


def normalize_country(value: object) -> str | None:
    """Conservatively normalize country labels; never fuzzy-match unrelated names."""
    if pd.isna(value):
        return None
    text = str(value).strip()
    text = re.sub(r"\[[^\]]*\]", "", text)
    text = re.sub(r"[\s\u00a0]*[*†‡⁎#]+$", "", text)
    text = re.sub(r"\([^)]*(?:estimate|census|disputed|claim)[^)]*\)", "", text, flags=re.I)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.replace("’", "'").replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text).strip(" ,;")
    key = text.casefold()
    if not key or key in {
        "total", "world", "earth", "antarctica", "africa", "asia", "europe", "oceania"
    }:
        return None
    return ALIASES.get(key, key)
