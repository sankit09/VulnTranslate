import os
import json
import time
from typing import List, Dict, Any
from openai import AzureOpenAI
from utils.azure_client import AzureOpenAIClient

class CVETranslator:
    """Translate CVE documents from English to Japanese using Azure OpenAI"""
    
    def __init__(self):
        self.client = AzureOpenAIClient()
        self.translation_cache = {}
        
        # Translation settings
        self.model_name = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        self.max_tokens = 2000
        self.temperature = 0.1  # Low temperature for consistent translations
        
        # CVE-specific translation guidelines
        self.system_prompt = """You are a specialized translator for cybersecurity and CVE (Common Vulnerabilities and Exposures) documents. 
Your task is to translate English text to Japanese while maintaining technical accuracy.

IMPORTANT RULES:
1. DO NOT translate:
   - CVE IDs (e.g., CVE-2025-41225)
   - CVSS scores and version numbers (e.g., CVSSv3, 8.8)
   - Product names and version numbers (e.g., VMware ESXi 7.0.3)
   - Technical identifiers and codes
   - URLs and email addresses
   - Company names (VMware, Microsoft, etc.)

2. DO translate:
   - Descriptions and explanations
   - Security impact descriptions
   - Mitigation steps and recommendations
   - General technical terms and concepts

3. Maintain:
   - Professional cybersecurity terminology
   - Sentence structure appropriate for technical documentation
   - Formal Japanese business language (敬語)

4. Output format:
   - Return only the translated text
   - Preserve paragraph breaks and formatting markers
   - Keep the same text structure as input

Translate the following text to Japanese:"""
    
    def translate_text(self, text: str) -> str:
        """Translate a single text block from English to Japanese"""
        
        # Check cache first
        cache_key = hash(text)
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # Skip translation for very short text that might be technical identifiers
        if len(text.strip()) < 3:
            return text
        
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": text}
            ]
            
            response = self.client.chat_completion(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            # Cache the result
            self.translation_cache[cache_key] = translated_text
            
            # Add small delay to respect rate limits
            time.sleep(0.1)
            
            return translated_text
            
        except Exception as e:
            # Log error and return original text as fallback
            print(f"Translation error for text '{text[:50]}...': {str(e)}")
            return text
    
    def translate_batch(self, text_blocks: List[str], batch_size: int = 5) -> List[str]:
        """Translate multiple text blocks in batches"""
        
        if not text_blocks:
            return []
        
        translated_blocks = []
        
        # Process in batches to optimize API calls
        for i in range(0, len(text_blocks), batch_size):
            batch = text_blocks[i:i + batch_size]
            
            # Create batch prompt
            batch_text = "\n\n---SEPARATOR---\n\n".join(batch)
            
            try:
                messages = [
                    {"role": "system", "content": self.system_prompt + "\n\nTranslate each section separated by ---SEPARATOR--- and return them in the same order, separated by the same marker."},
                    {"role": "user", "content": batch_text}
                ]
                
                response = self.client.chat_completion(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=self.max_tokens * len(batch),
                    temperature=self.temperature
                )
                
                translated_batch = response.choices[0].message.content.strip()
                
                # Split the response back into individual translations
                translations = translated_batch.split("---SEPARATOR---")
                
                # Ensure we have the right number of translations
                if len(translations) == len(batch):
                    for j, translation in enumerate(translations):
                        cache_key = hash(batch[j])
                        clean_translation = translation.strip()
                        self.translation_cache[cache_key] = clean_translation
                        translated_blocks.append(clean_translation)
                else:
                    # Fallback to individual translation
                    for text in batch:
                        translated_blocks.append(self.translate_text(text))
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Batch translation error: {str(e)}")
                # Fallback to individual translations
                for text in batch:
                    translated_blocks.append(self.translate_text(text))
        
        return translated_blocks
    
    def translate_structured_content(self, content_block: Dict[str, Any]) -> Dict[str, Any]:
        """Translate structured content while preserving formatting"""
        
        block_type = content_block.get('type', '')
        
        if block_type == 'paragraph':
            return self._translate_paragraph(content_block)
        elif block_type == 'heading':
            return self._translate_heading(content_block)
        elif block_type == 'table':
            return self._translate_table(content_block)
        elif block_type == 'list':
            return self._translate_list(content_block)
        else:
            # Generic text translation
            if 'text' in content_block:
                content_block['translated_text'] = self.translate_text(content_block['text'])
            return content_block
    
    def _translate_paragraph(self, paragraph_block: Dict[str, Any]) -> Dict[str, Any]:
        """Translate paragraph content"""
        text = paragraph_block.get('text', '')
        
        if text:
            translated_text = self.translate_text(text)
            paragraph_block['translated_text'] = translated_text
        
        # Handle hyperlinks - translate link text but preserve URLs
        if 'hyperlinks' in paragraph_block:
            for link in paragraph_block['hyperlinks']:
                if 'text' in link:
                    link['translated_text'] = self.translate_text(link['text'])
        
        return paragraph_block
    
    def _translate_heading(self, heading_block: Dict[str, Any]) -> Dict[str, Any]:
        """Translate heading content"""
        text = heading_block.get('text', '')
        
        if text:
            translated_text = self.translate_text(text)
            heading_block['translated_text'] = translated_text
        
        return heading_block
    
    def _translate_table(self, table_block: Dict[str, Any]) -> Dict[str, Any]:
        """Translate table content while preserving structure"""
        rows = table_block.get('rows', [])
        
        for row in rows:
            for cell in row:
                cell_text = cell.get('text', '')
                if cell_text:
                    cell['translated_text'] = self.translate_text(cell_text)
        
        return table_block
    
    def _translate_list(self, list_block: Dict[str, Any]) -> Dict[str, Any]:
        """Translate list items"""
        items = list_block.get('items', [])
        
        for item in items:
            item_text = item.get('text', '')
            if item_text:
                item['translated_text'] = self.translate_text(item_text)
        
        return list_block
    
    def get_translation_statistics(self) -> Dict[str, Any]:
        """Get statistics about translation performance"""
        return {
            'cached_translations': len(self.translation_cache),
            'cache_hit_rate': 0.0,  # Would need to track hits vs misses
            'total_characters_translated': sum(len(text) for text in self.translation_cache.keys()),
            'model_used': self.model_name
        }
    
    def clear_cache(self):
        """Clear translation cache"""
        self.translation_cache.clear()
