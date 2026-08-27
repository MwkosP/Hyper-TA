# Search JSON Config

Config schema for `HyperTA.Search.searchHPSpace(df, config)`.

Package: `HyperTA/Search/`
- `dispatcher.py` — `searchHPSpace(df, config)`
- `search.py` — grid / random / bayesian algorithms
- `combinatorialSearch.py` — multi-indicator combine search
- `utils.py` — config expand / sample / evaluate helpers

Search enumerates hyperparameter combinations and returns **many states**.  
Each state = params for that trial + signals (`Date`, `Price`).

By default each indicator is searched **individually**.  
Optional `combine` merges selected indicators with a mode (`and` / `or` / `xor`).

---

## Rules

- Lists under an indicator = searchable values  
- Scalars = fixed  
- Top-level `indicators.threshold` = default threshold for every indicator that does not set its own  
- Per-indicator `threshold` overrides the default  
- No `combine` → each indicator produces its own list of states  
- `combine` present → listed indicators are merged with that mode; others stay solo  

---

## Individual search (default)

```json
{
  "search": {
    "type": "random",
    "kwargs": {
      "n_iter": 200,
      "seed": 7
    }
  },

  "indicators": {
    "threshold": "crossLevel",

    "rsi": {
      "period": [7, 14, 21],
      "level": [25, 30],
      "side": "up"
    },

    "macd": {
      "threshold": "crossLines",
      "fast": [8, 12],
      "slow": [21, 26],
      "signal": 9,
      "side": "up"
    }
  }
}
```

Mental result:

```text
rsi  → [state, state, ...]
macd → [state, state, ...]
```

---

## Combined search (optional)

```json
{
  "search": {
    "type": "bayesian",
    "optimiser": "pnl",
    "kwargs": {
      "n_iter": 300,
      "seed": 42,
      "n_jobs": -1
    }
  },

  "combine": {
    "mode": "and",
    "indicators": ["rsi", "macd"]
  },

  "indicators": {
    "threshold": "crossLevel",

    "rsi": {
      "period": [14, 21],
      "level": [30],
      "side": "up"
    },

    "macd": {
      "threshold": "crossLines",
      "fast": [12],
      "slow": [26],
      "signal": 9,
      "side": "up"
    },

    "atr": {
      "period": [14]
    }
  }
}
```

Here:

- `rsi` + `macd` combine with `and`
- `atr` is not listed under `combine.indicators` → stays individual
- `atr` has no `threshold` → uses default `"crossLevel"`

### Combine shortcuts

| Config | Behavior |
|---|---|
| no `combine` | every indicator searched alone |
| `"combine": { "mode": "and", "indicators": ["rsi", "macd"] }` | only listed ones merge |
| `"combine": { "mode": "or" }` (no list) | all indicators under `indicators` merge |

---

## Search object

| Field | Required | Notes |
|---|---|---|
| `type` | yes | `grid` \| `random` \| `bayesian` |
| `optimiser` | no | e.g. `"pnl"` — mainly for Bayesian |
| `kwargs` | no | algorithm args (`n_iter`, `seed`, `n_jobs`, …) |

### Random example

```json
{
  "search": {
    "type": "random",
    "kwargs": {
      "n_iter": 200,
      "seed": 7
    }
  }
}
```

### Bayesian example

```json
{
  "search": {
    "type": "bayesian",
    "optimiser": "pnl",
    "kwargs": {
      "n_iter": 300,
      "seed": 42,
      "n_jobs": -1
    }
  }
}
```

---

## State shape (output)

One trial from a search:

```json
{
  "params": {
    "rsi": {
      "period": 14,
      "threshold": "crossLevel",
      "level": 30,
      "side": "up"
    }
  },
  "signals": {
    "columns": ["Date", "Price"],
    "rows": []
  }
}
```

(`signals` is a DataFrame in Python: `Date`, `Price`.)

---

## Notes

- Asset / provider / date range can sit beside this later (`"asset": { ... }`) — not mixed into `indicators`.
- External series / file imports are deferred; for now sources are HyperTA indicators only.
- This doc describes the intended public JSON API; implementation may follow later.
