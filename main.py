#=====================IMPORTS========================
import os, threading, time, uvicorn, json, pandas as pd,matplotlib.pyplot as plt,numpy
from pprint import pprint
from src.ta import * # The "Single Line" for your library - # Now you access everything via or without the 'ta' namespace: # ta.download_underlying_stock() - or just download_underlying_stock() 
from configs.searchSpaces import *
from src.ta.functions.metrics.derivatives import *
from src.ta.functions.metrics.entropy import *
import matplotlib
from src.ta.functions.plots.plot_indicators import *
from src.ta.functions.plots.plot_metrics import *


#=====================CONFIGS========================
pd.set_option('display.max_rows', None) # Set to None to show ALL rows
pd.set_option('display.max_columns', None) # Set to None to show ALL columns
matplotlib.use("TkAgg")


underlying_stock = "BTC-USD" #TAO22974-USD
start="2021-01-01"
end="2026-02-19"
tmfrm='1d' #1d 1wk

#Download Set
df = fetch_asset(title=underlying_stock,start=start,end=end,tmfrm="1d",plot=False)
#print(df)
#rsi = calculate_indicator(df,plot=False,type="rsi")







def main():
    print("🚀 Program running...")

    # Generate composite signals
    #signals = mixThresholds(df, [irtBUY[1],ttBUY[7]], search="bayesian",mode="and")

    #print(signals)
    #plot_signals_pdf(df, signals, pdf_name="assets/data/plots.pdf", top_n=None)
   
#----------------------------------------------------------
    '''
    #1st-2nd Der
    slopes = rolling_derivative(df=df,k=40,alpha=0.5,derivative='both')
    plot_price_and_derivatives(df=df,indicator_df=slopes)
    
    #Skew + kurt
    plot_price_skew_kurt(df, window=40, skew_range=(-2,2),kurt_range=(-5,5),use_log=True)

    
    #stdV
    EMA_PERIOD = 40  #EMA
    SIGMA = 1.8      #STDV 
    WINDOW = 50
    KURT_WINDOW = 50 
    DELTA_K = 0.9
    N_LOOKBACK = 5

    final_buys, final_sells = stdvBandsThreshold(df,ema_period=EMA_PERIOD,sigma=SIGMA,window=WINDOW)
    visualize_stdvThresholdEMA(df, final_buys, final_sells, ema_period=40, sigma=1.8)
    


    #Entropy
    calculate_entropy(df, column='close', bins=10)
    visualize_entropy(df, column='close', bins=10)
    
    ind_df = calculate_rolling_entropy(df, window=40,alpha=0.5)
    plot_rolling_entropy(df, ind_df, metric="both")  
    '''  
#----------------------------------------------------------
    #stdV
    EMA_PERIOD = 40  #EMA
    SIGMA = 1.8      #STDV 
    WINDOW = 50
    KURT_WINDOW = 50 
    DELTA_K = 0.9
    N_LOOKBACK = 5

    final_buys, final_sells = stdvBandsThreshold(df,ema_period=EMA_PERIOD,sigma=SIGMA,window=WINDOW)
    visualize_stdvThresholdEMA(df, final_buys, final_sells, ema_period=40, sigma=1.8)






    



















    #?-------------------------------------------------------
    #?-------------------------------------------------------
    #?-------------------------------------------------------
    '''
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




