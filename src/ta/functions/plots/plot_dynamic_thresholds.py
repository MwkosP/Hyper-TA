import plotly.graph_objects as go

def visualize_stdvThresholdEMA(df, signals_above, signals_below, ema_period=10, window=50, sigma=0.8):
    # 1. Re-calculate the SYMMETRICAL bands for plotting
    df = df.copy()
    df['ema'] = df['close'].ewm(span=ema_period, adjust=False).mean()
    df['dist'] = df['close'] - df['ema']
    
    # Calculate only standard deviation
    rolling_std = df['dist'].rolling(window=window).std()
    
    # Symmetrical 'walls' centered exactly on the EMA
    df['upper_band'] = df['ema'] + (sigma * rolling_std)
    df['lower_band'] = df['ema'] - (sigma * rolling_std)

    fig = go.Figure()

    # Main Price Line
    fig.add_trace(go.Scatter(x=df['Date'], y=df['close'], name="Price", line=dict(color='black', width=1)))

    # EMA Line (Blue)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['ema'], name=f"EMA {ema_period}", line=dict(color='blue', width=1.5)))

    # Sigma Bands (Mirrored)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['upper_band'], name=f"+{sigma}σ Band", line=dict(color='rgba(255,0,0,0.3)', dash='dot')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['lower_band'], name=f"-{sigma}σ Band", line=dict(color='rgba(0,255,0,0.3)', dash='dot')))

    # Add Buy Signals (Green Triangles)
    if not signals_below.empty:
        buys = df[df['Date'].isin(signals_below['Date'])]
        fig.add_trace(go.Scatter(
            x=buys['Date'], y=buys['close'], mode='markers',
            name='Below Threshold (Buy)', marker=dict(symbol='triangle-up', size=12, color='green')
        ))

    # Add Sell Signals (Red Triangles)
    if not signals_above.empty:
        sells = df[df['Date'].isin(signals_above['Date'])]
        fig.add_trace(go.Scatter(
            x=sells['Date'], y=sells['close'], mode='markers',
            name='Above Threshold (Sell)', marker=dict(symbol='triangle-down', size=12, color='red')
        ))

    fig.update_layout(
        title=f"Symmetrical Market Sigma Analysis ({sigma}σ)",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        height=700,
        hovermode="x unified"
    )
    
    fig.show()









import plotly.graph_objects as go
from plotly.subplots import make_subplots

def visualize_kurtosisskewnessThreshold(df, signals_df, window=20, k_range=(-2.0, 1.0)):
    """
    Plots Price on top and Kurtosis on bottom, highlighting the trigger range.
    """
    df = df.copy()
    
    # 1. Standardize Date column
    if 'Date' not in df.columns:
        df = df.reset_index()

    # 2. Identify and standardize the price column
    close_col = 'Close' if 'Close' in df.columns else 'close'
    
    # Calculate Kurtosis for the visualizer
    df['returns'] = df[close_col].pct_change()
    df['kurt'] = df['returns'].rolling(window=window).kurt()

    # 3. Create Subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.7, 0.3])

    # --- TOP PANE: PRICE ---
    fig.add_trace(go.Scatter(x=df['Date'], y=df[close_col], name="Price", 
                             line=dict(color='black', width=1)), row=1, col=1)
    
    # 4. Add Markers (Fixed Merge Logic)
    if not signals_df.empty:
        # We merge with the original df to get the price for those signal dates
        sig_merged = signals_df[['Date']].merge(df[['Date', close_col]], on='Date')
        
        fig.add_trace(go.Scatter(
            x=sig_merged['Date'], 
            y=sig_merged[close_col], # This now matches the existing column
            mode='markers', name='Kurtosis Trigger',
            marker=dict(symbol='star', size=10, color='gold')
        ), row=1, col=1)

    # --- BOTTOM PANE: KURTOSIS ---
    fig.add_trace(go.Scatter(x=df['Date'], y=df['kurt'], name="Kurtosis", 
                             line=dict(color='darkorange')), row=2, col=1)
    
    # Add shaded area for trigger zone
    fig.add_hrect(y0=k_range[0], y1=k_range[1], fillcolor="green", 
                  opacity=0.1, line_width=0, row=2, col=1)

    fig.update_layout(height=800, title=f"Kurtosis Analysis {k_range}",
                      template="plotly_white", hovermode="x unified")
    fig.show()