"""
Provider module for external service integrations
Contains implementations for translation, embedding, and other external APIs
"""

from .azure_translator import AzureOpenAITranslator
from .openai_embeddings import OpenAIEmbeddingProvider
from .cve_term_preserver import CVETermPreserver

__all__ = [
    'AzureOpenAITranslator',
    'OpenAIEmbeddingProvider', 
    'CVETermPreserver'
]