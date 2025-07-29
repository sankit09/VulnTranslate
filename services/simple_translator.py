import os
import json
import time
from typing import List, Dict, Any
from openai import AzureOpenAI
from openai import OpenAI
import numpy as np

class SimpleCVETranslator:
    """Simplified CVE translator for proof of concept"""
    
    def __init__(self):
        # Initialize Azure OpenAI for translation
        self.azure_key = os.getenv("AZURE_OPENAI_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not self.azure_key or not self.azure_endpoint:
            raise ValueError("Azure OpenAI credentials not configured")
        
        self.azure_client = AzureOpenAI(
            api_key=self.azure_key,
            api_version=self.azure_api_version,
            azure_endpoint=self.azure_endpoint
        )
        
        # Initialize OpenAI for validation
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OpenAI API key required for validation")
        
        self.openai_client = OpenAI(api_key=openai_key)
        
        # Model settings
        self.translation_model = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        self.embedding_model = "text-embedding-3-small"
        
        # CVE-specific prompt
        self.system_prompt = """You are a cybersecurity translation specialist. Translate English CVE documents to Japanese while preserving technical accuracy.

CRITICAL RULES:
1. DO NOT translate:
   - CVE IDs (e.g., CVE-2025-41225)
   - CVSS scores (e.g., CVSSv3, 8.8)
   - Product names and versions (e.g., VMware ESXi 7.0.3)
   - Company names (VMware, Microsoft, etc.)
   - URLs and technical identifiers

2. DO translate:
   - Descriptions and explanations
   - Security impact descriptions
   - Technical concepts and terms

3. Use formal Japanese business language (敬語) appropriate for technical documentation.

Translate the following text to Japanese:"""
    
    def translate_text(self, text: str) -> str:
        """Translate text from English to Japanese"""
        if len(text.strip()) < 3:
            return text
        
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": text}
            ]
            
            response = self.azure_client.chat.completions.create(
                model=self.translation_model,
                messages=messages,
                max_tokens=2000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else text
            
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return text
    
    def validate_translation(self, original: str, translated: str) -> Dict[str, Any]:
        """Validate translation quality using semantic similarity"""
        try:
            # Get embeddings
            original_embedding = self._get_embedding(original)
            translated_embedding = self._get_embedding(translated)
            
            # Calculate cosine similarity
            similarity = np.dot(original_embedding, translated_embedding) / (
                np.linalg.norm(original_embedding) * np.linalg.norm(translated_embedding)
            )
            
            # Normalize to 0-1 range
            similarity_score = max(0.0, min(1.0, (similarity + 1) / 2))
            
            return {
                'similarity_score': similarity_score,
                'quality': 'Good' if similarity_score > 0.7 else 'Needs Review',
                'technical_terms_preserved': self._check_technical_preservation(original, translated)
            }
            
        except Exception as e:
            return {
                'similarity_score': 0.0,
                'quality': f'Validation Error: {str(e)}',
                'technical_terms_preserved': False
            }
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding vector for text"""
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text.replace("\n", " ")
        )
        return np.array(response.data[0].embedding)
    
    def _check_technical_preservation(self, original: str, translated: str) -> bool:
        """Check if technical terms are preserved"""
        import re
        
        # Technical patterns that should be preserved
        patterns = [
            r'CVE-\d{4}-\d{4,7}',
            r'CVSS[v]?\d+(\.\d+)?',
            r'VMware|Microsoft|Oracle|Adobe',
            r'https?://[^\s]+',
        ]
        
        for pattern in patterns:
            original_matches = set(re.findall(pattern, original, re.IGNORECASE))
            translated_matches = set(re.findall(pattern, translated, re.IGNORECASE))
            
            if original_matches and not original_matches.issubset(translated_matches):
                return False
        
        return True