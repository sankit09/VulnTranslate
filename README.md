# CVE Document Translation System

A professional AI-powered translation system that converts English CVE (Common Vulnerabilities and Exposures) documents to Japanese while preserving technical formatting and replacing the first page with a Japanese template.

## Features

- **Complete First Page Replacement**: Removes original English first page and replaces with Japanese template image
- **Technical Term Preservation**: Maintains CVE identifiers, product names, version numbers, and technical specifications
- **Format Preservation**: Keeps original document formatting, tables, and structure
- **Quality Validation**: Uses semantic similarity to ensure translation accuracy
- **Professional Japanese**: Enterprise-grade Japanese cybersecurity terminology

## Quick Start

1. **Run the Application**:
   ```bash
   streamlit run modular_app.py --server.port 5000
   ```

2. **Configure API Keys**: Set up your environment variables:
   - `AZURE_OPENAI_KEY`: Your Azure OpenAI API key
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
   - `OPENAI_API_KEY`: Your OpenAI API key for embeddings

3. **Upload Document**: Upload a DOCX file containing CVE information

4. **Download Result**: Get your translated document with Japanese first page

## System Architecture

- **modular_app.py**: Main Streamlit application entry point
- **core/**: Core interfaces and data models
- **providers/**: AI service providers (Azure OpenAI, OpenAI Embeddings, CVE Term Protection)
- **processors/**: Document processing (DOCX format handling)
- **orchestration/**: Translation workflow coordination
- **validation/**: Quality assurance and semantic validation
- **config/**: Application configuration management

## Requirements

- Python 3.11+
- Azure OpenAI GPT-4o access
- OpenAI API access for embeddings
- Streamlit for web interface

## Security

- No persistent storage of uploaded documents
- Secure API credential handling
- Enterprise-grade document processing

---

*Professional CVE document translation for cybersecurity teams*