import os
from typing import Dict, Any

class Config:
    """Application configuration"""
    
    # Azure OpenAI settings
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # OpenAI settings (for embeddings)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Translation settings
    TRANSLATION_MODEL = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
    VALIDATION_MODEL = "gpt-4o"
    EMBEDDING_MODEL = "text-embedding-3-small"
    
    # Processing settings
    MAX_TOKENS_PER_REQUEST = 2000
    TEMPERATURE = 0.1
    BATCH_SIZE = 5
    
    # Validation thresholds
    SEMANTIC_SIMILARITY_THRESHOLD = 0.7
    QUALITY_SCORE_THRESHOLD = 0.7
    TECHNICAL_PRESERVATION_THRESHOLD = 0.8
    
    # File processing
    MAX_FILE_SIZE_MB = 50
    SUPPORTED_FORMATS = ['docx', 'html']
    
    # UI settings
    PAGE_TITLE = "CVE Translation System"
    PAGE_ICON = "🔒"
    
    @classmethod
    def validate_configuration(cls) -> Dict[str, Any]:
        """Validate application configuration"""
        
        issues = []
        
        if not cls.AZURE_OPENAI_KEY:
            issues.append("AZURE_OPENAI_KEY not configured")
        
        if not cls.AZURE_OPENAI_ENDPOINT:
            issues.append("AZURE_OPENAI_ENDPOINT not configured")
        
        if not cls.OPENAI_API_KEY:
            issues.append("OPENAI_API_KEY not configured (required for embeddings)")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    @classmethod
    def get_display_config(cls) -> Dict[str, Any]:
        """Get configuration for display (without sensitive data)"""
        
        return {
            'translation_model': cls.TRANSLATION_MODEL,
            'validation_model': cls.VALIDATION_MODEL,
            'embedding_model': cls.EMBEDDING_MODEL,
            'max_file_size_mb': cls.MAX_FILE_SIZE_MB,
            'supported_formats': cls.SUPPORTED_FORMATS,
            'azure_endpoint_configured': bool(cls.AZURE_OPENAI_ENDPOINT),
            'openai_key_configured': bool(cls.OPENAI_API_KEY)
        }
