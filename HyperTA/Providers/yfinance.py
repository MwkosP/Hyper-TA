import yfinance as yf
import pandas as pd


def fetchAsset(title: str, start: str, end: str, tmfrm: str) -> pd.DataFrame:
    try:
        df = yf.download(title, start=start, end=end, interval=tmfrm, auto_adjust=True)
        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df.reset_index().rename(columns={"Datetime": "Date", "date": "Date"})
    except Exception as e:
        print(f"fetchAsset failed: {e}")
        return pd.DataFrame()
