# === External libraries ===
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def fetch_asset(title: str, start: str, end: str, tmfrm: str, plot: bool = False) -> pd.DataFrame:
    up = yf.download(title, start=start, end=end, interval=tmfrm, auto_adjust=True)

    # flatten column names if needed
    up.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in up.columns]

    # reset index and normalize column name
    up = up.reset_index().rename(columns={"Datetime": "Date", "date": "Date"})

    if up.empty:
        print(f"⚠️ No data found for {title} ({tmfrm}, {start} -> {end})")
        return pd.DataFrame()

    if plot:
        latest_price = up['close'].iloc[-1]
        plt.figure(figsize=(14, 6))
        plt.plot(up['Date'], up['close'], color='orange', label=f"{title} Price (USD)")
        plt.axhline(latest_price, color='gray', linestyle=':', label=f'Current Price: ${latest_price:.2f}')
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Price ($)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    return up



