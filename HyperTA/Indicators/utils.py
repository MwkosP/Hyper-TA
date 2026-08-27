"""Internal helpers for the Indicators package."""


def _transformForFinta(df):
    """
    finta expects lowercase open/high/low/close/volume.
    Our public schema uses Capitalized OHLCV + Date.
    """
    return df.rename(columns={c: c.lower() for c in df.columns})
