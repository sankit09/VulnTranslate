import os
import tempfile
from typing import Dict, List, Any, Tuple
from io import BytesIO
import aspose.words as aw
from bs4 import BeautifulSoup
import re

class DocumentProcessor:
    """Process DOCX and HTML documents while preserving structure"""
    
    def __init__(self):
        self.technical_patterns = [
            r'CVE-\d{4}-\d{4,7}',
            r'VMSA-\d{4}-\d{4}',
            r'CVSS[v]?\d+(\.\d+)?',
            r'\d+\.\d+[\.\d+]*',
            r'VMware|Microsoft|Oracle|Adobe|Cisco',
            r'ESXi|vCenter|Workstation|Fusion',
            r'https?://[^\s]+',
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        ]
    
    def process_docx(self, file_content: bytes) -> Dict[str, Any]:
        """Process DOCX file and extract translatable content"""
        try:
            # Save uploaded content to temporary file
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            # Load document with Aspose.Words
            doc = aw.Document(temp_file_path)
            
            # Extract text blocks with structure information
            content_blocks = []
            
            # Process all paragraphs
            for section_idx in range(doc.sections.count):
                section = doc.sections[section_idx]
                
                # Process paragraphs in section
                for para_idx in range(section.body.paragraphs.count):
                    paragraph = section.body.paragraphs[para_idx]
                    text = paragraph.get_text().strip()
                    
                    if text and len(text) > 5:  # Skip very short text
                        # Determine if heading based on style
                        style_name = paragraph.paragraph_format.style_name if paragraph.paragraph_format.style else ""
                        is_heading = "heading" in style_name.lower() or paragraph.paragraph_format.outline_level > 0
                        
                        block = {
                            'type': 'heading' if is_heading else 'paragraph',
                            'text': text,
                            'position': {'section': section_idx, 'paragraph': para_idx},
                            'style': style_name,
                            'translatable': self._is_translatable(text),
                            'formatting': self._extract_paragraph_formatting(paragraph)
                        }
                        
                        if is_heading:
                            block['level'] = max(1, paragraph.paragraph_format.outline_level)
                        
                        content_blocks.append(block)
                
                # Process tables in section
                for table_idx in range(section.body.tables.count):
                    table = section.body.tables[table_idx]
                    table_block = self._process_table(table, section_idx, table_idx)
                    if table_block:
                        content_blocks.append(table_block)
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            return {
                'content_blocks': content_blocks,
                'document_type': 'docx',
                'original_document': doc,
                'total_blocks': len(content_blocks),
                'translatable_blocks': len([b for b in content_blocks if b.get('translatable', False)])
            }
            
        except Exception as e:
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            raise Exception(f"Failed to process DOCX: {str(e)}")
    
    def process_html(self, file_content: bytes) -> Dict[str, Any]:
        """Process HTML file and extract translatable content"""
        try:
            html_content = file_content.decode('utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            content_blocks = []
            block_idx = 0
            
            # Process body content
            if soup.body:
                elements = soup.body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'table', 'ul', 'ol'])
                
                for element in elements:
                    block = self._process_html_element(element, block_idx)
                    if block:
                        content_blocks.append(block)
                        block_idx += 1
            
            return {
                'content_blocks': content_blocks,
                'document_type': 'html',
                'original_soup': soup,
                'total_blocks': len(content_blocks),
                'translatable_blocks': len([b for b in content_blocks if b.get('translatable', False)])
            }
            
        except Exception as e:
            raise Exception(f"Failed to process HTML: {str(e)}")
    
    def reconstruct_docx(self, original_doc: aw.Document, translated_blocks: List[Dict[str, Any]]) -> BytesIO:
        """Reconstruct DOCX with translated content"""
        try:
            # Create new document
            new_doc = aw.Document()
            builder = aw.DocumentBuilder(new_doc)
            
            # Clear default content
            new_doc.first_section.body.remove_all_children()
            
            # Add translated content
            for block in translated_blocks:
                self._add_block_to_docx(builder, block)
            
            # Save to BytesIO
            output = BytesIO()
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                new_doc.save(temp_file.name, aw.SaveFormat.DOCX)
                
                with open(temp_file.name, 'rb') as f:
                    output.write(f.read())
                
                os.unlink(temp_file.name)
            
            output.seek(0)
            return output
            
        except Exception as e:
            raise Exception(f"Failed to reconstruct DOCX: {str(e)}")
    
    def reconstruct_html(self, original_soup: BeautifulSoup, translated_blocks: List[Dict[str, Any]]) -> BytesIO:
        """Reconstruct HTML with translated content"""
        try:
            # Create new soup based on original
            new_soup = BeautifulSoup(str(original_soup), 'html.parser')
            
            # Clear body and rebuild
            if new_soup.body:
                new_soup.body.clear()
            else:
                new_soup.html.append(new_soup.new_tag('body'))
            
            # Add translated content
            for block in translated_blocks:
                element = self._create_html_element(new_soup, block)
                if element and new_soup.body:
                    new_soup.body.append(element)
            
            # Convert to bytes
            html_content = str(new_soup).encode('utf-8')
            output = BytesIO(html_content)
            output.seek(0)
            
            return output
            
        except Exception as e:
            raise Exception(f"Failed to reconstruct HTML: {str(e)}")
    
    def _is_translatable(self, text: str) -> bool:
        """Check if text should be translated"""
        if len(text.strip()) < 5:
            return False
        
        # Check if mostly technical terms
        technical_chars = 0
        for pattern in self.technical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                technical_chars += len(match)
        
        tech_ratio = technical_chars / len(text) if text else 0
        return tech_ratio < 0.8  # Translate if less than 80% technical
    
    def _extract_paragraph_formatting(self, paragraph) -> Dict[str, Any]:
        """Extract formatting from paragraph"""
        formatting = {
            'style_name': '',
            'font_size': 12,
            'is_bold': False,
            'is_italic': False,
            'alignment': 'left'
        }
        
        try:
            if paragraph.paragraph_format.style:
                formatting['style_name'] = paragraph.paragraph_format.style_name
            
            if paragraph.runs and paragraph.runs.count > 0:
                first_run = paragraph.runs[0]
                if first_run.font:
                    formatting['font_size'] = first_run.font.size or 12
                    formatting['is_bold'] = first_run.font.bold or False
                    formatting['is_italic'] = first_run.font.italic or False
        except:
            pass
        
        return formatting
    
    def _process_table(self, table, section_idx: int, table_idx: int) -> Dict[str, Any]:
        """Process table content"""
        rows = []
        
        try:
            for row_idx in range(table.rows.count):
                row = table.rows[row_idx]
                cells = []
                
                for cell_idx in range(row.cells.count):
                    cell = row.cells[cell_idx]
                    cell_text = cell.get_text().strip()
                    
                    if cell_text:
                        cells.append({
                            'text': cell_text,
                            'translatable': self._is_translatable(cell_text),
                            'position': {'row': row_idx, 'cell': cell_idx}
                        })
                
                if cells:
                    rows.append(cells)
            
            if rows:
                return {
                    'type': 'table',
                    'rows': rows,
                    'position': {'section': section_idx, 'table': table_idx},
                    'translatable': True
                }
        except:
            pass
        
        return None
    
    def _process_html_element(self, element, block_idx: int) -> Dict[str, Any]:
        """Process HTML element"""
        tag_name = element.name
        text = element.get_text().strip()
        
        if not text and tag_name != 'table':
            return None
        
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return {
                'type': 'heading',
                'level': int(tag_name[1]),
                'text': text,
                'translatable': self._is_translatable(text),
                'position': {'block': block_idx},
                'html_tag': tag_name,
                'attributes': dict(element.attrs)
            }
        
        elif tag_name == 'table':
            return self._process_html_table(element, block_idx)
        
        elif tag_name in ['p', 'div']:
            return {
                'type': 'paragraph',
                'text': text,
                'translatable': self._is_translatable(text),
                'position': {'block': block_idx},
                'html_tag': tag_name,
                'attributes': dict(element.attrs)
            }
        
        return None
    
    def _process_html_table(self, table_element, block_idx: int) -> Dict[str, Any]:
        """Process HTML table"""
        rows = []
        
        for row_idx, row in enumerate(table_element.find_all('tr')):
            cells = []
            for cell_idx, cell in enumerate(row.find_all(['td', 'th'])):
                cell_text = cell.get_text().strip()
                if cell_text:
                    cells.append({
                        'text': cell_text,
                        'translatable': self._is_translatable(cell_text),
                        'is_header': cell.name == 'th',
                        'position': {'row': row_idx, 'cell': cell_idx}
                    })
            
            if cells:
                rows.append(cells)
        
        if rows:
            return {
                'type': 'table',
                'rows': rows,
                'position': {'block': block_idx},
                'translatable': True,
                'html_tag': 'table',
                'attributes': dict(table_element.attrs)
            }
        
        return None
    
    def _add_block_to_docx(self, builder: aw.DocumentBuilder, block: Dict[str, Any]):
        """Add block to DOCX document"""
        block_type = block.get('type', 'paragraph')
        text = block.get('translated_text', block.get('text', ''))
        
        if not text:
            return
        
        if block_type == 'heading':
            # Apply heading formatting
            level = block.get('level', 1)
            builder.font.bold = True
            builder.font.size = max(16 - level * 2, 10)
            builder.writeln(text)
            builder.font.bold = False
            builder.font.size = 12
        
        elif block_type == 'table':
            self._add_table_to_docx(builder, block)
        
        else:
            # Regular paragraph
            formatting = block.get('formatting', {})
            if formatting.get('is_bold'):
                builder.font.bold = True
            if formatting.get('is_italic'):
                builder.font.italic = True
            
            builder.writeln(text)
            
            # Reset formatting
            builder.font.bold = False
            builder.font.italic = False
    
    def _add_table_to_docx(self, builder: aw.DocumentBuilder, table_block: Dict[str, Any]):
        """Add table to DOCX"""
        rows = table_block.get('rows', [])
        if not rows:
            return
        
        # Start table
        builder.start_table()
        
        for row_data in rows:
            for cell_data in row_data:
                builder.insert_cell()
                cell_text = cell_data.get('translated_text', cell_data.get('text', ''))
                builder.write(cell_text)
            builder.end_row()
        
        builder.end_table()
    
    def _create_html_element(self, soup: BeautifulSoup, block: Dict[str, Any]):
        """Create HTML element from block"""
        block_type = block.get('type', 'paragraph')
        text = block.get('translated_text', block.get('text', ''))
        
        if not text:
            return None
        
        if block_type == 'heading':
            level = block.get('level', 1)
            tag = soup.new_tag(f'h{level}')
            tag.string = text
            
            # Restore original attributes
            attributes = block.get('attributes', {})
            for key, value in attributes.items():
                tag[key] = value
            
            return tag
        
        elif block_type == 'table':
            return self._create_html_table_element(soup, block)
        
        else:
            # Regular paragraph or div
            tag_name = block.get('html_tag', 'p')
            tag = soup.new_tag(tag_name)
            tag.string = text
            
            # Restore original attributes
            attributes = block.get('attributes', {})
            for key, value in attributes.items():
                tag[key] = value
            
            return tag
    
    def _create_html_table_element(self, soup: BeautifulSoup, table_block: Dict[str, Any]):
        """Create HTML table element"""
        table = soup.new_tag('table')
        tbody = soup.new_tag('tbody')
        
        # Restore original attributes
        attributes = table_block.get('attributes', {})
        for key, value in attributes.items():
            table[key] = value
        
        rows = table_block.get('rows', [])
        for row_data in rows:
            tr = soup.new_tag('tr')
            
            for cell_data in row_data:
                tag_name = 'th' if cell_data.get('is_header', False) else 'td'
                td = soup.new_tag(tag_name)
                cell_text = cell_data.get('translated_text', cell_data.get('text', ''))
                td.string = cell_text
                tr.append(td)
            
            tbody.append(tr)
        
        table.append(tbody)
        return table