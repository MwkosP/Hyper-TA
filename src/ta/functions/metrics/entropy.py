import numpy as np
import pandas as pd

def calculate_entropy(df, column='close', bins=10):
    data = df[column].dropna()
    
    # 1. Όρια κάδων
    min_val = (data.min() // bins) * bins
    max_val = (data.max() // bins + 1) * bins
    custom_bins = np.arange(min_val, max_val + bins, bins)
    
    # 2. Κατηγοριοποίηση και Πιθανότητες
    bin_series = pd.cut(data, bins=custom_bins)
    value_counts = bin_series.value_counts(sort=False)
    probabilities = value_counts / len(data)
    
    # 3. Καθαρισμός για υπολογισμούς
    probs_clean = probabilities[probabilities > 0]
    
    # --- ΝΕΑ METRICS ---
    mean_bin_probability = probs_clean.mean()
    # Τυπική απόκλιση των ποσοστών των κάδων
    std_bin_probability = probs_clean.std() 
    
    # 4. Shannon Entropy
    raw_entropy = - (probs_clean * np.log2(probs_clean)).sum()
    num_bins_created = len(custom_bins) - 1
    normalized_entropy = raw_entropy / np.log2(num_bins_created)
    
    print("--- FIXED BINS STATS ---")
    print(probabilities)
    print(f"Mean Prob: {mean_bin_probability:.4f}")
    print(f"Std Dev of Probs: {std_bin_probability:.4f}") # <--- Αυτό ζήτησες
    
    return normalized_entropy, std_bin_probability



import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def visualize_entropy(df, column='close', bins=10):
    # 1. Calculate Histogram Data
    counts, bin_edges = np.histogram(df[column], bins=bins)
    
    # 2. Calculate Entropy & Normalize it to 0-1
    #TODO: clean     
    probs = counts / len(df[column])
    probs = probs[probs > 0]
    raw_entropy = -np.sum(probs * np.log2(probs))
    
    # Κανονικοποίηση: Διαίρεση με το μέγιστο δυνατό (log2 των bins)
    normalized_entropy = raw_entropy / np.log2(bins)

    # 3. Create Subplots
    fig = make_subplots(
        rows=1, cols=2, 
        column_widths=[0.7, 0.3],
        # Χρησιμοποιούμε το normalized_entropy στον τίτλο
        subplot_titles=(f"Price Action (Normalized Entropy: {normalized_entropy:.4f})", "Distribution"),
        horizontal_spacing=0.05
    )

    # Left: Price Line
    fig.add_trace(
        go.Scatter(x=df.index, y=df[column], name="Price", line=dict(color='royalblue')),
        row=1, col=1
    )

    # Add the Bin Edges as Horizontal Lines
    for edge in bin_edges:
        fig.add_hline(y=edge, line_dash="dash", line_color="red", opacity=0.3, row=1, col=1)

    # Right: Horizontal Histogram
    fig.add_trace(
        go.Bar(
            y=(bin_edges[:-1] + bin_edges[1:]) / 2, 
            x=counts, 
            orientation='h',
            marker_color='gray',
            name="Frequency"
        ),
        row=1, col=2
    )

    fig.update_layout(height=600, width=1200, showlegend=False, template="plotly_white")
    fig.show()


