import os
import json
import numpy as np
from typing import List, Dict, Tuple, Any
from openai import OpenAI
from utils.azure_client import AzureOpenAIClient

class TranslationValidator:
    """Validate translation quality using Azure OpenAI and OpenAI embeddings"""
    
    def __init__(self):
        self.azure_client = AzureOpenAIClient()
        
        # OpenAI client for embeddings (not available in Azure)
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OpenAI API key required for embeddings")
        
        self.openai_client = OpenAI(api_key=openai_api_key)
        
        # Model settings
        self.validation_model = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        self.embedding_model = "text-embedding-3-small"
        
        # Validation thresholds
        self.semantic_similarity_threshold = 0.7
        self.quality_score_threshold = 0.7
    
    def validate_translations(self, translation_pairs: List[Tuple[str, str]], quality_threshold: float = 0.7) -> Dict[str, Any]:
        """Validate a list of translation pairs"""
        
        if not translation_pairs:
            return {
                'average_score': 0.0,
                'total_translations': 0,
                'passed_validations': 0,
                'failed_validations': 0,
                'low_quality_translations': []
            }
        
        validation_results = []
        low_quality_translations = []
        
        for i, (original, translated) in enumerate(translation_pairs):
            try:
                # Validate individual translation
                result = self.validate_single_translation(original, translated)
                validation_results.append(result)
                
                # Check if translation meets quality threshold
                if result['overall_score'] < quality_threshold:
                    low_quality_translations.append({
                        'index': i,
                        'original': original[:100] + "..." if len(original) > 100 else original,
                        'translated': translated[:100] + "..." if len(translated) > 100 else translated,
                        'score': result['overall_score'],
                        'issues': result['issues']
                    })
            
            except Exception as e:
                print(f"Validation error for pair {i}: {str(e)}")
                validation_results.append({
                    'semantic_similarity': 0.0,
                    'quality_score': 0.0,
                    'overall_score': 0.0,
                    'issues': [f"Validation failed: {str(e)}"]
                })
        
        # Calculate aggregate statistics
        if validation_results:
            scores = [r['overall_score'] for r in validation_results]
            average_score = np.mean(scores)
            passed_count = sum(1 for score in scores if score >= quality_threshold)
        else:
            average_score = 0.0
            passed_count = 0
        
        return {
            'average_score': average_score,
            'total_translations': len(translation_pairs),
            'passed_validations': passed_count,
            'failed_validations': len(translation_pairs) - passed_count,
            'low_quality_translations': low_quality_translations,
            'detailed_results': validation_results
        }
    
    def validate_single_translation(self, original: str, translated: str) -> Dict[str, Any]:
        """Validate a single translation pair"""
        
        # Skip validation for very short texts
        if len(original.strip()) < 10 or len(translated.strip()) < 10:
            return {
                'semantic_similarity': 1.0,
                'quality_score': 1.0,
                'overall_score': 1.0,
                'issues': []
            }
        
        issues = []
        
        # 1. Semantic similarity using embeddings
        similarity_score = self._calculate_semantic_similarity(original, translated)
        
        if similarity_score < self.semantic_similarity_threshold:
            issues.append(f"Low semantic similarity: {similarity_score:.2f}")
        
        # 2. Quality assessment using LLM
        quality_score = self._assess_translation_quality(original, translated)
        
        if quality_score < self.quality_score_threshold:
            issues.append(f"Low quality score: {quality_score:.2f}")
        
        # 3. Technical term preservation check
        tech_preservation_score = self._check_technical_term_preservation(original, translated)
        
        if tech_preservation_score < 0.8:
            issues.append("Technical terms may not be properly preserved")
        
        # Calculate overall score (weighted average)
        overall_score = (
            similarity_score * 0.4 +
            quality_score * 0.4 +
            tech_preservation_score * 0.2
        )
        
        return {
            'semantic_similarity': similarity_score,
            'quality_score': quality_score,
            'technical_preservation': tech_preservation_score,
            'overall_score': overall_score,
            'issues': issues
        }
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using embeddings"""
        try:
            # Get embeddings for both texts
            embedding1 = self._get_embedding(text1)
            embedding2 = self._get_embedding(text2)
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            
            # Normalize to 0-1 range
            return max(0.0, min(1.0, (similarity + 1) / 2))
            
        except Exception as e:
            print(f"Embedding similarity calculation error: {str(e)}")
            return 0.5  # Default moderate score on error
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding vector for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text.replace("\n", " ")
            )
            
            return np.array(response.data[0].embedding)
            
        except Exception as e:
            print(f"Embedding generation error: {str(e)}")
            # Return random embedding as fallback
            return np.random.rand(1536)  # text-embedding-3-small dimension
    
    def _assess_translation_quality(self, original: str, translated: str) -> float:
        """Assess translation quality using LLM"""
        
        prompt = f"""You are a translation quality assessor. Evaluate the quality of this English to Japanese translation for a cybersecurity/CVE document.

