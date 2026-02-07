import numpy as np


#?-------------------------------------------------------
#?CrossUpThreshold BUY Search Space
#TODO: Make ranges correct  
#?-------------------------------------------------------
cutBUY = [

    # =====================================================
    # MACD BUY — crosses up above 0 (bullish momentum begins)
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "macd",

        "period": list(range(5, 21, 5)),    # indicator period sweep
        "threshold": [-10],                   # BUY when macd crosses ABOVE 0
        "wd": 0,

        "indicator_params": {
            "fast": list(range(5, 21, 5)),
            "slow": list(range(10, 51, 10)),
            "signal": list(range(5, 16, 5))
        }
    },

    # =====================================================
    # RSI BUY — crosses up above 30 (oversold→recovery)
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "rsi",

        "period": list(range(7, 29, 7)),
        "threshold": [30],              # BUY when RSI crosses UP through 30
        "wd": 0,

        "indicator_params": {
            "indicator_period": list(range(7, 29, 7))
        }
    },

    # =====================================================
    # StochRSI BUY — crosses up above 0.2 (oversold to rising)
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "stochrsi",

        "period": list(range(14, 50, 4)),
        "threshold": [round(x, 3) for x in np.arange(0.05, 0.40, 0.05)],    # correct for 0–1 range
        "wd": 0,

        "indicator_params": {
            "rsi_length": [14],
            "stoch_length": [14],
            "k": [3],
            "d": [3]
        }
    },

    # =====================================================
    # MA BUY — price crossing up above MA
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "ma",

        "period": list(range(5, 101, 5)),
        "threshold": [0],              # Later interpreted as crossing above MA
        "wd": 0,

        "indicator_params": {
            "period": list(range(5, 101, 5))
        }
    },

    # =====================================================
    # EMA BUY — crossing above EMA
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "ema",

        "period": list(range(5, 101, 5)),
        "threshold": [0],            # BUY when price crosses above EMA
        "wd": 0,

        "indicator_params": {
            "period": list(range(5, 101, 5))
        }
    },

    # =====================================================
    # ADX BUY — crosses up above 25 (strong trend forming)
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "adx",

        "period": list(range(14, 29, 7)),
        "threshold": [25],           # BUY when ADX rises above 25
        "wd": 0,

        "indicator_params": {
            "period": list(range(14, 29, 7))
        }
    },

    # =====================================================
    # ROC BUY — crosses above 0 (momentum turns positive)
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "roc",

        "period": list(range(7, 29, 7)),
        "threshold": [-15],           # BUY when momentum becomes positive
        "wd": 0,

        "indicator_params": {
            "indicator_period": list(range(7, 29, 7))
        }
    },

    # =====================================================
    # Williams %R BUY — crosses up above -80 (leaving oversold)
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "williams",

        "period": list(range(7, 50, 1)),
        "threshold": list(range(-80,-100, -1)),         # oversold level, BUY when crossing up
        "wd": 0,

        "indicator_params": {
            
        }
    },

    # =====================================================
    # ATR BUY — crosses up above chosen threshold (volatility expansion)
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "atr",

        "period": list(range(7, 29, 7)),
        "threshold": list(range(1, 11)),   # BUY when ATR expands
        "wd": 0,

        "indicator_params": {
            "period": list(range(7, 29, 7))
        }
    },

    # =====================================================
    # Donchian BUY — cross above midrange (breakout)
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "donchian",

        "period": list(range(20, 61, 20)),
        "threshold": [0],          # used as breakout logic
        "wd": 0,

        "indicator_params": {
            "period": list(range(20, 61, 20))
        }
    },

    # =====================================================
    # Bollinger Bands BUY — cross above lower band midpoint
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "bbands",

        "period": list(range(20, 61, 20)),
        "threshold": [-1],            # below mid → bullish reversal
        "wd": 0,

        "indicator_params": {
            "indicator_period": list(range(20, 61, 20)),
            "std": [1, 2, 3]
        }
    },

]



