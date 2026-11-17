import pandas as pd


def correlation_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Return pairwise correlations for numeric columns only."""
    return frame.corr(numeric_only=True)
