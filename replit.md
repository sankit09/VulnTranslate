# CVE Translation System

## Overview

This is an AI-powered translation system specifically designed for CVE (Common Vulnerabilities and Exposures) documents. The application translates English CVE documents to Japanese while preserving technical formatting, hyperlinks, tables, and CVE-specific terminology. It uses a Streamlit frontend with Azure OpenAI for translation and OpenAI for embeddings-based validation.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a service-oriented architecture with clear separation of concerns:

- **Frontend**: Streamlit web application providing user interface
- **Services Layer**: Core business logic for document processing, translation, and validation
- **Utilities Layer**: Helper classes for Azure/OpenAI client management and text processing
- **Configuration**: Centralized configuration management with environment variable support

## Key Components

### Frontend Layer
- **app.py**: Main Streamlit application entry point with user interface and workflow orchestration
- Provides file upload, configuration options, and real-time processing feedback
- Includes sidebar for API credential validation and translation settings

### Core Services
- **DocumentParser**: Handles DOCX and HTML document parsing using Aspose.Words and BeautifulSoup
- **CVETranslator**: Manages translation using Azure OpenAI GPT-4o with CVE-specific prompts
- **TranslationValidator**: Validates translation quality using semantic similarity and quality scoring
- **DocumentReconstructor**: Rebuilds translated documents while preserving original formatting

### Utility Components
- **AzureOpenAIClient**: Wrapper for Azure OpenAI API interactions
- **TextProcessor**: Handles technical term preservation and content preparation for translation

### Configuration Management
- **Config**: Centralized settings including API credentials, model configurations, and processing thresholds
- Environment variable-based configuration for sensitive data

## Data Flow

1. **Document Upload**: User uploads DOCX or HTML file through Streamlit interface
2. **Document Parsing**: DocumentParser extracts content blocks and formatting metadata
3. **Content Preparation**: TextProcessor identifies translatable content and preserves technical terms
4. **Translation**: CVETranslator processes content blocks using Azure OpenAI GPT-4o
5. **Validation**: TranslationValidator checks translation quality using embeddings and semantic analysis
6. **Reconstruction**: DocumentReconstructor rebuilds the document with translated content
7. **Output**: User downloads the translated document with preserved formatting

## External Dependencies

### Primary APIs
- **Azure OpenAI**: Main translation service using GPT-4o model
- **OpenAI**: Embeddings service for translation validation using text-embedding-3-small

### Document Processing
- **Aspose.Words**: DOCX document parsing and reconstruction
- **BeautifulSoup**: HTML document processing

### Frontend Framework
- **Streamlit**: Web application framework for user interface

### Authentication Requirements
- Azure OpenAI API key and endpoint
- OpenAI API key for embeddings
- All credentials managed through environment variables

## Deployment Strategy

The application is designed for cloud deployment with the following considerations:

### Environment Configuration
- Requires AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, and OPENAI_API_KEY environment variables
- Configuration validation on startup with clear error messaging
- Support for different API versions through AZURE_OPENAI_API_VERSION

### Scalability Considerations
- Batch processing with configurable batch sizes
- Token limit management (2000 tokens per request)
- Translation caching to reduce API calls
- File size limits (50MB maximum)

### Security Features
- API credential validation on startup
- Secure handling of sensitive documents in temporary files
- No persistent storage of user documents or translations

### Performance Optimizations
- Low temperature settings (0.1) for consistent translations
- Configurable quality thresholds for validation
- Efficient text processing with compiled regex patterns
- Memory-efficient document processing using BytesIO streams

The system is architected to handle CVE documents specifically, with specialized prompts and technical term preservation logic to maintain the accuracy and integrity of cybersecurity documentation during translation.

## Recent Changes

### July 29, 2025
- Fixed Aspose.Words ICU globalization issues by creating minimal translator
- Added python-docx library for full DOCX format preservation  
- Implemented DOCXTranslator service that maintains formatting, images, tables, and hyperlinks
- Enhanced user interface with document preview and statistics
- Preserved all document elements while translating only text content