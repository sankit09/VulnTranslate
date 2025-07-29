"""
Simple CVE Translation Upload Interface
Direct access to upload functionality without initialization
"""

import streamlit as st
import os
from typing import Dict, Any

def main():
    """Simple upload interface"""
    st.set_page_config(
        page_title="CVE Translation - Upload Interface",
        page_icon="🔒",
        layout="wide"
    )
    
    st.title("🔒 CVE Translation System - Upload Interface")
    st.markdown("**Quick Upload Access** | Upload and translate CVE documents")
    
    # Check API keys
    azure_key = os.getenv("AZURE_OPENAI_KEY", "")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    if not azure_key or not azure_endpoint:
        st.error("❌ Azure OpenAI credentials missing. Please configure environment variables.")
        return
    
    # Upload interface
    st.header("📄 Document Upload Options")
    
    # File type selection
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
            st.success(f"📄 Uploaded: {uploaded_file.name}")
            st.info("💡 File uploaded successfully! Use the main application for translation processing.")
            
            # Show file details
            st.subheader("📋 File Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**File type:** {uploaded_file.type}")
            with col2:
                st.write(f"**File size:** {uploaded_file.size:,} bytes")
                file_extension = '.' + uploaded_file.name.split('.')[-1].lower()
                st.write(f"**Extension:** {file_extension}")
    
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
        
        if pasted_content:
            st.success("✅ Content ready for translation!")
            st.info("💡 Content pasted successfully! Use the main application for translation processing.")
            
            # Show content preview
            st.subheader("📋 Content Preview")
            preview_length = min(500, len(pasted_content))
            st.text_area(
                "Preview (first 500 characters):",
                pasted_content[:preview_length] + ("..." if len(pasted_content) > 500 else ""),
                height=150,
                disabled=True
            )
    
    with upload_tab3:
        st.markdown("**Load from URL:**")
        url_input = st.text_input(
            "Enter URL:",
            placeholder="https://example.com/cve-document.html"
        )
        
        if url_input:
            if st.button("📥 Load from URL", type="primary"):
                try:
                    import requests
                    
                    with st.spinner(f"Loading content from {url_input}..."):
                        response = requests.get(url_input, timeout=10)
                        response.raise_for_status()
                        
                        st.success(f"✅ Successfully loaded content from {url_input}")
                        st.info("💡 URL content loaded! Use the main application for translation processing.")
                        
                        # Show URL details
                        st.subheader("📋 URL Information")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**URL:** {url_input}")
                            st.write(f"**Status:** {response.status_code}")
                        with col2:
                            content_type = response.headers.get('content-type', 'unknown')
                            st.write(f"**Content Type:** {content_type}")
                            st.write(f"**Content Size:** {len(response.content):,} bytes")
                        
                except Exception as e:
                    st.error(f"❌ Failed to load URL: {str(e)}")
    
    # Instructions
    st.markdown("---")
    st.subheader("🚀 Next Steps")
    st.markdown("""
    **To complete translation processing:**
    
    1. **Main Application**: Go back to the main CVE translation system
    2. **Click "Force Initialize"**: Use the blue button to access full functionality  
    3. **Navigate to "Document Translation"**: Find the tab at the top
    4. **Process your content**: Upload and translate with full AI processing
    
    **Direct Access**: You can also access the main application at the primary URL and use the Force Initialize button.
    """)

if __name__ == "__main__":
    main()