#?-------------------------------------------------------
#?CrossUpThreshold SELL Search Space
#?-------------------------------------------------------
cutSELL = [

    # =====================================================
    # MACD SELL — crosses DOWN below 0 (bearish momentum)
    # =====================================================
    {
        "type": "crossUpThreshold",              # still "crossUpThreshold", logic inverted via threshold
        "indicator": "macd",

        "period": list(range(5, 21, 5)),
        "threshold": [0],                        # SELL when MACD crosses DOWN through 0
        "wd": 0,

        "indicator_params": {
            "fast": list(range(5, 21, 5)),
            "slow": list(range(10, 51, 10)),
            "signal": list(range(5, 16, 5))
        },

        #TODO SELL inversion rule used later in threshold logic:
        # previous > thr and now < thr
        "sell": True
    },

    # =====================================================
    # RSI SELL — crosses DOWN below 70 (overbought reversal)
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "rsi",

        "period": list(range(7, 50, 1)),
        "threshold": list(range(80, 90, 1)),                   # SELL when RSI crosses DOWN through 70
        "wd": 0,

        "indicator_params": {
            "indicator_period": list(range(7, 50, 3))
        },

        "sell": True
    },

    # =====================================================
    # StochRSI SELL — crosses DOWN below 0.8
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "stochrsi",

        "period": list(range(14, 29, 7)),
        "threshold": [0.8],                 # SELL when crossing down
        "wd": 0,

        "indicator_params": {
            "rsi_length": list(range(7, 29, 7)),
            "stoch_length": list(range(7, 29, 7)),
            "k": list(range(3, 10)),
            "d": list(range(3, 10))
        },

        "sell": True
    },

    # =====================================================
    # MA SELL — price crosses DOWN below MA
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "ma",

        "period": list(range(5, 101, 5)),
        "threshold": [0],                    # interpreted as price < MA
        "wd": 0,

        "indicator_params": {
            "period": list(range(5, 101, 5))
        },

        "sell": True
    },

    # =====================================================
    # EMA SELL — price crosses DOWN below EMA
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "ema",

        "period": list(range(5, 101, 5)),
        "threshold": [0],
        "wd": 0,

        "indicator_params": {
            "period": list(range(5, 101, 5))
        },

        "sell": True
    },

    # =====================================================
    # ADX SELL — crosses DOWN below 25 (trend weakens)
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "adx",

        "period": list(range(14, 29, 7)),
        "threshold": [25],
        "wd": 0,

        "indicator_params": {
            "period": list(range(14, 29, 7))
        },

        "sell": True
    },

    # =====================================================
    # ROC SELL — crosses DOWN below 0 (momentum turns negative)
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "roc",

        "period": list(range(7, 29, 7)),
        "threshold": [0],
        "wd": 0,

        "indicator_params": {
            "period": list(range(7, 29, 7))
        },

        "sell": True
    },

    # =====================================================
    # Williams %R SELL — crosses DOWN below -20 (overbought exit)
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "williams",

        "period": list(range(7, 29, 7)),
        "threshold": [-20],              # SELL when dropping from overbought
        "wd": 0,

        "indicator_params": {
            "period": list(range(7, 29, 7))
        },

        "sell": True
    },

    # =====================================================
    # ATR SELL — crosses DOWN below shrinking volatility level
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "atr",

        "period": list(range(7, 29, 7)),
        "threshold": list(range(1, 11)),
        "wd": 0,

        "indicator_params": {
            "period": list(range(7, 29, 7))
        },

        "sell": True
    },

    # =====================================================
    # Donchian SELL — crosses DOWN below breakout midline
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "donchian",

        "period": list(range(20, 61, 20)),
        "threshold": [0],
        "wd": 0,

        "indicator_params": {
            "period": list(range(20, 61, 20))
        },

        "sell": True
    },

    # =====================================================
    # Bollinger SELL — crosses DOWN below mid-band
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "bbands",

        "period": list(range(20, 61, 20)),
        "threshold": [1],              # above mid → reversal downward
        "wd": 0,

        "indicator_params": {
            "period": list(range(20, 61, 20)),
            "std": [1, 2, 3]
        },

        "sell": True
    },

    # =====================================================
    # EMA Ribbon SELL — crosses below largest EMA
    # =====================================================
    {
        "type": "crossUpThreshold",
        "indicator": "ema_ribbon",

        "period": [233],
        "threshold": [0],
        "wd": 0,

        "indicator_params": {
            "periods": [list(range(8, 233, 13))]
        },

        "sell": True
    }
]


