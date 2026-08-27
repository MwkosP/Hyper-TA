"""Hyperparameter search over indicators + thresholds.

Public API: searchHPSpace(df, config)

- search.py — grid / random / bayesian
- combinatorialSearch.py — multi-space combine search
Config schema: Assets/docs/search-json.md
"""

from .dispatcher import *
from .search import *
from .combinatorialSearch import *
