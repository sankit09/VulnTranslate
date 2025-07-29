"""
OpenAI Embedding Provider
Implements IEmbeddingProvider interface using OpenAI embeddings API
"""

import os
import numpy as np
from typing import List
from openai import OpenAI

from core.interfaces import IEmbeddingProvider
from core.exceptions import EmbeddingError, AuthenticationError


class OpenAIEmbeddingProvider(IEmbeddingProvider):
    """OpenAI-based embedding generation for translation validation"""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self._client = None
        self._dimension = 1536  # Default for text-embedding-3-small
        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise AuthenticationError(
                "OpenAI API key not configured",
                error_code="OPENAI_AUTH_MISSING",
                details={"required_vars": ["OPENAI_API_KEY"]}
            )
        
        try:
            self._client = OpenAI(api_key=api_key)
            # Test connection and get actual dimension
            self._test_and_get_dimension()
        except Exception as e:
            raise AuthenticationError(
                f"Failed to initialize OpenAI client: {str(e)}",
                error_code="OPENAI_CLIENT_INIT_FAILED"
            )

    def _test_and_get_dimension(self):
        """Test connection and determine embedding dimension"""
        try:
            response = self._client.embeddings.create(
                model=self.model,
                input="test"
            )
            self._dimension = len(response.data[0].embedding)
        except Exception as e:
            # Fall back to default dimension if test fails
            self._dimension = 1536

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        if not self._client:
            raise EmbeddingError("Client not initialized")
        
        if not text or not text.strip():
            return [0.0] * self._dimension
        
        try:
            # Clean text for embedding
            clean_text = text.replace("\n", " ").strip()
            
            response = self._client.embeddings.create(
                model=self.model,
                input=clean_text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            if "rate limit" in str(e).lower():
                raise EmbeddingError(
                    f"Rate limit exceeded: {str(e)}",
                    error_code="EMBEDDING_RATE_LIMIT"
                )
            elif "authentication" in str(e).lower():
                raise AuthenticationError(
                    f"Authentication failed: {str(e)}",
                    error_code="OPENAI_AUTH_FAILED"
                )
            else:
                raise EmbeddingError(
                    f"Embedding generation failed: {str(e)}",
                    error_code="EMBEDDING_FAILED"
                )

    def get_embedding_dimension(self) -> int:
        """Return the dimension of embeddings"""
        return self._dimension

    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch"""
        if not self._client:
            raise EmbeddingError("Client not initialized")
        
        if not texts:
            return []
        
        try:
            # Clean texts
            clean_texts = [text.replace("\n", " ").strip() for text in texts if text.strip()]
            
            if not clean_texts:
                return []
            
            response = self._client.embeddings.create(
                model=self.model,
                input=clean_texts
            )
            
            return [item.embedding for item in response.data]
            
        except Exception as e:
            raise EmbeddingError(
                f"Batch embedding generation failed: {str(e)}",
                error_code="BATCH_EMBEDDING_FAILED"
            )

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            magnitude1 = np.linalg.norm(vec1)
            magnitude2 = np.linalg.norm(vec2)
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            
            # Normalize to 0-1 range
            return max(0.0, min(1.0, (similarity + 1) / 2))
            
        except Exception as e:
            raise EmbeddingError(
                f"Similarity calculation failed: {str(e)}",
                error_code="SIMILARITY_CALCULATION_FAILED"
            )

    def test_connection(self) -> dict:
        """Test OpenAI connection"""
        try:
            embedding = self.get_embedding("test connection")
            return {
                "success": True,
                "model": self.model,
                "dimension": len(embedding)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }