"""
Custom exception classes for CVE Translation System
Defines specialized errors for different system components
"""


class CVETranslationError(Exception):
    """Base exception for CVE translation system"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class ValidationError(CVETranslationError):
    """Exception raised during translation validation"""
    pass


class ProcessingError(CVETranslationError):
    """Exception raised during document processing"""
    pass


class TranslationServiceError(CVETranslationError):
    """Exception raised by translation service"""
    pass


class ConfigurationError(CVETranslationError):
    """Exception raised for configuration issues"""
    pass


class AuthenticationError(CVETranslationError):
    """Exception raised for API authentication issues"""
    pass


class RateLimitError(CVETranslationError):
    """Exception raised when API rate limits are exceeded"""
    pass


class UnsupportedFormatError(ProcessingError):
    """Exception raised for unsupported document formats"""
    pass


class EmbeddingError(CVETranslationError):
    """Exception raised during embedding generation"""
    pass