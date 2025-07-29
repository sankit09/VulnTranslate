import os
import tempfile
from typing import Dict, List, Any
from io import BytesIO
import aspose.words as aw
from bs4 import BeautifulSoup

class DocumentReconstructor:
    """Reconstruct translated documents while preserving formatting"""
    
    def __init__(self):
        self.output_buffer = BytesIO()
    
    def reconstruct_document(self, 
                           original_document_data: Dict[str, Any],
                           translated_blocks: List[Dict[str, Any]],
                           preserve_formatting: bool = True,
                           preserve_hyperlinks: bool = True,
                           preserve_tables: bool = True) -> BytesIO:
        """Reconstruct document with translated content"""
        
        document_type = original_document_data.get('document_type', 'docx')
        
        if document_type == 'docx':
            return self._reconstruct_docx(
                original_document_data, 
                translated_blocks, 
                preserve_formatting, 
                preserve_hyperlinks, 
                preserve_tables
            )
        else:
            return self._reconstruct_html(
                original_document_data, 
                translated_blocks, 
                preserve_formatting, 
                preserve_hyperlinks, 
                preserve_tables
            )
    
    def _reconstruct_docx(self, 
                         original_data: Dict[str, Any],
                         translated_blocks: List[Dict[str, Any]],
                         preserve_formatting: bool,
                         preserve_hyperlinks: bool,
                         preserve_tables: bool) -> BytesIO:
        """Reconstruct DOCX document with translations"""
        
        try:
            # Create new document
            doc = aw.Document()
            builder = aw.DocumentBuilder(doc)
            
            # Clear existing content
            builder.document.first_section.body.remove_all_children()
            
            # Process translated blocks
            for block in translated_blocks:
                self._add_block_to_docx(doc, builder, block, preserve_formatting, preserve_hyperlinks)
            
            # Save to buffer
            output_buffer = BytesIO()
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                doc.save(temp_file.name, aw.SaveFormat.DOCX)
                
                # Read the saved file into buffer
                with open(temp_file.name, 'rb') as saved_file:
                    output_buffer.write(saved_file.read())
                
                # Clean up temp file
                os.unlink(temp_file.name)
            
            output_buffer.seek(0)
            return output_buffer
            
        except Exception as e:
            raise Exception(f"Failed to reconstruct DOCX document: {str(e)}")
    
    def _reconstruct_html(self, 
                         original_data: Dict[str, Any],
                         translated_blocks: List[Dict[str, Any]],
                         preserve_formatting: bool,
                         preserve_hyperlinks: bool,
                         preserve_tables: bool) -> BytesIO:
        """Reconstruct HTML document with translations"""
        
        try:
            # Get original soup or create new one
            soup = original_data.get('original_soup')
            if not soup:
                soup = BeautifulSoup('<html><head><title>Translated Document</title></head><body></body></html>', 'html.parser')
            
            # Clear body content and rebuild with translations
            if soup.body:
                soup.body.clear()
            else:
                if soup.html:
                    soup.html.append(soup.new_tag('body'))
                else:
                    body_tag = soup.new_tag('body')
                    soup.append(body_tag)
            
            # Process translated blocks
            for block in translated_blocks:
                element = self._create_html_element(soup, block, preserve_formatting, preserve_hyperlinks)
                if element and soup.body:
                    soup.body.append(element)
            
            # Convert to bytes
            html_content = str(soup).encode('utf-8')
            output_buffer = BytesIO(html_content)
            output_buffer.seek(0)
            
            return output_buffer
            
        except Exception as e:
            raise Exception(f"Failed to reconstruct HTML document: {str(e)}")
    
    def _add_block_to_docx(self, 
                          doc: aw.Document,
                          builder: aw.DocumentBuilder,
                          block: Dict[str, Any],
                          preserve_formatting: bool,
                          preserve_hyperlinks: bool):
        """Add a translated block to DOCX document"""
        
        block_type = block.get('type', '')
        translated_text = block.get('translated_text', block.get('text', ''))
        
        if block_type == 'heading':
            self._add_heading_to_docx(builder, block, translated_text, preserve_formatting)
        
        elif block_type == 'paragraph':
            self._add_paragraph_to_docx(builder, block, translated_text, preserve_formatting, preserve_hyperlinks)
        
        elif block_type == 'table':
            self._add_table_to_docx(builder, block, preserve_formatting)
        
        elif block_type == 'list':
            self._add_list_to_docx(builder, block, preserve_formatting)
        
        else:
            # Generic text block
            if translated_text:
                builder.writeln(translated_text)
    
    def _add_heading_to_docx(self, 
                            builder: aw.DocumentBuilder,
                            block: Dict[str, Any],
                            text: str,
                            preserve_formatting: bool):
        """Add heading to DOCX"""
        
        # Set heading style - simplified approach
        level = block.get('level', 1)
        
        # Apply basic heading formatting
        builder.font.bold = True
        builder.font.size = max(16 - level * 2, 10)  # Decrease size by level
        
        builder.writeln(text)
        
        # Reset formatting
        builder.font.bold = False
        builder.font.size = 12
    
    def _add_paragraph_to_docx(self, 
                              builder: aw.DocumentBuilder,
                              block: Dict[str, Any],
                              text: str,
                              preserve_formatting: bool,
                              preserve_hyperlinks: bool):
        """Add paragraph to DOCX"""
        
        # Apply formatting if preserving
        if preserve_formatting:
            formatting = block.get('formatting', {})
            self._apply_docx_formatting(builder, formatting)
        
        # Handle hyperlinks
        hyperlinks = block.get('hyperlinks', [])
        if preserve_hyperlinks and hyperlinks:
            # Simple implementation - add text with hyperlinks
            for link in hyperlinks:
                if 'url' in link:
                    translated_link_text = link.get('translated_text', link.get('text', ''))
                    builder.insert_hyperlink(translated_link_text, link['url'], False)
                    builder.write(" ")
        else:
            builder.writeln(text)
    
    def _add_table_to_docx(self, 
                          builder: aw.DocumentBuilder,
                          block: Dict[str, Any],
                          preserve_formatting: bool):
        """Add table to DOCX"""
        
        rows = block.get('rows', [])
        if not rows:
            return
        
        # Start table
        table = builder.start_table()
        
        for row_data in rows:
            for cell_data in row_data:
                builder.insert_cell()
                
                # Apply cell formatting if preserving
                if preserve_formatting:
                    cell_formatting = cell_data.get('formatting', {})
                    # Apply formatting (simplified implementation)
                
                # Insert translated text
                translated_text = cell_data.get('translated_text', cell_data.get('text', ''))
                builder.write(translated_text)
            
            builder.end_row()
        
        builder.end_table()
    
    def _add_list_to_docx(self, 
                         builder: aw.DocumentBuilder,
                         block: Dict[str, Any],
                         preserve_formatting: bool):
        """Add list to DOCX"""
        
        items = block.get('items', [])
        list_type = block.get('list_type', 'unordered')
        
        # Simplified list implementation
        for i, item in enumerate(items):
            translated_text = item.get('translated_text', item.get('text', ''))
            if list_type == 'ordered':
                builder.writeln(f"{i + 1}. {translated_text}")
            else:
                builder.writeln(f"• {translated_text}")
    
    def _apply_docx_formatting(self, builder: aw.DocumentBuilder, formatting: Dict[str, Any]):
        """Apply formatting to DOCX paragraph"""
        
        font = builder.font
        
        # Font properties
        if formatting.get('font_name'):
            font.name = formatting['font_name']
        
        if formatting.get('font_size'):
            font.size = formatting['font_size']
        
        if formatting.get('is_bold'):
            font.bold = True
        
        if formatting.get('is_italic'):
            font.italic = True
        
        if formatting.get('is_underline'):
            font.underline = aw.Underline.SINGLE
    
    def _create_html_element(self, 
                           soup: BeautifulSoup,
                           block: Dict[str, Any],
                           preserve_formatting: bool,
                           preserve_hyperlinks: bool):
        """Create HTML element from translated block"""
        
        block_type = block.get('type', '')
        translated_text = block.get('translated_text', block.get('text', ''))
        
        if block_type == 'heading':
            level = block.get('level', 1)
            tag = soup.new_tag(f'h{level}')
            tag.string = translated_text
            
            if preserve_formatting:
                self._apply_html_formatting(tag, block.get('formatting', {}))
            
            return tag
        
        elif block_type == 'paragraph':
            tag = soup.new_tag('p')
            
            # Handle hyperlinks
            hyperlinks = block.get('hyperlinks', [])
            if preserve_hyperlinks and hyperlinks:
                # Create paragraph with hyperlinks
                for link in hyperlinks:
                    link_tag = soup.new_tag('a', href=link.get('url', ''))
                    link_tag.string = link.get('translated_text', link.get('text', ''))
                    tag.append(link_tag)
                    tag.append(' ')
            else:
                tag.string = translated_text
            
            if preserve_formatting:
                self._apply_html_formatting(tag, block.get('formatting', {}))
            
            return tag
        
        elif block_type == 'table':
            return self._create_html_table(soup, block, preserve_formatting)
        
        elif block_type == 'list':
            return self._create_html_list(soup, block, preserve_formatting)
        
        else:
            # Generic div
            tag = soup.new_tag('div')
            tag.string = translated_text
            return tag
    
    def _create_html_table(self, soup: BeautifulSoup, block: Dict[str, Any], preserve_formatting: bool):
        """Create HTML table element"""
        
        table = soup.new_tag('table')
        tbody = soup.new_tag('tbody')
        
        rows = block.get('rows', [])
        for row_data in rows:
            tr = soup.new_tag('tr')
            
            for cell_data in row_data:
                # Use th for headers, td for regular cells
                cell_tag_name = 'th' if cell_data.get('is_header', False) else 'td'
                td = soup.new_tag(cell_tag_name)
                
                translated_text = cell_data.get('translated_text', cell_data.get('text', ''))
                td.string = translated_text
                
                if preserve_formatting:
                    self._apply_html_formatting(td, cell_data.get('formatting', {}))
                
                tr.append(td)
            
            tbody.append(tr)
        
        table.append(tbody)
        
        if preserve_formatting:
            self._apply_html_formatting(table, block.get('table_formatting', {}))
        
        return table
    
    def _create_html_list(self, soup: BeautifulSoup, block: Dict[str, Any], preserve_formatting: bool):
        """Create HTML list element"""
        
        list_type = block.get('list_type', 'unordered')
        list_tag = soup.new_tag('ol' if list_type == 'ordered' else 'ul')
        
        items = block.get('items', [])
        for item in items:
            li = soup.new_tag('li')
            translated_text = item.get('translated_text', item.get('text', ''))
            li.string = translated_text
            
            if preserve_formatting:
                self._apply_html_formatting(li, item.get('formatting', {}))
            
            list_tag.append(li)
        
        return list_tag
    
    def _apply_html_formatting(self, tag, formatting: Dict[str, Any]):
        """Apply CSS formatting to HTML element"""
        
        styles = []
        
        # Font properties
        if formatting.get('font_weight') and formatting['font_weight'] != 'normal':
            styles.append(f"font-weight: {formatting['font_weight']}")
        
        if formatting.get('font_style') and formatting['font_style'] != 'normal':
            styles.append(f"font-style: {formatting['font_style']}")
        
        if formatting.get('text_decoration') and formatting['text_decoration'] != 'none':
            styles.append(f"text-decoration: {formatting['text_decoration']}")
        
        if formatting.get('color'):
            styles.append(f"color: {formatting['color']}")
        
        if formatting.get('background_color'):
            styles.append(f"background-color: {formatting['background_color']}")
        
        # Apply existing CSS styles
        existing_style = formatting.get('css_style', '')
        if existing_style:
            styles.append(existing_style)
        
        # Set combined styles
        if styles:
            tag['style'] = '; '.join(styles)
        
        # Apply CSS classes
        css_classes = formatting.get('css_classes', [])
        if css_classes:
            tag['class'] = css_classes
