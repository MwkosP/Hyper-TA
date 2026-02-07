from fastapi import APIRouter, Query
import pandas as pd
from src.ta.data.fetch_yfinance import download_underlying_stock
from src.ta.functions.indicators import INDICATOR_MAP

router = APIRouter(prefix="/functions",tags=["TA - Functions"]
)

# Root endpoint for FUNCTIONS
@router.get("/")
def root():
    return {"message": "✅ Functions API running"}



@router.get("/indicators")
def get_indicator(
    symbol: str = Query(..., example="BTC-USD"),
    start: str = Query("2024-09-01"),
    end: str = Query("2025-09-12"),
    interval: str = Query("1d"),
    indicator: str = Query(..., enum=list(INDICATOR_MAP.keys())),
    period: int = Query(14)
):
    df = download_underlying_stock(symbol, start, end, interval, plot=False)
    func = INDICATOR_MAP[indicator]
    result = func(df) 

    # ✅ Let FastAPI auto-convert to JSON
    return result
