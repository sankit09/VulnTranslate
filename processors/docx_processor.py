"""
DOCX Document Processor
Implements IDocumentProcessor interface for DOCX files using python-docx
"""

import tempfile
import io
from typing import Dict, Any, List
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_COLOR_INDEX

from core.interfaces import IDocumentProcessor
from core.models import DocumentContent, DocumentType
from core.exceptions import ProcessingError, UnsupportedFormatError


class DOCXProcessor(IDocumentProcessor):
    """DOCX document processor with full format preservation"""
    
    def __init__(self):
        self.supported_extensions = ['.docx']
        self.preserve_formatting = True
        self.preserve_images = True
        self.preserve_tables = True
        self.preserve_hyperlinks = True

    def can_process(self, file_extension: str) -> bool:
        """Check if processor can handle DOCX files"""
        return file_extension.lower() in self.supported_extensions

    def extract_content(self, file_content: bytes) -> Dict[str, Any]:
        """Extract translatable content from DOCX while preserving structure"""
        try:
            # Load document from bytes
            doc = Document(io.BytesIO(file_content))
            
            content_blocks = []
            tables = []
            hyperlinks = []
            images = []
            
            # Process document paragraphs
            for para_idx, paragraph in enumerate(doc.paragraphs):
                content_block = self._process_paragraph(paragraph, para_idx)
                if content_block:
                    content_blocks.append(content_block)
            
            # Process text boxes and shapes
            for shape_idx, shape in enumerate(self._get_document_shapes(doc)):
                shape_content = self._process_shape_text(shape, shape_idx)
                if shape_content:
                    content_blocks.extend(shape_content)
            
            # Process tables
            for table_idx, table in enumerate(doc.tables):
                table_data = self._process_table(table, table_idx)
                tables.append(table_data)
                
                # Add table cell content to content blocks
                for row_idx, row in enumerate(table.rows):
                    for cell_idx, cell in enumerate(row.cells):
                        for para_idx, paragraph in enumerate(cell.paragraphs):
                            content_block = self._process_paragraph(
                                paragraph, 
                                f"table_{table_idx}_row_{row_idx}_cell_{cell_idx}_para_{para_idx}"
                            )
                            if content_block:
                                content_block['location'] = 'table'
                                content_block['table_info'] = {
                                    'table_idx': table_idx,
                                    'row_idx': row_idx,
                                    'cell_idx': cell_idx
                                }
                                content_blocks.append(content_block)
            
            # Extract hyperlinks
            for paragraph in doc.paragraphs:
                hyperlinks.extend(self._extract_hyperlinks(paragraph))
            
            # Count statistics
            total_paragraphs = len(doc.paragraphs)
            translatable_paragraphs = len([b for b in content_blocks if b.get('translatable', False)])
            technical_paragraphs = total_paragraphs - translatable_paragraphs
            
            document_content = DocumentContent(
                content_blocks=content_blocks,
                metadata={
                    'original_file_size': len(file_content),
                    'document_sections': len(doc.sections),
                    'total_elements': len(content_blocks)
                },
                document_type=DocumentType.DOCX,
                total_paragraphs=total_paragraphs,
                translatable_paragraphs=translatable_paragraphs,
                technical_paragraphs=technical_paragraphs,
                tables=tables,
                hyperlinks=hyperlinks,
                images=images
            )
            
            return {
                'document_content': document_content,
                'original_document': doc,
                'success': True
            }
            
        except Exception as e:
            raise ProcessingError(
                f"Failed to extract content from DOCX: {str(e)}",
                error_code="DOCX_EXTRACTION_FAILED"
            )

    def reconstruct_document(self, content: Dict[str, Any], translations: Dict[str, str]) -> bytes:
        """Reconstruct DOCX document with translated content"""
        try:
            original_doc = content.get('original_document')
            if not original_doc:
                raise ProcessingError("Original document not found in content")
            
            # Create a copy of the document for modification
            doc_copy = self._deep_copy_document(original_doc)
            
            # Apply translations to paragraphs
            self._apply_translations_to_paragraphs(doc_copy, translations)
            
            # Apply translations to tables
            self._apply_translations_to_tables(doc_copy, translations)
            
            # Save to bytes
            output_buffer = io.BytesIO()
            doc_copy.save(output_buffer)
            output_buffer.seek(0)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            raise ProcessingError(
                f"Failed to reconstruct DOCX document: {str(e)}",
                error_code="DOCX_RECONSTRUCTION_FAILED"
            )

    def _process_paragraph(self, paragraph, para_id) -> Dict[str, Any]:
        """Process individual paragraph and extract content"""
        text = paragraph.text.strip()
        
        if not text:
            return None
        
        # Determine if paragraph is translatable
        translatable = self._is_translatable_text(text)
        
        content_block = {
            'id': str(para_id),
            'text': text,
            'translatable': translatable,
            'location': 'body',
            'formatting': self._extract_paragraph_formatting(paragraph),
            'runs': self._extract_run_formatting(paragraph)
        }
        
        return content_block

    def _get_document_shapes(self, doc):
        """Extract shapes and text boxes from document"""
        shapes = []
        try:
            # Get shapes from document sections
            for section in doc.sections:
                # Access the underlying XML to find text boxes and shapes
                for element in section._sectPr.xpath('.//w:drawing'):
                    shapes.append(element)
        except Exception:
            pass  # If we can't access shapes, continue without them
        return shapes

    def _process_shape_text(self, shape, shape_idx):
        """Extract text from shapes and text boxes"""
        try:
            content_blocks = []
            # This is a simplified version - full implementation would need
            # more complex XML parsing to extract text from shapes
            # For now, we'll focus on improving paragraph and table processing
            return content_blocks
        except Exception:
            return []

    def _process_table(self, table, table_idx) -> Dict[str, Any]:
        """Process table structure and content"""
        table_data = {
            'index': table_idx,
            'rows': len(table.rows),
            'columns': len(table.columns) if table.rows else 0,
            'cells': []
        }
        
        for row_idx, row in enumerate(table.rows):
            row_data = []
            for cell_idx, cell in enumerate(row.cells):
                cell_text = cell.text.strip()
                cell_data = {
                    'text': cell_text,
                    'translatable': self._is_translatable_text(cell_text),
                    'row': row_idx,
                    'column': cell_idx
                }
                row_data.append(cell_data)
            table_data['cells'].append(row_data)
        
        return table_data

    def _extract_hyperlinks(self, paragraph) -> List[Dict[str, Any]]:
        """Extract hyperlinks from paragraph"""
        hyperlinks = []
        
        # Note: python-docx doesn't have direct hyperlink access
        # This is a simplified implementation
        if hasattr(paragraph, '_element'):
            for run in paragraph.runs:
                if hasattr(run, '_element'):
                    # Check for hyperlink relationships
                    # This would need more complex implementation for full hyperlink extraction
                    pass
        
        return hyperlinks

    def _extract_paragraph_formatting(self, paragraph) -> Dict[str, Any]:
        """Extract paragraph-level formatting"""
        formatting = {}
        
        if paragraph.style:
            formatting['style'] = paragraph.style.name
        
        if hasattr(paragraph, 'alignment') and paragraph.alignment:
            formatting['alignment'] = str(paragraph.alignment)
        
        return formatting

    def _extract_run_formatting(self, paragraph) -> List[Dict[str, Any]]:
        """Extract run-level formatting for each text run"""
        runs = []
        
        for run in paragraph.runs:
            run_data = {
                'text': run.text,
                'bold': run.bold,
                'italic': run.italic,
                'underline': run.underline,
                'font_size': run.font.size.pt if run.font.size else None,
                'font_name': run.font.name,
                'font_color': self._get_font_color(run)
            }
            runs.append(run_data)
        
        return runs

    def _get_font_color(self, run) -> str:
        """Extract font color from run"""
        try:
            if run.font.color and run.font.color.rgb:
                return str(run.font.color.rgb)
        except:
            pass
        return None

    def _is_translatable_text(self, text: str) -> bool:
        """Determine if text should be translated"""
        if not text or len(text.strip()) < 3:
            return False
        
        # Skip technical patterns
        import re
        technical_patterns = [
            r'^CVE-\d{4}-\d{4,7}$',
            r'^https?://',
            r'^\d+\.\d+[\.\d+]*$',
            r'^[A-Z_][A-Z0-9_]*$',  # Constants
            r'^\w+@\w+\.\w+$'  # Emails
        ]
        
        for pattern in technical_patterns:
            if re.match(pattern, text.strip(), re.IGNORECASE):
                return False
        
        return True

    def _deep_copy_document(self, original_doc):
        """Create a deep copy of the document for modification"""
        # Save original to buffer and reload
        buffer = io.BytesIO()
        original_doc.save(buffer)
        buffer.seek(0)
        return Document(buffer)

    def _apply_translations_to_paragraphs(self, doc, translations: Dict[str, str]):
        """Apply translations to document paragraphs"""
        for para_idx, paragraph in enumerate(doc.paragraphs):
            para_id = str(para_idx)
            if para_id in translations:
                # Replace paragraph text while preserving formatting
                self._replace_paragraph_text(paragraph, translations[para_id])

    def _apply_translations_to_tables(self, doc, translations: Dict[str, str]):
        """Apply translations to table cells"""
        for table_idx, table in enumerate(doc.tables):
            for row_idx, row in enumerate(table.rows):
                for cell_idx, cell in enumerate(row.cells):
                    for para_idx, paragraph in enumerate(cell.paragraphs):
                        key = f"table_{table_idx}_row_{row_idx}_cell_{cell_idx}_para_{para_idx}"
                        if key in translations:
                            self._replace_paragraph_text(paragraph, translations[key])

    def _replace_paragraph_text(self, paragraph, new_text: str):
        """Replace paragraph text while preserving formatting"""
        if not paragraph.runs:
            paragraph.text = new_text
            return
        
        # Store original formatting from all runs
        original_runs_formatting = []
        for run in paragraph.runs:
            original_runs_formatting.append({
                'bold': run.bold,
                'italic': run.italic,
                'underline': run.underline,
                'font_size': run.font.size,
                'font_name': run.font.name,
                'text': run.text
            })
        
        # Clear all runs but preserve paragraph
        for run in list(paragraph.runs):
            run._element.getparent().remove(run._element)
        
        # Add new text with preserved formatting from first run
        if original_runs_formatting:
            new_run = paragraph.add_run(new_text)
            first_run_format = original_runs_formatting[0]
            
            if first_run_format['bold'] is not None:
                new_run.bold = first_run_format['bold']
            if first_run_format['italic'] is not None:
                new_run.italic = first_run_format['italic']
            if first_run_format['underline'] is not None:
                new_run.underline = first_run_format['underline']
            if first_run_format['font_size']:
                new_run.font.size = first_run_format['font_size']
            if first_run_format['font_name']:
                new_run.font.name = first_run_format['font_name']
        else:
            paragraph.add_run(new_text)
        
        # Add new text with original formatting
        if original_run:
            new_run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
            new_run.text = new_text
            # Copy formatting from original run
            if original_run.bold is not None:
                new_run.bold = original_run.bold
            if original_run.italic is not None:
                new_run.italic = original_run.italic
            if original_run.underline is not None:
                new_run.underline = original_run.underline
            if original_run.font.size:
                new_run.font.size = original_run.font.size
            if original_run.font.name:
                new_run.font.name = original_run.font.name
        else:
            paragraph.add_run(new_text)

    def get_document_statistics(self, file_content: bytes) -> Dict[str, Any]:
        """Get detailed statistics about the document"""
        try:
            doc = Document(io.BytesIO(file_content))
            
            stats = {
                'total_paragraphs': len(doc.paragraphs),
                'total_tables': len(doc.tables),
                'total_sections': len(doc.sections),
                'total_pages': self._estimate_page_count(doc),
                'word_count': self._count_words(doc),
                'character_count': self._count_characters(doc)
            }
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}

    def _estimate_page_count(self, doc) -> int:
        """Estimate page count based on content"""
        # Simple estimation based on paragraph count
        paragraph_count = len(doc.paragraphs)
        table_count = len(doc.tables)
        return max(1, (paragraph_count + table_count * 5) // 30)

    def _count_words(self, doc) -> int:
        """Count total words in document"""
        total_words = 0
        for paragraph in doc.paragraphs:
            total_words += len(paragraph.text.split())
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    total_words += len(cell.text.split())
        
        return total_words

    def _count_characters(self, doc) -> int:
        """Count total characters in document"""
        total_chars = 0
        for paragraph in doc.paragraphs:
            total_chars += len(paragraph.text)
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    total_chars += len(cell.text)
        
        return total_chars