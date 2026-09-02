"""Fatuus: Desconstrução de marcas sintéticas e humanização de texto."""

from .detector import FatuusDetector
from .sanitizer import FatuusSanitizer

__version__ = "0.1.0"
__all__ = ["FatuusDetector", "FatuusSanitizer"]
