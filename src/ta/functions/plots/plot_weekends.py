import matplotlib.pyplot as plt
import pandas as pd

def plot_price_with_marked_days(df, days_to_mark=None, dot_color="orange"):
    """
    Plot price and optionally mark specific weekday candles.
    
    Parameters:
        df (DataFrame): must contain Date and close.
        days_to_mark (list of ints or None):
            Example: [5, 6] → Saturday & Sunday
                     [4] → Friday only
                     None → plot only price (no dots)
        dot_color (str): color for markers
    """

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    # Plot price
    plt.figure(figsize=(14, 6))
    plt.plot(df["Date"], df["close"], color="black", label="Price")

    # If days_to_mark is provided → mark days
    if days_to_mark is not None and len(days_to_mark) > 0:

        df["weekday"] = df["Date"].dt.weekday

        for day in days_to_mark:
            day_df = df[df["weekday"] == day]

            plt.scatter(
                day_df["Date"], day_df["close"],
                color=dot_color, s=30,
                label=f"Day {day}"  # optional label
            )

    plt.title("Price with Optional Marked Weekday Dots")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.legend()
    plt.show()
