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
