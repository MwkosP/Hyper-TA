"""Statistical signal filtering after threshold detection.

Public API: filterByStatistics(signals, df, **criteria)

- filtering.py — win rate, Sharpe, and related filters
Config thresholds: see Assets/docs/claude.md (Filter step)
"""

from .filtering import *
