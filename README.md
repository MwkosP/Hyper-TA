![HyperTA](https://raw.githubusercontent.com/MwkosP/Hyper-TA/main/assets/img/Hyperta.png)

# HyperTA - Technical Analysis Signal Generator & Hyperparameter Optimization Framework




[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python)](https://www.python.org/)
[![CI](https://github.com/MwkosP/Hyper-TA/actions/workflows/ci.yaml/badge.svg)](https://github.com/MwkosP/Hyper-TA/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

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

This Library uses UV package manager to turn runtimes 10-100x times faster than with normal pip runtimes. 

---

##  Technical Indicators

### Momentum / Oscillators
- **RSI**, **StochRSI**, **ROC**, **Williams %R**, **ADX**, **MACD**

### Trend Indicators
- **MA**, **EMA**, **EMA Ribbon**, **EMA Crossover**, **Ichimoku Cloud** 

### Volatility / Range Indicators
- **Bollinger Bands**, **ATR**, **Donchian Channels**

---

##  Signal Engine

### Threshold Detection Types

The framework supports distinct signal Threshold trigger mechanisms:

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

Define parameter ranges to explore all(or most - depending on search algorithm) combinations:

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
4. More to be added...

![Search Visualization](https://raw.githubusercontent.com/MwkosP/Hyper-TA/main/assets/img/search.png)

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
strategy = mixThresholds(price,[searchconfig[0],searchconfig[1]], search="bayesian",mode="and" )
```

This creates **extremely powerful composite signals** that combine multiple technical perspectives.

![Signal Generation](https://raw.githubusercontent.com/MwkosP/Hyper-TA/main/assets/img/signals.png)

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
- `numpy`, `pandas`, `matplotlib`, `plotly`, `yfinance`, `finta`, `scikit-learn`, `optuna`, `scipy`, `tensorflow` / `pytorch`, `FastAPI`, `SQLite`, `joblib`, `typer`, 
- And many more..

---
## With CLI support
```bash
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ docs             Open the official Hyper-TA documentation in your browser.                                           │
│ guide            Display a quick-start guide for Threshold and Mixed strategies.                                     │
│ test             Run the project test suite using pytest.                                                            │
│ health           Check the system health and project environment.                                                    │
│ version          Display the current version of Hyper-TA.                                                            │
│ fetch            Fetch the current live price for a specific ticker.                                                 │
│ list-functions   List all functions within the ta package.                                                           │
│ list-thresholds  List all available Threshold and Mixed Threshold strategies.                                        │
│ list-strategies  List all specific Threshold and Mixed Threshold strategy types.                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
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

```bash
1. INDICATORS (RSI, MACD, etc.)
         ↓
2. THRESHOLD LOGIC (crossUp, inRange, etc.)
         ↓
3. mixThresholds() → GENERATES SIGNALS
         ↓
4. SEARCH ALGORITHMS (Grid/Random/Bayesian) ← ALREADY BUILT-IN!
         ↓
5. BACKTESTING ← YOU ONLY NEED THIS PART!
```
---

##  Use Cases

- **Quantitative Strategy Research** - Systematic exploration of indicator combinations
- **Signal Generation & Backtesting** - Automated signal discovery and validation
- **Multi-Indicator Optimization** - Find optimal parameter sets across 10+ dimensions
- **Trading System Prototyping** - Rapid iteration on strategy ideas
- **Market Regime Detection** - Identify and classify market conditions
- **ML Feature Engineering** - Generate high-quality input features for predictive models

---

## Quick Start
```bash
# 1. Install uv (if you havent)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup
git clone https://github.com/MwkosP/Hyper-TA.git
cd Hyper-TA
uv sync

# 3. Run
uv run python main.py
```

That's it!
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


















