# HyperTA - Technical Analysis Framework (Claude Context)

## Project Structure

```
src/ta/
├── api/                                    # FastAPI routes
│   ├── routes_backtesting.py              # Backtesting endpoints
│   ├── routes_data.py                     # Data fetching endpoints
│   ├── routes_functions.py                # Function execution endpoints
│   ├── routes_ml.py                       # ML model endpoints
│   ├── routes_strategies.py               # Strategy endpoints
│   └── routes_utils.py                    # Utility endpoints
│
├── backtesting/                            # Backtesting engine
│   └── signalQuality.py                   # Signal quality metrics
│
├── data/                                   # Data ingestion layer
│   └── fetch_yfinance.py                  # Yahoo Finance data fetcher
│
├── db/                                     # Database layer
│   ├── market.db                          # SQLite database
│   └── market_db.py                       # Database operations
│
├── functions/
│   ├── indicators/                        # Technical indicators
│   │   ├── momentum_indicators.py         # RSI, StochRSI, ROC, Williams %R, ADX, MACD
│   │   ├── trend_indicators.py            # MA, EMA, EMA Ribbon, Ichimoku
│   │   ├── volatility_indicators.py       # Bollinger Bands, ATR, Donchian
│   │   ├── volume_indicators.py           # Volume-based indicators
│   │   ├── threshold_functions.py         # Threshold detection logic
│   │   ├── universal_indicator_dispatcher.py   # Indicator router
│   │   └── universal_threshold_dispatcher.py   # Threshold router
│   │
│   ├── metrics/                           # Statistical metrics
│   │   ├── entropy.py                     # Entropy calculations
│   │   └── universal_metrics_dispatcher.py # Metrics router
│   │
│   ├── plots/                             # Visualization functions
│   │   ├── plot_signals.py                # Signal plotting
│   │   ├── plot_indicators.py             # Indicator plotting
│   │   ├── plot_dynamic_thresholds.py     # Dynamic threshold viz
│   │   └── plot_weekends.py               # Weekend marking
│   │
│   └── structures/                        # Market structure analysis
│       ├── market_structure/              # Price action structures
│       │   ├── breakouts.py               # Breakout detection
│       │   ├── candlestick_formations.py  # Candlestick patterns
│       │   ├── chart_patterns.py          # Chart patterns (H&S, triangles, etc.)
│       │   ├── divergences.py             # Price/indicator divergences
│       │   ├── fibonacci.py               # Fibonacci retracements/extensions
│       │   ├── gaps.py                    # Gap detection and classification
│       │   ├── hh_hl_lh_ll.py            # Higher highs, lower lows detection
│       │   ├── sr_levels.py               # Support/resistance levels
│       │   ├── swing_points.py            # Swing high/low detection
│       │   ├── trendlines.py              # Trendline detection
│       │   └── volume_profile.py          # Volume profile analysis
│       │
│       └── orderflow/                     # Order flow analysis
│           ├── footprint.py               # Footprint charts
│           ├── liquidity_sweeps.py        # Liquidity sweep detection
│           ├── orderblocks.py             # Order block detection
│           └── orderbook.py               # Order book analysis
│
├── ml/                                     # Machine learning
│   └── optimizers/                        # Hyperparameter optimization
│       ├── search.py                      # Grid/Random/Bayesian search
│       └── searchSpaces.py                # Search space definitions
│
├── strategies/                             # Pre-built trading strategies
│   └── (strategy implementations)
│
├── tests/                                  # Unit & integration tests
│   ├── general.py                         # General test utilities
│   ├── test_backtesting.py                # Backtesting tests
│   ├── test_indicators.py                 # Indicator tests
│   ├── test_ml.py                         # ML tests
│   ├── test_strategies.py                 # Strategy tests
│   └── test_structures.py                 # Structure detection tests
│
└── utils/                                  # Utility modules
    ├── config.py                          # Configuration management
    ├── file_utils.py                      # Data I/O operations
    ├── helper.py                          # General utilities
    ├── logger.py                          # Logging framework
    └── plot_utils.py                      # Chart generation utilities
```

---

## Naming Conventions

### Threshold Function Naming Pattern
All threshold detection functions follow this pattern:
```
{action}Threshold

Examples:
- crossUpThreshold       # Indicator crosses UP above a level
- crossUpLineThreshold   # Fast line crosses UP above slow line
- inRangeThreshold       # Indicator enters a range
- timeThreshold          # Condition persists for N candles
```

### Indicator Function Naming
Indicators are named using lowercase with underscores:
```python
# Momentum indicators
calculate_rsi(data, period=14)
calculate_stoch_rsi(data, period=14, smooth_k=3, smooth_d=3)
calculate_roc(data, period=12)
calculate_williams_r(data, period=14)
calculate_adx(data, period=14)
calculate_macd(data, fast=12, slow=26, signal=9)

# Trend indicators
calculate_sma(data, period=20)
calculate_ema(data, period=20)
calculate_ema_ribbon(data, periods=[8, 13, 21, 34, 55])
calculate_ichimoku(data, conversion=9, base=26, span_b=52, displacement=26)

# Volatility indicators
calculate_bollinger_bands(data, period=20, std_dev=2)
calculate_atr(data, period=14)
calculate_donchian_channels(data, period=20)
```

