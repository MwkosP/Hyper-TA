import vectorbt as vbt
import pandas as pd
import numpy as np

from ta.functions.indicators.universal_threshold_dispatcher import mixThresholds
from configs.searchSpaces import *
from main import *

# Your signal generation
def generate_signals_from_config(data, config):
    """Your existing mixThresholds logic"""
    signals = mixThresholds(df, [irtBUY[1],ttBUY[7]], search="bayesian",mode="and")
    
    # Convert to vectorbt format
    entries = pd.Series(False, index=data.index)
    exits = pd.Series(False, index=data.index)
    
    for _, signal in signals.iterrows():
        if signal['signal_type'] == 'BUY':
            entries.loc[signal['timestamp']] = True
        elif signal['signal_type'] == 'SELL':
            exits.loc[signal['timestamp']] = True
    
    return entries, exits

# Load data
data = vbt.YFData.download('AAPL', start='2020-01-01').get()
price = data['Close']

# Test MULTIPLE configs at once (vectorized!)
rsi_periods = [7, 14, 21, 28]
rsi_thresholds = [20, 25, 30, 35, 40]

# Create all combinations
all_entries = []
all_exits = []

for period in rsi_periods:
    for threshold in rsi_thresholds:
        config = {
            "operator": "AND",
            "blocks": [{
                "type": "crossUpThreshold",
                "indicator": "rsi",
                "threshold": threshold,
                "indicator_params": {"period": period}
            }]
        }
        
        entries, exits = generate_signals_from_config(data, config)
        all_entries.append(entries)
        all_exits.append(exits)

# Combine into DataFrame (each column = different config)
entries_df = pd.concat(all_entries, axis=1)
exits_df = pd.concat(all_exits, axis=1)

# Backtest ALL configs at once!
pf = vbt.Portfolio.from_signals(
    price, 
    entries_df, 
    exits_df,
    init_cash=10000,
    fees=0.001
)

# Get results for all configs
results = pf.stats()
print(results)

# Find best config
best_idx = pf.total_return().idxmax()
print(f"Best config: {best_idx}")
print(f"Sharpe: {pf.sharpe_ratio()[best_idx]}")
print(f"Total Return: {pf.total_return()[best_idx]}")

# Plot best config
pf[best_idx].plot().show()