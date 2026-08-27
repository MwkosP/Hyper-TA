# HyperTA - Technical Analysis Framework (Claude Context)

## Project Structure

```
Assets/                                     # Static assets (images, etc.)
Configs/                                    # Search-space definitions (Configs.searchSpaces)
Tests/                                      # Unit & integration tests
HyperTA/                                    # Core package
├── Filtering/                              # Statistical signal filtering
├── Statistical/                            # Sensitivity, Monte Carlo, statistical tests
│   ├── statistical.py
│   └── utils.py
├── Providers/                              # Data providers
│   └── yfinance.py                        # fetchAsset
├── Indicators/                             # calculate* indicators
│   ├── indicators.py                      # All calculate* indicators
│   └── dispatcher.py                      # calculateIndicator
├── Thresholds/                             # Signal trigger layer
│   ├── thresholds.py                      # crossLevel, stdvBandsThreshold, …
│   ├── dispatcher.py                      # mixThresholds
│   └── utils.py                           # Internal: runThreshold
├── Metrics/                                # Entropy, derivatives, stats
│   ├── utils.py                           # Internal: firstDerivative, secondDerivative
│   ├── derivatives.py                     # rollingDerivative (user-facing)
│   ├── entropy.py
│   └── universal_metrics_dispatcher.py
├── Plots/                                  # Visualization
│   ├── utils.py                           # Internal: _render, _theme, _applyTheme
│   ├── asset.py                           # plotChart — price line
│   ├── signals.py                         # plotSignals (+ optional threshold rules)
│   ├── indicators.py                      # plotIndicator
│   └── metrics.py                         # plotMetrics
├── Structures/                             # Market structure + orderflow
│   ├── market_structure/
│   └── orderflow/
├── ML/
│   └── optimizers/
│       ├── search.py                      # grid/random/bayesian (user-facing)
│       └── utils.py                       # Internal search helpers
├── Strategies/
├── Reporting/                              # Reports / result summaries
└── Utils/                                  # Cross-cutting stubs (config/logger/...)
```

---

## Naming Conventions

### Threshold Function Naming Pattern
All threshold detection functions follow this pattern:
```
{action}Threshold

Examples:
- crossLevel       # Indicator crosses UP above a level
- crossLines   # Fast line crosses UP above slow line
- inRange       # Indicator enters a range
- holdLevel          # Condition persists for N candles
```

### Indicator Function Naming
Indicators use camelCase:
```python
# Momentum indicators
calculateRsi(data, period=14)
calculateStochrsi(data, period=14, smooth_k=3, smooth_d=3)
calculateRoc(data, period=12)
calculateWilliams(data, period=14)
calculateAdx(data, period=14)
calculateMacd(data, fast=12, slow=26, signal=9)

# Trend indicators
calculateMa(data, period=20)
calculateEma(data, period=20)
calculateEmaRibbon(data, periods=[8, 13, 21, 34, 55])
calculateIchimoku(data, conversion=9, base=26, span_b=52, displacement=26)

# Volatility indicators
calculateBbands(data, period=20, std_dev=2)
calculateAtr(data, period=14)
calculateDonchian(data, period=20)
```

### Class Naming
- **PascalCase** for classes: `SignalEngine`, `ThresholdDetector`, `DataLoader`
- **camelCase** for functions/methods: `detectSignals()`, `filterByStatistics()`, `generatePdf()`

### Variable Naming
- **snake_case** for variables: `threshold_config`, `signal_list`, `data_frame`
- **UPPER_CASE** for constants: `DEFAULT_RSI_PERIOD = 14`, `MAX_LOOKBACK = 500`

---

## Core Data Structures

### Threshold Configuration Schema