#?-------------------------------------------------------
#?crossUpLineThreshold BUY Search Space
#?-------------------------------------------------------
cultBUY = [

    # =====================================================
    # EMA crosses ABOVE MA → BUY
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["ema", "ma"],     # ema crosses ABOVE ma

        # periods = [periods_for_ind1, periods_for_ind2]
        "periods": [
            list(range(5, 51, 5)),       # EMA periods
            list(range(10, 101, 10))     # MA periods
        ],

        "wd": 0
    },

    # =====================================================
    # EMA fast crosses ABOVE EMA slow (EMA crossover BUY)
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["ema", "ema"],    # EMA fast > EMA slow

        "periods": [
            list(range(5, 21, 5)),       # fast EMA
            list(range(20, 101, 20))     # slow EMA
        ],

        "wd": 0
    },

    # =====================================================
    # MA fast crosses ABOVE MA slow → BUY trend change
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["ma", "ma"],      # faster MA crosses above slower MA

        "periods": [
            list(range(5, 51, 5)),       # fast MA
            list(range(20, 201, 20))     # slow MA
        ],

        "wd": 0
    },

    # =====================================================
    # RSI fast vs RSI slow (custom two-line RSI crossover)
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["rsi", "rsi"],

        "periods": [
            list(range(7, 21, 7)),       # fast RSI
            list(range(21, 56, 7))       # slow RSI
        ],

        "wd": 0
    },

    # =====================================================
    # ATR shorter period crosses ABOVE longer ATR → volatility expansion BUY
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["atr", "atr"],

        "periods": [
            list(range(7, 21, 7)),       # short ATR
            list(range(21, 56, 7))       # long ATR
        ],

        "wd": 0
    },

    # =====================================================
    # Donchian midline crossover (short crosses above long)
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["donchian", "donchian"],

        "periods": [
            list(range(20, 61, 20)),     # short Donchian
            list(range(60, 121, 20))     # long Donchian
        ],

        "wd": 0
    },

    # =====================================================
    # Bollinger midline (BB basis) shorter period crosses above slower BB → BUY
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["bbands", "bbands"],

        "periods": [
            list(range(10, 41, 10)),     # short BB
            list(range(40, 101, 20))     # long BB
        ],

        "wd": 0
    },

    # =====================================================
    # ATR → EMA (volatility crosses above trendline)
    # Interesting strategy combination
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["atr", "ema"],

        "periods": [
            list(range(7, 29, 7)),       # ATR
            list(range(20, 101, 20))     # EMA
        ],

        "wd": 0
    },

    # =====================================================
    # ROC crosses ABOVE EMA of ROC → BUY momentum trigger
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["roc", "ema"],

        "periods": [
            list(range(7, 29, 7)),           # ROC period
            list(range(20, 101, 20))         # EMA period
        ],

        "wd": 0
    }
]




#?-------------------------------------------------------
#?crossUpLineThreshold SELL Search Space
#?-------------------------------------------------------
cultSELL = [

    # =====================================================
    # EMA crosses BELOW MA → SELL
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["ema", "ma"],     # ema drops below ma

        "periods": [
            list(range(5, 51, 5)),       # EMA periods (fast)
            list(range(10, 101, 10))     # MA periods (slow)
        ],

        "wd": 0,
        "sell": True
    },

    # =====================================================
    # EMA fast crosses BELOW EMA slow → SELL
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["ema", "ema"],

        "periods": [
            list(range(5, 21, 5)),       # fast EMA
            list(range(20, 101, 20))     # slow EMA
        ],

        "wd": 0,
        "sell": True
    },

    # =====================================================
    # MA fast crosses BELOW MA slow → SELL
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["ma", "ma"],

        "periods": [
            list(range(5, 51, 5)),       # fast MA
            list(range(20, 201, 20))     # slow MA
        ],

        "wd": 0,
        "sell": True
    },

    # =====================================================
    # RSI fast crosses BELOW RSI slow → SELL
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["rsi", "rsi"],

        "periods": [
            list(range(7, 21, 7)),       # fast RSI
            list(range(21, 56, 7))       # slow RSI
        ],

        "wd": 0,
        "sell": True
    },

    # =====================================================
    # ATR short crosses BELOW ATR long → volatility contraction SELL
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["atr", "atr"],

        "periods": [
            list(range(7, 21, 7)),       # short ATR
            list(range(21, 56, 7))       # long ATR
        ],

        "wd": 0,
        "sell": True
    },

    # =====================================================
    # Donchian short crosses BELOW Donchian long → SELL
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["donchian", "donchian"],

        "periods": [
            list(range(20, 61, 20)),     # short Donchian
            list(range(60, 121, 20))     # long Donchian
        ],

        "wd": 0,
        "sell": True
    },

    # =====================================================
    # Bollinger short crosses BELOW long → SELL
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["bbands", "bbands"],

        "periods": [
            list(range(10, 41, 10)),     # short BB
            list(range(40, 101, 20))     # long BB
        ],

        "wd": 0,
        "sell": True
    },

    # =====================================================
    # ATR crosses BELOW EMA → SELL (volatility fades under trend)
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["atr", "ema"],

        "periods": [
            list(range(7, 29, 7)),       # ATR
            list(range(20, 101, 20))     # EMA
        ],

        "wd": 0,
        "sell": True
    },

    # =====================================================
    # ROC crosses BELOW EMA(ROC) → SELL momentum shift
    # =====================================================
    {
        "type": "crossUpLineThreshold",

        "indicators": ["roc", "ema"],

        "periods": [
            list(range(7, 29, 7)),       # ROC
            list(range(20, 101, 20))     # EMA
        ],

        "wd": 0,
        "sell": True
    }
]






