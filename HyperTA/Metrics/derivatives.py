import numpy as np
import pandas as pd

from HyperTA.Metrics.utils import _firstDerivative, _secondDerivative


def rollingDerivative(df, k=40, alpha=1.0, scale=True, derivative="first"):
    """
    Rolling derivative calculator.

    Parameters
    ----------
    df : pd.DataFrame (must contain 'Close')
    k : int
        Window size
    alpha : float
        Weight coefficient
    scale : bool
    derivative : str
        "first", "second", or "both"

    Returns
    -------
    pd.DataFrame
    """

    if "Close" not in df.columns:
        raise ValueError("Column 'Close' not found in DataFrame")

    y_full = df["Close"]
    n = len(y_full)

    first_vals = np.full(n, np.nan)
    second_vals = np.full(n, np.nan)

    for i in range(k - 1, n):

        window = y_full.iloc[i - k + 1 : i + 1]

        if derivative == "first":
            first_vals[i] = _firstDerivative(k, window, alpha, scale)

        elif derivative == "second":
            second_vals[i] = _secondDerivative(k, window, alpha, scale)

        elif derivative == "both":
            first_vals[i] = _firstDerivative(k, window, alpha, scale)
            second_vals[i] = _secondDerivative(k, window, alpha, scale)

        else:
            raise ValueError("derivative must be 'first', 'second', or 'both'")

    # ---- Return proper structure ----
    if derivative == "first":
        return pd.DataFrame({
            "Date": df["Date"],
            "First_Derivative": first_vals
        })

    elif derivative == "second":
        return pd.DataFrame({
            "Date": df["Date"],
            "Second_Derivative": second_vals
        })

    elif derivative == "both":
        return pd.DataFrame({
            "Date": df["Date"],
            "First_Derivative": first_vals,
            "Second_Derivative": second_vals
        })


