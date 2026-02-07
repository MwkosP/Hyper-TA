#External libraries
from fastapi import APIRouter
import pandas as pd
#Internal Imports
from src.ta.functions.indicators.threshold_functions import *
from src.ta.functions.indicators.universal_indicator_dispatcher import *
from src.ta.functions.indicators.universal_threshold_dispatcher import *
from main import df
from src.ta.functions.plots.plot_signals import *
from src.ta.ml.optimizers.searchSpaces import*


router = APIRouter(prefix="/strategies", tags=["TA - Strategies"])


@router.get("/")
def utils_root():
    return {"message": "🛠 Strategies API online"}





#? ============================================================
#? PAIR ENDPOINTS
#? ============================================================
@router.get("/pair1")
def strategy_pair1():
    signals = mixThresholds(df, [ssBUY[0]], mode="and")
    return {
        "title": "RSI TimeThreshold (14, below 40, min 2 candles)",
        "signals": signals.to_dict(orient="records")
    }


@router.get("/pair2")
def strategy_pair2():
    signals = mixThresholds(df, [cutBUY[1]], mode="and")
    return {
        "title": "RSI CrossUpThreshold (oversold → recovery)",
        "signals": signals.to_dict(orient="records")
    }


@router.get("/pair3")
def strategy_pair3():
    signals = mixThresholds(df, [irtBUY[7]], mode="and")
    return {
        "title": "Williams %R InRange (-100 to -80)",
        "signals": signals.to_dict(orient="records")
    }


@router.get("/pair4")
def strategy_pair4():
    signals = mixThresholds(df, [ttBUY[1]], mode="and")
    return {
        "title": "RSI TimeThreshold (below 35 for multiple candles)",
        "signals": signals.to_dict(orient="records")
    }


@router.get("/pair5")
def strategy_pair5():
    signals = mixThresholds(df, [ttBUY[6]], mode="and")
    return {
        "title": "ROC TimeThreshold (below -7, momentum accumulation)",
        "signals": signals.to_dict(orient="records")
    }


@router.get("/pair6")
def strategy_pair6():
    signals = mixThresholds(df, [ttBUY[7]], mode="and")
    return {
        "title": "Williams TimeThreshold (below -80 for X candles)",
        "signals": signals.to_dict(orient="records")
    }


@router.get("/pair7")
def strategy_pair7():
    signals = mixThresholds(df, [cultBUY[0]], mode="and")
    return {
        "title": "EMA Cross Above MA (LineThreshold)",
        "signals": signals.to_dict(orient="records")
    }




@router.get("/pair8")
def strategy_pair8():
    signals = mixThresholds(df, [ssBUY[2]], mode="and")
    return {
        "title": "RSI CrossUpThreshold (30 breakout)",
        "signals": signals.to_dict(orient="records")
    }


@router.get("/pair9")
def strategy_pair9():
    signals = mixThresholds(df, [cultBUY[1]], mode="and")
    return {
        "title": "EMA fast crosses ABOVE EMA slow",
        "signals": signals.to_dict(orient="records")
    }


@router.get("/pair10")
def strategy_pair10():
    signals = mixThresholds(df, [irtBUY[1]], mode="and")
    return {
        "title": "RSI InRange (consolidation-buy zone)",
        "signals": signals.to_dict(orient="records")
    }


@router.get("/pair11")
def strategy_pair11():
    signals = mixThresholds(df, [irtBUY[5]], mode="and")
    return {
        "title": "ADX InRange",
        "signals": signals.to_dict(orient="records")
    }


@router.get("/pair12")
def strategy_pair12():
    signals = mixThresholds(df, [ttBUY[5]], mode="and")
    return {
        "title": "ROC timeThreshold",
        "signals": signals.to_dict(orient="records")
    }


@router.get("/pair13")
def strategy_pair13():
    signals = mixThresholds(df, [cultBUY[2]], mode="and")
    return {
        "title": "MA Fast CrossUp Slow (trend reversal)",
        "signals": signals.to_dict(orient="records")
    }


@router.get("/pair14")
def strategy_pair14():
    signals = mixThresholds(df, [cultBUY[4]], mode="and")
    return {
        "title": "ATR Short CrossAbove ATR Long (volatility expansion)",
        "signals": signals.to_dict(orient="records")
    }


@router.get("/pair15")
def strategy_pair15():
    signals = mixThresholds(df, [irtBUY[7], ttBUY[7]], mode="and")
    return {
        "title": "Williams InRange (-100→-80) AND Williams Hold (below -80)",
        "signals": signals.to_dict(orient="records")
    }





#? ============================================================
#? PERCENTAGE DISTANCE PAIR ENDPOINTS
#? ============================================================
'''
@router.get("/pair1Percent")
def pair1_percent():
    return {"pair": 1, "percent_distance": threshold_distance(df, ssBUY[0])}

@router.get("/pair2Percent")
def pair2_percent():
    return {"pair": 2, "percent_distance": threshold_distance(df, cutBUY[1])}

@router.get("/pair3Percent")
def pair3_percent():
    return {"pair": 3, "percent_distance": threshold_distance(df, irtBUY[7])}

@router.get("/pair4Percent")
def pair4_percent():
    return {"pair": 4, "percent_distance": threshold_distance(df, ttBUY[1])}

@router.get("/pair5Percent")
def pair5_percent():
    return {"pair": 5, "percent_distance": threshold_distance(df, ttBUY[6])}

@router.get("/pair6Percent")
def pair6_percent():
    return {"pair": 6, "percent_distance": threshold_distance(df, ttBUY[7])}

@router.get("/pair7Percent")
def pair7_percent():
    return {"pair": 7, "percent_distance": threshold_distance(df, cultBUY[0])}

@router.get("/pair8Percent")
def pair8_percent():
    return {"pair": 8, "percent_distance": threshold_distance(df, ssBUY[2])}

@router.get("/pair9Percent")
def pair9_percent():
    return {"pair": 9, "percent_distance": threshold_distance(df, cultBUY[1])}

@router.get("/pair10Percent")
def pair10_percent():
    return {"pair": 10, "percent_distance": threshold_distance(df, irtBUY[1])}

@router.get("/pair11Percent")
def pair11_percent():
    return {"pair": 11, "percent_distance": threshold_distance(df, irtBUY[5])}

@router.get("/pair12Percent")
def pair12_percent():
    return {"pair": 12, "percent_distance": threshold_distance(df, ttBUY[5])}

@router.get("/pair13Percent")
def pair13_percent():
    return {"pair": 13, "percent_distance": threshold_distance(df, cultBUY[2])}

@router.get("/pair14Percent")
def pair14_percent():
    return {"pair": 14, "percent_distance": threshold_distance(df, cultBUY[4])}

@router.get("/pair15Percent")
def pair15_percent():
    p1 = threshold_distance(df, irtBUY[7])
    p2 = threshold_distance(df, ttBUY[7])
    return {
        "pair": 15,
        "percent_distance": max(p1, p2),  # worst-case distance
        "sub_distances": [p1, p2]
    }
    '''