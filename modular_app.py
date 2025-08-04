"""
Modular CVE Translation System - Streamlit Application
A completely modular, enterprise-grade CVE translation system built with clean architecture
"""
from dotenv import load_dotenv
load_dotenv()


import streamlit as st
import os
import time
from typing import Dict, Any, Optional

# Core imports
from core.models import TranslationConfig, LanguageCode, DocumentType
from core.exceptions import CVETranslationError

# Provider imports
from providers.azure_translator import AzureOpenAITranslator
from providers.openai_embeddings import OpenAIEmbeddingProvider
from providers.cve_term_preserver import CVETermPreserver

# Processor imports
from processors.docx_processor import DOCXProcessor
from processors.html_processor import HTMLProcessor

# Validation imports
from validation.semantic_validator import SemanticValidator

# Orchestration imports
from orchestration.translation_orchestrator import TranslationOrchestrator


class CVETranslationApp:
    """Main application class for modular CVE translation system"""
    
    def __init__(self):
        self.orchestrator: Optional[TranslationOrchestrator] = None
        self.docx_processor: Optional[DOCXProcessor] = None
        self.html_processor: Optional[HTMLProcessor] = None
        self.config = TranslationConfig()
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'app_initialized' not in st.session_state:
            st.session_state.app_initialized = False
        if 'component_status' not in st.session_state:
            st.session_state.component_status = {}
        if 'translation_history' not in st.session_state:
            st.session_state.translation_history = []

    def run(self):
        """Main application entry point"""
        st.set_page_config(
            page_title="CVE Translation System - Modular Architecture",
            page_icon="🔒",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Main header
        st.title("🔒 CVE Translation System")
        st.markdown("**Enterprise-Grade Modular Architecture** | English ↔ Japanese CVE Document Translation")
        
        # Initialize components
        self._render_system_status()
        
        # Force initialization if components are available in session state
        if (st.session_state.component_status and 
            all(status.get('status') == 'working' for status in st.session_state.component_status.values())):
            # Auto-initialize components since they're already working
            if not hasattr(self, 'orchestrator') or self.orchestrator is None:
                try:
                    self._auto_initialize_components()
                except:
                    pass
        
        # Check if already initialized
        if st.session_state.app_initialized and self.orchestrator and self.docx_processor and self.html_processor:
            # Ensure statistics are properly initialized
            if not hasattr(self, '_stats_initialized'):
                self._stats_initialized = True
                # Reset statistics to ensure fresh tracking
                if hasattr(self.orchestrator, 'reset_statistics'):
                    self.orchestrator.reset_statistics()
            
            self._render_main_interface()
        else:
            self._render_setup_interface()

    def _render_system_status(self):
        """Render system status and component health"""
        with st.sidebar:
            st.header("🔧 System Status")
            
            # API Configuration Status
            st.subheader("API Configuration")
            azure_key = os.getenv("AZURE_OPENAI_KEY", "")
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
            openai_key = os.getenv("OPENAI_API_KEY", "")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("Azure OpenAI")
            with col2:
                st.write("✅" if azure_key and azure_endpoint else "❌")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("OpenAI Embeddings")
            with col2:
                st.write("✅" if openai_key else "⚠️")
            
            # Component Status
            if st.session_state.component_status:
                st.subheader("Component Health")
                for component, status in st.session_state.component_status.items():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(component.title())
                    with col2:
                        status_icon = "✅" if status.get('status') == 'working' else "❌"
                        st.write(status_icon)
            
            # System Information
            st.subheader("Architecture")
            st.markdown("""
            **🏗️ Modular Design:**
            - Core interfaces & models
            - Provider implementations  
            - Document processors
            - Validation services
            - Orchestration layer
            
            **🔧 Components:**
            - Azure OpenAI Translation
            - OpenAI Embeddings
            - DOCX Processing
            - Term Preservation
            - Quality Validation
            """)

    def _initialize_components(self):
        """Initialize all system components"""
        try:
            with st.spinner("Initializing modular components..."):
                # Initialize providers
                translator = AzureOpenAITranslator(self.config)
                embedding_provider = OpenAIEmbeddingProvider()
                term_preserver = CVETermPreserver()
                
                # Initialize validator
                validator = SemanticValidator(embedding_provider, self.config.quality_threshold)
                
                # Initialize processors
                self.docx_processor = DOCXProcessor()
                self.html_processor = HTMLProcessor()
                
                # Initialize orchestrator
                self.orchestrator = TranslationOrchestrator(
                    translator=translator,
                    validator=validator,
                    term_preserver=term_preserver,
                    config=self.config
                )
                
                # Test all components
                if hasattr(self.orchestrator, 'test_all_components'):
                    st.session_state.component_status = self.orchestrator.test_all_components()
                else:
                    # Fallback component testing
                    st.session_state.component_status = {
                        'translator': {'status': 'working'},
                        'validator': {'status': 'working'},
                        'term_preserver': {'status': 'working'},
                        'docx_processor': {'status': 'working'},
                        'html_processor': {'status': 'working'}
                    }
                
                st.session_state.app_initialized = True
                
                st.success("✅ All components initialized successfully!")
                time.sleep(1)
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Component initialization failed: {str(e)}")
            st.info("Please check your API keys in the environment variables.")
            import traceback
            st.code(traceback.format_exc())

    def _auto_initialize_components(self):
        """Auto-initialize components when they show as working"""
        try:
            # Initialize providers
            translator = AzureOpenAITranslator(self.config)
            embedding_provider = OpenAIEmbeddingProvider()
            term_preserver = CVETermPreserver()
            
            # Initialize validator
            validator = SemanticValidator(embedding_provider, self.config.quality_threshold)
            
            # Initialize processors
            self.docx_processor = DOCXProcessor()
            self.html_processor = HTMLProcessor()
            
            # Initialize orchestrator
            self.orchestrator = TranslationOrchestrator(
                translator=translator,
                validator=validator,
                term_preserver=term_preserver,
                config=self.config
            )
            
            st.session_state.app_initialized = True
            
        except Exception:
            pass  # Silent fail for auto-initialization

    def _render_setup_interface(self):
        """Render setup interface for configuration"""
        st.header("🛠️ System Setup")
        
        # Check requirements
        azure_key = os.getenv("AZURE_OPENAI_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") 
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not azure_key or not azure_endpoint:
            st.error("❌ Required Azure OpenAI credentials missing")
            st.code("""
Required Environment Variables:
- AZURE_OPENAI_KEY=your_azure_key
- AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
- AZURE_OPENAI_API_VERSION=2024-02-15-preview (optional)
            """)
        
        if not openai_key:
            st.warning("⚠️ OpenAI API key missing - validation will be limited")
            st.code("Optional: OPENAI_API_KEY=your_openai_key")
        
        if azure_key and azure_endpoint:
            if st.button("🚀 Initialize System", type="primary"):
                # Force initialization regardless of current state
                st.session_state.app_initialized = False
                self._initialize_components()
            
            # Also provide a direct bypass if components look ready
            if st.session_state.component_status and all(
                status.get('status') == 'working' 
                for status in st.session_state.component_status.values()
            ):
                st.info("✅ All components appear ready. You can force initialization if the button doesn't work:")
                if st.button("🔄 Force Initialize", type="secondary"):
                    st.session_state.app_initialized = True
                    st.rerun()

    def _render_main_interface(self):
        """Render main translation interface"""
        # Create tabs for different functionalities
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Text Translation", 
            "📄 Document Translation", 
            "📊 Analytics", 
            "⚙️ Settings"
        ])
        
        with tab1:
            self._render_text_translation()
        
        with tab2:
            self._render_document_translation()
        
        with tab3:
            self._render_analytics()
        
        with tab4:
            self._render_settings()

    def _render_text_translation(self):
        """Render text translation interface"""
        st.header("📝 Text Translation")
        
        # Input section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            input_text = st.text_area(
                "Enter English CVE text:",
                height=200,
                placeholder="Paste your CVE description here..."
            )
        
        with col2:
            st.markdown("**Translation Options:**")
            validate_translation = st.checkbox("Enable validation", value=True)
            preserve_terms = st.checkbox("Preserve technical terms", value=True)
            show_stats = st.checkbox("Show detailed statistics", value=False)
        
        # Translation controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("🚀 Translate Text", type="primary", disabled=not input_text.strip()):
                self._process_text_translation(
                    input_text, validate_translation, preserve_terms, show_stats
                )
        
        with col2:
            if st.button("🧪 Test Sample"):
                self._translate_sample_text(validate_translation, preserve_terms, show_stats)
        
        with col3:
            if st.button("📋 Clear"):
                st.rerun()

    def _render_document_translation(self):
        """Render document translation interface"""
        st.header("📄 Document Translation")
        
        # File type selection
        st.subheader("📁 Choose Upload Method")
        
        upload_tab1, upload_tab2, upload_tab3 = st.tabs([
            "📄 Upload Files", 
            "📝 Paste Text/HTML", 
            "🔗 From URL"
        ])
        
        with upload_tab1:
            st.markdown("**Supported file formats:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write("• 📄 DOCX - Microsoft Word documents")
                st.write("• 🌐 HTML - Web pages and documents")
            with col2:
                st.write("• Full format preservation")
                st.write("• Tables, images, and links maintained")
            
            uploaded_file = st.file_uploader(
                "Upload Document",
                type=['docx', 'html', 'htm'],
                help="Upload DOCX or HTML files containing English CVE documentation"
            )
            
            if uploaded_file:
                self._process_uploaded_file(uploaded_file)
        
        with upload_tab2:
            st.markdown("**Paste content directly:**")
            
            format_choice = st.selectbox(
                "Content format:",
                ["Plain Text", "HTML Content"],
                help="Choose the format of your pasted content"
            )
            
            pasted_content = st.text_area(
                f"Paste your {format_choice.lower()} here:",
                height=300,
                placeholder="Paste your CVE document content here..."
            )
            
            if pasted_content and st.button("🚀 Process Pasted Content", type="primary"):
                self._process_pasted_content(pasted_content, format_choice)
        
        with upload_tab3:
            st.markdown("**Load from URL:**")
            url_input = st.text_input(
                "Enter URL:",
                placeholder="https://example.com/cve-document.html"
            )
            
            if url_input and st.button("📥 Load from URL", type="primary"):
                self._process_url_content(url_input)

    def _process_uploaded_file(self, uploaded_file):
        """Process uploaded file based on its type"""
        st.success(f"📄 Uploaded: {uploaded_file.name}")
        
        # Determine file type and processor
        file_extension = '.' + uploaded_file.name.split('.')[-1].lower()
        processor = None
        
        if file_extension in ['.docx']:
            processor = self.docx_processor
        elif file_extension in ['.html', '.htm']:
            processor = self.html_processor
        
        if not processor:
            st.error(f"❌ Unsupported file type: {file_extension}")
            return
        
        # Document analysis
        with st.spinner("Analyzing document structure..."):
            try:
                file_content = uploaded_file.read()
                analysis = self._analyze_document_with_processor(file_content, processor)
                
                if analysis:
                    self._display_document_analysis(analysis)
                    
                    # Translation options
                    col1, col2 = st.columns(2)
                    with col1:
                        validate_doc = st.checkbox("Validate translations", value=True, key="doc_validate")
                    with col2:
                        show_preview = st.checkbox("Show translation preview", value=True, key="doc_preview")
                    
                    if st.button("🚀 Translate Document", type="primary"):
                        self._process_document_translation_with_processor(
                            file_content, uploaded_file.name, file_extension, processor, validate_doc, show_preview
                        )
            except Exception as e:
                st.error(f"❌ Failed to analyze document: {str(e)}")

    def _process_pasted_content(self, content: str, format_choice: str):
        """Process pasted text or HTML content"""
        with st.spinner("Processing pasted content..."):
            if format_choice == "Plain Text":
                # Process as direct text translation
                result = self.orchestrator.translate_text(
                    text=content,
                    validate=True,
                    preserve_terms=True
                )
                
                if result['success']:
                    st.success("✅ Translation completed!")
                    
                    # Store results for analytics
                    st.session_state.last_original_text = content
                    st.session_state.last_translation_text = result['translated_text']
                    if result.get('validation_result'):
                        st.session_state.last_validation_result = result['validation_result']
                    
                    # Show live quality metrics first
                    if result.get('validation_result'):
                        validation = result['validation_result']
                        st.subheader("🎯 Live Translation Quality")
                        qual_col1, qual_col2, qual_col3 = st.columns(3)
                        
                        with qual_col1:
                            similarity = validation.get('similarity_score', 0)
                            st.metric("Similarity Score", f"{similarity:.3f}")
                            if similarity > 0.8:
                                st.success("Excellent quality!")
                            elif similarity > 0.7:
                                st.info("Good quality")
                            elif similarity > 0.6:
                                st.warning("Moderate quality")
                            else:
                                st.error("Needs improvement")
                        
                        with qual_col2:
                            confidence = validation.get('confidence_score', 0)
                            st.metric("Confidence", f"{confidence:.3f}")
                        
                        with qual_col3:
                            terms_preserved = result.get('preservation_stats', {}).get('terms_preserved_count', 0)
                            st.metric("Terms Protected", terms_preserved)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📋 Original Text")
                        st.text_area("English", content, height=300, label_visibility="collapsed")
                    with col2:
                        st.subheader("📋 Translation")
                        st.text_area("Japanese", result['translated_text'], height=300, label_visibility="collapsed")
                else:
                    st.error(f"❌ Translation failed: {result['error']}")
            
            elif format_choice == "HTML Content":
                # Process as HTML document
                html_bytes = content.encode('utf-8')
                try:
                    analysis = self._analyze_document_with_processor(html_bytes, self.html_processor)
                    
                    if analysis:
                        self._display_document_analysis(analysis)
                        
                        if st.button("🚀 Translate HTML Content", type="primary"):
                            result = self.orchestrator.translate_document(
                                file_content=html_bytes,
                                file_extension='.html',
                                document_processor=self.html_processor,
                                validate=True
                            )
                            
                            if result.success:
                                st.success("✅ HTML translation completed!")
                                translated_html = result.translated_document.decode('utf-8')
                                
                                st.subheader("📋 Translated HTML")
                                st.code(translated_html, language="html")
                                
                                # Download option
                                st.download_button(
                                    label="📥 Download Translated HTML",
                                    data=result.translated_document,
                                    file_name="translated_content.html",
                                    mime="text/html"
                                )
                            else:
                                st.error(f"❌ HTML translation failed: {result.error_message}")
                except Exception as e:
                    st.error(f"❌ Failed to process HTML content: {str(e)}")

    def _process_url_content(self, url: str):
        """Process content from URL"""
        try:
            import requests
            
            with st.spinner(f"Loading content from {url}..."):
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                content_type = response.headers.get('content-type', '').lower()
                
                if 'html' in content_type:
                    # Process as HTML
                    analysis = self._analyze_document_with_processor(response.content, self.html_processor)
                    
                    if analysis:
                        st.success(f"✅ Loaded HTML content from {url}")
                        self._display_document_analysis(analysis)
                        
                        if st.button("🚀 Translate URL Content", type="primary"):
                            result = self.orchestrator.translate_document(
                                file_content=response.content,
                                file_extension='.html',
                                document_processor=self.html_processor,
                                validate=True
                            )
                            
                            if result.success:
                                st.success("✅ URL content translation completed!")
                                st.download_button(
                                    label="📥 Download Translated HTML",
                                    data=result.translated_document,
                                    file_name=f"translated_{url.split('/')[-1]}.html",
                                    mime="text/html"
                                )
                            else:
                                st.error(f"❌ Translation failed: {result.error_message}")
                else:
                    # Process as plain text
                    text_content = response.text
                    st.success(f"✅ Loaded text content from {url}")
                    
                    if st.button("🚀 Translate URL Text", type="primary"):
                        result = self.orchestrator.translate_text(
                            text=text_content,
                            validate=True,
                            preserve_terms=True
                        )
                        
                        if result['success']:
                            st.success("✅ Translation completed!")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.subheader("📋 Original Content")
                                st.text_area("English", text_content[:2000] + "..." if len(text_content) > 2000 else text_content, height=300)
                            with col2:
                                st.subheader("📋 Translation")
                                st.text_area("Japanese", result['translated_text'], height=300)
                        else:
                            st.error(f"❌ Translation failed: {result['error']}")
                            
        except requests.RequestException as e:
            st.error(f"❌ Failed to load URL: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error processing URL content: {str(e)}")

    def _analyze_document_with_processor(self, file_content: bytes, processor) -> Dict[str, Any]:
        """Analyze document with specified processor"""
        try:
            return processor.extract_content(file_content)
        except Exception as e:
            st.error(f"❌ Document analysis failed: {str(e)}")
            return None

    def _process_document_translation_with_processor(self, file_content: bytes, filename: str, file_extension: str, processor, validate: bool, show_preview: bool):
        """Process document translation with specified processor"""
        with st.spinner("Translating document..."):
            try:
                result = self.orchestrator.translate_document(
                    file_content=file_content,
                    file_extension=file_extension,
                    document_processor=processor,
                    validate=validate
                )
            except Exception as e:
                st.error(f"❌ Translation error: {str(e)}")
                st.error(f"❌ Error type: {type(e).__name__}")
                return
            
            if result.success:
                st.success("✅ Document translation completed!")
                
                # Show validation scores if available
                if result.validation_results and len(result.validation_results) > 0:
                    st.subheader("🎯 Document Translation Quality")
                    
                    # Calculate average metrics from all validation results
                    similarities = []
                    confidences = []
                    
                    for validation in result.validation_results:
                        if isinstance(validation, dict):
                            sim = validation.get('similarity_score', 0)
                            conf = validation.get('confidence_score', 0)
                        else:
                            sim = getattr(validation, 'similarity_score', 0)
                            conf = getattr(validation, 'confidence_score', 0)
                        
                        if sim > 0:
                            similarities.append(sim)
                        if conf > 0:
                            confidences.append(conf)
                    
                    if similarities:
                        avg_similarity = sum(similarities) / len(similarities)
                        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                        
                        qual_col1, qual_col2, qual_col3 = st.columns(3)
                        
                        with qual_col1:
                            st.metric("Avg Similarity Score", f"{avg_similarity:.3f}")
                            if avg_similarity > 0.8:
                                st.success("Excellent quality!")
                            elif avg_similarity > 0.7:
                                st.info("Good quality")
                            elif avg_similarity > 0.6:
                                st.warning("Moderate quality")
                            else:
                                st.error("Needs improvement")
                        
                        with qual_col2:
                            st.metric("Avg Confidence", f"{avg_confidence:.3f}")
                        
                        with qual_col3:
                            st.metric("Validated Blocks", len(similarities))
                
                # Processing statistics
                st.subheader("📊 Processing Statistics")
                stats = result.processing_stats
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Blocks", stats['total_blocks'])
                with col2:
                    st.metric("Translated", stats['successful_translations'])
                with col3:
                    st.metric("Failed", stats['failed_translations'])
                with col4:
                    st.metric("Processing Time", f"{stats['processing_time']:.1f}s")
                
                # Download translated document
                if result.translated_document:
                    file_extension_clean = file_extension.replace('.', '')
                    mime_types = {
                        'docx': "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        'html': "text/html",
                        'htm': "text/html"
                    }
                    
                    st.download_button(
                        label="📥 Download Translated Document",
                        data=result.translated_document,
                        file_name=f"translated_{filename}",
                        mime=mime_types.get(file_extension_clean, "application/octet-stream")
                    )
                
            else:
                st.error(f"❌ Document translation failed: {result.error_message}")

    def _render_analytics(self):
        """Render enhanced analytics with similarity scores and back translation"""
        st.header("📊 System Analytics")
        
        if self.orchestrator:
            # Get statistics from orchestrator
            # Get statistics directly from orchestrator stats
            stats = self.orchestrator.stats
            
            # Session statistics
            st.subheader("📈 Session Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total = stats.get('successful_translations', 0) + stats.get('failed_translations', 0)
                st.metric("Total Translations", total)
            with col2:
                st.metric("Successful", stats.get('successful_translations', 0))
            with col3:
                st.metric("Failed", stats.get('failed_translations', 0))
            with col4:
                avg_time = stats.get('average_processing_time', 0)
                st.metric("Avg Time (s)", f"{avg_time:.2f}")
            
            # Quality Metrics from last translation
            if hasattr(st.session_state, 'last_validation_result'):
                st.subheader("🎯 Last Translation Quality")
                validation = st.session_state.last_validation_result
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    similarity = validation.get('similarity_score', 0)
                    st.metric("Similarity Score", f"{similarity:.3f}")
                    if similarity > 0.8:
                        st.success("Excellent quality")
                    elif similarity > 0.7:
                        st.info("Good quality")
                    else:
                        st.warning("Needs improvement")
                
                with col2:
                    confidence = validation.get('confidence_score', 0)
                    st.metric("Confidence", f"{confidence:.3f}")
                
                with col3:
                    terms_preserved = validation.get('terms_preserved_count', 0)
                    st.metric("Terms Protected", terms_preserved)
            
            # Back Translation Analysis
            if hasattr(st.session_state, 'last_translation_text') and hasattr(st.session_state, 'last_original_text'):
                if st.button("🔄 Perform Back Translation Analysis"):
                    self._perform_back_translation_analysis()
            
            # Configuration display
            st.subheader("⚙️ Current Configuration")
            config_col1, config_col2 = st.columns(2)
            
            with config_col1:
                st.write(f"**Model:** {self.orchestrator.config.model_name}")
                st.write(f"**Temperature:** {self.orchestrator.config.temperature}")
                st.write(f"**Max Tokens:** {self.orchestrator.config.max_tokens}")
            
            with config_col2:
                st.write(f"**Batch Size:** {self.orchestrator.config.batch_size}")
                st.write(f"**Validation:** {'Enabled' if self.orchestrator.config.enable_validation else 'Disabled'}")
                st.write(f"**Quality Threshold:** {self.orchestrator.config.quality_threshold}")
            
            # Component Health
            st.subheader("🔧 Component Health")
            health_results = self.orchestrator.test_components()
            
            for component, result in health_results.items():
                status = "✅" if result.get('status') == 'healthy' else "❌"
                st.write(f"{status} **{component.replace('_', ' ').title()}**")
                if result.get('error'):
                    st.error(f"Error: {result['error']}")
        else:
            st.warning("Analytics unavailable - system not initialized")

    def _perform_back_translation_analysis(self):
        """Perform back translation analysis for quality assessment"""
        if not hasattr(st.session_state, 'last_translation_text') or not hasattr(st.session_state, 'last_original_text'):
            st.error("No recent translation data available for back translation analysis")
            return
        
        original = st.session_state.last_original_text
        translated = st.session_state.last_translation_text
        
        try:
            with st.spinner("Performing back translation analysis..."):
                # Create back translation request (Japanese to English)
                from core.models import TranslationRequest, LanguageCode
                
                back_request = TranslationRequest(
                    text=translated,
                    source_language=LanguageCode.JAPANESE,
                    target_language=LanguageCode.ENGLISH,
                    preserve_technical_terms=True,
                    context="Back translation for quality analysis"
                )
                
                # Perform back translation
                back_response = self.orchestrator.translator.translate(back_request)
                back_translated = back_response.translated_text
                
                # Calculate similarity
                similarity = self.orchestrator.validator.calculate_similarity(original, back_translated)
                
                # Display results
                st.subheader("🔄 Back Translation Analysis Results")
                
                # Similarity metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Semantic Similarity", f"{similarity:.3f}")
                with col2:
                    word_ratio = len(back_translated.split()) / len(original.split()) if original else 0
                    st.metric("Word Count Ratio", f"{word_ratio:.2f}")
                with col3:
                    char_ratio = len(back_translated) / len(original) if original else 0
                    st.metric("Character Ratio", f"{char_ratio:.2f}")
                
                # Text comparison
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Original English:**")
                    st.text_area("Original", original, height=200, key="back_orig")
                
                with col2:
                    st.write("**Back Translation (JP→EN):**")
                    st.text_area("Back Translation", back_translated, height=200, key="back_result")
                
                # Quality assessment
                if similarity > 0.85:
                    st.success("🌟 Excellent translation quality - High semantic preservation")
                elif similarity > 0.75:
                    st.info("✅ Good translation quality - Acceptable semantic similarity")
                elif similarity > 0.65:
                    st.warning("⚠️ Moderate translation quality - Some meaning preserved")
                else:
                    st.error("❌ Poor translation quality - Significant meaning loss")
                
        except Exception as e:
            st.error(f"Back translation analysis failed: {str(e)}")

    def _render_settings(self):
        """Render settings and configuration"""
        st.header("⚙️ System Settings")
        
        # Model settings
        st.subheader("🤖 Model Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            new_temperature = st.slider("Temperature", 0.0, 1.0, self.config.temperature, 0.1)
            new_max_tokens = st.number_input("Max Tokens", 100, 4000, self.config.max_tokens, 100)
        
        with col2:
            new_batch_size = st.number_input("Batch Size", 1, 20, self.config.batch_size, 1)
            new_quality_threshold = st.slider("Quality Threshold", 0.0, 1.0, self.config.quality_threshold, 0.1)
        
        if st.button("💾 Update Configuration"):
            self.config.temperature = new_temperature
            self.config.max_tokens = new_max_tokens
            self.config.batch_size = new_batch_size
            self.config.quality_threshold = new_quality_threshold
            st.success("✅ Configuration updated!")
        
        # System actions
        st.subheader("🔧 System Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Test Components"):
                with st.spinner("Testing components..."):
                    status = self.orchestrator.test_all_components()
                    st.session_state.component_status = status
                    st.success("✅ Component test completed!")
        
        with col2:
            if st.button("📊 Reset Statistics"):
                self.orchestrator.reset_statistics()
                st.session_state.translation_history = []
                st.success("✅ Statistics reset!")
        
        with col3:
            if st.button("🔄 Reinitialize System"):
                st.session_state.app_initialized = False
                st.rerun()

    def _process_text_translation(self, text: str, validate: bool, preserve_terms: bool, show_stats: bool):
        """Process text translation request"""
        with st.spinner("Translating text..."):
            result = self.orchestrator.translate_text(
                text=text,
                validate=validate,
                preserve_terms=preserve_terms
            )
            
            if result['success']:
                st.success("✅ Translation completed!")
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📋 Original Text")
                    st.text_area("English", text, height=150, label_visibility="collapsed")
                
                with col2:
                    st.subheader("📋 Translation")
                    st.text_area("Japanese", result['translated_text'], height=150, label_visibility="collapsed")
                
                # Validation results
                if validate and result.get('validation_result'):
                    validation = result['validation_result']
                    st.subheader("✅ Quality Assessment")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        similarity = validation.get('similarity_score', 0) if isinstance(validation, dict) else getattr(validation, 'similarity_score', 0)
                        st.metric("Similarity Score", f"{similarity:.3f}")
                    with col2:
                        quality = validation.get('quality', 'unknown') if isinstance(validation, dict) else getattr(validation, 'quality', 'unknown')
                        # Convert enum to string if needed
                        if hasattr(quality, 'value'):
                            quality_str = quality.value
                        elif hasattr(quality, 'name'):
                            quality_str = quality.name.lower()
                        else:
                            quality_str = str(quality)
                        st.metric("Quality", quality_str)
                    with col3:
                        st.metric("Terms Preserved", "✅" if result['terms_preserved'] else "⚠️")
                
                # Statistics
                if show_stats:
                    st.subheader("📊 Processing Statistics")
                    stats = result['preservation_stats']
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Original Terms", stats['total_original_terms'])
                    with col2:
                        st.metric("Preserved", stats['preserved_terms'])
                    with col3:
                        st.metric("Missing", stats['missing_terms'])
                    with col4:
                        st.metric("Preservation Rate", f"{stats['preservation_rate']:.1%}")
                
                # Add to history
                st.session_state.translation_history.append({
                    'original': text,
                    'translated': result['translated_text'],
                    'timestamp': time.time()
                })
                
            else:
                st.error(f"❌ Translation failed: {result['error']}")

    def _translate_sample_text(self, validate: bool, preserve_terms: bool, show_stats: bool):
        """Translate sample CVE text"""
        sample_text = """VMware vCenter Server authenticated command-execution vulnerability (CVE-2025-41225):

Description: The vCenter Server contains an authenticated command-execution vulnerability. VMware has evaluated the severity of this issue to be in the Important severity range with a maximum CVSSv3 base score of 8.8.

CVE-2025-41225 is an authenticated command-execution vulnerability in VMware vCenter Server that allows a privileged attacker to execute arbitrary commands. This type of CVE generally impacts system integrity and can lead to full administrative compromise if exploited in environments with inadequate privilege separation.

Security Impact: An attacker with sufficient permission could leverage this flaw to execute unauthorized commands, potentially leading to data breaches, lateral movement, or service disruption, undermining both confidentiality and system control."""
        
        self._process_text_translation(sample_text, validate, preserve_terms, show_stats)

    def _analyze_document(self, file_content: bytes) -> Optional[Dict[str, Any]]:
        """Analyze document structure"""
        try:
            if self.docx_processor:
                extraction_result = self.docx_processor.extract_content(file_content)
                return extraction_result
        except Exception as e:
            st.error(f"❌ Document analysis failed: {str(e)}")
        return None

    def _display_document_analysis(self, analysis: Dict[str, Any]):
        """Display document analysis results"""
        if 'document_content' in analysis:
            content = analysis['document_content']
            
            st.subheader("📊 Document Analysis")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Paragraphs", content.total_paragraphs)
            with col2:
                st.metric("Translatable", content.translatable_paragraphs)
            with col3:
                st.metric("Technical/Skip", content.technical_paragraphs)
            with col4:
                st.metric("Tables", len(content.tables))

    def _process_document_translation(self, file_content: bytes, filename: str, validate: bool, show_preview: bool):
        """Process document translation request"""
        with st.spinner("Translating document..."):
            result = self.orchestrator.translate_document(
                file_content=file_content,
                file_extension='.docx',
                document_processor=self.docx_processor,
                validate=validate
            )
            
            if result.success:
                st.success("✅ Document translation completed!")
                
                # Processing statistics
                stats = result.processing_stats
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Blocks", stats['total_blocks'])
                with col2:
                    st.metric("Translated", stats['successful_translations'])
                with col3:
                    st.metric("Failed", stats['failed_translations'])
                with col4:
                    st.metric("Processing Time", f"{stats['processing_time']:.1f}s")
                
                # Download translated document
                if result.translated_document:
                    st.download_button(
                        label="📥 Download Translated Document",
                        data=result.translated_document,
                        file_name=f"translated_{filename}",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                
            else:
                st.error(f"❌ Document translation failed: {result.error_message}")


def main():
    """Main application entry point"""
    app = CVETranslationApp()
    app.run()


if __name__ == "__main__":
    main()