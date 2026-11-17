from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.data.make_dataset import build_dataset
from src.scraping.fetch import FetchError, fetch_html
from src.scraping.parse import parse_source
from src.scraping.sources import SOURCES
from src.utils.logger import get_logger

ROOT = Path(__file__).resolve().parent
LOGGER = get_logger()


def scrape_stage() -> dict:
    raw_dir = ROOT / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    reports = []
    errors = []
    for source in SOURCES:
        try:
            html = fetch_html(source.url)
            extracted, report = parse_source(html, source)
            extracted.to_csv(raw_dir / f"{source.key}.csv", index=False)
            reports.append(report)
            LOGGER.info("%s: %s registros extraídos", source.key, len(extracted))
        except (FetchError, ValueError, pd.errors.ParserError) as exc:
            errors.append({"source": source.key, "url": source.url, "error": str(exc)})
            LOGGER.error("%s: %s", source.key, exc)
    summary = {
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources_ok": len(reports),
        "sources_failed": len(errors),
        "records_by_source": {item["source"]: item["records"] for item in reports},
        "reports": reports,
        "errors": errors,
    }
    (ROOT / "outputs" / "reports").mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs" / "reports" / "extraction_report.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if errors:
        raise RuntimeError(
            f"Scraping incompleto: {len(errors)} fuentes fallaron; vea outputs/reports/extraction_report.json"
        )
    return summary


def clean_stage() -> dict:
    _, report = build_dataset()
    path = ROOT / "outputs" / "reports" / "data_quality.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def run_stage(stage: str) -> None:
    if stage == "scrape":
        result = scrape_stage()
    elif stage == "clean":
        result = clean_stage()
    elif stage == "analyze":
        from src.analysis.exploratory import run_analysis

        result = run_analysis()
    elif stage == "train":
        from src.models.train import run_training

        result = run_training()
    else:
        raise ValueError(f"Etapa desconocida: {stage}")
    LOGGER.info("Etapa %s completada: %s", stage, json.dumps(result, ensure_ascii=False, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(description="Global Development Analytics")
    parser.add_argument("--stage", choices=["scrape", "clean", "analyze", "train"])
    parser.add_argument("--all", action="store_true", help="Ejecutar las cuatro etapas en orden")
    args = parser.parse_args()
    if args.all == bool(args.stage):
        parser.error("Indique exactamente una opción: --stage ETAPA o --all")
    stages = ["scrape", "clean", "analyze", "train"] if args.all else [args.stage]
    for stage in stages:
        run_stage(stage)


if __name__ == "__main__":
    main()
