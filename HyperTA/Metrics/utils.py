"""Internal helpers for metrics (building blocks; users call rollingDerivative)."""
import numpy as np
import pandas as pd

#!make the df[clsoe]  --   y = y.iloc[:, 0] -- problem of close name etc
def _firstDerivative(k, y, alpha=1.0, scale=True):
    """
    Local weighted linear regression (first derivative)
    -AVOIDING NOISE OF NORMAL 1ST DERIVATIVE WITH THIS FUNC

    Parameters
    ----------
    k : int
        Window size
    y : array-like / pd.Series
        Last k values of signal
    alpha : float
        Weight coefficient (0 < alpha <= 1)
        Smaller alpha -> stronger emphasis on recent data
        alpha=1 -> uniform weights
    scale : bool
        Whether to scale time to [-1,1]

    Returns
    -------
    slope : float
    """

    # ---- Prepare y ----
    if isinstance(y, pd.DataFrame):
        y = y.iloc[:, 0]

    # ---- Data preperation ----
    y = pd.Series(y).dropna()
    #y = y[::-1]
    y= np.log(y)


    y = np.asarray(y).flatten()

    if len(y) != k:
        raise ValueError("Length of y must equal k")

    # ---- Build time vector ----
    t = np.arange(k)

    # ---- Build weights (recent bigger) ----
    if alpha <= 0:
        raise ValueError("alpha must be > 0")

    # raw weights
    w_raw = alpha ** (k - 1 - t)  #is this k data?

    # normalize by mean (your type)
    w = w_raw / np.mean(w_raw)

    # diagonal matrix
    W = np.diag(w)

    # ---- Weighted centering ----
    t_bar = np.sum(w * t) / np.sum(w)
    t_centered = t - t_bar

    # ---- Scaling ----
    if scale:
        S = (k - 1) / 2
        if S != 0:
            t_scaled = t_centered / S
        else:
            t_scaled = t_centered
    else:
        t_scaled = t_centered

    # ---- Design matrix ----
    X = np.column_stack([np.ones(k), t_scaled])

    # ---- Solve WLS ----
    theta = np.linalg.solve(X.T @ W @ X, X.T @ W @ y)

    slope = theta[1]

    return slope






#!make the df[clsoe] +FIRST DERIVATIVE MUST BE TAKEN AS INPUT
def _secondDerivative(k,y,alpha=1.0, scale=True):
    """
    Local weighted quadratic regression (second derivative)

    Parameters
    ----------
    k : int
        Window size
    y : array-like / pd.Series
        Last k values
    alpha : float
        Weight coefficient (0 < alpha <= 1)
    scale : bool
        Whether to scale time to [-1,1]

    Returns
    -------
    second_deriv : float
        Estimated second derivative (2*beta2)
    """

    # ---- Prepare y ----
    if isinstance(y, pd.DataFrame):
        y = y.iloc[:, 0]

    y = pd.Series(y).dropna()
    #y = y[::-1]        # keep if you intentionally invert
    y = np.log(y)      # optional but consistent with first derivative

    y = np.asarray(y).flatten()

    if len(y) != k:
        raise ValueError("Length of y must equal k")

    # ---- Time vector ----
    t = np.arange(k)

    # ---- Weights (recent bigger) ----
    if alpha <= 0:
        raise ValueError("alpha must be > 0")

    w_raw = alpha ** (k - 1 - t)
    w = w_raw / np.mean(w_raw)
    W = np.diag(w)

    # ---- Weighted centering ----
    t_bar = np.sum(w * t) / np.sum(w)
    t_centered = t - t_bar

    # ---- Scaling ----
    if scale:
        S = (k - 1) / 2
        t_scaled = t_centered / S if S != 0 else t_centered
    else:
        t_scaled = t_centered

    # ---- Design matrix (k x 3) ----
    X = np.column_stack([
        np.ones(k),
        t_scaled,
        t_scaled**2
    ])

    # ---- Solve WLS ----
    theta = np.linalg.solve(X.T @ W @ X, X.T @ W @ y)

    beta2 = theta[2]

    # Second derivative of quadratic = 2*beta2
    second_deriv = 2 * beta2

    return second_deriv