### Class Naming
- **PascalCase** for classes: `SignalEngine`, `ThresholdDetector`, `DataLoader`
- **snake_case** for methods: `detect_signals()`, `filter_by_statistics()`, `generate_pdf()`

### Variable Naming
- **snake_case** for variables: `threshold_config`, `signal_list`, `data_frame`
- **UPPER_CASE** for constants: `DEFAULT_RSI_PERIOD = 14`, `MAX_LOOKBACK = 500`

---

## Core Data Structures

### Threshold Configuration Schema

```python
# Basic threshold config
{
    "type": "crossUpThreshold",           # Required: threshold type
    "indicator": "rsi",                    # Required: indicator name
    "threshold": 30,                       # Required for fixed thresholds
    "period": 14,                          # Optional: signal period
    "indicator_params": {                  # Optional: indicator-specific params
        "indicator_period": 14
    }
}

# Multi-dimensional search config (for optimization)
{
    "type": "crossUpThreshold",
    "indicator": "rsi",
    "period": [5, 7, 14, 21],             # List = search space
    "threshold": [25, 30, 35, 40],         # 4 × 4 = 16 combinations
    "indicator_params": {
        "indicator_period": [7, 14, 21]    # 16 × 3 = 48 total configs
    }
}

# Line crossover config
{
    "type": "crossUpLineThreshold",
    "indicator": "macd",
    "fast_period": 12,
    "slow_period": 26,
    "signal_period": 9
}

# Range threshold config
{
    "type": "inRangeThreshold",
    "indicator": "rsi",
    "lower": 30,
    "upper": 70
}

# Time-based threshold config
{
    "type": "timeThreshold",
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
    "type": "crossUpThreshold",            # Threshold type
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
        {"indicator": "rsi", "type": "crossUpThreshold", "threshold": 30},
        {"indicator": "macd", "type": "crossUpLineThreshold"}
    ]
}

# OR logic (any condition can be true)
{
    "logic": "OR",
    "conditions": [
        {"indicator": "bbands", "type": "inRangeThreshold"},
        {"indicator": "stochrsi", "type": "crossUpThreshold", "threshold": 20}
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
        {"indicator": "macd", "type": "crossUpLineThreshold"}
    ]
}
```

---

## Key Function Signatures

### Threshold Detection (from threshold_functions.py)
```python
def crossUpThreshold(
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

def crossUpLineThreshold(
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

def inRangeThreshold(
    df,
    type,           # Indicator type
    period,         # Period
    lower,          # Lower bound
    upper,          # Upper bound
    kwargs={}       # Indicator params
):
    """Detect when indicator enters a range."""
    pass

def timeThreshold(
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
def evaluate_config(df, cfg):
    """Evaluate a single configuration."""
    pass

def expand_params(param_dict):
    """Expand parameter lists into individual configs."""
    pass

def generate_flat_configs(space):
    """Generate all flat configurations from search space."""
    pass

def get_total_grid_size(search_space):
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
# From src/ta/data/fetch_yfinance.py
def download_underlying_stock(
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

# From src/ta/db/market_db.py
def save_table(table: str, df: pd.DataFrame):
    """Save DataFrame to SQLite database table."""
    pass

def load_table(table: str) -> pd.DataFrame:
    """Load DataFrame from SQLite database table."""
    pass

def drop_table(table: str):
    """Delete a table from the database."""
    pass

def list_tables():
    """List all tables in the database."""
    pass

def drop_all_tables():
    """Delete all tables from the database."""
    pass
```


---

## Data Flow

1. **Load Data** → `download_underlying_stock()` → Returns `pd.DataFrame` (OHLCV)
2. **Save/Load DB** (optional) → `save_table()` / `load_table()` → SQLite persistence
3. **Calculate Indicators** → Auto-calculated via dispatchers → Adds columns to DataFrame
4. **Define Config** → Create threshold config dict(s)
5. **Detect Signals** → Threshold detection → Returns list of signal dicts
6. **Mix Signals** (optional) → Logic combination → Combines multiple configs
7. **Filter** (optional) → Statistical filtering → Removes low-quality signals
8. **Visualize** (optional) → `plot_signals()` → Creates charts

### Example Workflow
```python
# 1. Load data
from src.ta.data.fetch_yfinance import download_underlying_stock
data = download_underlying_stock("AAPL", "2023-01-01", "2024-01-01", "1d")

# 2. Save to database (optional)
from src.ta.db.market_db import save_table, load_table
save_table("AAPL_daily", data)

# 3. Calculate indicators (handled by dispatchers)
# Indicators are calculated automatically when needed

# 4. Define threshold config
config = {
    "type": "crossUpThreshold",
    "indicator": "rsi",
    "threshold": 30,
    "period": 14
}

# 5. Detect signals (using threshold dispatcher)
signals = detect_signals(data, config)

# 6. Filter by statistics
filtered_signals = filter_by_statistics(
    signals, 
    data, 
    min_win_rate=0.6,
    min_sharpe=1.5
)

# 7. Generate chart
from src.ta.functions.plots.plot_signals import plot_signals
plot_signals(data, filtered_signals, "output.pdf")
```

