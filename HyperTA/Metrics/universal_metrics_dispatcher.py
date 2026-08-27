import pandas as pd


# UNIVERSAL METRICS DISPATCHER
def calculateMetrics(df, ma_period=20, ema_period=20, verbose=False):
    
    variance = df['Close'].var()
    std_dev  = df['Close'].std()
    skewness = df['Close'].skew()
    kurtosis = df['Close'].kurt()
    
    # Metrics counted by hand(MA, EMA)
    df['MA'] = df['Close'].rolling(window=ma_period).mean()
    #df['EMA'] = df['Close'].ewm(span=ema_period, adjust=False).mean()
    df['EMA'] = df['Close'].ewm(alpha=0.8, adjust=False).mean()
    #last value of dictionary. 
    current_ma = df['MA'].iloc[-1]
    current_ema = df['EMA'].iloc[-1]
    
    if verbose:
        print(f"--- METRICS: ---")
        print(f"Variance (Διακύμανση): {variance:.4f}")
        print(f"StDev (Τυπική Απόκλιση): {std_dev:.4f}")
        print(f"Skew (Ασυμμετρία): {skewness:.4f}")
        print(f"Kurtosis (Κύρτωση): {kurtosis:.4f}")
        #print(f"--- Τεχνικοί Δείκτες (Τρέχουσες Τιμές) ---")
        print(f"MA ({ma_period}): {current_ma:.4f}")
        print(f"EMA ({ema_period}): {current_ema:.4f}")
        
    # Επιστρέφουμε τα αποτελέσματα
    return {
        "variance": variance,
        "std_dev": std_dev,
        "skewness": skewness,
        "kurtosis": kurtosis,
        "current_ma": current_ma,
        "current_ema": current_ema
    }

# Παράδειγμα Χρήσης:
# metrics = calculateMetrics(df, ma_period=50, ema_period=20, verbose=True)
# print(f"Ο τρέχων EMA είναι: {metrics['current_ema']}")