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
            
            # Process ALL document paragraphs (excluding first page content)
            for para_idx, paragraph in enumerate(doc.paragraphs):
                # Skip first page content - only translate from page 2 onwards
                if self._is_first_page_content(paragraph, para_idx):
                    continue
                    
                content_block = self._process_paragraph(paragraph, para_idx)
                # Include paragraphs from page 2 onwards, even empty ones, to maintain structure
                if content_block is not None:
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
                
                # Add table cell content to content blocks (skip first page tables)
                for row_idx, row in enumerate(table.rows):
                    for cell_idx, cell in enumerate(row.cells):
                        for para_idx, paragraph in enumerate(cell.paragraphs):
                            # Skip tables that are part of the first page
                            if table_idx == 0 and self._is_first_page_content(paragraph, 0):
                                continue
                                
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
        """Reconstruct DOCX document with translated content and Japanese first page"""
        try:
            original_doc = content.get('original_document')
            if not original_doc:
                raise ProcessingError("Original document not found in content")
            
            # Create a copy of the document for modification
            doc_copy = self._deep_copy_document(original_doc)
            
            # Replace first page with Japanese template
            self._replace_first_page_with_japanese_template(doc_copy)
            
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
        """Process individual paragraph and extract content - INCLUDE ALL paragraphs"""
        text = paragraph.text.strip()
        
        # CRITICAL: Include ALL paragraphs for complete document coverage
        # Empty paragraphs maintain document structure and spacing
        
        # Determine if paragraph is translatable (even empty ones need processing)
        translatable = self._is_translatable_text(text) if text else False
        
        content_block = {
            'id': str(para_id),
            'text': text if text else '',  # Include empty paragraphs
            'translatable': translatable,
            'location': 'body',
            'formatting': self._extract_paragraph_formatting(paragraph),
            'runs': self._extract_run_formatting(paragraph),
            'is_empty': not bool(text),  # Track empty paragraphs for reconstruction
            'structure_important': True  # All paragraphs maintain document structure
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

    def _get_static_translations(self) -> Dict[str, str]:
        """Static translations for recurring first-page content"""
        return {
            "Attack Surface": "攻撃対象領域",
            "Advanced Vulnerability Management": "高度脆弱性管理",
            "Advanced Vulnerability Management (AVM)": "高度脆弱性管理（AVM）",
            "Cyber Security Advisory": "サイバーセキュリティアドバイザリ",
            "vulnerability management": "脆弱性管理",
            "threat actors": "脅威アクター",
            "Risk-Based Approach": "リスクベースアプローチ",
            "Asset Value": "資産価値",
            "Severity of Vulnerabilities": "脆弱性の深刻度",
            "Threat Actors": "脅威アクター",
            "Vulnerability Management System": "脆弱性管理システム",
            "proactive and predictive approach": "予防的で予測的なアプローチ",
            "sophisticated threat actors": "高度な脅威アクター",
            "embrace of risk-based methodologies": "リスクベース手法の採用",
            "utilization of advanced threat intelligence": "高度な脅威インテリジェンスの活用",
            "alignment with the broader security architecture": "より広範なセキュリティアーキテクチャとの整合",
            "Contemporary vulnerability management": "現代的な脆弱性管理",
            "organization's distinct threat environment": "組織の独特な脅威環境",
            "customize remediation strategies accordingly": "対応する修復戦略のカスタマイズ"
        }

    def _apply_static_translation(self, text: str) -> str:
        """Apply static translations to known recurring content"""
        static_translations = self._get_static_translations()
        
        # Check for exact matches first
        if text.strip() in static_translations:
            return static_translations[text.strip()]
        
        # Check for partial matches in longer sentences
        translated_text = text
        for english, japanese in static_translations.items():
            if english.lower() in text.lower():
                translated_text = translated_text.replace(english, japanese)
        
        return translated_text

    def _is_first_page_content(self, paragraph, para_idx: int) -> bool:
        """Determine if paragraph is part of the first page that should be skipped"""
        # Skip the first 15-20 paragraphs which typically contain the first page content
        # This includes the header image, title, and main text box content
        if para_idx < 20:
            return True
        
        # Also check for specific first-page indicators in the text
        text = paragraph.text.strip().lower()
        first_page_indicators = [
            "cyber security advisory",
            "attack surface",
            "advanced vulnerability management",
            "proactive and predictive approach",
            "risk-based approach",
            "contemporary vulnerability management"
        ]
        
        for indicator in first_page_indicators:
            if indicator in text:
                return True
        
        return False

    def _replace_first_page_with_japanese_template(self, doc):
        """Replace the first page content with pre-translated Japanese template"""
        try:
            # First, insert Japanese content at the beginning
            self._insert_japanese_first_page_content(doc)
            
            # Then remove original first page content (now pushed down)
            paragraphs_to_remove = []
            
            # Start checking from paragraph 3 onwards (after our inserted Japanese content)
            for i, paragraph in enumerate(doc.paragraphs[3:], start=3):
                text = paragraph.text.strip().lower()
                
                # Check if this is original first page content that needs removal
                if ("attack surface" in text or
                    "cyber security advisory" in text or
                    "vulnerability management" in text or
                    "advanced vulnerability management" in text or
                    "avm" in text or
                    "risk-based approach" in text or
                    "threat actors" in text or
                    "proactive" in text or
                    "predictive approach" in text or
                    "transformation calls" in text or
                    "contemporary vulnerability" in text):
                    paragraphs_to_remove.append(paragraph)
                else:
                    # Stop when we reach actual CVE content
                    if ("cve-" in text or "vmware" in text or "vmsa-" in text) and i > 5:
                        break
            
            # Remove identified original first page paragraphs
            for paragraph in paragraphs_to_remove:
                try:
                    p = paragraph._element
                    p.getparent().remove(p)
                except Exception:
                    pass  # Continue if removal fails
            
        except Exception as e:
            print(f"Warning: Could not replace first page: {e}")
    
    def _insert_japanese_first_page_content(self, doc):
        """Insert the Japanese first page content at the document start"""
        try:
            # Use simple paragraph insertion at the beginning for more reliable placement
            # Create a new paragraph at the start of the document
            body = doc._element.body
            
            # Create paragraphs in reverse order for insertion at the beginning
            paragraphs_to_add = []
            
            # Main content paragraph
            main_text = """アタックサーフェスが拡大し、より洗練された脅威アクターが台頭する中、脆弱性管理はリアクティブな姿勢からプロアクティブで予測的なアプローチへと変化している。この変革には、リスクベースの手法の採用、高度な脅威インテリジェンスの活用、より広範なセキュリティアーキテクチャとの連携が必要です。現代の脆弱性管理は、組織特有の脅威環境を考慮に入れ、それに応じて修復戦略をカスタマイズする必要があります。

そこで、当社のプロアクティブな高度脆弱性管理（AVM）サービスが登場し、リスクベースのアプローチ、資産価値、脆弱性の深刻度、脅威環境に基づく堅牢な脆弱性管理システムの構築を支援します。"""
            
            # Add using Document methods for better compatibility
            # Insert header first
            header_para = doc.add_paragraph("サイバーセキュリティアドバイザリ")
            
            # Add spacing
            spacing_para = doc.add_paragraph()
            
            # Add main content
            content_para = doc.add_paragraph(main_text)
            
            # Move these paragraphs to the beginning by manipulating the XML
            body_element = doc._element.body
            
            # Remove the paragraphs from their current position
            header_element = header_para._element
            spacing_element = spacing_para._element
            content_element = content_para._element
            
            # Remove from current position
            header_element.getparent().remove(header_element)
            spacing_element.getparent().remove(spacing_element)
            content_element.getparent().remove(content_element)
            
            # Insert at the beginning
            if len(body_element) > 0:
                body_element.insert(0, header_element)
                body_element.insert(1, spacing_element)
                body_element.insert(2, content_element)
            else:
                body_element.append(header_element)
                body_element.append(spacing_element)
                body_element.append(content_element)
                
        except Exception as e:
            print(f"Warning: Could not insert Japanese content with XML manipulation: {e}")
            # Simple fallback - just add at the end and hope for the best
            try:
                doc.add_paragraph("サイバーセキュリティアドバイザリ")
                doc.add_paragraph()
                doc.add_paragraph("""アタックサーフェスが拡大し、より洗練された脅威アクターが台頭する中、脆弱性管理はリアクティブな姿勢からプロアクティブで予測的なアプローチへと変化している。この変革には、リスクベースの手法の採用、高度な脅威インテリジェンスの活用、より広範なセキュリティアーキテクチャとの連携が必要です。現代の脆弱性管理は、組織特有の脅威環境を考慮に入れ、それに応じて修復戦略をカスタマイズする必要があります。

そこで、当社のプロアクティブな高度脆弱性管理（AVM）サービスが登場し、リスクベースのアプローチ、資産価値、脆弱性の深刻度、脅威環境に基づく堅牢な脆弱性管理システムの構築を支援します。""")
            except Exception:
                pass

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
        """Apply translations to document paragraphs with structured reconstruction"""
        for para_idx, paragraph in enumerate(doc.paragraphs):
            para_id = str(para_idx)
            
            # Apply translation if available (including empty strings for empty paragraphs)
            if para_id in translations:
                translated_text = translations[para_id]
                try:
                    # Use enhanced text replacement that preserves formatting
                    self._replace_paragraph_text(paragraph, translated_text)
                except Exception as e:
                    # Fallback to simple text replacement
                    if translated_text:  # Only set non-empty translations
                        paragraph.text = translated_text
            else:
                # Check for static translations for untranslated paragraphs
                original_text = paragraph.text.strip()
                if original_text and len(original_text) > 0:
                    static_translation = self._apply_static_translation(original_text)
                    if static_translation != original_text:
                        try:
                            self._replace_paragraph_text(paragraph, static_translation)
                        except Exception:
                            paragraph.text = static_translation
            
            # Maintain document structure even for untranslated paragraphs

    def _apply_translations_to_tables(self, doc, translations: Dict[str, str]):
        """Apply translations to table cells"""
        for table_idx, table in enumerate(doc.tables):
            for row_idx, row in enumerate(table.rows):
                for cell_idx, cell in enumerate(row.cells):
                    for para_idx, paragraph in enumerate(cell.paragraphs):
                        key = f"table_{table_idx}_row_{row_idx}_cell_{cell_idx}_para_{para_idx}"
                        if key in translations:
                            try:
                                self._replace_paragraph_text(paragraph, translations[key])
                            except Exception as e:
                                # Fallback to simple text replacement
                                paragraph.text = translations[key]
                        else:
                            # Apply static translations to untranslated table content
                            original_text = paragraph.text.strip()
                            if original_text and len(original_text) > 0:
                                static_translation = self._apply_static_translation(original_text)
                                if static_translation != original_text:
                                    try:
                                        self._replace_paragraph_text(paragraph, static_translation)
                                    except Exception:
                                        paragraph.text = static_translation

    def _replace_paragraph_text(self, paragraph, new_text: str):
        """Replace paragraph text while preserving formatting"""
        if not paragraph.runs:
            paragraph.text = new_text
            return
        
        # Store original formatting from the first meaningful run
        original_formatting = None
        for run in paragraph.runs:
            if run.text.strip():  # Only use non-empty runs for formatting
                original_formatting = {
                    'bold': run.bold,
                    'italic': run.italic,
                    'underline': run.underline,
                    'font_size': run.font.size,
                    'font_name': run.font.name,
                    'font_color': run.font.color.rgb if run.font.color.rgb else None
                }
                break
        
        # Simple and reliable approach: clear and rebuild
        paragraph.clear()
        
        # Add new text with preserved formatting
        new_run = paragraph.add_run(new_text)
        
        if original_formatting:
            try:
                # Apply preserved formatting to new run
                if original_formatting['bold'] is not None:
                    new_run.bold = original_formatting['bold']
                if original_formatting['italic'] is not None:
                    new_run.italic = original_formatting['italic']
                if original_formatting['underline'] is not None:
                    new_run.underline = original_formatting['underline']
                if original_formatting['font_size']:
                    new_run.font.size = original_formatting['font_size']
                if original_formatting['font_name']:
                    new_run.font.name = original_formatting['font_name']
                if original_formatting['font_color']:
                    new_run.font.color.rgb = original_formatting['font_color']
            except Exception:
                # If any formatting application fails, continue with plain text
                pass

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