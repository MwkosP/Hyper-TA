"""Internal helpers for the thresholds package (not part of the simple user API)."""
from HyperTA.Thresholds.thresholds import (
    crossLevel,
    crossLines,
    inRange,
    holdLevel,
)


def _runThreshold(df, cfg):
    """Dispatch a single threshold config dict to the matching threshold function."""
    t = cfg["type"]
    if t == "crossLevel":
        return crossLevel(
            df,
            type=cfg["indicator"],
            thr=(
                cfg["thr"]
                if "thr" in cfg
                else cfg["threshold"][0]
                if isinstance(cfg["threshold"], list)
                else cfg["threshold"]
            ),
            period=cfg["period"][0] if isinstance(cfg["period"], list) else cfg["period"],
            wd=cfg.get("wd", 0),
            sell=cfg.get("sell", False),
            **cfg.get("indicator_params", {}),
        )
    elif t == "crossLines":
        return crossLines(
            df,
            type1=cfg["ind1"] if "ind1" in cfg else cfg["indicators"][0],
            period1=cfg["period1"] if "period1" in cfg else cfg["periods"][0][0],
            type2=cfg["ind2"] if "ind2" in cfg else cfg["indicators"][1],
            period2=cfg["period2"] if "period2" in cfg else cfg["periods"][1][0],
            wd=cfg.get("wd", 0),
        )
    elif t == "inRange":
        return inRange(
            df,
            type=cfg["indicator"],
            period=cfg["period"][0] if isinstance(cfg["period"], list) else cfg["period"],
            lower=cfg["lower"][0] if isinstance(cfg["lower"], list) else cfg["lower"],
            upper=cfg["upper"][0] if isinstance(cfg["upper"], list) else cfg["upper"],
            **cfg.get("indicator_params", {}),
        )
    elif t == "holdLevel":
        return holdLevel(
            df,
            type=cfg["indicator"],
            period=cfg["period"][0] if isinstance(cfg["period"], list) else cfg["period"],
            level=(
                cfg["threshold"][0]
                if isinstance(cfg["threshold"], list)
                else cfg["threshold"]
            ),
            direction=(
                cfg["direction"][0]
                if isinstance(cfg["direction"], list)
                else cfg["direction"]
            ),
            min_candles=(
                cfg["min_candles"][0]
                if isinstance(cfg["min_candles"], list)
                else cfg["min_candles"]
            ),
            wd=cfg.get("wd", 0),
            **cfg.get("indicator_params", {}),
        )
    else:
        raise ValueError(f"Unknown: {t}")