```python
# Basic threshold config
{
    "type": "crossLevel",           # Required: threshold type
    "indicator": "rsi",                    # Required: indicator name
    "threshold": 30,                       # Required for fixed thresholds
    "period": 14,                          # Optional: signal period
    "indicator_params": {                  # Optional: indicator-specific params
        "indicator_period": 14
    }
}

# Multi-dimensional search config (for optimization)
{
    "type": "crossLevel",
    "indicator": "rsi",
    "period": [5, 7, 14, 21],             # List = search space
    "threshold": [25, 30, 35, 40],         # 4 × 4 = 16 combinations
    "indicator_params": {
        "indicator_period": [7, 14, 21]    # 16 × 3 = 48 total configs
    }
}

# Line crossover config
{
    "type": "crossLines",
    "indicator": "macd",
    "fast_period": 12,
    "slow_period": 26,
    "signal_period": 9
}

# Range threshold config
{
    "type": "inRange",
    "indicator": "rsi",
    "lower": 30,
    "upper": 70
}

# Time-based threshold config
{
    "type": "holdLevel",
    "indicator": "rsi",
    "threshold": 50,
    "direction": "above",                  # "above" or "below"
    "min_candles": 3                       # Consecutive candles required
}
```

### Signal Output Format

```python
{
    "timestamp": "2024-01-15 09:30:00",    # Signal trigger time
    "indicator": "rsi",                     # Indicator name
    "type": "crossLevel",            # Threshold type
    "value": 32.5,                         # Indicator value at trigger
    "threshold": 30,                       # Threshold that was crossed
    "config": {...},                       # Full config used
    "metadata": {                          # Optional metadata
        "period": 14,
        "score": 0.85
    }
}
```

### mixThresholds() Logic Structure

```python
# AND logic (all conditions must be true)
{
    "logic": "AND",
    "conditions": [
        {"indicator": "rsi", "type": "crossLevel", "threshold": 30},
        {"indicator": "macd", "type": "crossLines"}
    ]
}

# OR logic (any condition can be true)
{
    "logic": "OR",
    "conditions": [
        {"indicator": "bbands", "type": "inRange"},
        {"indicator": "stochrsi", "type": "crossLevel", "threshold": 20}
    ]
}

# Nested logic (complex combinations)
{
    "logic": "AND",
    "conditions": [
        {
            "logic": "OR",
            "conditions": [
                {"indicator": "rsi", "threshold": 30},
                {"indicator": "stochrsi", "threshold": 20}
            ]
        },
        {"indicator": "macd", "type": "crossLines"}
    ]
}
```

---

## Key Function Signatures

### Threshold Detection (from thresholds/thresholds.py)
```python
def crossLevel(
    df,
    type,           # Indicator type/name
    thr,            # Threshold level
    period,         # Signal period
    wd=0,           # Warmup/delay candles
    sell=False,     # Sell signal instead of buy
    **kwargs
):
    """Detect when indicator crosses UP above a threshold level."""
    pass

def crossLines(
    df,
    type1,          # Fast indicator type
    period1,        # Fast period
    type2,          # Slow indicator type
    period2,        # Slow period
    wd=1,           # Warmup/delay candles
    kwargs1={},     # Fast indicator params
    kwargs2={}      # Slow indicator params
):
    """Detect fast line crossing UP above slow line."""
    pass

def inRange(
    df,
    type,           # Indicator type
    period,         # Period
    lower,          # Lower bound
    upper,          # Upper bound
    kwargs={}       # Indicator params
):
    """Detect when indicator enters a range."""
    pass

def holdLevel(
    df,
    type,           # Indicator type
    period,         # Period
    level,          # Threshold level
    direction="above",  # "above" or "below"
    min_candles=3,  # Consecutive candles required
    wd=0,           # Warmup/delay
    **kwargs
):
    """Detect when indicator stays above/below level for N candles."""
    pass

def stdvThresholdEMA(
    df,
    ema_period=10,
    window=50,
    sigma=0.8,
    wd=0
):
    """Standard deviation based threshold on EMA."""
    pass

def kurtosisThreshold(
    df,
    window=20,
    k_range=(-2.0, 1.0),
    label="trigger_active"
):
    """Kurtosis-based threshold detection."""
    pass

def run_kurtosis_delta_strategy(
    df,
    ema_p=20,
    sig=1.5,
    k_win=50,
    delta_k=0.5,
    n=5
):
    """Run kurtosis delta strategy."""
    pass
```

### Signal Mixing
```python
def mixThresholds(
    data: pd.DataFrame,
    configs: list[dict],
    logic: str = "AND"
) -> list[dict]:
    """
    Combine multiple threshold configs using set logic.
    
    Args:
        data: OHLCV DataFrame
        configs: List of threshold configurations
        logic: "AND", "OR", or "XOR"
        
    Returns:
        Combined signal list
    """
    pass
```

