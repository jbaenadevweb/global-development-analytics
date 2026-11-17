from pathlib import Path
import json

import pandas as pd

from src.features.build_features import FEATURE_CANDIDATES
from src.visualization.plots import create_eda_plots


ROOT = Path(__file__).resolve().parents[2]


def run_analysis() -> dict:
    path = ROOT / "data" / "processed" / "country_indicators.csv"
    if not path.exists():
        raise FileNotFoundError("Ejecute primero: python main.py --stage clean")
    frame = pd.read_csv(path)
    required = ["life_expectancy"] + [column for column in FEATURE_CANDIDATES if column in frame]
    analysis = frame[required].copy()
    analysis = analysis.dropna(subset=["life_expectancy"])
    (ROOT / "outputs" / "tables").mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs" / "reports").mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs" / "figures").mkdir(parents=True, exist_ok=True)
    analysis.describe().T.to_csv(ROOT / "outputs" / "tables" / "descriptive_statistics.csv")
    analysis.corr(numeric_only=True).to_csv(ROOT / "outputs" / "tables" / "correlations.csv")
    indicator_columns = ["life_expectancy"] + [column for column in FEATURE_CANDIDATES if column in frame]
    if "country" in frame:
        extremes = {}
        for column in indicator_columns:
            valid = frame[["country", column]].dropna()
            extremes[column] = pd.concat(
                [
                    valid.nsmallest(10, column).assign(extreme="lowest"),
                    valid.nlargest(10, column).assign(extreme="highest"),
                ],
                ignore_index=True,
            )
        pd.concat(
            [table.assign(indicator=column) for column, table in extremes.items()],
            ignore_index=True,
        ).to_csv(ROOT / "outputs" / "tables" / "indicator_extremes.csv", index=False)
    plots = create_eda_plots(frame, ROOT / "outputs" / "figures")
    report = {
        "rows_with_target": int(len(analysis)),
        "predictors_available": [column for column in FEATURE_CANDIDATES if column in frame],
        "missing_by_column": {key: int(value) for key, value in frame.isna().sum().items()},
        "target_summary": analysis["life_expectancy"].describe().to_dict(),
        "correlations_with_target": analysis.corr(numeric_only=True)["life_expectancy"].drop("life_expectancy", errors="ignore").to_dict(),
        "plots": plots,
        "continent_available": bool("continent" in frame and frame["continent"].notna().any()),
        "interpretation": "Las correlaciones son asociaciones descriptivas; no implican causalidad.",
    }
    (ROOT / "outputs" / "reports" / "analysis_summary.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    correlation_markdown = pd.Series(report["correlations_with_target"]).to_string()
    (ROOT / "outputs" / "reports" / "analysis_report.md").write_text(
        "# Informe de análisis exploratorio\n\n"
        f"- Países con objetivo disponible: {len(analysis)}\n"
        f"- Variables numéricas: {', '.join(required)}\n"
        "- Las asociaciones observadas no demuestran causalidad.\n\n"
        f"## Correlaciones con esperanza de vida\n\n```text\n{correlation_markdown}\n```\n",
        encoding="utf-8",
    )
    return report
