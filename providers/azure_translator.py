"""
Azure OpenAI Translation Provider
Implements ITranslator interface using Azure OpenAI GPT models
"""

import os
import time
from typing import Dict, Any
from openai import AzureOpenAI

from core.interfaces import ITranslator
from core.models import (
    TranslationRequest, 
    TranslationResponse, 
    LanguageCode,
    TranslationConfig
)
from core.exceptions import (
    TranslationServiceError, 
    AuthenticationError,
    ConfigurationError
)


class AzureOpenAITranslator(ITranslator):
    """Azure OpenAI-based translator for CVE documents"""
    
    def __init__(self, config: TranslationConfig = None):
        self.config = config or TranslationConfig()
        self._client = None
        self._initialize_client()
        
        # CVE-specific translation prompt
        self.system_prompt = """You are a cybersecurity translation specialist. Translate English CVE documents to Japanese while preserving technical accuracy.

CRITICAL RULES:
1. DO NOT translate:
   - CVE IDs (e.g., CVE-2025-41225)
   - CVSS scores (e.g., CVSSv3, 8.8)
   - Product names and versions (e.g., VMware ESXi 7.0.3)
   - Company names (VMware, Microsoft, etc.)
   - URLs and technical identifiers
   - Version numbers and build numbers

2. DO translate:
   - Descriptions and explanations
   - Security impact descriptions
   - Technical concepts and terms
   - Instructions and procedures

3. Use formal Japanese business language (敬語) appropriate for technical documentation.
4. Maintain the original sentence structure when possible.
5. Preserve technical accuracy over linguistic fluency.

Translate the following text to Japanese:"""

    def _initialize_client(self):
        """Initialize Azure OpenAI client"""
        azure_key = os.getenv("AZURE_OPENAI_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not azure_key or not azure_endpoint:
            raise AuthenticationError(
                "Azure OpenAI credentials not configured",
                error_code="AZURE_AUTH_MISSING",
                details={
                    "required_vars": ["AZURE_OPENAI_KEY", "AZURE_OPENAI_ENDPOINT"],
                    "optional_vars": ["AZURE_OPENAI_API_VERSION"]
                }
            )
        
        try:
            self._client = AzureOpenAI(
                api_key=azure_key,
                api_version=azure_api_version,
                azure_endpoint=azure_endpoint
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize Azure OpenAI client: {str(e)}",
                error_code="AZURE_CLIENT_INIT_FAILED"
            )

    def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate text using Azure OpenAI"""
        if not self._client:
            raise TranslationServiceError("Client not initialized")
        
        if len(request.text.strip()) < 3:
            return TranslationResponse(
                translated_text=request.text,
                original_text=request.text,
                source_language=request.source_language,
                target_language=request.target_language,
                confidence_score=1.0
            )
        
        start_time = time.time()
        
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": request.text}
            ]
            
            # Add context if provided
            if request.context:
                messages.insert(1, {
                    "role": "system", 
                    "content": f"Additional context: {request.context}"
                })
            
            response = self._client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            translated_text = response.choices[0].message.content
            if not translated_text:
                raise TranslationServiceError("Empty response from Azure OpenAI")
            
            processing_time = time.time() - start_time
            
            return TranslationResponse(
                translated_text=translated_text.strip(),
                original_text=request.text,
                source_language=request.source_language,
                target_language=request.target_language,
                confidence_score=self._calculate_confidence(response),
                processing_time=processing_time,
                metadata={
                    "model": self.config.model_name,
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                    "finish_reason": response.choices[0].finish_reason
                }
            )
            
        except Exception as e:
            if "rate limit" in str(e).lower():
                raise TranslationServiceError(
                    f"Rate limit exceeded: {str(e)}",
                    error_code="RATE_LIMIT_EXCEEDED"
                )
            elif "authentication" in str(e).lower():
                raise AuthenticationError(
                    f"Authentication failed: {str(e)}",
                    error_code="AZURE_AUTH_FAILED"
                )
            else:
                raise TranslationServiceError(
                    f"Translation failed: {str(e)}",
                    error_code="TRANSLATION_FAILED"
                )

    def supports_language_pair(self, source: str, target: str) -> bool:
        """Check if the translator supports the language pair"""
        supported_pairs = {
            (LanguageCode.ENGLISH.value, LanguageCode.JAPANESE.value): True,
            (LanguageCode.JAPANESE.value, LanguageCode.ENGLISH.value): True
        }
        return supported_pairs.get((source, target), False)

    def _calculate_confidence(self, response) -> float:
        """Calculate confidence score based on response metadata"""
        # Basic confidence calculation based on finish reason
        if hasattr(response.choices[0], 'finish_reason'):
            if response.choices[0].finish_reason == "stop":
                return 0.95
            elif response.choices[0].finish_reason == "length":
                return 0.7
            else:
                return 0.5
        return 0.8

    def get_supported_models(self) -> list:
        """Get list of supported models"""
        return ["gpt-4o", "gpt-4", "gpt-35-turbo"]

    def test_connection(self) -> Dict[str, Any]:
        """Test Azure OpenAI connection"""
        try:
            test_request = TranslationRequest(
                text="Test connection",
                source_language=LanguageCode.ENGLISH,
                target_language=LanguageCode.JAPANESE
            )
            response = self.translate(test_request)
            return {
                "success": True,
                "model": self.config.model_name,
                "response_time": response.processing_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }