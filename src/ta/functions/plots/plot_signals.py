# === External libraries ===
import pandas as pd
import matplotlib.pyplot as plt


from src.ta.functions.indicators.trend_indicators import *
from src.ta.functions.indicators.momentum_indicators import *
from src.ta.functions.indicators.volatility_indicators  import *


#USAGE:
#plot_signals(btc, signals2, title="Buy Signals (EMA + RSI)")
#plot_signals(btc, signals1, title="Buy Signals (EMA + RSI)")

def plot_signals(df: pd.DataFrame, signal_dates: list, title: str = "Buy Signals on BTC Price"):
    """
    Plots BTC price with green upward arrows (↑) below signal dates.

    Parameters:
        df (pd.DataFrame): Must contain 'Date' and 'close'.
        signal_dates (list): List of datetime objects.
        title (str): Plot title.
    """
    plt.figure(figsize=(14, 6))
    plt.plot(df['Date'], df['close'], label='BTC Price', color='black')

    signal_dates = pd.to_datetime(signal_dates)

    for date in signal_dates:
        row = df[df['Date'] == date]
        if not row.empty:
            price = row['close'].values[0]
            # Arrow appears below price
            plt.annotate('↑', xy=(date, price*0.98 ), fontsize=25, color='red',
                         ha='center', va='top')

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("BTC Price ($)")
    plt.grid(True)
    plt.legend(['BTC Price'])
    plt.tight_layout()
    plt.show()