---

## Search Algorithm Usage

### Grid Search Example
```python
from src.ta.ml.optimizers.search import gridSearch

search_space = {
    "type": "crossUpThreshold",
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
from src.ta.ml.optimizers.search import randomSearch

search_space = {
    "type": "crossUpThreshold",
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
from src.ta.ml.optimizers.search import bayesianSearch

# Same search space as random, but uses Bayesian optimization
results = bayesianSearch(df, search_space, n_iter=50, n_jobs=-1)
# Converges faster than random search
```

### Combinatorial Search (Multi-Strategy)
```python
from src.ta.ml.optimizers.search import combinatorialGridSearch

# Define multiple search spaces for different strategies
search_spaces = [
    {"type": "crossUpThreshold", "indicator": "rsi", ...},
    {"type": "crossUpLineThreshold", "indicator": "macd", ...}
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

Test files are located in `src/ta/tests/` and follow pytest conventions:

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
        data[indicator] = calculate_indicator(data, **kwargs)
    
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
- **Indicator implementations**: `src/ta/functions/indicators/{momentum,trend,volatility,volume}_indicators.py`
- **Threshold detection**: `src/ta/functions/indicators/threshold_functions.py`
- **Indicator dispatcher**: `src/ta/functions/indicators/universal_indicator_dispatcher.py`
- **Threshold dispatcher**: `src/ta/functions/indicators/universal_threshold_dispatcher.py`

**Market Structure:**
- **Price action**: `src/ta/functions/structures/market_structure/*.py`
  - Breakouts, candlestick patterns, chart patterns, divergences
  - Fibonacci levels, gaps, swing points, S/R levels, trendlines
- **Order flow**: `src/ta/functions/structures/orderflow/*.py`
  - Footprint, liquidity sweeps, order blocks, orderbook

**Optimization & ML:**
- **Search algorithms**: `src/ta/ml/optimizers/search.py`
- **Search space definitions**: `src/ta/ml/optimizers/searchSpaces.py`

**Data & Database:**
- **Data fetching**: `src/ta/data/fetch_yfinance.py`
- **Database operations**: `src/ta/db/market_db.py`
- **SQLite database**: `src/ta/db/market.db`

**Backtesting:**
- **Signal quality**: `src/ta/backtesting/signalQuality.py`

**Visualization:**
- **Plot signals**: `src/ta/functions/plots/plot_signals.py`
- **Plot indicators**: `src/ta/functions/plots/plot_indicators.py`
- **Plot dynamic thresholds**: `src/ta/functions/plots/plot_dynamic_thresholds.py`
- **Plot utilities**: `src/ta/utils/plot_utils.py`

**API Routes:**
- **FastAPI endpoints**: `src/ta/api/routes_{backtesting,data,functions,ml,strategies,utils}.py`

**Utilities:**
- **Config management**: `src/ta/utils/config.py`
- **File operations**: `src/ta/utils/file_utils.py`
- **Helpers**: `src/ta/utils/helper.py`
- **Logging**: `src/ta/utils/logger.py`

**Tests:**
- `src/ta/tests/test_{indicators,strategies,structures,ml,backtesting}.py`
- `src/ta/tests/general.py` - Test utilities

### Most Important Functions

**Threshold Detection:**
1. `crossUpThreshold()` - Indicator crosses above level
2. `crossUpLineThreshold()` - Fast/slow line crossover
3. `inRangeThreshold()` - Indicator enters range
4. `timeThreshold()` - Condition persists N candles

**Search & Optimization:**
5. `gridSearch()` - Exhaustive parameter search
6. `randomSearch()` - Stochastic parameter sampling
7. `bayesianSearch()` - Bayesian optimization
8. `combinatorialGridSearch()` - Multi-strategy grid search

**Data Management:**
9. `download_underlying_stock()` - Fetch Yahoo Finance data
10. `save_table()` / `load_table()` - Database persistence

**Visualization:**
11. `plot_results_pdf()` - Generate result PDFs
12. `plot_signals()` - Plot signals on charts

---

## Tips for Navigation

- **All threshold functions** are in `threshold_functions.py` and follow pattern: `{action}{Direction}Threshold`
- **All indicator functions** are in `{momentum,trend,volatility,volume}_indicators.py`
- **All search functions** are in `ml/optimizers/search.py` (gridSearch, randomSearch, bayesianSearch)
- **Combinatorial searches** support multi-strategy optimization with AND/OR logic
- **Threshold configs** use lowercase keys: `"type"`, `"indicator"`, `"threshold"`, `"period"`
- **DataFrames** are passed as `df` parameter (not `data`)
- **Search results** are lists sorted by performance metric
- **Dispatchers** (`universal_*_dispatcher.py`) route to appropriate functions
- **Parallel processing** controlled via `n_jobs` parameter (-1 = all cores)
