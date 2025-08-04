"""
Interface definitions for CVE Translation System
Defines contracts for all major components
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .models import TranslationRequest, TranslationResponse, ValidationResult


class ITranslator(ABC):
    """Interface for translation services"""
    
    @abstractmethod
    def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate text from source to target language"""
        pass
    
    @abstractmethod
    def supports_language_pair(self, source: str, target: str) -> bool:
        """Check if translator supports the language pair"""
        pass


class IValidator(ABC):
    """Interface for translation validation services"""
    
    @abstractmethod
    def validate(self, original: str, translated: str, **kwargs) -> ValidationResult:
        """Validate translation quality and accuracy"""
        pass
    
    @abstractmethod
    def get_validation_metrics(self) -> List[str]:
        """Return available validation metrics"""
        pass


class IDocumentProcessor(ABC):
    """Interface for document processing services"""
    
    @abstractmethod
    def can_process(self, file_extension: str) -> bool:
        """Check if processor can handle the file type"""
        pass
    
    @abstractmethod
    def extract_content(self, file_content: bytes) -> Dict[str, Any]:
        """Extract translatable content from document"""
        pass
    
    @abstractmethod
    def reconstruct_document(self, content: Dict[str, Any], translations: Dict[str, str]) -> bytes:
        """Reconstruct document with translated content"""
        pass


class IEmbeddingProvider(ABC):
    """Interface for embedding generation services"""
    
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Return the dimension of embeddings"""
        pass


class ITermPreserver(ABC):
    """Interface for technical term preservation"""
    
    @abstractmethod
    def extract_terms(self, text: str) -> List[str]:
        """Extract technical terms that should be preserved"""
        pass
    
    @abstractmethod
    def verify_preservation(self, original: str, translated: str) -> bool:
        """Verify that technical terms are preserved in translation"""
        pass