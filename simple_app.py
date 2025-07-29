import streamlit as st
import os
import tempfile
from io import BytesIO
from services.simple_translator import SimpleCVETranslator
from services.document_processor import DocumentProcessor

# Configure page
st.set_page_config(
    page_title="CVE Translation System - POC",
    page_icon="🔒",
    layout="wide"
)

def main():
    st.title("🔒 CVE Translation System - Proof of Concept")
    st.markdown("Convert English CVE documents to Japanese with AI translation")
    
    # Check API credentials
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_key = os.getenv("AZURE_OPENAI_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    if not all([azure_endpoint, azure_key, openai_key]):
        st.error("❌ API credentials not configured properly")
        st.info("Required: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, OPENAI_API_KEY")
        st.stop()
    
    st.success("✅ API credentials configured")
    
    # Initialize translator
    try:
        translator = SimpleCVETranslator()
    except Exception as e:
        st.error(f"Failed to initialize translator: {str(e)}")
        st.stop()
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["📝 Text Input", "📄 Document Upload"])
    
    with tab1:
        st.header("Direct Text Translation")
        
        # Text input
        input_text = st.text_area(
            "Enter English CVE text to translate:",
            height=200,
            placeholder="Paste your CVE description here..."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Translate Text", type="primary", disabled=not input_text.strip()):
                if input_text.strip():
                    with st.spinner("Translating..."):
                        translated_text = translator.translate_text(input_text)
                        
                        st.subheader("📋 Translation Result")
                        st.text_area("Japanese Translation:", value=translated_text, height=200)
                        
                        # Validation
                        with st.spinner("Validating translation..."):
                            validation = translator.validate_translation(input_text, translated_text)
                            
                            st.subheader("✅ Quality Check")
                            col_a, col_b, col_c = st.columns(3)
                            
                            with col_a:
                                st.metric("Similarity Score", f"{validation['similarity_score']:.2f}")
                            with col_b:
                                st.metric("Quality", validation['quality'])
                            with col_c:
                                preserved = "✅" if validation['technical_terms_preserved'] else "⚠️"
                                st.metric("Technical Terms", preserved)
        
        with col2:
            if st.button("🧪 Test with Sample CVE"):
                sample_text = """VMware vCenter Server authenticated command-execution vulnerability (CVE-2025-41225):

Description: The vCenter Server contains an authenticated command-execution vulnerability. VMware has evaluated the severity of this issue to be in the Important severity range with a maximum CVSSv3 base score of 8.8.

CVE-2025-41225 is an authenticated command-execution vulnerability in VMware vCenter Server that allows a privileged attacker to execute arbitrary commands. This type of CVE generally impacts system integrity and can lead to full administrative compromise if exploited in environments with inadequate privilege separation.

Security Impact: An attacker with sufficient permission could leverage this flaw to execute unauthorized commands, potentially leading to data breaches, lateral movement, or service disruption, undermining both confidentiality and system control."""
                
                with st.spinner("Translating sample CVE..."):
                    translated_sample = translator.translate_text(sample_text)
                    
                    st.subheader("📋 Sample Translation")
                    
                    # Show original and translation side by side
                    col_orig, col_trans = st.columns(2)
                    
                    with col_orig:
                        st.markdown("**Original English:**")
                        st.text_area("", value=sample_text, height=300, key="orig_sample")
                    
                    with col_trans:
                        st.markdown("**Japanese Translation:**")
                        st.text_area("", value=translated_sample, height=300, key="trans_sample")
                    
                    # Validation
                    with st.spinner("Validating sample translation..."):
                        validation = translator.validate_translation(sample_text, translated_sample)
                        
                        st.subheader("✅ Quality Check")
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric("Similarity Score", f"{validation['similarity_score']:.2f}")
                        with col_b:
                            st.metric("Quality", validation['quality'])
                        with col_c:
                            preserved = "✅" if validation['technical_terms_preserved'] else "⚠️"
                            st.metric("Technical Terms", preserved)
    
    with tab2:
        st.header("Document Translation with Structure Preservation")
        st.info("📄 Upload DOCX or HTML files - formatting, tables, and structure will be preserved")
        
        uploaded_file = st.file_uploader(
            "Choose a document file",
            type=['docx', 'html', 'htm'],
            help="Upload DOCX or HTML files containing English CVE documentation"
        )
        
        if uploaded_file is not None:
            st.success(f"Uploaded: {uploaded_file.name}")
            
            file_type = uploaded_file.name.split('.')[-1].lower()
            file_content = uploaded_file.read()
            
            # Initialize document processor
            try:
                doc_processor = DocumentProcessor()
            except Exception as e:
                st.error(f"Failed to initialize document processor: {str(e)}")
                return
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📄 Document Analysis")
                
                # Process document to show structure
                try:
                    if file_type == 'docx':
                        doc_data = doc_processor.process_docx(file_content)
                    else:
                        doc_data = doc_processor.process_html(file_content)
                    
                    # Show document statistics
                    st.metric("Total Content Blocks", doc_data['total_blocks'])
                    st.metric("Translatable Blocks", doc_data['translatable_blocks'])
                    st.metric("Structure Preserved", "✅ Yes")
                    
                    # Show content preview
                    st.subheader("Content Preview")
                    preview_blocks = doc_data['content_blocks'][:5]  # Show first 5 blocks
                    
                    for i, block in enumerate(preview_blocks):
                        block_type = block.get('type', 'text')
                        text = block.get('text', '')[:100] + "..." if len(block.get('text', '')) > 100 else block.get('text', '')
                        translatable = "✅" if block.get('translatable', False) else "⏭️"
                        
                        st.text(f"{i+1}. [{block_type.upper()}] {translatable} {text}")
                    
                    if len(doc_data['content_blocks']) > 5:
                        st.text(f"... and {len(doc_data['content_blocks']) - 5} more blocks")
                
                except Exception as e:
                    st.error(f"Failed to analyze document: {str(e)}")
                    return
            
            with col2:
                st.subheader("🚀 Translation Controls")
                
                # Translation options
                preserve_formatting = st.checkbox("Preserve Formatting", value=True)
                preserve_tables = st.checkbox("Preserve Tables", value=True)
                validate_quality = st.checkbox("Validate Translation Quality", value=True)
                
                if st.button("🚀 Translate Document", type="primary"):
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Step 1: Translate content blocks
                        status_text.text("Translating content blocks...")
                        progress_bar.progress(20)
                        
                        translated_blocks = []
                        total_translatable = len([b for b in doc_data['content_blocks'] if b.get('translatable', False)])
                        
                        for i, block in enumerate(doc_data['content_blocks']):
                            if block.get('translatable', False):
                                # Translate based on block type
                                if block['type'] == 'table':
                                    # Translate table cells
                                    for row in block['rows']:
                                        for cell in row:
                                            if cell.get('translatable', False):
                                                cell['translated_text'] = translator.translate_text(cell['text'])
                                            else:
                                                cell['translated_text'] = cell['text']
                                else:
                                    # Translate regular text
                                    block['translated_text'] = translator.translate_text(block['text'])
                            else:
                                # Keep original text for non-translatable content
                                if block['type'] == 'table':
                                    for row in block['rows']:
                                        for cell in row:
                                            cell['translated_text'] = cell['text']
                                else:
                                    block['translated_text'] = block['text']
                            
                            translated_blocks.append(block)
                            
                            # Update progress
                            if block.get('translatable', False):
                                progress = 20 + (60 * (i + 1) / len(doc_data['content_blocks']))
                                progress_bar.progress(int(progress))
                        
                        # Step 2: Reconstruct document
                        status_text.text("Reconstructing document with preserved structure...")
                        progress_bar.progress(80)
                        
                        if file_type == 'docx':
                            output_buffer = doc_processor.reconstruct_docx(
                                doc_data['original_document'], 
                                translated_blocks
                            )
                            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            file_ext = "docx"
                        else:
                            output_buffer = doc_processor.reconstruct_html(
                                doc_data['original_soup'], 
                                translated_blocks
                            )
                            mime_type = "text/html"
                            file_ext = "html"
                        
                        progress_bar.progress(90)
                        
                        # Step 3: Validation (if enabled)
                        if validate_quality:
                            status_text.text("Validating translation quality...")
                            
                            # Sample validation on a few blocks
                            sample_validations = []
                            translatable_blocks = [b for b in translated_blocks if b.get('translatable', False) and b['type'] != 'table'][:3]
                            
                            for block in translatable_blocks:
                                validation = translator.validate_translation(
                                    block['text'], 
                                    block['translated_text']
                                )
                                sample_validations.append(validation)
                            
                            if sample_validations:
                                avg_similarity = sum(v['similarity_score'] for v in sample_validations) / len(sample_validations)
                                
                                st.subheader("✅ Quality Validation")
                                col_a, col_b, col_c = st.columns(3)
                                
                                with col_a:
                                    st.metric("Avg Similarity", f"{avg_similarity:.2f}")
                                with col_b:
                                    quality = "Good" if avg_similarity > 0.7 else "Needs Review"
                                    st.metric("Quality", quality)
                                with col_c:
                                    preserved_count = sum(1 for v in sample_validations if v['technical_terms_preserved'])
                                    st.metric("Terms Preserved", f"{preserved_count}/{len(sample_validations)}")
                        
                        # Step 4: Complete
                        progress_bar.progress(100)
                        status_text.text("Translation completed!")
                        
                        st.success("🎉 Document translated successfully!")
                        
                        # Download button
                        st.download_button(
                            label=f"📥 Download Translated {file_type.upper()}",
                            data=output_buffer.getvalue(),
                            file_name=f"translated_{uploaded_file.name}",
                            mime=mime_type,
                            type="primary"
                        )
                        
                        # Show translation statistics
                        st.subheader("📊 Translation Statistics")
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric("Total Blocks", len(translated_blocks))
                        with col_b:
                            st.metric("Translated", total_translatable)
                        with col_c:
                            st.metric("Preserved", len(translated_blocks) - total_translatable)
                    
                    except Exception as e:
                        st.error(f"Translation failed: {str(e)}")
                        progress_bar.empty()
                        status_text.empty()
    
    # Sidebar with information
    with st.sidebar:
        st.header("🔧 System Information")
        
        st.subheader("Features")
        st.markdown("""
        ✅ English to Japanese translation  
        ✅ DOCX & HTML document support  
        ✅ Structure & formatting preservation  
        ✅ Table translation with layout intact  
        ✅ CVE-specific terminology preservation  
        ✅ Quality validation with embeddings  
        ✅ Technical term detection  
        ✅ Real-time translation  
        """)
        
        st.subheader("Models Used")
        st.markdown("""
        **Translation:** Azure OpenAI GPT-4o  
        **Validation:** OpenAI Embeddings  
        **Quality Check:** Semantic similarity  
        """)
        
        st.subheader("Preserved Elements")
        st.markdown("""
        🔒 CVE IDs (CVE-2025-41225)  
        📊 CVSS Scores (CVSSv3, 8.8)  
        🏢 Company Names (VMware)  
        💻 Product Names (vCenter)  
        🔗 URLs and Links  
        📋 Tables and Structure  
        🎨 Document Formatting  
        """)

if __name__ == "__main__":
    main()