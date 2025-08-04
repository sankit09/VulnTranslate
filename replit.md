# CVE Translation System

## Overview

A professional AI-powered translation system that converts English CVE documents to Japanese while completely replacing the first page with a Japanese template image and preserving all technical formatting. Single entry point through `modular_app.py` with clean, modular architecture.

## User Preferences

Preferred communication style: Simple, everyday language.
Project structure: Clean and professional with single entry point and essential files only.

## System Architecture

The application follows an **agentic multi-agent architecture** with autonomous decision-making and intelligent coordination between specialized agents:

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

### August 4, 2025 - Project Cleanup and Documentation

#### **Complete Project Structure Cleanup**
- **Single Entry Point**: Consolidated to `modular_app.py` as the sole application entry point
- **Professional README**: Created comprehensive README with mermaid diagrams showing system architecture and workflow
- **Clean File Structure**: Removed all unnecessary files, keeping only essential components
- **Updated Workflow**: Single "CVE Translation System" workflow running on port 5000
- **Documentation Updates**: Updated `replit.md` to reflect clean, professional project structure

#### **Enhanced First Page Removal Strategy**
- **Critical Fix Implemented**: Early removal strategy that removes first page content BEFORE translation occurs
- **Two-Stage Approach**: Early removal during extraction + late removal during reconstruction
- **Comprehensive Detection**: Enhanced detection with 20+ specific first page content indicators
- **Perfect Workflow Order**: Content removed → Translation happens → Japanese image inserted
- **User Confirmed Success**: Japanese template "脆弱性の詳細および解決策:" appears correctly with clean results

### July 29, 2025 - Major System Enhancements

#### **Initial Modular Architecture (Morning)**
- **Modular Architecture Redesign**: Complete refactoring into enterprise-grade modular system
- **Core Module**: Created interfaces, models, and exceptions for clean separation of concerns
- **Provider Layer**: Implemented Azure OpenAI translator, OpenAI embeddings, and CVE term preserver
- **Processor Layer**: Built DOCX processor with full format preservation using python-docx
- **Validation Layer**: Created semantic validator with embedding-based quality assessment
- **Orchestration Layer**: Developed translation orchestrator for workflow coordination
- **Modular Application**: New Streamlit app with component health monitoring and analytics
- **Error Handling**: Comprehensive exception hierarchy with detailed error reporting
- **Batch Processing**: Parallel translation capabilities with configurable batch sizes
- **Quality Control**: Multi-layer validation with technical term preservation verification

#### **Critical Bug Fixes and API Integration (Afternoon)**
- **API Credential Resolution**: Fixed "AI services temporarily unavailable" errors with fresh Azure OpenAI and OpenAI API keys
- **Document Processing Fixes**: Resolved "original_run not defined" error in DOCX paragraph text replacement
- **Format Preservation**: Enhanced text formatting retention (bold, italic, underline, fonts, colors)
- **Statistics Tracking**: Fixed analytics display to show real-time translation metrics
- **Error Handling**: Added comprehensive fallback methods for document reconstruction
- **Translation Workflow**: Verified end-to-end translation functionality with proper Japanese output

#### **Enterprise-Grade Translation Quality (Evening)**
- **Advanced CVE Translation Prompt**: 
  * Domain-specific cybersecurity terminology mapping (脆弱性, 攻撃ベクター, セキュリティ影響)
  * Professional Japanese business language (丁寧語・尊敬語) for enterprise documentation
  * JPCERT/CC and NISC compliance standards integration
  * Severity level translations (Critical → 緊急, High → 重要, Medium → 中程度, Low → 低)

- **Named-Entity Protection System**:
  * Domain token tagging ([KEEP:0001] for CVE-2025-41225)
  * Enhanced regex patterns for comprehensive term preservation
  * Version numbers, build numbers, product editions protection
  * Company names (VMware, Microsoft, Oracle, Cisco, etc.)
  * Technical identifiers (URLs, IP addresses, file paths, registry keys)
  * Score ranges (4.3-8.8), port numbers, file extensions

- **Complete Document Coverage**:
  * Fixed missing first section translation by processing ALL paragraphs
  * Enhanced paragraph processing to maintain document structure and spacing
  * Structured chunk reconstruction preventing misplaced sections
  * Empty paragraph preservation for proper document formatting

- **Anti-Hallucination Safeguards**:
  * Critical constraints in translation prompt preventing invented CVEs
  * Token-based protection ensuring exact technical term preservation
  * Strict validation against adding non-existent vulnerability information
  * Term preservation verification with detailed logging

- **Advanced Format Preservation**:
  * Improved bold, italic, underline retention in translated text
  * Font size, color, and family preservation
  * Reliable paragraph reconstruction with comprehensive error handling
  * Enhanced run formatting preservation for complex documents

#### **Technical Implementation Details**
- **Token Protection System**: Processes 1-25+ terms per paragraph with unique tokens
- **Comprehensive Regex Patterns**: 15+ pattern types for technical term identification
- **Structured Document Processing**: Maintains original document hierarchy and formatting
- **Real-time Analytics**: Live statistics showing protected terms and translation progress
- **Enterprise Error Handling**: Multi-layer fallback systems for robust document processing

#### **Agentic System Characteristics**
- **Autonomous Decision Making**: Intelligent content assessment and processing strategy selection
- **Multi-Agent Coordination**: Specialized agents (Translation, Protection, Quality, Document, Analytics)
- **Adaptive Processing**: Content-aware chunking and error recovery mechanisms
- **Knowledge-Based Reasoning**: Domain expertise in cybersecurity and Japanese language standards
- **Self-Monitoring**: Real-time performance analytics and quality validation
- **Goal-Oriented Behavior**: Maintains technical accuracy while optimizing readability and format preservation