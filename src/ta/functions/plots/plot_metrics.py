import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.ta.functions.indicators.threshold_functions import skewThreshold,kurtosisThreshold

def plot_price_skew_kurt(df,window=20,skew_range=(-2.0, 1.0),kurt_range=(6.0, 6.0),use_log=True,log_returns=True):

    df_temp = df.copy()
    df_temp.columns = df_temp.columns.str.lower()

    if 'date' not in df_temp.columns:
        df_temp = df_temp.reset_index()

    df_temp['date'] = pd.to_datetime(df_temp['date'])

    if 'close' not in df_temp.columns:
        raise ValueError("DataFrame must contain 'close' column")

    # ---------------------------------
    # USE YOUR THRESHOLD FUNCTIONS
    # ---------------------------------
    skew_df = skewThreshold(df.copy(),window=window,s_range=skew_range)

    kurt_df = kurtosisThreshold(df.copy(),window=window,k_range=kurt_range)

    # ---------------------------------
    # Recompute FULL series using SAME logic
    # (needed because threshold returns only filtered rows)
    # ---------------------------------
    df_temp['returns'] = np.log(df_temp['close'] / df_temp['close'].shift(1))

    df_temp['skew'] = df_temp['returns'].rolling(window=window).skew()
    df_temp['kurt'] = df_temp['returns'].rolling(window=window).kurt()

    price = np.log(df_temp['close']) if use_log else df_temp['close']

    # ---------------------------------
    # PLOT
    # ---------------------------------
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.25, 0.25]
    )

    # PRICE
    fig.add_trace(
        go.Scatter(
            x=df_temp['date'],
            y=price,
            name="Price",
            mode="lines"
        ),
        row=1, col=1
    )

    # SKEW
    fig.add_trace(
        go.Scatter(
            x=df_temp['date'],
            y=df_temp['skew'],
            name=f"Rolling Skew ({window})",
            mode="lines"
        ),
        row=2, col=1
    )

    fig.add_hline(y=skew_range[0], row=2, col=1, line_dash="dash")
    fig.add_hline(y=skew_range[1], row=2, col=1, line_dash="dash")
    fig.add_hline(y=0, row=2, col=1)

    # KURT
    fig.add_trace(
        go.Scatter(
            x=df_temp['date'],
            y=df_temp['kurt'],
            name=f"Rolling Kurt ({window})",
            mode="lines"
        ),
        row=3, col=1
    )

    fig.add_hline(y=kurt_range[0], row=3, col=1, line_dash="dash")
    fig.add_hline(y=kurt_range[1], row=3, col=1, line_dash="dash")
    fig.add_hline(y=0, row=3, col=1)

    fig.update_layout(
        title="Price, Rolling Skew & Kurtosis",
        template="plotly_white",
        hovermode="x unified",
        height=950
    )

    fig.show()













def plot_rolling_entropy(df, ind_df, column='close', metric="both"):
    """
    Plot rolling entropy / stdv with price.

    Parameters:
        df : original dataframe (must contain Date + price)
        ind_df : output of calculate_rolling_entropy_stdv()
        column : price column
        metric : "entropy", "stdv", or "both"
    """

    if metric not in ["entropy", "stdv", "both"]:
        raise ValueError("metric must be 'entropy', 'stdv', or 'both'")

    # Determine subplot rows
    rows = 2 if metric != "both" else 3

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5] + [0.25] * (rows - 1)
    )

    # === 1. Price (Top Panel)
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[column],
            name="Price",
            line=dict(color="royalblue")
        ),
        row=1, col=1
    )

    # === 2. Entropy
    if metric in ["entropy", "both"]:
        fig.add_trace(
            go.Scatter(
                x=ind_df["Date"],
                y=ind_df["entropy"],
                name="Entropy",
                line=dict(color="orange")
            ),
            row=2 if metric != "both" else 2,
            col=1
        )

    # === 3. Std
    if metric in ["stdv", "both"]:
        fig.add_trace(
            go.Scatter(
                x=ind_df["Date"],
                y=ind_df["stdv"],
                name="Std(Pᵢ)",
                line=dict(color="green")
            ),
            row=2 if metric == "stdv" else 3,
            col=1
        )

    fig.update_layout(
        height=800 if metric == "both" else 600,
        width=1200,
        template="plotly_white",
        showlegend=True
    )

    fig.show()