### Hyperparameter Search (from ml/optimizers/search.py)
```python
def gridSearch(
    df,
    search_space,
    n_jobs=-1       # Parallel jobs (-1 = all cores)
):
    """
    Exhaustive grid search over parameter space.
    
    Args:
        df: OHLCV DataFrame
        search_space: Dict with list values for each param
        n_jobs: Number of parallel jobs
        
    Returns:
        List of results sorted by metric score
    """
    pass

def randomSearch(
    df,
    search_space,
    n_iter=100,     # Number of random samples
    n_jobs=-1
):
    """Random sampling of parameter space."""
    pass

def bayesianSearch(
    df,
    search_space,
    n_iter=100,     # Number of Bayesian iterations
    n_jobs=-1
):
    """Bayesian optimization using Optuna."""
    pass

def combinatorialGridSearch(
    df,
    search_spaces_list,  # List of search spaces
    mode="and"           # "and" or "or" logic
):
    """Grid search with multiple strategy combinations."""
    pass

def combinatorialRandomSearch(
    df,
    search_spaces_list,
    n_iter=100,
    mode="and"
):
    """Random search with multiple strategy combinations."""
    pass

def combinatorialBayesianSearch(
    df,
    search_spaces_list,
    n_iter=100,
    mode="and"
):
    """Bayesian search with multiple strategy combinations."""
    pass

# Helper functions
def evaluateConfig(df, cfg):
    """Evaluate a single configuration."""
    pass

def expandParams(param_dict):
    """Expand parameter lists into individual configs."""
    pass

def generateFlatConfigs(space):
    """Generate all flat configurations from search space."""
    pass

def getTotalGridSize(search_space):
    """Calculate total number of grid combinations."""
    pass

def plot_results_pdf(
    df,
    results,
    pdf_name="all_plots.pdf",
    top_n=None,
    signal_range=None
):
    """Generate PDF with result visualizations."""
    pass
```

### Data Loading & Database
```python
# From HyperTA/Providers/yfinance.py
def fetchAsset(
    title: str,
    start: str,
    end: str,
    tmfrm: str,
    plot: bool = False
) -> pd.DataFrame:
    """
    Download OHLCV data from Yahoo Finance.
    
    Args:
        title: Stock ticker symbol (e.g., "AAPL")
        start: Start date (e.g., "2023-01-01")
        end: End date (e.g., "2024-01-01")
        tmfrm: Timeframe (e.g., "1d", "1h", "15m")
        plot: Whether to plot the data
        
    Returns:
        DataFrame with OHLCV columns and DatetimeIndex
    """
    pass

```


---

## Data Flow

1. **Load Data** → `fetchAsset()` → Returns `pd.DataFrame` (OHLCV)
2. **Calculate Indicators** → Auto-calculated via dispatchers → Adds columns to DataFrame
3. **Define Config** → Create threshold config dict(s)
4. **Detect Signals** → Threshold detection → Returns list of signal dicts
5. **Mix Signals** (optional) → Logic combination → Combines multiple configs
6. **Filter** (optional) → Statistical filtering → Removes low-quality signals
7. **Visualize** (optional) → `plotSignals()` → Creates charts

### Example Workflow
```python
# 1. Load data
from HyperTA.Providers.yfinance import fetchAsset
data = fetchAsset("AAPL", "2023-01-01", "2024-01-01", "1d")

# 3. Calculate indicators (handled by dispatchers)
# Indicators are calculated automatically when needed

# 4. Define threshold config
config = {
    "type": "crossLevel",
    "indicator": "rsi",
    "threshold": 30,
    "period": 14
}

# 5. Detect signals (using threshold dispatcher)
signals = detectSignals(data, config)

# 6. Filter by statistics
filtered_signals = filterByStatistics(
    signals, 
    data, 
    min_win_rate=0.6,
    min_sharpe=1.5
)

# 7. Generate chart
from HyperTA.Plots import plotSignals
plotSignals(data, filtered_signals, "output.pdf")
```

---

## Search Algorithm Usage

