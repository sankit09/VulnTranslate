"""
Validation module for translation quality assessment
Contains implementations for different validation strategies
"""

from .semantic_validator import SemanticValidator

__all__ = [
    'SemanticValidator'
]