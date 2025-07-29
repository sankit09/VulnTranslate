import streamlit as st
import os
import tempfile
import json
from io import BytesIO
from services.document_parser import DocumentParser
from services.translator import CVETranslator
from services.validator import TranslationValidator
from services.document_reconstructor import DocumentReconstructor
from utils.text_processor import TextProcessor

# Configure page
st.set_page_config(
    page_title="CVE Translation System",
    page_icon="🔒",
    layout="wide"
)

def main():
    st.title("🔒 AI-Powered CVE Translation System")
    st.markdown("Convert English CVE documents to Japanese while preserving formatting")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Configuration check
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        azure_key = os.getenv("AZURE_OPENAI_KEY", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        
        if not azure_endpoint or not azure_key:
            st.error("Azure OpenAI credentials not configured")
            st.stop()
        
        if not openai_key:
            st.error("OpenAI API key not configured for embeddings")
            st.stop()
        
        st.success("✅ API credentials configured")
        
        # Translation settings
        st.subheader("Translation Settings")
        preserve_technical_terms = st.checkbox("Preserve CVE IDs & Version Numbers", value=True)
        preserve_hyperlinks = st.checkbox("Preserve Hyperlinks", value=True)
        preserve_tables = st.checkbox("Preserve Table Formatting", value=True)
        
        # Validation settings
        st.subheader("Validation Settings")
        enable_validation = st.checkbox("Enable Translation Validation", value=True)
        validation_threshold = st.slider("Quality Threshold", 0.0, 1.0, 0.7, 0.1)

    # Main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['docx', 'html'],
            help="Upload English CVE documents in DOCX or HTML format"
        )
        
        if uploaded_file is not None:
            st.success(f"Uploaded: {uploaded_file.name}")
            file_type = uploaded_file.name.split('.')[-1].lower()
            
            if st.button("🚀 Start Translation", type="primary"):
                translate_document(
                    uploaded_file, 
                    file_type,
                    preserve_technical_terms,
                    preserve_hyperlinks,
                    preserve_tables,
                    enable_validation,
                    validation_threshold
                )
    
    with col2:
        st.header("📊 Translation Status")
        if 'translation_status' not in st.session_state:
            st.info("Upload a document to begin translation")
        else:
            display_translation_status()

def translate_document(uploaded_file, file_type, preserve_technical, preserve_links, preserve_tables, validate, threshold):
    """Main translation workflow"""
    
    # Initialize progress tracking
    st.session_state.translation_status = {
        'stage': 'starting',
        'progress': 0,
        'details': [],
        'errors': []
    }
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Stage 1: Parse document
        update_progress(progress_bar, status_text, 10, "Parsing document...")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type}') as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name
        
        parser = DocumentParser()
        if file_type == 'docx':
            document_data = parser.parse_docx(tmp_file_path)
        else:
            document_data = parser.parse_html(tmp_file_path)
        
        st.session_state.translation_status['details'].append(f"Parsed {len(document_data.get('content_blocks', []))} content blocks")
        
        # Stage 2: Process and filter text
        update_progress(progress_bar, status_text, 20, "Processing text content...")
        
        processor = TextProcessor()
        processed_content = processor.prepare_for_translation(
            document_data['content_blocks'],
            preserve_technical_terms=preserve_technical
        )
        
        # Stage 3: Translate content
        update_progress(progress_bar, status_text, 30, "Translating content...")
        
        translator = CVETranslator()
        translated_blocks = []
        
        total_blocks = len(processed_content)
        for i, block in enumerate(processed_content):
            if block['translatable']:
                translated_text = translator.translate_text(block['text'])
                block['translated_text'] = translated_text
            else:
                block['translated_text'] = block['text']  # Keep original
            
            translated_blocks.append(block)
            
            # Update progress
            progress = 30 + (50 * (i + 1) / total_blocks)
            update_progress(progress_bar, status_text, progress, f"Translated {i+1}/{total_blocks} blocks")
        
        # Stage 4: Validate translations (if enabled)
        if validate:
            update_progress(progress_bar, status_text, 80, "Validating translations...")
            
            validator = TranslationValidator()
            validation_results = validator.validate_translations(
                [(block['text'], block['translated_text']) for block in translated_blocks if block['translatable']],
                threshold
            )
            
            st.session_state.translation_status['validation'] = validation_results
        
        # Stage 5: Reconstruct document
        update_progress(progress_bar, status_text, 90, "Reconstructing document...")
        
        reconstructor = DocumentReconstructor()
        output_buffer = reconstructor.reconstruct_document(
            document_data,
            translated_blocks,
            preserve_formatting=True,
            preserve_hyperlinks=preserve_links,
            preserve_tables=preserve_tables
        )
        
        # Stage 6: Complete
        update_progress(progress_bar, status_text, 100, "Translation complete!")
        
        # Store results
        st.session_state.translation_status.update({
            'stage': 'complete',
            'output_file': output_buffer,
            'filename': f"translated_{uploaded_file.name}",
            'blocks_translated': len([b for b in translated_blocks if b['translatable']]),
            'total_blocks': total_blocks
        })
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        st.success("🎉 Translation completed successfully!")
        st.rerun()
        
    except Exception as e:
        st.session_state.translation_status['errors'].append(str(e))
        st.error(f"Translation failed: {str(e)}")

def update_progress(progress_bar, status_text, progress, message):
    """Update progress indicators"""
    progress_bar.progress(int(progress))
    status_text.text(message)
    st.session_state.translation_status['progress'] = progress
    st.session_state.translation_status['stage'] = message

def display_translation_status():
    """Display current translation status and results"""
    status = st.session_state.translation_status
    
    # Progress indicator
    st.metric("Progress", f"{status['progress']:.0f}%")
    
    if status['stage'] == 'complete':
        # Translation completed
        st.success("✅ Translation Complete")
        
        # Statistics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Blocks Translated", status.get('blocks_translated', 0))
        with col2:
            st.metric("Total Blocks", status.get('total_blocks', 0))
        
        # Validation results
        if 'validation' in status:
            validation = status['validation']
            st.metric("Average Quality Score", f"{validation['average_score']:.2f}")
            
            if validation['low_quality_translations']:
                st.warning(f"⚠️ {len(validation['low_quality_translations'])} translations below threshold")
        
        # Download button
        if 'output_file' in status:
            st.download_button(
                label="📥 Download Translated Document",
                data=status['output_file'].getvalue(),
                file_name=status['filename'],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary"
            )
    
    elif status['errors']:
        # Show errors
        st.error("❌ Translation Failed")
        for error in status['errors']:
            st.error(error)
    
    else:
        # Show current stage
        st.info(f"🔄 {status['stage']}")
    
    # Show processing details
    if status['details']:
        with st.expander("Processing Details"):
            for detail in status['details']:
                st.text(detail)

if __name__ == "__main__":
    main()