### Grid Search Example
```python
from HyperTA.ML.optimizers.search import gridSearch

search_space = {
    "type": "crossLevel",
    "indicator": "rsi",
    "period": [5, 7, 14, 21],              # 4 values
    "threshold": [25, 30, 35, 40],         # 4 values
    "indicator_params": {
        "indicator_period": [7, 14, 21]    # 3 values
    }
}
# Total: 4 × 4 × 3 = 48 combinations

results = gridSearch(df, search_space, n_jobs=-1)
best_config = results[0]  # Highest scoring config
```

### Random Search Example
```python
from HyperTA.ML.optimizers.search import randomSearch

search_space = {
    "type": "crossLevel",
    "indicator": "rsi",
    "period": list(range(5, 30)),          # 25 values
    "threshold": list(range(20, 50)),      # 30 values
    "indicator_params": {
        "indicator_period": list(range(5, 30))
    }
}
# Total space: 25 × 30 × 25 = 18,750 combinations
# Random search samples N=100 of these

results = randomSearch(df, search_space, n_iter=100, n_jobs=-1)
```

### Bayesian Search Example
```python
from HyperTA.ML.optimizers.search import bayesianSearch

# Same search space as random, but uses Bayesian optimization
results = bayesianSearch(df, search_space, n_iter=50, n_jobs=-1)
# Converges faster than random search
```

### Combinatorial Search (Multi-Strategy)
```python
from HyperTA.ML.optimizers.search import combinatorialGridSearch

# Define multiple search spaces for different strategies
search_spaces = [
    {"type": "crossLevel", "indicator": "rsi", ...},
    {"type": "crossLines", "indicator": "macd", ...}
]

# Combine with AND logic (both must trigger)
results = combinatorialGridSearch(df, search_spaces, mode="and")

# Or with OR logic (either can trigger)
results = combinatorialGridSearch(df, search_spaces, mode="or")
```

---

## Configuration Files

### config.py Structure
```python
# Default indicator periods
DEFAULT_RSI_PERIOD = 14
DEFAULT_MACD_FAST = 12
DEFAULT_MACD_SLOW = 26
DEFAULT_BB_PERIOD = 20
DEFAULT_BB_STD = 2

# Search algorithm settings
DEFAULT_GRID_SEARCH_MAX_COMBINATIONS = 10000
DEFAULT_RANDOM_SEARCH_ITERATIONS = 100
DEFAULT_BAYESIAN_ITERATIONS = 50

# Statistical filtering thresholds
MIN_WIN_RATE = 0.55
MIN_SHARPE_RATIO = 1.0
MIN_PROFIT_FACTOR = 1.2

# Data settings
DEFAULT_LOOKBACK = 500
DEFAULT_TIMEFRAME = "1d"
```

---

## Testing Conventions

Test files are located in `HyperTA/tests/` and follow pytest conventions:

```python
# test_indicators.py
def test_rsi_calculation():
    """Test RSI indicator calculation."""
    pass

def test_rsi_crossup_threshold():
    """Test RSI cross-up threshold detection."""
    pass

# test_strategies.py
def test_mix_thresholds_and_logic():
    """Test mixThresholds with AND logic."""
    pass

def test_mix_thresholds_or_logic():
    """Test mixThresholds with OR logic."""
    pass
```

---

## Common Code Patterns

### Indicator Calculation Pattern
All indicator functions follow this pattern:
```python
def calculate_indicator_name(
    data: pd.DataFrame,
    period: int = DEFAULT_PERIOD,
    **kwargs
) -> pd.Series:
    """
    Calculate INDICATOR_NAME.
    
    Args:
        data: DataFrame with OHLCV columns
        period: Lookback period
        **kwargs: Additional indicator-specific params
        
    Returns:
        Series with indicator values, same index as data
    """
    # Validation
    if len(data) < period:
        raise ValueError(f"Insufficient data: need {period}, got {len(data)}")
    
    # Calculation
    indicator = ...  # compute indicator
    
    return indicator
```

