"""
Document processors module
Contains implementations for different document format processors
"""

from .docx_processor import DOCXProcessor
from .html_processor import HTMLProcessor

__all__ = [
    'DOCXProcessor',
    'HTMLProcessor'
]