#?-------------------------------------------------------
#?inRangeThreshold BUY Search Space
#?-------------------------------------------------------
irtBUY = [

    # =====================================================
    # MACD BUY — MACD inside bullish consolidation zone
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "macd",

        "period": list(range(5, 21, 3)),
        "lower": list(range(-10, 1, 3)),      # MACD slightly negative to 0
        "upper": list(range(0, 21, 3)),       # up to 20
        "wd": 0,

        "indicator_params": {
            "fast": list(range(5, 21, 3)),
            "slow": list(range(10, 51, 3)),
            "signal": list(range(5, 16, 3)),
        }
    },

    # =====================================================
    # RSI BUY — RSI between oversold (30) and mid (50)
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "rsi",

        "period": list(range(7, 50, 1)),
        "lower": list(range(0, 22, 3)),              # oversold area
        "upper": list(range(23,40 , 2)),              # rising but not overbought
        "wd": list(range(0,3 , 1)),

        "indicator_params": {
            
        }
    },

    # =====================================================
    # StochRSI BUY — inside 0.1 to 0.4 zone
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "stochrsi",

        "period": list(range(14, 29, 7)),
        "lower": np.arange(0.1, 0.3, 0.01),
        "upper": np.arange(0.31, 0.5, 0.01),
        "wd": 0,

        "indicator_params": {
            "rsi_length": list(range(7, 29, 1)),
            "stoch_length": list(range(7, 29, 1)),
            "k": list(range(3, 10,1)),
            "d": list(range(3, 10,1))
        }
    },

    # =====================================================
    # MA BUY — price near or slightly above MA
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "ma",

        "period": list(range(5, 101, 5)),
        "lower": [-5],                # price slightly below MA
        "upper": [90000],                 # to slightly above MA
        "wd": 0,

        "indicator_params": {
            
        }
    },

    # =====================================================
    # EMA BUY — price inside EMA zone
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "ema",

        "period": list(range(5, 101, 5)),
        "lower": [80000],
        "upper": [90000],
        "wd": 0,

        "indicator_params": {
            
        }
    },

    # =====================================================
    # ADX BUY — ADX between 20–40 (trend strengthening)
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "adx",

        "period": list(range(14, 29, 7)),
        "lower": [0, 15],
        "upper": [21, 25],
        "wd": 0,

        "indicator_params": {
            
        }
    },

    # =====================================================
    # ROC BUY — small positive range (momentum forming)
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "roc",

        "period": list(range(7, 50, 1)),
        "lower": list(range(-50, -30, 1)),
        "upper": list(range(-31,-20 , 1)),
        "wd": list(range(0,3 , 1)),

        "indicator_params": {
            
        }
    },

    # =====================================================
    # Williams %R BUY — between -100 and -80 (oversold)
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "williams",

        "period": list(range(7, 50, 3)),
        "lower": list(range(-100, -90, 8)),   
        "upper": list(range(-90, -80, 8)),    
        "wd": 0,

        "indicator_params": {
            
        }
    },

    # =====================================================
    # ATR BUY — low-moderate volatility (ideal entries)
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "atr",

        "period": list(range(7, 29, 7)),
        "lower": list(range(1500, 2000)),     # ATR small
        "upper": list(range(4000, 5000)),    # ATR rising
        "wd": 0,

        "indicator_params": {
           
        }
    },

    # =====================================================
    # Donchian BUY — price inside lower to mid channel
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "donchian",

        "period": list(range(20, 61, 20)),
        "lower": [70000],             # use normalized range logic
        "upper": [10000],
        "wd": 0,

        "indicator_params": {
            
        }
    },

    # =====================================================
    # BBANDS BUY — price inside lower to mid band
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "bbands",

        "period": list(range(20, 61, 20)),
        "lower": [-2],               # below mid
        "upper": [0],                # at mid band
        "wd": 0,

        "indicator_params": {
            
            "std": [1, 2, 3],
        }
    },

    # =====================================================
    # EMA Ribbon BUY — price inside ribbon lower half
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "ema_ribbon",

        "period": [14],             # largest EMA base
        "lower": [7000],
        "upper": [9000],                # between mid and top ribbon
        "wd": 0,

        "indicator_params": {
            
        }
    },

]





