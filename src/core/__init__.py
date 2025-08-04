"""
Core module for CVE Translation System
Contains base classes, interfaces, and core business logic
"""

from .interfaces import ITranslator, IValidator, IDocumentProcessor
from .models import TranslationRequest, TranslationResponse, ValidationResult
from .exceptions import CVETranslationError, ValidationError, ProcessingError

__all__ = [
    'ITranslator',
    'IValidator', 
    'IDocumentProcessor',
    'TranslationRequest',
    'TranslationResponse',
    'ValidationResult',
    'CVETranslationError',
    'ValidationError',
    'ProcessingError'
]