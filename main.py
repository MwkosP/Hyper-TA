#=====================IMPORTS========================
import os, threading, time, uvicorn, json, pandas as pd,numpy
import matplotlib.pyplot as plt
from pprint import pprint
from src.ta import * # The "Single Line" for your library - # Now you access everything via or without the 'ta' namespace: # ta.download_underlying_stock() - or just download_underlying_stock() 

#=====================CONFIGS========================
pd.set_option('display.max_rows', None) # Set to None to show ALL rows
pd.set_option('display.max_columns', None) # Set to None to show ALL columns

underlying_stock = "BTC-USD" #TAO22974-USD
start="2024-01-01"
end="2026-02-01"
tmfrm='1d' #1d 1wk

#Download Set
df = download_underlying_stock(title=underlying_stock,start=start,end=end,tmfrm="1d",plot=False)
#print(df)
s = calculate_rsi(df, plot=False, period= 14)



'''
#? StdvEMA
# --- SETTINGS ---
EMA_P = 20
WIN = 50
SIG = 1.5
WD = 0       # Set higher than 0 to filter clusters

# 1. Run Calculation - Unpacking exactly 2 values
s_above, s_below = stdvThresholdEMA(df, EMA_P, WIN, SIG, WD)

# 2. Print Summary for your 2-year test
print(f"--- Strategy Results ({SIG} sigma) ---")
print(f"Total Above (Sell) Signals: {len(s_above)}")
print(f"Total Below (Buy) Signals:  {len(s_below)}")

# 3. Visualize
visualize_stdvThresholdEMA(df, s_above, s_below, EMA_P, WIN, SIG)






#?Kurtosis
# --- SETTINGS ---
WIN_KURT = 20
K_RANGE = (-2, 1)
LABEL = "stable_regime"

# 1. Run Calculation - Unpacking the single signals DataFrame
k_signals = kurtosisThreshold(df, window=WIN_KURT, k_range=K_RANGE, label=LABEL)

# 2. Print Summary
print(f"--- Kurtosis Analysis (Range: {K_RANGE}) ---")
print(f"Total 'Stable' Days Found: {len(k_signals)}")

# 3. Visualize
# This uses your specific Kurtosis visualization function
#visualize_kurtosisskewnessThreshold(df, k_signals, window=WIN_KURT, k_range=K_RANGE)





# --- STEP 1: Combine Buy Signals ---
# (Sigma Below + Kurtosis Range)
combined_buy = s_below.merge(k_signals[['Date']], on='Date', how='inner')

# --- STEP 2: Combine Sell Signals ---
# (Sigma Above + Kurtosis Range)
combined_sell = s_above.merge(k_signals[['Date']], on='Date', how='inner')

# --- STEP 3: Print Consolidated Summary ---
print(f"\n" + "="*45)
print(f"--- FULL STRATEGY RESULTS ({SIG}σ) ---")
print(f"Combined BUY Signals:  {len(combined_buy)}")
print(f"Combined SELL Signals: {len(combined_sell)}")
print("="*45)

if not combined_buy.empty:
    print("\n[Final BUY Dates]")
    #print(combined_buy[['Date', 'close']].to_string(index=False))

if not combined_sell.empty:
    print("\n[Final SELL Dates]")
    #print(combined_sell[['Date', 'close']].to_string(index=False))
'''


'''
# Visualize the full Buy/Sell strategy on the Price Chart
visualize_stdvThresholdEMA(
    df, 
    signals_above=combined_sell, 
    signals_below=combined_buy, 
    ema_period=EMA_P, 
    window=WIN, 
    sigma=SIG
)'''


# --- 1. Define Strategy Settings ---
EMA_P = 50        # Base EMA period
SIGMA_VAL = 2   # Distance from EMA
WIN_KURT = 50     # Lookback for Kurtosis
DELTA_K = 0.2     # Required drop in Kurtosis (ΔK)
N=5

# --- 2. Call the Strategy Function ---
# This returns exactly two DataFrames: (final_buys, final_sells)
final_buys, final_sells = run_kurtosis_delta_strategy(
    df, 
    ema_p=EMA_P, 
    sig=SIGMA_VAL, 
    k_win=WIN_KURT, 
    delta_k=DELTA_K,
    n=N
)

# --- 3. Print the Result Summary ---
print(f"--- Strategy Execution Summary ({SIGMA_VAL}σ) ---")
print(f"Final Buy Signals (Filtered by ΔK): {len(final_buys)}")
print(f"Final Sell Signals (Filtered by ΔK): {len(final_sells)}")