#?-------------------------------------------------------
#?inRangeThreshold SELL Search Space
#?-------------------------------------------------------
irtSELL = [

    # =====================================================
    # MACD SELL — MACD inside topping zone
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "macd",

        "period": list(range(5, 21, 5)),
        "lower": list(range(10, 31, 10)),     # MACD positive, slowing
        "upper": list(range(30, 61, 10)),     # high → turning zone
        "wd": 0,

        "indicator_params": {
            "fast": list(range(5, 21, 5)),
            "slow": list(range(10, 51, 10)),
            "signal": list(range(5, 16, 5)),
        },

        "sell": True
    },

    # =====================================================
    # RSI SELL — RSI between 60–80 (overbought zone)
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "rsi",

        "period": list(range(7, 29, 7)),
        "lower": [60, 65, 70],           # rising to overbought
        "upper": [75, 80],               # heavy SELL area
        "wd": 0,

        "indicator_params": {
            "period": list(range(7, 29, 7))
        },

        "sell": True
    },

    # =====================================================
    # StochRSI SELL — distribution zone 0.6–1.0
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "stochrsi",

        "period": list(range(14, 29, 7)),
        "lower": [0.6, 0.7],
        "upper": [0.9, 1.0],
        "wd": 0,

        "indicator_params": {
            "rsi_length": list(range(7, 29, 7)),
            "stoch_length": list(range(7, 29, 7)),
            "k": list(range(3, 10)),
            "d": list(range(3, 10)),
        },

        "sell": True
    },

    # =====================================================
    # MA SELL — price near or above MA (topping)
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "ma",

        "period": list(range(5, 101, 5)),
        "lower": [0],               # touching MA
        "upper": [10],              # slightly above
        "wd": 0,

        "indicator_params": {
            "period": list(range(5, 101, 5))
        },

        "sell": True
    },

    # =====================================================
    # EMA SELL — price inside upper EMA zone
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "ema",

        "period": list(range(5, 101, 5)),
        "lower": [0],
        "upper": [10],
        "wd": 0,

        "indicator_params": {
            "period": list(range(5, 101, 5))
        },

        "sell": True
    },

    # =====================================================
    # ADX SELL — ADX between 40–60 (trend exhaustion)
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "adx",

        "period": list(range(14, 29, 7)),
        "lower": [30, 35, 40],
        "upper": [50, 55, 60],
        "wd": 0,

        "indicator_params": {
            "period": list(range(14, 29, 7))
        },

        "sell": True
    },

    # =====================================================
    # ROC SELL — negative to strongly negative zone
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "roc",

        "period": list(range(7, 29, 7)),
        "lower": list(range(-15, -5, 5)),    # soft decline
        "upper": list(range(-5, 1, 5)),      # strong downward momentum
        "wd": 0,

        "indicator_params": {
            "period": list(range(7, 29, 7))
        },

        "sell": True
    },

    # =====================================================
    # Williams %R SELL — between -20 and 0 (overbought)
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "williams",

        "period": list(range(7, 29, 7)),
        "lower": [-20],
        "upper": [0],
        "wd": 0,

        "indicator_params": {
            "period": list(range(7, 29, 7))
        },

        "sell": True
    },

    # =====================================================
    # ATR SELL — low volatility (trend dying)
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "atr",

        "period": list(range(7, 29, 7)),
        "lower": list(range(1, 4)),      # declining ATR
        "upper": list(range(4, 7)),      # flattening ATR
        "wd": 0,

        "indicator_params": {
            "period": list(range(7, 29, 7))
        },

        "sell": True
    },

    # =====================================================
    # Donchian SELL — price inside top channel
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "donchian",

        "period": list(range(20, 61, 20)),
        "lower": [2],                   # top region
        "upper": [3],                   # near breakout failure
        "wd": 0,

        "indicator_params": {
            "period": list(range(20, 61, 20))
        },

        "sell": True
    },

    # =====================================================
    # BBANDS SELL — price between mid & upper band
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "bbands",

        "period": list(range(20, 61, 20)),
        "lower": [0],                  # mid band
        "upper": [2],                  # upper region
        "wd": 0,

        "indicator_params": {
            "period": list(range(20, 61, 20)),
            "std": [1, 2, 3],
        },

        "sell": True
    },

    # =====================================================
    # EMA Ribbon SELL — inside upper ribbon half
    # =====================================================
    {
        "type": "inRangeThreshold",
        "indicator": "ema_ribbon",

        "period": [233],
        "lower": [0],                 # mid ribbon
        "upper": [20],                # top ribbon
        "wd": 0,

        "indicator_params": {
            "periods": [list(range(8, 233, 13))]
        },

        "sell": True
    },

]









