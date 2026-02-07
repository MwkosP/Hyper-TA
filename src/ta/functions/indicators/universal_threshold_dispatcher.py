import pandas as pd
from src.ta.functions.indicators.threshold_functions import *
from src.ta.functions.indicators.universal_indicator_dispatcher import *

# === (Keep existing run_threshold and helper functions) ===
def run_threshold(df, cfg):
    # ... (Same as previous version) ...
    # Copy paste the full run_threshold function from your previous code
    t = cfg["type"]
    if t == "crossUpThreshold":
        return crossUpThreshold(df, type=cfg["indicator"], thr=cfg["thr"] if "thr" in cfg else cfg["threshold"][0] if isinstance(cfg["threshold"], list) else cfg["threshold"], period=cfg["period"][0] if isinstance(cfg["period"], list) else cfg["period"], wd=cfg.get("wd", 0), sell=cfg.get("sell", False), **cfg.get("indicator_params", {}))
    elif t == "crossUpLineThreshold":
        return crossUpLineThreshold(df, type1=cfg["ind1"] if "ind1" in cfg else cfg["indicators"][0], period1=cfg["period1"] if "period1" in cfg else cfg["periods"][0][0], type2=cfg["ind2"] if "ind2" in cfg else cfg["indicators"][1], period2=cfg["period2"] if "period2" in cfg else cfg["periods"][1][0], wd=cfg.get("wd", 0))
    elif t == "inRangeThreshold":
        return inRangeThreshold(df, type=cfg["indicator"], period=cfg["period"][0] if isinstance(cfg["period"], list) else cfg["period"], lower=cfg["lower"][0] if isinstance(cfg["lower"], list) else cfg["lower"], upper=cfg["upper"][0] if isinstance(cfg["upper"], list) else cfg["upper"], **cfg.get("indicator_params", {}))
    elif t == "timeThreshold":
        return timeThreshold(df, type=cfg["indicator"], period=cfg["period"][0] if isinstance(cfg["period"], list) else cfg["period"], level=cfg["threshold"][0] if isinstance(cfg["threshold"], list) else cfg["threshold"], direction=cfg["direction"][0] if isinstance(cfg["direction"], list) else cfg["direction"], min_candles=cfg["min_candles"][0] if isinstance(cfg["min_candles"], list) else cfg["min_candles"], wd=cfg.get("wd", 0), **cfg.get("indicator_params", {}))
    else: raise ValueError(f"Unknown: {t}")

# ======================================================
# mixThresholds — MASTER DISPATCHER
# ======================================================
def mixThresholds(df, configs, mode="and", search="grid"):
    """
    Routes to the correct Combinatorial Search engine.
    """
    from src.ta.ml.optimizers.search import (
        combinatorialGridSearch,
        combinatorialRandomSearch,
        combinatorialBayesianSearch
    )

    # If it's a list of blocks, we assume Combinatorial Logic is desired.
    # (Testing interactions between blocks).
    
    if search == "grid":
        print("🚀 Dispatching to Combinatorial GRID Search...")
        return combinatorialGridSearch(df, configs, mode=mode)
    
    elif search == "random":
        print("🚀 Dispatching to Combinatorial RANDOM Search...")
        return combinatorialRandomSearch(df, configs, n_iter=300, mode=mode)
        
    elif search == "bayesian":
        print("🚀 Dispatching to Combinatorial BAYESIAN Search...")
        return combinatorialBayesianSearch(df, configs, n_iter=300, mode=mode)
        
    else:
        raise ValueError(f"Unknown search type: {search}")