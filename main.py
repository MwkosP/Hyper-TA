from datetime import date
from HyperTA.Indicators import calculateRsi, calculateMacd, calculateIchimoku, calculateBbands
from HyperTA.Providers.yfinance import fetchAsset
from HyperTA.Plots import plotChart, plotIndicator
from HyperTA.Metrics import calculateRollingEntropy, rollingDerivative, calculateMetrics
from HyperTA.Plots import plotMetrics
from HyperTA.Plots import plotSignals
from HyperTA.Plots import plotStructure
from HyperTA.Thresholds import crossLevel, inRange, stdvBandsThreshold
from HyperTA.Structures import (
    calculateSwingPoints,
    calculateFib,
    calculateSR,
    calculateTrendlines,
    calculateCandleFormations,
    calculateChartPatterns,
    calculateDoubleTopBottom,
    calculateGaps,
    calculateWyckoff,
    calculateDivergence,
    calculateHhLl,
    calculateRange,
    calculateChannel,
    calculateTrend,
)

TICKER = "BTC-USD"
START = "2024-01-01"
END = date.today().strftime("%Y-%m-%d")
INTERVAL = "1d"

df = fetchAsset(TICKER, START, END, INTERVAL)
from HyperTA.Indicators.utils import _transformForFinta
print(_transformForFinta(df))



## ________________________ PLOTS/ ____________________________

# asset.py
plotChart(df, title=f"{TICKER} price", label=TICKER)

# indicators.py
rsi = calculateRsi(df, period=14)
plotIndicator(rsi, title="RSI(14)")
macd = calculateMacd(df)
plotIndicator(macd, kind="macd", title="MACD")
bb = calculateBbands(df)
plotIndicator(bb, kind="bbands", price_df=df, title="Bollinger")
ichi = calculateIchimoku(df)
plotIndicator(ichi, kind="ichimoku", price_df=df, title="Ichimoku")

# metrics.py
plotMetrics(df, kind="distribution")
plotMetrics(calculateRollingEntropy(df, window=40), kind="entropy", price_df=df)
plotMetrics(rollingDerivative(df, k=40, derivative="both"), kind="derivative", price_df=df)
plotMetrics(calculateMetrics(df), kind="summary", price_df=df)

# signals.py
fake_signals = df["Date"].iloc[::25].tolist()
macd = calculateMacd(df)
plotSignals(df, fake_signals, indicator_df=macd, kind="macd",
            showIndicator=True, showIndicatorSignals=True, showSignalsOnIndicator=True)

# signals.py (+ optional threshold rules via rule=)
rsi = calculateRsi(df, period=14)
sigs = crossLevel(df, type="rsi", thr=30, period=14)
plotSignals(df, sigs, rule="level", thr=30, indicator_df=rsi, kind="rsi",
            showIndicator=True, title="RSI crossLevel 30")
range_sigs = inRange(df, type="rsi", period=14, lower=30, upper=70)
plotSignals(df, range_sigs, rule="band", band=(30, 70), indicator_df=rsi, kind="rsi",
            showIndicator=True, title="RSI inRange 30-70")
above, below = stdvBandsThreshold(df, ema_period=10, window=50, sigma=0.8)
plotSignals(df, (above, below), rule="sigma", ema_period=10, window=50, sigma=0.8,
            showIndicator=False, title="EMA ± σ bands")

# structures.py
swings = calculateSwingPoints(df, left=3, right=3)
plotStructure(df, swings, title=f"{TICKER} swings")

fib = calculateFib(df, left=5, right=5)
# fib = calculateFib(df, lookback=180)  # alt: min/max of last N bars
plotStructure(df, fib, title=f"{TICKER} fib")

sr = calculateSR(df, left=3, right=3)
plotStructure(df, sr, title=f"{TICKER} S/R")

tls = calculateTrendlines(df, min_points=3)
plotStructure(df, tls, title=f"{TICKER} trendlines")

# candles = calculateCandleFormations(df)                 # default popular patterns
candles = calculateCandleFormations(df, patterns="all")
plotStructure(df, candles, title=f"{TICKER} candles", zoom=False)

# div = calculateDivergence(df, period=14, left=5, right=5, mode="both")
div = calculateDivergence(df, indicator_df=calculateRsi(df), mode="regular")
plotStructure(df, div, title=f"{TICKER} RSI divergence")

hhll = calculateHhLl(df, left=5, right=5)
plotStructure(df, hhll, title=f"{TICKER} HH/HL/LH/LL", zoom=False)

boxes = calculateRange(df, max_width_pct=0.20, window=30, max_ranges=15)
plotStructure(df, boxes, title=f"{TICKER} ranges", zoom=False)

ch = calculateChannel(df, window=60, max_channels=2)
plotStructure(df, ch, title=f"{TICKER} channels")

# sensitivity: small = reactive spikes, large = macro trend
trend_macro = calculateTrend(df, sensitivity=0.15)   # big picture
trend_swing = calculateTrend(df, sensitivity=0.04)   # swings / spikes
plotStructure(df, trend_macro, title=f"{TICKER} trend macro (0.15)", zoom=False)
plotStructure(df, trend_swing, title=f"{TICKER} trend swing (0.04)", zoom=False)

doubles = calculateDoubleTopBottom(df)
plotStructure(df, doubles, title=f"{TICKER} double top/bottom", zoom=False)

charts = calculateChartPatterns(df)  # doubles, H&S, triangles, flags, …
plotStructure(df, charts, title=f"{TICKER} chart patterns", zoom=False)

# crypto 24/7 rarely gaps — still works on stocks / thin sessions
gaps = calculateGaps(df, min_gap_pct=0.001)
if len(gaps):
    plotStructure(df, gaps, title=f"{TICKER} gaps", zoom=False)

wk = calculateWyckoff(df)
plotStructure(df, wk, title=f"{TICKER} Wyckoff", zoom=False)
