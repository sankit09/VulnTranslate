"""
Semantic Validator
Implements IValidator interface using embedding-based semantic similarity
"""

from typing import Dict, Any, List
import time

from core.interfaces import IValidator, IEmbeddingProvider
from core.models import ValidationResult, TranslationQuality
from core.exceptions import ValidationError


class SemanticValidator(IValidator):
    """Validates translation quality using semantic similarity"""
    
    def __init__(self, embedding_provider: IEmbeddingProvider, quality_threshold: float = 0.7):
        self.embedding_provider = embedding_provider
        self.quality_threshold = quality_threshold
        
        # Quality thresholds
        self.quality_thresholds = {
            TranslationQuality.EXCELLENT: 0.9,
            TranslationQuality.GOOD: 0.7,
            TranslationQuality.NEEDS_REVIEW: 0.5,
            TranslationQuality.POOR: 0.0
        }

    def validate(self, original: str, translated: str, **kwargs) -> ValidationResult:
        """Validate translation using semantic similarity"""
        if not original or not translated:
            return ValidationResult(
                similarity_score=0.0,
                quality=TranslationQuality.POOR,
                technical_terms_preserved=False,
                confidence_score=0.0,
                suggestions=["Empty text provided"]
            )
        
        try:
            start_time = time.time()
            
            # Get embeddings for both texts
            original_embedding = self.embedding_provider.get_embedding(original)
            translated_embedding = self.embedding_provider.get_embedding(translated)
            
            # Calculate semantic similarity
            similarity_score = self.embedding_provider.calculate_similarity(
                original_embedding, translated_embedding
            )
            
            # Determine quality level
            quality = self._determine_quality(similarity_score)
            
            # Calculate confidence based on text characteristics
            confidence_score = self._calculate_confidence(original, translated, similarity_score)
            
            # Generate suggestions if needed
            suggestions = self._generate_suggestions(similarity_score, quality)
            
            processing_time = time.time() - start_time
            
            return ValidationResult(
                similarity_score=similarity_score,
                quality=quality,
                technical_terms_preserved=True,  # Will be overridden by composite validator
                confidence_score=confidence_score,
                details={
                    'processing_time': processing_time,
                    'original_length': len(original),
                    'translated_length': len(translated),
                    'length_ratio': len(translated) / len(original) if original else 0
                },
                suggestions=suggestions
            )
            
        except Exception as e:
            raise ValidationError(
                f"Semantic validation failed: {str(e)}",
                error_code="SEMANTIC_VALIDATION_FAILED"
            )

    def get_validation_metrics(self) -> List[str]:
        """Return available validation metrics"""
        return [
            'similarity_score',
            'quality_level',
            'confidence_score',
            'processing_time',
            'length_ratio'
        ]

    def _determine_quality(self, similarity_score: float) -> TranslationQuality:
        """Determine quality level based on similarity score"""
        if similarity_score >= self.quality_thresholds[TranslationQuality.EXCELLENT]:
            return TranslationQuality.EXCELLENT
        elif similarity_score >= self.quality_thresholds[TranslationQuality.GOOD]:
            return TranslationQuality.GOOD
        elif similarity_score >= self.quality_thresholds[TranslationQuality.NEEDS_REVIEW]:
            return TranslationQuality.NEEDS_REVIEW
        else:
            return TranslationQuality.POOR

    def _calculate_confidence(self, original: str, translated: str, similarity_score: float) -> float:
        """Calculate confidence score based on various factors"""
        confidence_factors = []
        
        # Similarity-based confidence
        confidence_factors.append(similarity_score)
        
        # Length ratio confidence (penalize extreme length differences)
        length_ratio = len(translated) / len(original) if original else 0
        if 0.5 <= length_ratio <= 2.0:
            length_confidence = 1.0
        elif 0.3 <= length_ratio <= 3.0:
            length_confidence = 0.8
        else:
            length_confidence = 0.5
        confidence_factors.append(length_confidence)
        
        # Text complexity confidence (longer texts generally more reliable)
        complexity_confidence = min(1.0, max(0.3, len(original) / 1000))
        confidence_factors.append(complexity_confidence)
        
        # Average confidence
        return sum(confidence_factors) / len(confidence_factors)

    def _generate_suggestions(self, similarity_score: float, quality: TranslationQuality) -> List[str]:
        """Generate improvement suggestions based on validation results"""
        suggestions = []
        
        if quality == TranslationQuality.POOR:
            suggestions.extend([
                "Consider retranslating this text",
                "Check for missing or incorrect translations",
                "Verify that technical terms are properly preserved"
            ])
        elif quality == TranslationQuality.NEEDS_REVIEW:
            suggestions.extend([
                "Review translation for accuracy",
                "Consider alternative phrasing for better flow"
            ])
        elif similarity_score < 0.6:
            suggestions.append("Low semantic similarity - verify meaning preservation")
        
        return suggestions

    def batch_validate(self, text_pairs: List[tuple]) -> List[ValidationResult]:
        """Validate multiple translation pairs in batch"""
        results = []
        
        try:
            # Extract texts for batch embedding
            original_texts = [pair[0] for pair in text_pairs]
            translated_texts = [pair[1] for pair in text_pairs]
            
            # Get batch embeddings
            original_embeddings = self.embedding_provider.get_batch_embeddings(original_texts)
            translated_embeddings = self.embedding_provider.get_batch_embeddings(translated_texts)
            
            # Process each pair
            for i, (original, translated) in enumerate(text_pairs):
                if i < len(original_embeddings) and i < len(translated_embeddings):
                    similarity_score = self.embedding_provider.calculate_similarity(
                        original_embeddings[i], translated_embeddings[i]
                    )
                    
                    quality = self._determine_quality(similarity_score)
                    confidence_score = self._calculate_confidence(original, translated, similarity_score)
                    suggestions = self._generate_suggestions(similarity_score, quality)
                    
                    result = ValidationResult(
                        similarity_score=similarity_score,
                        quality=quality,
                        technical_terms_preserved=True,
                        confidence_score=confidence_score,
                        suggestions=suggestions
                    )
                    results.append(result)
                else:
                    # Fallback for failed embeddings
                    results.append(ValidationResult(
                        similarity_score=0.0,
                        quality=TranslationQuality.POOR,
                        technical_terms_preserved=False,
                        confidence_score=0.0,
                        suggestions=["Failed to process embeddings"]
                    ))
            
        except Exception as e:
            # Return error results for all pairs
            for _ in text_pairs:
                results.append(ValidationResult(
                    similarity_score=0.0,
                    quality=TranslationQuality.POOR,
                    technical_terms_preserved=False,
                    confidence_score=0.0,
                    suggestions=[f"Batch validation error: {str(e)}"]
                ))
        
        return results

    def set_quality_threshold(self, threshold: float):
        """Update quality threshold"""
        if 0.0 <= threshold <= 1.0:
            self.quality_threshold = threshold
        else:
            raise ValueError("Quality threshold must be between 0.0 and 1.0")

    def get_quality_threshold(self) -> float:
        """Get current quality threshold"""
        return self.quality_threshold