#?-------------------------------------------------------
#?timeThreshold BUY Search Space
#?-------------------------------------------------------
ttBUY = [

    # =====================================================
    # MACD BUY — stays BELOW 0 for several candles (accumulation)
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "macd",

        "period": list(range(5, 21, 5)),
        "threshold": [0],                 # stays below zero
        "direction": ["below"],           # then BUY
        "min_candles": list(range(2, 6)), # accumulation window
        "wd": 0,

        "indicator_params": {
            "fast": list(range(5, 21, 5)),
            "slow": list(range(10, 51, 10)),
            "signal": list(range(5, 16, 5)),
        }
    },

    # =====================================================
    # RSI BUY — stays BELOW 30 (oversold) for X candles
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "rsi",

        "period": list(range(14, 50, 3)),
        "threshold": [35],
        "direction": ["below"],           # oversold
        "min_candles": list(range(2, 6, 1)),
        "wd": 0,

        "indicator_params": {
            
        }
    },

    # =====================================================
    # StochRSI BUY — stays below 0.2 (deep oversold)
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "stochrsi",

        "period": list(range(14, 29, 7)),
        "threshold": [0.2],
        "direction": ["below"],
        "min_candles": list(range(2, 6)),
        "wd": 0,

        "indicator_params": {
            "rsi_length": list(range(7, 29, 7)),
            "stoch_length": list(range(7, 29, 7)),
            "k": list(range(3, 10,5)),
            "d": list(range(3, 10,5)),
        }
    },

    # =====================================================
    # MA BUY — price stays ABOVE MA
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "ma",

        "period": list(range(5, 101, 5)),
        "threshold": [0],
        "direction": ["above"],           # above MA = bullish confirmation
        "min_candles": list(range(2, 6)),
        "wd": 0,

        "indicator_params": {
            
        }
    },

    # =====================================================
    # EMA BUY — price stays ABOVE EMA
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "ema",

        "period": list(range(5, 101, 5)),
        "threshold": [0],
        "direction": ["above"],
        "min_candles": list(range(2, 6)),
        "wd": 0,

        "indicator_params": {
           
        }
    },

    # =====================================================
    # ADX BUY — ADX stays ABOVE 25 (trend strengthening)
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "adx",

        "period": list(range(14, 29, 7)),
        "threshold": [25],
        "direction": ["above"],
        "min_candles": list(range(2, 6)),
        "wd": 0,

        "indicator_params": {
            
        }
    },

    # =====================================================
    # ROC BUY — stays ABOVE 0 (positive momentum persists)
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "roc",

        "period": list(range(7, 29, 7)),
        "threshold": [-7],
        "direction": ["below"],
        "min_candles": list(range(2, 6)),
        "wd": 0,

        "indicator_params": {
           
        }
    },

    # =====================================================
    # Williams %R BUY — stays BELOW -80 (deep oversold)
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "williams",

        "period": list(range(7, 50, 3)),
        "threshold": list(range(-80, -100, -5)),
        "direction": ["below"],           # oversold hold → BUY
        "min_candles": list(range(3, 6)),
        "wd": 0,

        "indicator_params": {
            
        }
    },

    # =====================================================
    # ATR BUY — stays ABOVE rising volatility threshold
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "atr",

        "period": list(range(7, 29, 7)),
        "threshold": list(range(70000, 100000)),  # sustained volatility → breakout incoming
        "direction": ["below"],
        "min_candles": list(range(2, 6)),
        "wd": 0,

        "indicator_params": {
            
        }
    },

    # =====================================================
    # Donchian BUY — stays ABOVE mid-channel
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "donchian",

        "period": list(range(20, 61, 20)),
        "threshold": [0],                 # above midline
        "direction": ["below"],
        "min_candles": list(range(2, 6)),
        "wd": 0,

        "indicator_params": {
            
        }
    },

    # =====================================================
    # BBANDS BUY — stays BELOW lower band midpoint
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "bbands",

        "period": list(range(20, 61, 20)),
        "threshold": [-1],                # deep dip
        "direction": ["below"],           # staying "cheap" = strong BUY
        "min_candles": list(range(2, 6)),
        "wd": 0,

        "indicator_params": {
            
            "std": [1, 2, 3],
        }
    },

    # =====================================================
    # EMA Ribbon BUY — stays BELOW upper side of ribbon
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "ema_ribbon",

        "period": [233],
        "threshold": [0],
        "direction": ["below"],           # inside ribbon lower area
        "min_candles": list(range(2, 6)),
        "wd": 0,

        "indicator_params": {
           
        }
    },
]


