import pandas as pd


# UNIVERSAL METRICS DISPATCHER
def calculate_metrics(df, ma_period=20, ema_period=20, verbose=False):
    
    variance = df['close'].var()
    std_dev  = df['close'].std()
    skewness = df['close'].skew()
    kurtosis = df['close'].kurt()
    
    # Metrics counted by hand(MA, EMA)
    df['MA'] = df['close'].rolling(window=ma_period).mean()
    #df['EMA'] = df['close'].ewm(span=ema_period, adjust=False).mean()
    df['EMA'] = df['close'].ewm(alpha=0.8, adjust=False).mean()
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
# metrics = calculate_metrics(df, ma_period=50, ema_period=20, verbose=True)
# print(f"Ο τρέχων EMA είναι: {metrics['current_ema']}")