### Threshold Detection Pattern
```python
def detect_{threshold_type}(
    data: pd.DataFrame,
    indicator: str,
    threshold: float,
    **kwargs
) -> list[dict]:
    """Detect {threshold_type} signals."""
    
    # Calculate indicator if not present
    if indicator not in data.columns:
        data[indicator] = calculateIndicator(data, **kwargs)
    
    # Detect crossings/conditions
    signals = []
    for i in range(1, len(data)):
        if condition_met(data.iloc[i], data.iloc[i-1]):
            signals.append({
                "timestamp": data.index[i],
                "indicator": indicator,
                "value": data[indicator].iloc[i],
                "threshold": threshold
            })
    
    return signals
```

---

## Quick Reference

### Where to Find Things

**Core Modules:**
- **Indicator implementations**: `HyperTA/Indicators/{momentum,trend,volatility,volume}_indicators.py`
- **Threshold detection**: `HyperTA/Thresholds/thresholds.py`
- **Indicator dispatcher**: `HyperTA/Indicators/dispatcher.py`
- **Threshold dispatcher**: `HyperTA/Thresholds/dispatcher.py`

**Market Structure:**
- **Price action**: `HyperTA/Structures/market_structure/*.py`
  - Breakouts, candlestick patterns, chart patterns, divergences
  - Fibonacci levels, gaps, swing points, S/R levels, trendlines
- **Order flow**: `HyperTA/Structures/orderflow/*.py`
  - Footprint, liquidity sweeps, order blocks, orderbook

**Optimization & ML:**
- **Search algorithms**: `HyperTA/ML/optimizers/search.py`
- **Search space definitions**: `HyperTA/ML/optimizers/searchSpaces.py`

**Data & Database:**
- **Data fetching**: `HyperTA/Providers/yfinance.py`

**Filtering:**
- **Signal filtering**: `HyperTA/Filtering/filtering.py`

**Statistical:**
- **Analysis**: `HyperTA/Statistical/statistical.py`

**Visualization:**
- **Plot signals / thresholds**: `HyperTA/Plots/signals.py` (`plotSignals`, optional `rule=`)
- **Plot indicators**: `HyperTA/Plots/indicators.py`
- **Plot metrics**: `HyperTA/Plots/metrics.py`
- **Plot asset price**: `HyperTA/Plots/asset.py`
- **Plot utilities**: `HyperTA/Utils/plot_utils.py`

**Utilities:**
- **Config management**: `HyperTA/Utils/config.py`
- **File operations**: `HyperTA/Utils/file_utils.py`
- **Logging**: `HyperTA/Utils/logger.py`

**Tests:**
- `HyperTA/tests/test_{indicators,strategies,structures,ml,filtering}.py`
- `HyperTA/tests/general.py` - Test utilities

### Most Important Functions

**Threshold Detection:**
1. `crossLevel()` - Indicator crosses above level
2. `crossLines()` - Fast/slow line crossover
3. `inRange()` - Indicator enters range
4. `holdLevel()` - Condition persists N candles
5. `mixThresholds()` - Mix Multiple Threshold logics into signals.

**Search & Optimization:**
5. `gridSearch()` - Exhaustive parameter search
6. `randomSearch()` - Stochastic parameter sampling
7. `bayesianSearch()` - Bayesian optimization
8. `combinatorialGridSearch()` - Multi-strategy grid search

**Data Management:**
9. `fetchAsset()` - Fetch Yahoo Finance data

**Visualization:**
11. `plot_results_pdf()` - Generate result PDFs
12. `plotSignals()` - Plot signals on charts

---

## Tips for Navigation

- **All threshold functions** are in `thresholds/thresholds.py` and follow pattern: `{action}Threshold`
- **All indicator functions** are in `{momentum,trend,volatility,volume}_indicators.py`
- **All search functions** are in `ml/optimizers/search.py` (gridSearch, randomSearch, bayesianSearch)
- **Combinatorial searches** support multi-strategy optimization with AND/OR logic
- **Threshold configs** use lowercase keys: `"type"`, `"indicator"`, `"threshold"`, `"period"`
- **DataFrames** are passed as `df` parameter (not `data`)
- **Search results** are lists sorted by performance metric
- **Dispatchers** (`universal_*_dispatcher.py`) route to appropriate functions
- **Parallel processing** controlled via `n_jobs` parameter (-1 = all cores)