#?-------------------------------------------------------
#?timeThreshold SELL Search Space
#?-------------------------------------------------------
ttSELL = [

    # =====================================================
    # MACD SELL — stays BELOW 0 (sustained bearish)
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "macd",

        "period": list(range(5, 21, 5)),
        "threshold": [0],
        "direction": ["below"],
        "min_candles": [2, 3, 4, 5],
        "wd": 0,

        "indicator_params": {
            "fast": list(range(5, 21, 5)),
            "slow": list(range(10, 51, 10)),
            "signal": list(range(5, 16, 5)),
        },

        "sell": True
    },

    # =====================================================
    # RSI SELL — stays BELOW 50
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "rsi",

        "period": list(range(7, 29, 7)),
        "threshold": [50],
        "direction": ["below"],
        "min_candles": [2, 3, 4],
        "wd": 0,

        "indicator_params": {
            "period": list(range(7, 29, 7))
        },

        "sell": True
    },

    # =====================================================
    # StochRSI SELL — stays BELOW 0.5
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "stochrsi",

        "period": list(range(14, 29, 7)),
        "threshold": [0.5],
        "direction": ["below"],
        "min_candles": [2, 3, 4],
        "wd": 0,

        "indicator_params": {
            "rsi_length": list(range(7, 29, 7)),
            "stoch_length": list(range(7, 29, 7)),
            "k": list(range(3, 10)),
            "d": list(range(3, 10)),
        },

        "sell": True
    },

    # =====================================================
    # MA SELL — price stays BELOW MA
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "ma",

        "period": list(range(5, 101, 5)),
        "threshold": [0],
        "direction": ["below"],
        "min_candles": [2, 3, 5, 8],
        "wd": 0,

        "indicator_params": {
            "period": list(range(5, 101, 5))
        },

        "sell": True
    },

    # =====================================================
    # EMA SELL
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "ema",

        "period": list(range(5, 101, 5)),
        "threshold": [0],
        "direction": ["below"],
        "min_candles": [2, 3, 5, 8],
        "wd": 0,

        "indicator_params": {
            "period": list(range(5, 101, 5))
        },

        "sell": True
    },

    # =====================================================
    # ADX SELL — stays BELOW 20 (dead trend)
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "adx",

        "period": list(range(14, 29, 7)),
        "threshold": [20],
        "direction": ["below"],
        "min_candles": [1, 2, 3],
        "wd": 0,

        "indicator_params": {
            "period": list(range(14, 29, 7))
        },

        "sell": True
    },

    # =====================================================
    # ROC SELL — stays BELOW 0 (persistent negative momentum)
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "roc",

        "period": list(range(7, 29, 7)),
        "threshold": [0],
        "direction": ["below"],
        "min_candles": [1, 2, 3, 5],
        "wd": 0,

        "indicator_params": {
            "period": list(range(7, 29, 7))
        },

        "sell": True
    },

    # =====================================================
    # Williams %R SELL — stays BELOW -50 (bearish)
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "williams",

        "period": list(range(7, 29, 7)),
        "threshold": [-50],
        "direction": ["below"],
        "min_candles": [1, 2, 3],
        "wd": 0,

        "indicator_params": {
            "period": list(range(7, 29, 7))
        },

        "sell": True
    },

    # =====================================================
    # ATR SELL — stays BELOW shrinking volatility level
    # =====================================================
    {
        "type": "timeThreshold",
        "indicator": "atr",

        "period": list(range(7, 29, 7)),
        "threshold": list(range(3, 10, 2)),
        "direction": ["below"],
        "min_candles": [1, 2, 3],
        "wd": 0,

        "indicator_params": {
            "period": list(range(7, 29, 7))
        },

        "sell": True
    }
]










