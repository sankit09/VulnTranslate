"""
HTML Document Processor
Implements IDocumentProcessor interface for HTML files using BeautifulSoup
"""

import io
from typing import Dict, Any, List
from bs4 import BeautifulSoup, Tag, NavigableString
import re

from core.interfaces import IDocumentProcessor
from core.models import DocumentContent, DocumentType
from core.exceptions import ProcessingError, UnsupportedFormatError


class HTMLProcessor(IDocumentProcessor):
    """HTML document processor with structure preservation"""
    
    def __init__(self):
        self.supported_extensions = ['.html', '.htm']
        self.preserve_formatting = True
        self.preserve_links = True
        self.preserve_tables = True

    def can_process(self, file_extension: str) -> bool:
        """Check if processor can handle HTML files"""
        return file_extension.lower() in self.supported_extensions

    def extract_content(self, file_content: bytes) -> Dict[str, Any]:
        """Extract translatable content from HTML while preserving structure"""
        try:
            # Parse HTML content
            html_content = file_content.decode('utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            content_blocks = []
            tables = []
            hyperlinks = []
            images = []
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Process all text elements
            text_elements = soup.find_all(text=True)
            for idx, element in enumerate(text_elements):
                if isinstance(element, NavigableString) and element.strip():
                    parent = element.parent
                    if parent and parent.name not in ['script', 'style']:
                        content_block = self._process_text_element(element, idx, parent)
                        if content_block:
                            content_blocks.append(content_block)
            
            # Process tables
            for table_idx, table in enumerate(soup.find_all('table')):
                table_data = self._process_table(table, table_idx)
                tables.append(table_data)
            
            # Extract hyperlinks
            for link in soup.find_all('a', href=True):
                hyperlinks.append({
                    'text': link.get_text().strip(),
                    'href': link['href'],
                    'title': link.get('title', '')
                })
            
            # Extract images
            for img in soup.find_all('img'):
                images.append({
                    'src': img.get('src', ''),
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })
            
            # Count statistics
            total_elements = len(content_blocks)
            translatable_elements = len([b for b in content_blocks if b.get('translatable', False)])
            technical_elements = total_elements - translatable_elements
            
            document_content = DocumentContent(
                content_blocks=content_blocks,
                metadata={
                    'original_file_size': len(file_content),
                    'total_elements': len(content_blocks),
                    'encoding': 'utf-8'
                },
                document_type=DocumentType.HTML,
                total_paragraphs=total_elements,
                translatable_paragraphs=translatable_elements,
                technical_paragraphs=technical_elements,
                tables=tables,
                hyperlinks=hyperlinks,
                images=images
            )
            
            return {
                'document_content': document_content,
                'original_soup': soup,
                'success': True
            }
            
        except Exception as e:
            raise ProcessingError(
                f"Failed to extract content from HTML: {str(e)}",
                error_code="HTML_EXTRACTION_FAILED"
            )

    def reconstruct_document(self, content: Dict[str, Any], translations: Dict[str, str]) -> bytes:
        """Reconstruct HTML document with translated content"""
        try:
            original_soup = content.get('original_soup')
            if not original_soup:
                raise ProcessingError("Original HTML structure not found in content")
            
            # Create a copy of the soup for modification
            soup_copy = BeautifulSoup(str(original_soup), 'html.parser')
            
            # Apply translations to text elements
            self._apply_translations_to_html(soup_copy, translations)
            
            # Convert back to HTML string
            html_output = str(soup_copy)
            
            return html_output.encode('utf-8')
            
        except Exception as e:
            raise ProcessingError(
                f"Failed to reconstruct HTML document: {str(e)}",
                error_code="HTML_RECONSTRUCTION_FAILED"
            )

    def _process_text_element(self, element: NavigableString, element_id: int, parent: Tag) -> Dict[str, Any]:
        """Process individual text element"""
        text = element.strip()
        
        if not text or len(text) < 3:
            return None
        
        # Determine if text is translatable
        translatable = self._is_translatable_text(text)
        
        content_block = {
            'id': str(element_id),
            'text': text,
            'translatable': translatable,
            'location': 'html_text',
            'parent_tag': parent.name if parent else 'unknown',
            'css_classes': parent.get('class', []) if parent else [],
            'element_id': parent.get('id', '') if parent else ''
        }
        
        return content_block

    def _process_table(self, table: Tag, table_idx: int) -> Dict[str, Any]:
        """Process table structure and content"""
        rows = table.find_all('tr')
        table_data = {
            'index': table_idx,
            'rows': len(rows),
            'columns': 0,
            'cells': []
        }
        
        max_columns = 0
        for row_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            max_columns = max(max_columns, len(cells))
            
            row_data = []
            for cell_idx, cell in enumerate(cells):
                cell_text = cell.get_text().strip()
                cell_data = {
                    'text': cell_text,
                    'translatable': self._is_translatable_text(cell_text),
                    'row': row_idx,
                    'column': cell_idx,
                    'tag': cell.name
                }
                row_data.append(cell_data)
            table_data['cells'].append(row_data)
        
        table_data['columns'] = max_columns
        return table_data

    def _is_translatable_text(self, text: str) -> bool:
        """Determine if text should be translated"""
        if not text or len(text.strip()) < 3:
            return False
        
        # Skip technical patterns
        technical_patterns = [
            r'^CVE-\d{4}-\d{4,7}$',
            r'^https?://',
            r'^\d+\.\d+[\.\d+]*$',
            r'^[A-Z_][A-Z0-9_]*$',  # Constants
            r'^\w+@\w+\.\w+$',  # Emails
            r'^\d+$',  # Pure numbers
            r'^[<>=/\-\+\*\(\)\[\]{}]+$'  # Pure symbols
        ]
        
        for pattern in technical_patterns:
            if re.match(pattern, text.strip(), re.IGNORECASE):
                return False
        
        # Check if text is mostly HTML entities or special characters
        if len(re.sub(r'[a-zA-Z\s]', '', text)) > len(text) * 0.5:
            return False
        
        return True

    def _apply_translations_to_html(self, soup, translations: Dict[str, str]):
        """Apply translations to HTML document"""
        text_elements = soup.find_all(text=True)
        
        for idx, element in enumerate(text_elements):
            if isinstance(element, NavigableString) and element.strip():
                element_id = str(idx)
                if element_id in translations:
                    # Replace the text while preserving HTML structure
                    element.replace_with(translations[element_id])

    def get_document_statistics(self, file_content: bytes) -> Dict[str, Any]:
        """Get detailed statistics about the HTML document"""
        try:
            html_content = file_content.decode('utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements for counting
            for script in soup(["script", "style"]):
                script.decompose()
            
            text_elements = [elem for elem in soup.find_all(text=True) if elem.strip()]
            
            stats = {
                'total_text_elements': len(text_elements),
                'total_tables': len(soup.find_all('table')),
                'total_links': len(soup.find_all('a', href=True)),
                'total_images': len(soup.find_all('img')),
                'total_headings': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                'total_paragraphs': len(soup.find_all('p')),
                'word_count': self._count_words(soup),
                'character_count': self._count_characters(soup)
            }
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}

    def _count_words(self, soup) -> int:
        """Count total words in HTML document"""
        text = soup.get_text()
        return len(text.split())

    def _count_characters(self, soup) -> int:
        """Count total characters in HTML document"""
        text = soup.get_text()
        return len(text)

    def extract_text_preview(self, file_content: bytes, max_chars: int = 500) -> str:
        """Extract a text preview of the HTML document"""
        try:
            html_content = file_content.decode('utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get clean text
            text = soup.get_text()
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Truncate if necessary
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            return text
            
        except Exception as e:
            return f"Error extracting preview: {str(e)}"