if not final_buys.empty:
    print("\n[Final Buy Dates]")
    print(final_buys[['Date', 'close']].to_string(index=False))

if not final_sells.empty:
    print("\n[Final Buy Dates]")
    print(final_sells[['Date', 'close']].to_string(index=False))

# Visualize the combined logic on the Price/Band chart
visualize_stdvThresholdEMA(
    df, 
    signals_above=final_sells, 
    signals_below=final_buys, 
    ema_period=EMA_P, 
    window=50, 
    sigma=SIGMA_VAL
)






#metrics = calculate_metrics(df, verbose=True)


#s = calculate_rsi(df, plot=False, period= 14)
#e =calculate_entropy(df,column='close',bins=10)
#visualize_entropy(df, column='close', bins=10)

#calculate_metrics(df,verbose=True)



def main():
    print("✅ All dependencies ready. Program running...")


 
    
    
    
    
    
    
    #plot_price_with_marked_days(df, days_to_mark=[0])



    

    '''
    # Convert list-of-dicts → JSON string
    df = pd.DataFrame([{
        "name": "cutBUY",
        "config_json": json.dumps(cutBUY)
    }])

    # Save it
    taDB.save_table("search_spaces", df)
    


    df = taDB.load_table("search_spaces")
    row = df[df["name"] == "cutBUY"].iloc[0]
    cutBUY_loaded = json.loads(row["config_json"])
    pprint(cutBUY_loaded)
    '''
    
    #taDB.save_table("eth", df)
    #taDB.list_tables()
    #table = taDB.load_table("search_spaces")
    #print(table)

    '''
    signals = mixThresholds(df, [ssBUY[0]], mode="and")
    taDB.save_table("sigs", signals)

    table = taDB.load_table("sigs")
    print(table)
    '''


    '''
    f= ALL_SEARCH_SPACES["range_buy"]
    g= [cutBUY[7],irtBUY[5],ttBUY[1]]
    r= [irtBUY[1],irtBUY[7]]
    total_combinations = get_total_grid_size(r)
    print(f"Total size of Search space: {total_combinations:,}")
    # 3) Run mixThresholds 
    result = mixThresholds(
        df,
        r,
        mode="and",     # "and" , "or"
        search="bayesian"   #"grid" , "random" , "bayesian"
    )
    print(result)


    

    # 4) Print stats
    print("Total configs explored:", len(result))
    #print("Final signal count:", result["final"]["signals"])



    # --------------------------------------------------
    # 6) Plot ALL configurations (search results)
    # --------------------------------------------------
    # WARNING: this can be huge → so slice it
    plot_results_pdf(
        df,
        result[:400],        # first 400 configs only
        pdf_name="buy_first_400.pdf"
    )
    '''
    '''
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)
    


    
    signals0 = mixThresholds(df, [ssBUY[0]], mode="and")
    print("\n Config 0  :\n",signals0)
    
    signals1 = mixThresholds(df, [ssBUY[1]], mode="and")
    print("\n Config 1  :\n",signals1)

    signals2 = mixThresholds(df, [ssBUY[2]], mode="and")
    print("\n Config 2  :\n",signals2)

    signals = mixThresholds(df, [ssBUY[0],ssBUY[1],ssBUY[2]], mode="and")
    print("\nAll Configs (MixThresholds) :\n",signals)

    sig1 = mixThresholds(df, [cultBUY[0]], mode="and")
    print("\nAll Configs (MixThresholds) :\n",sig1)

    # Plot the results into a PDF
    plot_results_pdf(df, sig1, pdf_name="cutBuy.pdf",top_n=200)
    
  
    
    -----------------------------------------------------
    



    # Show links
    print("\n🚀 FastAPI server starting...")
    print("📑 Swagger docs:   http://127.0.0.1:8000/docs")

    
    # Kill any leftover uvicorn
    kill_uvicorn_on_port(8000)

    # ✅ Launch Swagger in browser BEFORE  uvicorn
    open_swagger("http://127.0.0.1:8000/docs")

    # Start cloudflared in background with delay
    #threading.Thread(target=start_cloudflared, daemon=True).start()

    # Run the GLOBAL app
    uvicorn.run("app:app", host="127.0.0.1", port=8000)
    '''
    
    

if __name__ == "__main__":
    main()