#?-------------------------------------------------------
#?Other Custom - exploring Search Spaces
#?-------------------------------------------------------


apiBUY = [
    # 0) RSI crossUpThreshold
    {
        "type": "crossUpThreshold",
        "indicator": "rsi",

        "period": [14,50],         # MUST BE LIST
        "threshold": [40],      # ALREADY LIST
        "wd": 0,

        "indicator_params": {}
    },

    # 1) Williams crossUpThreshold
    {
        "type": "crossUpThreshold",
        "indicator": "williams",
        "period": [14,30],
        "threshold": [-70],
        "wd": 0,
        "indicator_params": {}
    },

    # 2) EMA 9 cross above EMA 21
    {
        "type": "crossUpLineThreshold",
        "indicators": ["ema", "ema"],
        "periods": [
            [9],    # period1
            [21]    # period2
        ],
        "wd": 3
    },

    # 3) Williams in-range threshold
    {
        "type": "inRangeThreshold",
        "indicator": "williams",
        "period": [14],
        "lower": [-100],
        "upper": [-90],
        "wd": 0,
        "indicator_params": {}
    },

    # 4) RSI timeThreshold
    {
        "type": "timeThreshold",
        "indicator": "rsi",
        "period": [14],
        "threshold": [40],
        "direction": ["below"],
        "min_candles": [2],
        "wd": 0,
        "indicator_params": {}
    },

]



ssBUY=[
    # 0) RSI timeThreshold
    {
        "type": "timeThreshold",
        "indicator": "rsi",
        "period": [14],
        "threshold": [40],
        "direction": ["below"],
        "min_candles": [2],
        "wd": 0,
        "indicator_params": {}
    },

    # 1) RSI timeThreshold
    {
        "type": "timeThreshold",
        "indicator": "rsi",
        "period": [20],
        "threshold": [40],
        "direction": ["below"],
        "min_candles": [2],
        "wd": 0,
        "indicator_params": {}
    },


    #2) RSI crossUpThreshold
    {
        "type": "crossUpThreshold",
        "indicator": "rsi",

        "period": list(range(7, 29, 7)),
        "threshold": [30],              # BUY when RSI crosses UP through 30
        "wd": 0,

        "indicator_params": {
            "indicator_period": list(range(7, 29, 7))
        }
    },
    

    

]











#?-------------------------------------------------------
#?ALL SEARCH SPACES
#?-------------------------------------------------------
ALL_SEARCH_SPACES = {
    "crossUpThreshold_buy": cutBUY,
    "crossUpThreshold_sell": cutSELL,
    "line_buy": cultBUY,
    "line_sell": cultSELL,
    "range_buy": irtBUY,
    "range_sell": irtSELL,
    "time_buy": ttBUY,
    "time_sell": ttSELL
}




















#? =====================
#? Custom Search Spaces
#? =====================
buy_cfgs = [
    
    ttBUY[1],
    ttBUY[2],
    ttBUY[6],
    ttBUY[7],
    

    


    irtBUY[1],
    irtBUY[5],
    irtBUY[6],
    irtBUY[7]
]

b_cfg = [
    irtBUY[0],
    irtBUY[1],
    irtBUY[2]
]

cf = [
    {
        "type": "crossUpThreshold",
        "indicator": "rsi",

        "period": [14],
        "threshold": [30],              
        "wd": 2,

        "indicator_params": {}
    },    

    {
        "type": "crossUpThreshold",
        "indicator": "williams",

        "period": [14],
        "threshold": [-80],         # oversold level, BUY when crossing up
        "wd": 2,

        "indicator_params": {
            
        }
    },
]