"""governance-review — machine-readable scaffold validator with stable IDs."""

from .finding import Finding, Severity
from .registry import CHECKS, CheckSpec

__all__ = ["CHECKS", "CheckSpec", "Finding", "Severity"]
__version__ = "0.1.0"
