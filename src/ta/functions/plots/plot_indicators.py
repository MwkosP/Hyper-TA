import matplotlib.pyplot as plt

def plot_indicator(df, plot_name, **plot_kwargs):
    """Generic indicator plotter.
    
    df: DataFrame returned by calculate_indicator()
        Must contain 'Date' + indicator columns
    indicator_name: str
        Displayed on title
    plot_kwargs: dict
        Additional parameters for special indicators"""

    plt.figure(figsize=(14, 5))

    # All columns except 'Date'
    cols = [c for c in df.columns if c != "Date"]

    # Plot each indicator column
    for col in cols:
        plt.plot(df['Date'], df[col], label=col)

    plt.title(plot_name)
    plt.xlabel("Date")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()





import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_price_and_derivatives(
    df,
    indicator_df,
    price_col="close",
    first_col="First_Derivative",
    second_col="Second_Derivative"
):
    """
    Plots BTC price (top), first derivative (middle),
    and second derivative (bottom).
    """

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2]
    )

    # ---- PRICE (Row 1) ----
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[price_col],
            name="BTC Price",
            line=dict(color="black", width=1.5)
        ),
        row=1,
        col=1
    )

    # ---- FIRST DERIVATIVE (Row 2) ----
    fig.add_trace(
        go.Scatter(
            x=indicator_df["Date"],
            y=indicator_df[first_col],
            name="First Derivative",
            line=dict(color="orange", width=1.5)
        ),
        row=2,
        col=1
    )

    fig.add_hline(
        y=0,
        line=dict(color="gray", dash="dash"),
        row=2,
        col=1
    )

    # ---- SECOND DERIVATIVE (Row 3) ----
    fig.add_trace(
        go.Scatter(
            x=indicator_df["Date"],
            y=indicator_df[second_col],
            name="Second Derivative",
            line=dict(color="blue", width=1.5)
        ),
        row=3,
        col=1
    )

    fig.add_hline(
        y=0,
        line=dict(color="gray", dash="dash"),
        row=3,
        col=1
    )

    # ---- Layout ----
    fig.update_layout(
        height=900,
        title="BTC Price, First & Second Derivatives",
        template="plotly_white",
        hovermode="x unified"
    )

    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="First Derivative", row=2, col=1)
    fig.update_yaxes(title_text="Second Derivative", row=3, col=1)

    fig.show()
