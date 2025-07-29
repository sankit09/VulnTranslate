import re
from typing import List, Dict, Any

class TextProcessor:
    """Process text content for translation while preserving technical terms"""
    
    def __init__(self):
        # Technical patterns that should NOT be translated
        self.technical_patterns = [
            r'CVE-\d{4}-\d{4,7}',  # CVE IDs
            r'VMSA-\d{4}-\d{4}',   # VMware Security Advisories
            r'CVSS[v]?\d+(\.\d+)?',  # CVSS versions
            r'\d+\.\d+[\.\d+]*',   # Version numbers
            r'VMware|Microsoft|Oracle|Adobe|Cisco|Apple',  # Company names
            r'ESXi|vCenter|Workstation|Fusion|Windows|Linux|macOS',  # Product names
            r'https?://[^\s]+',    # URLs
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email addresses
            r'\b[A-Z]{2,}[-_]?\d+\b',  # Technical codes
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP addresses
            r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b',  # UUIDs
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.technical_patterns]
    
    def prepare_for_translation(self, content_blocks: List[Dict[str, Any]], preserve_technical_terms: bool = True) -> List[Dict[str, Any]]:
        """Prepare content blocks for translation"""
        
        processed_blocks = []
        
        for block in content_blocks:
            processed_block = self._process_single_block(block, preserve_technical_terms)
            processed_blocks.append(processed_block)
        
        return processed_blocks
    
    def _process_single_block(self, block: Dict[str, Any], preserve_technical_terms: bool) -> Dict[str, Any]:
        """Process a single content block"""
        
        # Copy original block
        processed_block = block.copy()
        
        # Determine if block should be translated
        block_type = block.get('type', '')
        text = block.get('text', '')
        
        # Check if block contains translatable content
        is_translatable = self._is_translatable_content(text, preserve_technical_terms)
        
        processed_block['translatable'] = is_translatable
        processed_block['original_text'] = text
        
        # If preserving technical terms, mark them for protection
        if preserve_technical_terms and is_translatable:
            processed_block['protected_terms'] = self._extract_technical_terms(text)
            processed_block['processed_text'] = self._mask_technical_terms(text)
        else:
            processed_block['protected_terms'] = []
            processed_block['processed_text'] = text
        
        # Process nested content (tables, lists, etc.)
        if block_type == 'table':
            processed_block = self._process_table_block(processed_block, preserve_technical_terms)
        elif block_type == 'list':
            processed_block = self._process_list_block(processed_block, preserve_technical_terms)
        
        return processed_block
    
    def _is_translatable_content(self, text: str, preserve_technical_terms: bool) -> bool:
        """Determine if content should be translated"""
        
        if not text or len(text.strip()) < 3:
            return False
        
        # Skip very short technical identifiers
        if len(text.strip()) < 10 and any(pattern.search(text) for pattern in self.compiled_patterns):
            return False
        
        # Check if text is mostly technical terms
        if preserve_technical_terms:
            technical_content = self._get_technical_content_ratio(text)
            if technical_content > 0.8:  # More than 80% technical terms
                return False
        
        # Check for specific non-translatable patterns
        non_translatable_patterns = [
            r'^\d+(\.\d+)*$',  # Version numbers only
            r'^[A-Z]{2,}[-_]?\d+$',  # Technical codes only
            r'^https?://',  # URLs
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',  # Emails
        ]
        
        for pattern in non_translatable_patterns:
            if re.match(pattern, text.strip(), re.IGNORECASE):
                return False
        
        return True
    
    def _get_technical_content_ratio(self, text: str) -> float:
        """Calculate ratio of technical content in text"""
        
        total_chars = len(text)
        if total_chars == 0:
            return 0.0
        
        technical_chars = 0
        
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            for match in matches:
                technical_chars += len(match)
        
        return technical_chars / total_chars
    
    def _extract_technical_terms(self, text: str) -> List[Dict[str, Any]]:
        """Extract technical terms and their positions"""
        
        technical_terms = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            for match in pattern.finditer(text):
                technical_terms.append({
                    'term': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'pattern_index': i
                })
        
        # Sort by position
        technical_terms.sort(key=lambda x: x['start'])
        
        return technical_terms
    
    def _mask_technical_terms(self, text: str) -> str:
        """Replace technical terms with placeholders for translation"""
        
        masked_text = text
        technical_terms = self._extract_technical_terms(text)
        
        # Replace from end to start to maintain positions
        for i, term_info in enumerate(reversed(technical_terms)):
            placeholder = f"__TECH_TERM_{len(technical_terms) - 1 - i}__"
            start = term_info['start']
            end = term_info['end']
            masked_text = masked_text[:start] + placeholder + masked_text[end:]
        
        return masked_text
    
    def restore_technical_terms(self, translated_text: str, technical_terms: List[Dict[str, Any]]) -> str:
        """Restore technical terms in translated text"""
        
        restored_text = translated_text
        
        # Replace placeholders with original terms
        for i, term_info in enumerate(technical_terms):
            placeholder = f"__TECH_TERM_{i}__"
            restored_text = restored_text.replace(placeholder, term_info['term'])
        
        return restored_text
    
    def _process_table_block(self, block: Dict[str, Any], preserve_technical_terms: bool) -> Dict[str, Any]:
        """Process table content for translation"""
        
        rows = block.get('rows', [])
        
        for row in rows:
            for cell in row:
                cell_text = cell.get('text', '')
                cell['translatable'] = self._is_translatable_content(cell_text, preserve_technical_terms)
                
                if preserve_technical_terms and cell['translatable']:
                    cell['protected_terms'] = self._extract_technical_terms(cell_text)
                    cell['processed_text'] = self._mask_technical_terms(cell_text)
                else:
                    cell['protected_terms'] = []
                    cell['processed_text'] = cell_text
        
        return block
    
    def _process_list_block(self, block: Dict[str, Any], preserve_technical_terms: bool) -> Dict[str, Any]:
        """Process list content for translation"""
        
        items = block.get('items', [])
        
        for item in items:
            item_text = item.get('text', '')
            item['translatable'] = self._is_translatable_content(item_text, preserve_technical_terms)
            
            if preserve_technical_terms and item['translatable']:
                item['protected_terms'] = self._extract_technical_terms(item_text)
                item['processed_text'] = self._mask_technical_terms(item_text)
            else:
                item['protected_terms'] = []
                item['processed_text'] = item_text
        
        return block
    
    def clean_text_for_translation(self, text: str) -> str:
        """Clean text before translation"""
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        # Handle special characters that might interfere with translation
        # (Add specific cleaning rules as needed)
        
        return cleaned
    
    def post_process_translation(self, translated_text: str, original_block: Dict[str, Any]) -> str:
        """Post-process translated text"""
        
        # Restore technical terms if they were protected
        protected_terms = original_block.get('protected_terms', [])
        if protected_terms:
            translated_text = self.restore_technical_terms(translated_text, protected_terms)
        
        # Clean up any formatting issues
        translated_text = self._clean_translation_artifacts(translated_text)
        
        return translated_text
    
    def _clean_translation_artifacts(self, text: str) -> str:
        """Clean up common translation artifacts"""
        
        # Remove double spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        
        # Fix spacing after punctuation
        text = re.sub(r'([.,;:!?])([^\s])', r'\1 \2', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    def get_processing_statistics(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about text processing"""
        
        total_blocks = len(blocks)
        translatable_blocks = sum(1 for block in blocks if block.get('translatable', False))
        
        total_technical_terms = 0
        for block in blocks:
            total_technical_terms += len(block.get('protected_terms', []))
        
        return {
            'total_blocks': total_blocks,
            'translatable_blocks': translatable_blocks,
            'non_translatable_blocks': total_blocks - translatable_blocks,
            'total_technical_terms_protected': total_technical_terms,
            'translatable_ratio': translatable_blocks / total_blocks if total_blocks > 0 else 0
        }
