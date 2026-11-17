from src.scraping.parse import parse_source
from src.scraping.sources import Source, SOURCES


def test_parse_realistic_html_table():
    source = Source("test", "https://example.org/table", ("country",), ("fertility",), "fertility_rate", "reference_year_fertility", "test")
    html = """
    <html><h2>Estimates for 2022</h2><table>
    <thead><tr><th>Country</th><th>Total fertility rate</th></tr></thead>
    <tbody><tr><td>United States</td><td>1.66<sup class="reference"><a href="#cite_note-1">[1]</a></sup></td></tr>
    <tr><td>Exampleland</td><td>3.2</td></tr></tbody></table></html>
    """
    data, report = parse_source(html, source, "2026-01-01T00:00:00+00:00")
    assert len(data) == 2
    assert data.iloc[0].fertility_rate == 1.66
    assert data.iloc[0].reference_year_fertility == 2022
    assert report["html_table_count"] == 1
    assert "[1]" in data.iloc[0].statistic_source


def test_life_expectancy_prefers_at_birth_not_age_80():
    source = next(item for item in SOURCES if item.key == "life_expectancy")
    html = """
    <html><h2>United Nations (2023)</h2><table>
    <thead><tr><th rowspan="2">Locations</th>
    <th colspan="2">Life expectancy overall</th><th>Male</th></tr>
    <tr><th>at birth</th><th>at 80</th><th>at birth</th></tr></thead>
    <tbody><tr><td>Exampleland</td><td>82.5</td><td>11.2</td><td>80.1</td></tr></tbody>
    </table></html>
    """
    data, report = parse_source(html, source, "2026-01-01T00:00:00+00:00")
    assert data.iloc[0].life_expectancy == 82.5
    assert report["reference_year"] == 2023
    assert report["selected_columns"]["value"] == "Life expectancy overall at birth"
