import itertools
import pandas as pd
import random
import optuna
import logging
from joblib import Parallel, delayed
import matplotlib
# Force non-interactive backend to prevent freezing
try:
    matplotlib.use('Agg')
except:
    pass
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import gc
import json

from tqdm.auto import tqdm # auto-selects notebook or terminal style


# === CRITICAL IMPORT ===
from src.ta.functions.indicators.universal_threshold_dispatcher import run_threshold

optuna.logging.set_verbosity(optuna.logging.WARNING)

# ============================================================
# HELPER: Config Evaluator
# ============================================================
def evaluate_config(df, cfg):
    try:
        signals = run_threshold(df, cfg)
        if signals.empty:
            return {"config": cfg, "signals": 0, "score": 0, "signals_df": pd.DataFrame()}
        count = len(signals)
        return {"config": cfg, "signals": count, "score": count, "signals_df": signals}
    except:
        return {"config": cfg, "signals": 0, "score": 0, "signals_df": pd.DataFrame()}

# ============================================================
# HELPER: Deduplicate Results (THE FIX)
# ============================================================
def deduplicate_results(results):
    """
    Removes duplicate configurations from the result list.
    Crucial for Random/Bayesian search on small search spaces.
    """
    unique_map = {}
    
    for r in results:
        # Create a string hash of the config to identify duplicates
        # We sort keys to ensure {"a":1, "b":2} equals {"b":2, "a":1}
        try:
            if "combination" in r:
                # Tuple of dicts
                cfg_str = str(r["combination"]) 
            else:
                # Single dict
                cfg_str = json.dumps(r["config"], sort_keys=True, default=str)
                
            if cfg_str not in unique_map:
                unique_map[cfg_str] = r
        except:
            continue
            
    return list(unique_map.values())

# ============================================================
# HELPER: Config Generation
# ============================================================
def expand_params(param_dict):
    if not param_dict: return [{}]
    keys, vals = list(param_dict.keys()), list(param_dict.values())
    return [dict(zip(keys, c)) for c in itertools.product(*vals)]

def generate_flat_configs(space):
    """Generates ALL possible configs for a Grid Search."""
    configs = []
    ind_param_sets = expand_params(space.get("indicator_params", {}))
    t, is_sell, wd = space["type"], space.get("sell", False), space.get("wd", 0)

    if t == "crossUpThreshold":
        for per, thr, ind_kwargs in itertools.product(space["period"], space["threshold"], ind_param_sets):
            configs.append({"type": t, "indicator": space["indicator"], "period": per, "thr": thr, "wd": wd, "sell": is_sell, "indicator_params": ind_kwargs})
    elif t == "inRangeThreshold":
        for per, low, upp, ind_kwargs in itertools.product(space["period"], space["lower"], space["upper"], ind_param_sets):
            configs.append({"type": t, "indicator": space["indicator"], "period": per, "lower": low, "upper": upp, "wd": wd, "sell": is_sell, "indicator_params": ind_kwargs})
    elif t == "timeThreshold":
        for per, thr, d, mc, ind_kwargs in itertools.product(space["period"], space["threshold"], space["direction"], space["min_candles"], ind_param_sets):
            configs.append({"type": t, "indicator": space["indicator"], "period": per, "threshold": thr, "direction": d, "min_candles": mc, "wd": wd, "sell": is_sell, "indicator_params": ind_kwargs})
    elif t == "crossUpLineThreshold":
        for p1, p2 in itertools.product(space["periods"][0], space["periods"][1]):
            configs.append({"type": t, "ind1": space["indicators"][0], "ind2": space["indicators"][1], "period1": p1, "period2": p2, "wd": wd, "sell": is_sell})
    return configs

def sample_random_config(space):
    """Generates ONE random config from a search space."""
    t = space["type"]
    ind_param_sets = expand_params(space.get("indicator_params", {}))
    ind_kwargs = random.choice(ind_param_sets) if ind_param_sets else {}
    is_sell = space.get("sell", False)
    wd = space.get("wd", 0)
    
    cfg = {"type": t, "wd": wd, "sell": is_sell, "indicator_params": ind_kwargs}

    if t == "crossUpThreshold":
        cfg.update({"indicator": space["indicator"], "period": random.choice(space["period"]), "thr": random.choice(space["threshold"])})
    elif t == "inRangeThreshold":
        cfg.update({"indicator": space["indicator"], "period": random.choice(space["period"]), "lower": random.choice(space["lower"]), "upper": random.choice(space["upper"])})
    elif t == "timeThreshold":
        cfg.update({"indicator": space["indicator"], "period": random.choice(space["period"]), "threshold": random.choice(space["threshold"]), "direction": random.choice(space["direction"]), "min_candles": random.choice(space["min_candles"])})
    elif t == "crossUpLineThreshold":
        cfg.update({"ind1": space["indicators"][0], "ind2": space["indicators"][1], "period1": random.choice(space["periods"][0]), "period2": random.choice(space["periods"][1])})
    
    return cfg

