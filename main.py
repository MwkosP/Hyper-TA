#=====================IMPORTS========================
import os, threading, time, uvicorn, json, pandas as pd,matplotlib.pyplot as plt,numpy
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








def main():
    print("🚀 Program running...")

    # Generate composite signals
    signals = mixThresholds(df, [irtBUY[1],ttBUY[7]], search="bayesian",mode="and")
    print(signals)

    plot_results_pdf(df, signals, pdf_name="assets/data/plots.pdf", top_n=None)





































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
