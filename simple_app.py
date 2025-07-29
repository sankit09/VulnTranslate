import streamlit as st
import os
import tempfile
from io import BytesIO
from services.simple_translator import SimpleCVETranslator

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
    tab1, tab2 = st.tabs(["📝 Text Input", "📄 File Upload"])
    
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
        st.header("Document Translation")
        st.info("📝 For this POC, upload text files (.txt) containing CVE content")
        
        uploaded_file = st.file_uploader(
            "Choose a text file",
            type=['txt'],
            help="Upload a .txt file containing English CVE documentation"
        )
        
        if uploaded_file is not None:
            st.success(f"Uploaded: {uploaded_file.name}")
            
            # Read file content
            content = uploaded_file.read().decode('utf-8')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📄 Original Content")
                st.text_area("File content:", value=content, height=400, key="file_orig")
            
            if st.button("🚀 Translate File", type="primary"):
                with st.spinner("Translating file content..."):
                    translated_content = translator.translate_text(content)
                    
                    with col2:
                        st.subheader("📄 Translated Content")
                        st.text_area("Japanese translation:", value=translated_content, height=400, key="file_trans")
                    
                    # Download button
                    translated_bytes = translated_content.encode('utf-8')
                    st.download_button(
                        label="📥 Download Translated File",
                        data=translated_bytes,
                        file_name=f"translated_{uploaded_file.name}",
                        mime="text/plain"
                    )
                    
                    # Validation
                    with st.spinner("Validating translation..."):
                        validation = translator.validate_translation(content, translated_content)
                        
                        st.subheader("✅ Translation Quality")
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric("Similarity Score", f"{validation['similarity_score']:.2f}")
                        with col_b:
                            st.metric("Quality", validation['quality'])
                        with col_c:
                            preserved = "✅" if validation['technical_terms_preserved'] else "⚠️"
                            st.metric("Technical Terms", preserved)
    
    # Sidebar with information
    with st.sidebar:
        st.header("🔧 System Information")
        
        st.subheader("Features")
        st.markdown("""
        ✅ English to Japanese translation  
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
        """)

if __name__ == "__main__":
    main()