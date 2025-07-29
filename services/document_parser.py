import os
import tempfile
from typing import Dict, List, Any
import aspose.words as aw
from bs4 import BeautifulSoup
import json

class DocumentParser:
    """Parse DOCX and HTML documents while preserving structure"""
    
    def __init__(self):
        self.content_blocks = []
        self.formatting_metadata = {}
    
    def parse_docx(self, file_path: str) -> Dict[str, Any]:
        """Parse DOCX document using Aspose.Words"""
        try:
            # Load document
            doc = aw.Document(file_path)
            
            # Extract document metadata
            metadata = {
                'title': doc.built_in_document_properties.title,
                'author': doc.built_in_document_properties.author,
                'subject': doc.built_in_document_properties.subject,
                'creation_time': doc.built_in_document_properties.creation_time,
                'last_save_time': doc.built_in_document_properties.last_save_time
            }
            
            # Extract content blocks
            content_blocks = []
            formatting_info = []
            
            # Process sections
            sections = [doc.sections[i] for i in range(doc.sections.count)]
            for section_idx, section in enumerate(sections):
                section_info = {
                    'type': 'section',
                    'index': section_idx,
                    'page_setup': {
                        'width': section.page_setup.page_width,
                        'height': section.page_setup.page_height,
                        'margins': {
                            'top': section.page_setup.top_margin,
                            'bottom': section.page_setup.bottom_margin,
                            'left': section.page_setup.left_margin,
                            'right': section.page_setup.right_margin
                        }
                    }
                }
                formatting_info.append(section_info)
                
                # Process paragraphs
                paragraphs = [section.body.paragraphs[i] for i in range(section.body.paragraphs.count)]
                for para_idx, paragraph in enumerate(paragraphs):
                    block = self._extract_paragraph_block(paragraph, section_idx, para_idx)
                    if block:
                        content_blocks.append(block)
                
                # Process tables
                tables = [section.body.tables[i] for i in range(section.body.tables.count)]
                for table_idx, table in enumerate(tables):
                    table_block = self._extract_table_block(table, section_idx, table_idx)
                    if table_block:
                        content_blocks.append(table_block)
            
            return {
                'metadata': metadata,
                'content_blocks': content_blocks,
                'formatting_info': formatting_info,
                'document_type': 'docx',
                'original_document': doc  # Keep reference for reconstruction
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse DOCX document: {str(e)}")
    
    def parse_html(self, file_path: str) -> Dict[str, Any]:
        """Parse HTML document while preserving structure"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract metadata
            metadata = {
                'title': soup.title.string if soup.title else '',
                'description': '',
                'keywords': ''
            }
            
            # Extract meta tags
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                if hasattr(meta, 'get'):
                    if meta.get('name') == 'description':
                        metadata['description'] = meta.get('content', '')
                    elif meta.get('name') == 'keywords':
                        metadata['keywords'] = meta.get('content', '')
            
            # Extract content blocks
            content_blocks = []
            formatting_info = []
            
            # Process body content
            if soup.body:
                block_idx = 0
                for element in soup.body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'table', 'ul', 'ol']):
                    block = self._extract_html_block(element, block_idx)
                    if block:
                        content_blocks.append(block)
                        block_idx += 1
            
            return {
                'metadata': metadata,
                'content_blocks': content_blocks,
                'formatting_info': formatting_info,
                'document_type': 'html',
                'original_soup': soup  # Keep reference for reconstruction
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse HTML document: {str(e)}")
    
    def _extract_paragraph_block(self, paragraph, section_idx: int, para_idx: int) -> Dict[str, Any]:
        """Extract paragraph content and formatting"""
        text = paragraph.get_text().strip()
        if not text:
            return {}
        
        # Extract formatting information
        formatting = {
            'font_name': '',
            'font_size': 0,
            'is_bold': False,
            'is_italic': False,
            'is_underline': False,
            'alignment': '',
            'style_name': paragraph.paragraph_format.style_name if paragraph.paragraph_format.style else ''
        }
        
        # Get formatting from first run if available
        if paragraph.runs and len(paragraph.runs) > 0:
            first_run = paragraph.runs[0]
            if first_run.font:
                formatting['font_name'] = first_run.font.name or ''
                formatting['font_size'] = first_run.font.size or 0
                formatting['is_bold'] = first_run.font.bold or False
                formatting['is_italic'] = first_run.font.italic or False
                formatting['is_underline'] = first_run.font.underline != aw.Underline.NONE
        
        # Extract hyperlinks (simplified implementation)
        hyperlinks = []
        # Note: Hyperlink extraction in Aspose.Words requires more complex field parsing
        # For now, we'll detect URLs in text using regex patterns
        
        return {
            'type': 'paragraph',
            'text': text,
            'formatting': formatting,
            'hyperlinks': hyperlinks,
            'position': {
                'section': section_idx,
                'paragraph': para_idx
            }
        }
    
    def _extract_table_block(self, table, section_idx: int, table_idx: int) -> Dict[str, Any]:
        """Extract table content and structure"""
        rows = []
        
        table_rows = [table.rows[i] for i in range(table.rows.count)]
        for row_idx, row in enumerate(table_rows):
            cells = []
            row_cells = [row.cells[i] for i in range(row.cells.count)]
            for cell_idx, cell in enumerate(row_cells):
                cell_text = cell.get_text().strip()
                cell_formatting = {
                    'background_color': '',
                    'border_style': '',
                    'alignment': ''
                }
                
                cells.append({
                    'text': cell_text,
                    'formatting': cell_formatting,
                    'position': {'row': row_idx, 'cell': cell_idx}
                })
            
            if cells:  # Only add non-empty rows
                rows.append(cells)
        
        if not rows:
            return {}
        
        return {
            'type': 'table',
            'rows': rows,
            'position': {
                'section': section_idx,
                'table': table_idx
            },
            'table_formatting': {
                'border_style': '',
                'width': '',
                'alignment': ''
            }
        }
    
    def _extract_html_block(self, element, block_idx: int) -> Dict[str, Any]:
        """Extract HTML element content and formatting"""
        tag_name = element.name
        text = element.get_text().strip()
        
        if not text and tag_name != 'table':
            return {}
        
        # Handle different element types
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return self._extract_html_heading(element, block_idx)
        elif tag_name == 'p':
            return self._extract_html_paragraph(element, block_idx)
        elif tag_name == 'table':
            return self._extract_html_table(element, block_idx)
        elif tag_name in ['ul', 'ol']:
            return self._extract_html_list(element, block_idx)
        elif tag_name == 'div':
            return self._extract_html_div(element, block_idx)
        
        return {}
    
    def _extract_html_heading(self, element, block_idx: int) -> Dict[str, Any]:
        """Extract HTML heading"""
        return {
            'type': 'heading',
            'level': int(element.name[1]),  # h1 -> 1, h2 -> 2, etc.
            'text': element.get_text().strip(),
            'formatting': self._get_html_formatting(element),
            'position': {'block': block_idx}
        }
    
    def _extract_html_paragraph(self, element, block_idx: int) -> Dict[str, Any]:
        """Extract HTML paragraph"""
        hyperlinks = []
        for link in element.find_all('a'):
            hyperlinks.append({
                'text': link.get_text().strip(),
                'url': link.get('href', '')
            })
        
        return {
            'type': 'paragraph',
            'text': element.get_text().strip(),
            'formatting': self._get_html_formatting(element),
            'hyperlinks': hyperlinks,
            'position': {'block': block_idx}
        }
    
    def _extract_html_table(self, element, block_idx: int) -> Dict[str, Any]:
        """Extract HTML table"""
        rows = []
        
        for row_idx, row in enumerate(element.find_all('tr')):
            cells = []
            for cell_idx, cell in enumerate(row.find_all(['td', 'th'])):
                cells.append({
                    'text': cell.get_text().strip(),
                    'formatting': self._get_html_formatting(cell),
                    'is_header': cell.name == 'th',
                    'position': {'row': row_idx, 'cell': cell_idx}
                })
            
            if cells:
                rows.append(cells)
        
        return {
            'type': 'table',
            'rows': rows,
            'position': {'block': block_idx},
            'table_formatting': self._get_html_formatting(element)
        }
    
    def _extract_html_list(self, element, block_idx: int) -> Dict[str, Any]:
        """Extract HTML list"""
        items = []
        for item in element.find_all('li'):
            items.append({
                'text': item.get_text().strip(),
                'formatting': self._get_html_formatting(item)
            })
        
        return {
            'type': 'list',
            'list_type': 'ordered' if element.name == 'ol' else 'unordered',
            'items': items,
            'position': {'block': block_idx}
        }
    
    def _extract_html_div(self, element, block_idx: int) -> Dict[str, Any]:
        """Extract HTML div"""
        return {
            'type': 'div',
            'text': element.get_text().strip(),
            'formatting': self._get_html_formatting(element),
            'position': {'block': block_idx}
        }
    
    def _get_html_formatting(self, element) -> Dict[str, Any]:
        """Extract CSS styling information from HTML element"""
        style = element.get('style', '')
        classes = element.get('class', [])
        
        formatting = {
            'css_style': style,
            'css_classes': classes if isinstance(classes, list) else [classes],
            'font_weight': 'normal',
            'font_style': 'normal',
            'text_decoration': 'none',
            'color': '',
            'background_color': ''
        }
        
        # Parse inline styles
        if style:
            style_pairs = [s.strip() for s in style.split(';') if s.strip()]
            for pair in style_pairs:
                if ':' in pair:
                    prop, value = pair.split(':', 1)
                    prop = prop.strip().lower()
                    value = value.strip()
                    
                    if prop == 'font-weight':
                        formatting['font_weight'] = value
                    elif prop == 'font-style':
                        formatting['font_style'] = value
                    elif prop == 'text-decoration':
                        formatting['text_decoration'] = value
                    elif prop == 'color':
                        formatting['color'] = value
                    elif prop == 'background-color':
                        formatting['background_color'] = value
        
        return formatting
