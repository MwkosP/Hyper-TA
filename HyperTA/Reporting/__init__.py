"""Multi-page PDF reports from search states (ReportLab).

Public API: buildReport(type, states, format="pdf", ...)

- pages.py — section/page builders (Platypus flowables)
- reporting.py — full report templates
- dispatcher.py — buildReport
"""

from .dispatcher import *
from .reporting import *
from .pages import *