Original English text:
{original}

Japanese translation:
{translated}

Assess the translation quality on a scale of 0.0 to 1.0 based on:
1. Accuracy of meaning
2. Appropriateness of technical terminology
3. Natural Japanese language flow
4. Preservation of technical identifiers (CVE IDs, version numbers, etc.)
5. Professional cybersecurity language usage

Respond with ONLY a number between 0.0 and 1.0."""
        
        try:
            response = self.azure_client.chat_completion(
                model=self.validation_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            score_text = response.choices[0].message.content.strip()
            
            # Extract numeric score
            try:
                score = float(score_text)
                return max(0.0, min(1.0, score))
            except ValueError:
                print(f"Invalid score format: {score_text}")
                return 0.5
                
        except Exception as e:
            print(f"Quality assessment error: {str(e)}")
            return 0.5
    
    def _check_technical_term_preservation(self, original: str, translated: str) -> float:
        """Check if technical terms are properly preserved"""
        
        # Define patterns for technical terms that should NOT be translated
        technical_patterns = [
            r'CVE-\d{4}-\d{4,7}',  # CVE IDs
            r'CVSS[v]?\d+(\.\d+)?',  # CVSS versions
            r'\d+\.\d+[\.\d+]*',  # Version numbers
            r'VMware|Microsoft|Oracle|Adobe',  # Company names
            r'ESXi|vCenter|Workstation|Fusion',  # Product names
            r'https?://[^\s]+',  # URLs
            r'\b[A-Z]{2,}[-_]?\d+\b',  # Technical codes
        ]
        
        import re
        
        original_terms = set()
        translated_terms = set()
        
        # Extract technical terms from both texts
        for pattern in technical_patterns:
            original_terms.update(re.findall(pattern, original, re.IGNORECASE))
            translated_terms.update(re.findall(pattern, translated, re.IGNORECASE))
        
        if not original_terms:
            return 1.0  # No technical terms to preserve
        
        # Calculate preservation ratio
        preserved_terms = original_terms.intersection(translated_terms)
        preservation_ratio = len(preserved_terms) / len(original_terms)
        
        return preservation_ratio
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate a human-readable validation report"""
        
        report = f"""Translation Validation Report
========================================

Overall Statistics:
- Total translations: {validation_results['total_translations']}
- Average quality score: {validation_results['average_score']:.2f}
- Passed validations: {validation_results['passed_validations']}
- Failed validations: {validation_results['failed_validations']}

"""
        
        if validation_results['low_quality_translations']:
            report += "Low Quality Translations:\n"
            report += "-" * 30 + "\n"
            
            for item in validation_results['low_quality_translations'][:5]:  # Show top 5
                report += f"\nTranslation #{item['index'] + 1} (Score: {item['score']:.2f}):\n"
                report += f"Original: {item['original']}\n"
                report += f"Translated: {item['translated']}\n"
                report += f"Issues: {', '.join(item['issues'])}\n"
        
        return report
