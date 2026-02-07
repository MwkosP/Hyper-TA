# HyperTA - Technical Analysis Signal Generator

## Project Overview
Python-based technical analysis framework for quantitative trading research with hyperparameter optimization capabilities.

## Core Components

### Data Layer
- **Source**: Yahoo Finance (yfinance) + extensible providers
- **Storage**: SQLite database
- **Features**: Price data, volume, extended market metrics

### Technical Indicators
- **Momentum**: RSI, StochRSI, ROC, Williams %R, ADX, MACD
- **Trend**: MA, EMA, EMA Ribbon, EMA Crossover, Ichimoku Cloud
- **Volatility**: Bollinger Bands, ATR, Donchian Channels

### Signal Engine
Threshold-based triggers with 4 detection types:
- `crossUpThreshold` - Crosses fixed numeric level
- `crossUpLineThreshold` - Fast/slow line crossover
- `inRangeThreshold` - Enters numerical band
- `timeThreshold` - Stays above/below for N candles

### Search Algorithms
Multi-dimensional parameter optimization:
- **Grid Search** - Exhaustive parameter combinations
- **Random Search** - Stochastic sampling
- **Bayesian Optimization** - Probabilistic guided search

### Signal Composition
`mixThresholds()` function:
- Expands parameter combinations
- Detects signals per configuration
- UNION/AND/OR logic across indicator blocks
- Generates composite multi-indicator signals

## Tech Stack
**Core**: NumPy, Pandas, Matplotlib, Plotly  
**ML**: scikit-learn, TensorFlow, PyTorch, Optuna  
**API**: FastAPI  
**Indicators**: FinTA  

## Workflow
1. Load historical data → SQLite
2. Compute technical indicators
3. Define threshold configurations (multi-dimensional search space)
4. Run search algorithm (Grid/Random/Bayesian)
5. Generate signals using mixThresholds()
6. Filter by statistical significance
7. Optional: Export PDF charts per configuration
8. (Future) Train ML models on best signal sets

## Use Cases
- Quantitative strategy research
- Signal generation & backtesting
- Multi-indicator optimization
- Trading system prototyping