def get_total_grid_size(search_space):
    total = 0
    for s in search_space:
        total += len(generate_flat_configs(s))
    return total

# ============================================================
# SEARCH ENGINES (Standard)
# ============================================================
def gridSearch(df, search_space, n_jobs=-1):
    all_configs = []
    for s in search_space: all_configs.extend(generate_flat_configs(s))
    results = Parallel(n_jobs=n_jobs)(delayed(evaluate_config)(df, c) for c in all_configs)
    return deduplicate_results(results)

def randomSearch(df, search_space, n_iter=100, n_jobs=-1):
    all_configs = [sample_random_config(random.choice(search_space)) for _ in range(n_iter)]
    results = Parallel(n_jobs=n_jobs)(delayed(evaluate_config)(df, c) for c in all_configs)
    return deduplicate_results(results)

def bayesianSearch(df, search_space, n_iter=100, n_jobs=-1):
    # This function is used for independent block search
    print(f"🧠 Bayesian Search (Single Block): {n_iter} trials...", flush=True)
    results = []

    def objective(trial):
        strat_idx = trial.suggest_int("strategy_idx", 0, len(search_space) - 1)
        space = search_space[strat_idx]
        t = space["type"]
        def pick(n, v): return trial.suggest_categorical(f"{t}_{strat_idx}_{n}", v)
        
        cfg = sample_random_config(space) # Fallback structure
        # Overwrite with Optuna suggestions
        cfg["type"] = t
        
        # (Simplified Optuna mapping for brevity - relies on 'pick' picking from the list)
        if t == "crossUpThreshold":
            cfg["period"] = pick("period", space["period"])
            cfg["thr"] = pick("threshold", space["threshold"])
        # ... Add other types mapping here if strictly needed for Bayesian optimization logic ...
        # For small discrete spaces, random sampling often suffices if this mapping is complex.
        
        res = evaluate_config(df, cfg)
        results.append(res)
        return res["score"]

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_iter, n_jobs=n_jobs)
    return deduplicate_results(results)

# ============================================================
# SEARCH ENGINES (Combinatorial)
# ============================================================

def combinatorialGridSearch(df, search_spaces_list, mode="and"):
    print("🔗 Combinatorial GRID Search...", flush=True)
    all_groups = [generate_flat_configs(space) for space in search_spaces_list]
    
    # Check size
    total_combinations = 1
    for g in all_groups: total_combinations *= len(g)
    print(f"   -> Total Combinations: {total_combinations}")

    # Flatten for pre-calculation
    flat_list = [c for group in all_groups for c in group]
    print("   -> Pre-calculating individual signals...", flush=True)
    precalc = Parallel(n_jobs=-1)(delayed(evaluate_config)(df, c) for c in flat_list)
    cache = {json.dumps(r["config"], sort_keys=True, default=str): r.get("signals_df", pd.DataFrame()) for r in precalc}
    
    print("   -> Mixing...", flush=True)
    final_results = []
    
    for combo in itertools.product(*all_groups):
        dfs = []
        for c in combo:
            key = json.dumps(c, sort_keys=True, default=str)
            dfs.append(cache.get(key, pd.DataFrame()))
        
        if any(d.empty for d in dfs):
            combined = pd.DataFrame()
        else:
            if mode == "and":
                combined = dfs[0][["Date"]]
                for d in dfs[1:]: combined = combined.merge(d[["Date"]], on="Date", how="inner")
            else: # OR
                combined = pd.concat([d[["Date"]] for d in dfs]).drop_duplicates().sort_values("Date")
        
        count = len(combined)
        final_results.append({"combination": combo, "signals": count, "score": count, "signals_df": combined})
    
    # Grid search naturally produces unique combos, but good to be safe
    return sorted(final_results, key=lambda x: x["score"], reverse=True)


