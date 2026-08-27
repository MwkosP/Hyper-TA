# === External libraries ===
import pandas as pd


# df here is from corresponding indicator. eg: df = Date, adx
def calculateIndicator(df: pd.DataFrame, type: str, **kwargs) -> pd.DataFrame:
    from HyperTA.Indicators import indicators as ind

    type = type.lower()

    if type == "rsi":
        return ind.calculateRsi(df, period=kwargs.get("period", 14))

    elif type == "williams":
        return ind.calculateWilliams(df, period=kwargs.get("period", 14))

    elif type == "ma":
        return ind.calculateMa(df, period=kwargs.get("period", 14))

    elif type == "ema":
        return ind.calculateEma(df, period=kwargs.get("period", 14))

    elif type == "ema_ribbon":
        return ind.calculateEmaRibbon(
            df, periods=kwargs.get("periods", [8, 13, 21, 34, 55, 89, 144, 233])
        )

    elif type == "ema_crossover":
        return ind.calculateEmaCrossover(
            df, fast=kwargs.get("fast", 9), slow=kwargs.get("slow", 21)
        )

    elif type == "macd":
        return ind.calculateMacd(
            df,
            fast=kwargs.get("fast", 12),
            slow=kwargs.get("slow", 26),
            signal=kwargs.get("signal", 9),
        )

    elif type == "roc":
        return ind.calculateRoc(df, period=kwargs.get("period", 14))

    elif type == "stochrsi":
        result = ind.calculateStochrsi(
            df,
            rsi_length=kwargs.get("rsi_length", 14),
            stoch_length=kwargs.get("stoch_length", 14),
            k=kwargs.get("k", 3),
            d=kwargs.get("d", 3),
        )
        line = kwargs.get("line", "stochrsi_k")
        return result[["Date", line]]

    elif type == "adx":
        result = ind.calculateAdx(df, period=kwargs.get("period", 14))
        return result[["Date", "adx"]]

    elif type == "ichimoku":
        return ind.calculateIchimoku(
            df,
            tenkan=kwargs.get("tenkan", 9),
            kijun=kwargs.get("kijun", 26),
            senkou=kwargs.get("senkou", 52),
        )

    elif type == "bbands":
        return ind.calculateBbands(
            df, period=kwargs.get("period", 20), std=kwargs.get("std_dev", 2)
        )

    elif type == "atr":
        return ind.calculateAtr(df, period=kwargs.get("period", 14))

    elif type == "donchian":
        return ind.calculateDonchian(df, period=kwargs.get("period", 20))

    else:
        raise ValueError(f"Unsupported indicator type: {type}")
