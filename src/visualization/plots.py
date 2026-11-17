from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def create_eda_plots(frame: pd.DataFrame, output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    generated = []
    target = frame.get("life_expectancy", pd.Series(dtype=float)).dropna()
    if target.empty:
        raise ValueError("No hay esperanza de vida válida para crear gráficos")
    fig, ax = plt.subplots()
    sns.histplot(target, kde=True, ax=ax)
    ax.set(title="Distribución de esperanza de vida", xlabel="Esperanza de vida (años)", ylabel="Países")
    fig.text(0.01, 0.01, "Interpretación: resume la distribución observada; no implica causalidad.", fontsize=8)
    generated.append(_save(fig, output_dir, "life_expectancy_histogram.png"))
    labels = {
        "gdp_per_capita_ppp": ("PIB per cápita PPP (dólares internacionales)", "PIB per cápita PPP vs esperanza de vida"),
        "fertility_rate": ("Tasa de fertilidad (nacimientos por mujer)", "Fertilidad vs esperanza de vida"),
        "population": ("Población (personas)", "Población vs esperanza de vida"),
    }
    for column, (xlabel, title) in labels.items():
        if column not in frame:
            continue
        subset = frame[[column, "life_expectancy"]].dropna()
        if subset.empty:
            continue
        fig, ax = plt.subplots()
        sns.scatterplot(data=subset, x=column, y="life_expectancy", ax=ax)
        if column == "population":
            ax.set_xscale("log")
        ax.set(title=title, xlabel=xlabel, ylabel="Esperanza de vida (años)")
        fig.text(0.01, 0.01, "Interpretación: asociación descriptiva; no implica causalidad.", fontsize=8)
        generated.append(_save(fig, output_dir, f"{column}_vs_life_expectancy.png"))
    numeric = frame.select_dtypes(include="number").corr()
    if not numeric.empty:
        fig, ax = plt.subplots(figsize=(9, 7))
        sns.heatmap(numeric, cmap="vlag", center=0, annot=True, fmt=".2f", ax=ax)
        ax.set_title("Matriz de correlación entre indicadores")
        fig.text(0.01, 0.01, "Interpretación: asociaciones lineales; no implican causalidad.", fontsize=8)
        generated.append(_save(fig, output_dir, "correlation_matrix.png"))
    if "continent" in frame and frame["continent"].notna().any():
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.boxplot(data=frame, x="continent", y="life_expectancy", ax=ax)
        ax.set(title="Esperanza de vida por continente", xlabel="Continente", ylabel="Esperanza de vida (años)")
        ax.tick_params(axis="x", rotation=30)
        fig.text(0.01, 0.01, "Interpretación: compara distribuciones observadas; cobertura desigual posible.", fontsize=8)
        generated.append(_save(fig, output_dir, "life_expectancy_by_continent.png"))
    return generated


def _save(fig, directory: Path, name: str) -> str:
    destination = directory / name
    fig.tight_layout()
    fig.savefig(destination, dpi=150)
    plt.close(fig)
    return str(destination)
