import pandas as pd


def resample(df: pd.DataFrame, interval: str, time_column: str) -> pd.DataFrame:
    """Resample DataFrame by <interval>."""
    df[time_column] = pd.to_datetime(df[time_column], unit="s")
    df.set_index(time_column, inplace=True)
    d = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    return df.resample(interval).agg(d)
