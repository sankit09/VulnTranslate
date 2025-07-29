"""
Data models for CVE Translation System
Defines request/response models and data structures
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class LanguageCode(Enum):
    """Supported language codes"""
    ENGLISH = "en"
    JAPANESE = "ja"


class DocumentType(Enum):
    """Supported document types"""
    DOCX = "docx"
    HTML = "html"
    TEXT = "txt"


class TranslationQuality(Enum):
    """Translation quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_REVIEW = "needs_review"
    POOR = "poor"


@dataclass
class TranslationRequest:
    """Request model for translation operations"""
    text: str
    source_language: LanguageCode = LanguageCode.ENGLISH
    target_language: LanguageCode = LanguageCode.JAPANESE
    preserve_technical_terms: bool = True
    context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TranslationResponse:
    """Response model for translation operations"""
    translated_text: str
    original_text: str
    source_language: LanguageCode
    target_language: LanguageCode
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0


@dataclass
class ValidationResult:
    """Result model for translation validation"""
    similarity_score: float
    quality: TranslationQuality
    technical_terms_preserved: bool
    confidence_score: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class DocumentContent:
    """Model for extracted document content"""
    content_blocks: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    document_type: DocumentType
    total_paragraphs: int = 0
    translatable_paragraphs: int = 0
    technical_paragraphs: int = 0
    tables: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    hyperlinks: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ProcessingResult:
    """Result model for document processing operations"""
    success: bool
    document_content: Optional[DocumentContent] = None
    translated_document: Optional[bytes] = None
    validation_results: List[ValidationResult] = field(default_factory=list)
    error_message: Optional[str] = None
    processing_stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CVETerms:
    """Model for CVE-specific technical terms"""
    cve_ids: List[str] = field(default_factory=list)
    cvss_scores: List[str] = field(default_factory=list)
    product_names: List[str] = field(default_factory=list)
    company_names: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    technical_identifiers: List[str] = field(default_factory=list)


@dataclass
class TranslationConfig:
    """Configuration model for translation operations"""
    model_name: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: int = 2000
    batch_size: int = 10
    enable_validation: bool = True
    preserve_formatting: bool = True
    quality_threshold: float = 0.7
    timeout_seconds: int = 60