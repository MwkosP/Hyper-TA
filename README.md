![HyperTA](https://raw.githubusercontent.com/MwkosP/Hyper-TA/main/Hyperta.png)

# HyperTA - Technical Analysis Signal Generator & Hyperparameter Optimization Framework

[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.13-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready technical analysis framework for quantitative trading research with advanced hyperparameter optimization capabilities.

---

##  Overview

HyperTA is a comprehensive **signal generation engine** for technical analysis that combines:

- **Multi-source data ingestion** from Yahoo Finance, custom providers, and more
- **50+ technical indicators** across momentum, trend, and volatility categories  
- **Threshold-based signal detection** with 4 different trigger mechanisms
- **Multi-dimensional hyperparameter optimization** (Grid, Random, Bayesian search)
- **Composite signal generation** via powerful `mixThresholds()` logic
- **Statistical filtering** based on historical performance
- **Automated PDF charting** for visual validation
- **ML-ready architecture** for model training on optimized signal sets

Built for **quantitative researchers**, **algorithmic traders**, and **strategy developers**.

---

##  Technical Indicators

### Momentum / Oscillators
- **RSI** (Relative Strength Index)
- **StochRSI** (Stochastic RSI)
- **ROC** (Rate of Change)
- **Williams %R**
- **ADX** (Average Directional Index)
- **MACD** (Moving Average Convergence Divergence)

### Trend Indicators
- **MA** (Moving Averages - SMA, WMA)
- **EMA** (Exponential Moving Average)
- **EMA Ribbon** (Multi-period EMA visualization)
- **EMA Crossover** (Fast/Slow crossover signals)
- **Ichimoku Cloud** (Full suite)

### Volatility / Range Indicators
- **Bollinger Bands**
- **ATR** (Average True Range)
- **Donchian Channels**

---

##  Signal Engine

### Threshold Detection Types

The framework supports 4 distinct signal trigger mechanisms:

#### 1. `crossUpThreshold`
Detects when an indicator crosses **above** a fixed numeric level.
```python
{
    "type": "crossUpThreshold",
    "indicator": "rsi",
    "threshold": 30,
    "period": 14
}
```

#### 2. `crossUpLineThreshold`
Detects **fast vs. slow line crossovers** (e.g., MACD signal line, EMA crossovers).
```python
{
    "type": "crossUpLineThreshold",
    "indicator": "macd",
    "fast_period": 12,
    "slow_period": 26
}
```

#### 3. `inRangeThreshold`
Triggers when an indicator enters a **predefined numerical band**.
```python
{
    "type": "inRangeThreshold",
    "indicator": "rsi",
    "lower": 30,
    "upper": 70
}
```

#### 4. `timeThreshold`
Requires an indicator to stay **above/below a level for N consecutive candles**.
```python
{
    "type": "timeThreshold",
    "indicator": "rsi",
    "threshold": 50,
    "min_candles": 3
}
```

---

##  Hyperparameter Optimization

### Multi-Dimensional Search Spaces

Define parameter ranges to explore all combinations:

```python
search_config = {
    "type": "crossUpThreshold",
    "indicator": "rsi",
    "period": [7, 14, 21],           # 3 values
    "threshold": [25, 30, 35],        # 3 values
    "indicator_params": {
        "indicator_period": [7, 14, 21]  # 3 values
    }
}
# Total combinations: 3 × 3 × 3 = 27 configurations
```

### Search Algorithms

1. **Grid Search** - Exhaustive exploration of all parameter combinations
2. **Random Search** - Stochastic sampling for faster iteration
3. **Bayesian Optimization** - Probabilistic guided search for optimal parameters

![Search Visualization](https://raw.githubusercontent.com/MwkosP/Hyper-TA/main/search.webp)

---

##  Signal Composition: `mixThresholds()`

The core innovation - **composite signal generation** via set logic:

### How It Works

1. **Expands** all parameter combinations from multi-dimensional configs
2. **Runs** threshold detection for each sub-configuration
3. **Collects** all signals into sets
4. **Combines** signals across indicator blocks using:
   - `UNION` (OR logic) - Any indicator triggers
   - `INTERSECTION` (AND logic) - All indicators must trigger
   - `DIFFERENCE` - Exclude specific patterns

### Example: Multi-Indicator Strategy

```python
strategy = mixThresholds([
    {
        "logic": "AND",
        "conditions": [
            {"indicator": "rsi", "threshold": 30, "type": "crossUpThreshold"},
            {"indicator": "macd", "type": "crossUpLineThreshold"}
        ]
    },
    {
        "logic": "OR",
        "conditions": [
            {"indicator": "bbands", "type": "inRangeThreshold"},
            {"indicator": "stochrsi", "threshold": 20}
        ]
    }
])
```

This creates **extremely powerful composite signals** that combine multiple technical perspectives.

![Signal Generation](https://raw.githubusercontent.com/MwkosP/Hyper-TA/main/signals.png)

---

##  Architecture

```
src/ta/
├── functions/
│   ├── indicators/          # Technical indicator implementations
│   ├── structures/
│   │   └── market_structure/  # Market structure detection
│   └── strategies/          # Pre-built trading strategies
├── ml/                      # Machine learning modules
├── tests/                   # Unit and integration tests
├──  utils/
    ├── config.py           # Configuration management
    ├── file_utils.py       # Data I/O operations
    ├── helper.py           # General utilities
    ├── logger.py           # Logging framework
    └── plot_utils.py       # Chart generation
├── data/
├── db/
├── backtesting/
├── utils/
└── strategies/
main.py
app.py 
```

---

##  Tech Stack

**Core Libraries:(Optimization,ML/AI,Backend)**
- `numpy` - Numerical computing
- `pandas` - Data manipulation
- `matplotlib` / `plotly` - Visualization
- `yfinance` - Market data retrieval
- `scikit-learn` - ML utilities
- `optuna` - Hyperparameter optimization
- `scipy` - Scientific computing
- `tensorflow` / `pytorch` - Deep learning
- `FastAPI` - REST API (optional)
- `SQLite` - Data persistence
- And many more..

---

##  Workflow

1. **Data Ingestion** → Fetch historical data from Yahoo Finance / custom sources
2. **Indicator Computation** → Calculate 50+ technical indicators
3. **Search Space Definition** → Configure multi-dimensional parameter ranges
4. **Optimization** → Run Grid/Random/Bayesian search algorithms
5. **Signal Generation** → Use `mixThresholds()` to create composite signals
6. **Statistical Filtering** → Filter by historical win rate, Sharpe ratio, etc.
7. **Visualization** → Auto-generate PDF charts for each configuration
8. **Model Training** *(Coming Soon)* → Train ML models on best signal sets

![Workflow Diagram](https://raw.githubusercontent.com/MwkosP/Hyper-TA/main/image.png)

---

##  Use Cases

- **Quantitative Strategy Research** - Systematic exploration of indicator combinations
- **Signal Generation & Backtesting** - Automated signal discovery and validation
- **Multi-Indicator Optimization** - Find optimal parameter sets across 10+ dimensions
- **Trading System Prototyping** - Rapid iteration on strategy ideas
- **Market Regime Detection** - Identify and classify market conditions
- **ML Feature Engineering** - Generate high-quality input features for predictive models

---

##  Roadmap

- [x] Core threshold detection engine
- [x] Multi-dimensional hyperparameter search
- [x] Composite signal generation (`mixThresholds`)
- [x] Statistical filtering framework
- [x] Automated PDF charting
- [ ] **ML model training on optimized signals**
- [ ] **Real-time signal generation API**
- [ ] **Portfolio-level optimization**
- [ ] **Interactive web dashboard**
- [ ] **Custom indicator plugin system**

---

##  License

MIT License - see [LICENSE](LICENSE) for details.

---

##  Contributing

Contributions welcome! Please open an issue or submit a PR.

---

## ⚠️ Disclaimer

This software is for **research and educational purposes only**. It is not financial advice. Trading involves substantial risk of loss. Always do your own research and consult with a qualified financial advisor before making investment decisions.

