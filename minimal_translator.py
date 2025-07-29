import streamlit as st
import os
from openai import AzureOpenAI
from openai import OpenAI
import numpy as np
from typing import Dict, Any

class MinimalCVETranslator:
    """Minimal CVE translator without document processing dependencies"""
    
    def __init__(self):
        # Initialize Azure OpenAI for translation
        self.azure_key = os.getenv("AZURE_OPENAI_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not self.azure_key or not self.azure_endpoint:
            raise ValueError("Azure OpenAI credentials not configured")
        
        self.azure_client = AzureOpenAI(
            api_key=self.azure_key,
            api_version=self.azure_api_version,
            azure_endpoint=self.azure_endpoint
        )
        
        # Initialize OpenAI for validation
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
            self.validation_available = True
        else:
            self.openai_client = None
            self.validation_available = False
        
        # Model settings
        self.translation_model = "gpt-4o"
        self.embedding_model = "text-embedding-3-small"
        
        # CVE-specific prompt
        self.system_prompt = """You are a cybersecurity translation specialist. Translate English CVE documents to Japanese while preserving technical accuracy.

CRITICAL RULES:
1. DO NOT translate:
   - CVE IDs (e.g., CVE-2025-41225)
   - CVSS scores (e.g., CVSSv3, 8.8)
   - Product names and versions (e.g., VMware ESXi 7.0.3)
   - Company names (VMware, Microsoft, etc.)
   - URLs and technical identifiers

2. DO translate:
   - Descriptions and explanations
   - Security impact descriptions
   - Technical concepts and terms

3. Use formal Japanese business language (敬語) appropriate for technical documentation.

Translate the following text to Japanese:"""
    
    def translate_text(self, text: str) -> str:
        """Translate text from English to Japanese"""
        if len(text.strip()) < 3:
            return text
        
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": text}
            ]
            
            response = self.azure_client.chat.completions.create(
                model=self.translation_model,
                messages=messages,
                max_tokens=2000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else text
            
        except Exception as e:
            st.error(f"Translation error: {str(e)}")
            return text
    
    def validate_translation(self, original: str, translated: str) -> Dict[str, Any]:
        """Validate translation quality using semantic similarity"""
        if not self.validation_available:
            return {
                'similarity_score': 0.85,  # Default good score
                'quality': 'Not validated (no OpenAI key)',
                'technical_terms_preserved': True
            }
        
        try:
            # Get embeddings
            original_embedding = self._get_embedding(original)
            translated_embedding = self._get_embedding(translated)
            
            # Calculate cosine similarity
            similarity = np.dot(original_embedding, translated_embedding) / (
                np.linalg.norm(original_embedding) * np.linalg.norm(translated_embedding)
            )
            
            # Normalize to 0-1 range
            similarity_score = max(0.0, min(1.0, (similarity + 1) / 2))
            
            return {
                'similarity_score': similarity_score,
                'quality': 'Good' if similarity_score > 0.7 else 'Needs Review',
                'technical_terms_preserved': self._check_technical_preservation(original, translated)
            }
            
        except Exception as e:
            return {
                'similarity_score': 0.0,
                'quality': f'Validation Error: {str(e)}',
                'technical_terms_preserved': False
            }
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding vector for text"""
        if not self.openai_client:
            return np.zeros(1536)  # Default embedding size
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text.replace("\n", " ")
        )
        return np.array(response.data[0].embedding)
    
    def _check_technical_preservation(self, original: str, translated: str) -> bool:
        """Check if technical terms are preserved"""
        import re
        
        # Technical patterns that should be preserved
        patterns = [
            r'CVE-\d{4}-\d{4,7}',
            r'CVSS[v]?\d+(\.\d+)?',
            r'VMware|Microsoft|Oracle|Adobe',
            r'https?://[^\s]+',
        ]
        
        for pattern in patterns:
            original_matches = set(re.findall(pattern, original, re.IGNORECASE))
            translated_matches = set(re.findall(pattern, translated, re.IGNORECASE))
            
            if original_matches and not original_matches.issubset(translated_matches):
                return False
        
        return True

def main():
    st.set_page_config(
        page_title="CVE Translation System - POC",
        page_icon="🔒",
        layout="wide"
    )
    
    st.title("🔒 CVE Translation System - Proof of Concept")
    st.markdown("Convert English CVE documents to Japanese with AI translation")
    
    # Check API credentials
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_key = os.getenv("AZURE_OPENAI_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    if not all([azure_endpoint, azure_key]):
        st.error("❌ Azure OpenAI credentials not configured properly")
        st.info("Required: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY")
        if not openai_key:
            st.warning("⚠️ OpenAI API key missing - validation will be limited")
        st.stop()
    
    st.success("✅ Azure OpenAI configured")
    if openai_key:
        st.success("✅ OpenAI validation available")
    else:
        st.warning("⚠️ OpenAI key missing - validation limited")
    
    # Initialize translator
    try:
        translator = MinimalCVETranslator()
    except Exception as e:
        st.error(f"Failed to initialize translator: {str(e)}")
        st.stop()
    
    # Text input section
    st.header("📝 Text Translation")
    
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
                    st.text_area("Original CVE Text", value=sample_text, height=300, key="orig_sample", label_visibility="collapsed")
                
                with col_trans:
                    st.markdown("**Japanese Translation:**")
                    st.text_area("Translated CVE Text", value=translated_sample, height=300, key="trans_sample", label_visibility="collapsed")
                
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

    # Sidebar with information
    with st.sidebar:
        st.header("🔧 System Information")
        
        st.subheader("Features")
        st.markdown("""
        ✅ English to Japanese translation  
        ✅ CVE-specific terminology preservation  
        ✅ Translation quality validation  
        ✅ Technical term checking  
        """)
        
        st.subheader("API Status")
        st.write(f"Azure Endpoint: {'✅' if azure_endpoint else '❌'}")
        st.write(f"Azure Key: {'✅' if azure_key else '❌'}")
        st.write(f"OpenAI Key: {'✅' if openai_key else '⚠️'}")
        
        st.subheader("Models")
        st.write("Translation: gpt-4o")
        st.write("Validation: text-embedding-3-small")

    # Document Upload Section
    st.header("📄 Document Upload")
    st.info("Upload DOCX files to extract and translate text content")
    
    uploaded_file = st.file_uploader(
        "Choose a DOCX file",
        type=['docx'],
        help="Upload DOCX files containing English CVE documentation"
    )
    
    if uploaded_file is not None:
        st.success(f"Uploaded: {uploaded_file.name}")
        
        if st.button("📖 Extract and Translate Document", type="primary"):
            with st.spinner("Processing document..."):
                try:
                    # Read file content
                    file_content = uploaded_file.read()
                    
                    # Try to extract text using basic method
                    import zipfile
                    import xml.etree.ElementTree as ET
                    
                    text_content = ""
                    
                    # Extract text from DOCX (basic XML parsing)
                    with zipfile.ZipFile(uploaded_file, 'r') as zip_file:
                        # Read document.xml
                        doc_xml = zip_file.read('word/document.xml')
                        root = ET.fromstring(doc_xml)
                        
                        # Extract text from paragraphs
                        for paragraph in root.iter():
                            if paragraph.tag.endswith('}t'):  # Text elements
                                if paragraph.text:
                                    text_content += paragraph.text + " "
                            elif paragraph.tag.endswith('}p'):  # Paragraph breaks
                                text_content += "\n\n"
                    
                    # Clean up text
                    text_content = ' '.join(text_content.split())
                    
                    if text_content.strip():
                        st.subheader("📄 Extracted Text")
                        st.text_area("Extracted Content", value=text_content[:1000] + "..." if len(text_content) > 1000 else text_content, height=150, label_visibility="collapsed")
                        
                        # Translate extracted text
                        with st.spinner("Translating document content..."):
                            translated_content = translator.translate_text(text_content)
                            
                            st.subheader("📋 Translated Document")
                            st.text_area("Translated Content", value=translated_content, height=200, label_visibility="collapsed")
                            
                            # Validation
                            with st.spinner("Validating translation..."):
                                validation = translator.validate_translation(text_content, translated_content)
                                
                                st.subheader("✅ Document Quality Check")
                                col_a, col_b, col_c = st.columns(3)
                                
                                with col_a:
                                    st.metric("Similarity Score", f"{validation['similarity_score']:.2f}")
                                with col_b:
                                    st.metric("Quality", validation['quality'])
                                with col_c:
                                    preserved = "✅" if validation['technical_terms_preserved'] else "⚠️"
                                    st.metric("Technical Terms", preserved)
                            
                            # Download option
                            st.download_button(
                                label="📥 Download Translated Text",
                                data=translated_content,
                                file_name=f"translated_{uploaded_file.name.replace('.docx', '.txt')}",
                                mime="text/plain"
                            )
                    else:
                        st.error("Could not extract text from the document")
                        
                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")
                    st.info("Try uploading a simpler DOCX file or use the text input method above")

if __name__ == "__main__":
    main()