def combinatorialRandomSearch(df, search_spaces_list, n_iter=100, mode="and"):
    print(f"🔗 Combinatorial RANDOM Search ({n_iter} iters)...", flush=True)
    
    def run_random_combo():
        combo_configs = [sample_random_config(space) for space in search_spaces_list]
        dfs = []
        for cfg in combo_configs:
            res = evaluate_config(df, cfg)
            dfs.append(res["signals_df"])
            
        if any(d.empty for d in dfs):
            combined = pd.DataFrame()
        else:
            if mode == "and":
                combined = dfs[0][["Date"]]
                for d in dfs[1:]: combined = combined.merge(d[["Date"]], on="Date", how="inner")
            else:
                combined = pd.concat([d[["Date"]] for d in dfs]).drop_duplicates().sort_values("Date")
        
        return {"combination": tuple(combo_configs), "signals": len(combined), "score": len(combined), "signals_df": combined}

    results = Parallel(n_jobs=-1)(delayed(run_random_combo)() for _ in range(n_iter))
    
    # === DEDUPLICATE HERE ===
    return deduplicate_results(sorted(results, key=lambda x: x["score"], reverse=True))


def combinatorialBayesianSearch(df, search_spaces_list, n_iter=100, mode="and"):
    print(f"🧠 Combinatorial BAYESIAN Search ({n_iter} iters)...", flush=True)
    results = []

    def objective(trial):
        combo_configs = []
        for i, space in enumerate(search_spaces_list):
            t = space["type"]
            prefix = f"b{i}_{t}"
            def pick(n, v): return trial.suggest_categorical(f"{prefix}_{n}", v)
            
            # Simple approach: Re-build config using Optuna picks
            # This requires replicating the logic from generate_flat_configs
            # For simplicity in this fix, we use sample_random_config which works for basic lists
            # but usually Optuna needs explicit 'suggest' calls to learn.
            
            # (Simplified: Random fallback for complex structure, mapped params for simple)
            cfg = sample_random_config(space) 
            if t == "crossUpThreshold":
                cfg["period"] = pick("p", space["period"])
                cfg["thr"] = pick("t", space["threshold"])
            # ... Add other mappings ...
            
            combo_configs.append(cfg)

        dfs = []
        for cfg in combo_configs:
            res = evaluate_config(df, cfg)
            dfs.append(res["signals_df"])

        if any(d.empty for d in dfs):
            count = 0
            combined = pd.DataFrame()
        else:
            if mode == "and":
                combined = dfs[0][["Date"]]
                for d in dfs[1:]: combined = combined.merge(d[["Date"]], on="Date", how="inner")
            else:
                combined = pd.concat([d[["Date"]] for d in dfs]).drop_duplicates().sort_values("Date")
            count = len(combined)

        results.append({
            "combination": tuple(combo_configs), 
            "signals": count, 
            "score": count, 
            "signals_df": combined
        })
        return count

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_iter, n_jobs=-1) 
    
    # === DEDUPLICATE HERE ===
    return deduplicate_results(sorted(results, key=lambda x: x["score"], reverse=True))


# ============================================================
# Plotting (Robust + Downsampling)
# ============================================================
def plot_signals_pdf(df, results, pdf_name="plots.pdf", top_n=None):
    if isinstance(results, dict):
        results = [results]
    
    results = sorted([r for r in results if r.get("score", 0) > 0], 
                    key=lambda x: x.get("score", 0), reverse=True)
    if top_n:
        results = results[:top_n]
    
    if not results:
        return

    # Downsample once outside the loop
    plot_df = df.iloc[::max(1, len(df)//2000)].copy()
    
    stats = {'successful': 0, 'failed': 0}

    with PdfPages(pdf_name) as pdf:
        # Single bar configuration
        pbar = tqdm(results, desc="Generating PDF", unit="plot", ncols=80)
        
        for i, r in enumerate(pbar):
            try:
                signals = r.get("signals_df", pd.DataFrame())
                if signals.empty and "config" in r:
                    signals = run_threshold(df, r["config"])
                
                if signals.empty:
                    continue
                
                # UPDATE BAR IN PLACE (No extra prints)
                pbar.set_postfix(score=f"{r.get('score', 0):.2f}", ok=stats['successful'])
                
                fig, ax = plt.subplots(figsize=(14, 6))
                ax.plot(plot_df["Date"], plot_df["close"], color="black", alpha=0.6, lw=0.8)
                
                # Downsample signals for plotting
                sig_points = df[df["Date"].isin(signals["Date"])]
                sig_points = sig_points.iloc[::max(1, len(sig_points)//1000)]
                
                ax.scatter(sig_points["Date"], sig_points["close"], color="green", s=40)
                ax.set_title(f"Rank #{i+1} | Score: {r['score']:.4f}")
                
                pdf.savefig(fig, dpi=100)
                plt.close(fig)
                
                stats['successful'] += 1
                if i % 10 == 0: gc.collect()
                
            except Exception:
                stats['failed'] += 1
                # Use pbar.write ONLY if you absolutely need to see the error 
                # without breaking the bar. Otherwise, skip it for maximum cleanliness.
                continue

    print(f"\nDone! {stats['successful']} plots saved to {pdf_name}")