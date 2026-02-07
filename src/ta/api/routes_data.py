from fastapi import APIRouter, Query
import pandas as pd
import requests

from src.ta.data.fetch_yfinance import download_underlying_stock 

router = APIRouter(prefix="/data", tags=["TA - Data"])


# 📌 Preloaded default assets (includes BTC-USD)
DEFAULT_TICKERS = ["BTC-USD", "ETH-USD", "AAPL"]

@router.get("/prices")
def get_prices(
    ticker: str = Query("BTC-USD", description="Ticker symbol (e.g., BTC-USD, AAPL)"),
    start: str = Query("2020-09-06", description="Start date (YYYY-MM-DD)"),
    end: str = Query("2025-07-30", description="End date (YYYY-MM-DD)"),
    interval: str = Query("1d", description="Timeframe (1d, 1wk, 1h, etc.)"),
    plot: bool = Query(False, description="Plot of the prices Chart.")
):
    """
    Fetch historical stock/crypto prices (only Date & Close).
    - /functions/prices                → returns BTC-USD, ETH-USD, AAPL
    - /functions/prices?ticker=BTC-USD → returns only BTC-USD
    """
    tickers_to_fetch = [ticker] if ticker else DEFAULT_TICKERS
    results = {}

    for t in tickers_to_fetch: #in case first doesnt work

        df = download_underlying_stock(t, start, end, interval, plot=False)

        if df is None or df.empty:
            results[t] = {"error": f"No data found for {t} between {start} and {end}"}
        else:
            # ✅ Keep only Date & Close
            filtered = df.reset_index()[["Date", "close"]]
            results[t] = filtered.to_dict(orient="records")

            if plot:
                download_underlying_stock(t, start, end, interval, plot=True)
    return results



BASE_URL = "https://api.coingecko.com/api/v3/simple/price"
@router.get("/crypto-prices")
def get_prices(ids: list[str] = Query(..., max_items=5), vs_currency: str = "usd"):
    ids_str = ",".join(ids)
    url = f"{BASE_URL}?ids={ids_str}&vs_currencies={vs_currency}"
    response = requests.get(url)
    return response.json()