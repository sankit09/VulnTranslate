# CVE Translation System - Local Setup Guide

## Prerequisites

1. **Python 3.8 or higher** installed on your system
2. **Git** for cloning the repository
3. **API Keys** for Azure OpenAI and OpenAI

## Step 1: Download the Project

### Option A: Clone from Replit
```bash
git clone <your-replit-repo-url>
cd cve-translation-system
```

### Option B: Download Files Manually
Create a new directory and download these core files:
- `minimal_translator.py` (main application)
- `services/docx_translator.py` (document processor)
- All files in the `services/` directory

## Step 2: Set Up Python Environment

### Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Install Required Packages
```bash
pip install streamlit==1.29.0
pip install openai==1.12.0
pip install numpy==1.24.3
pip install python-docx==1.2.0
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3
```

Or create a `requirements.txt` file with the above packages and run:
```bash
pip install -r requirements.txt
```

## Step 3: Set Up API Keys

### Get API Keys
1. **Azure OpenAI**: Get from Azure Portal
   - API Key
   - Endpoint URL
   - API Version (default: 2024-02-15-preview)

2. **OpenAI**: Get from OpenAI Platform
   - API Key (for embeddings validation)

### Configure Environment Variables

#### Option A: Create .env file (Recommended)
Create a `.env` file in your project root:
```bash
AZURE_OPENAI_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
OPENAI_API_KEY=your_openai_key_here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

And add this to the top of `minimal_translator.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

#### Option B: Set System Environment Variables

**Windows (Command Prompt):**
```cmd
set AZURE_OPENAI_KEY=your_azure_openai_key_here
set AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
set AZURE_OPENAI_API_VERSION=2024-02-15-preview
set OPENAI_API_KEY=your_openai_key_here
```

**Windows (PowerShell):**
```powershell
$env:AZURE_OPENAI_KEY="your_azure_openai_key_here"
$env:AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
$env:AZURE_OPENAI_API_VERSION="2024-02-15-preview"
$env:OPENAI_API_KEY="your_openai_key_here"
```

**macOS/Linux:**
```bash
export AZURE_OPENAI_KEY=your_azure_openai_key_here
export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
export AZURE_OPENAI_API_VERSION=2024-02-15-preview
export OPENAI_API_KEY=your_openai_key_here
```

## Step 4: Create Project Structure

Ensure your project has this structure:
```
cve-translation-system/
├── minimal_translator.py          # Main Streamlit app
├── services/
│   ├── __init__.py               # Empty file to make it a Python package
│   └── docx_translator.py        # DOCX processing service
├── .env                          # API keys (optional)
└── requirements.txt              # Dependencies (optional)
```

Create the `services/__init__.py` file:
```bash
# Create empty __init__.py file
touch services/__init__.py
# On Windows: type nul > services\__init__.py
```

## Step 5: Run the Application

### Start the Streamlit Application
```bash
streamlit run minimal_translator.py
```

The application will start and display:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### Access the Application
Open your web browser and go to `http://localhost:8501`

## Step 6: Test the Application

1. **Text Translation**: Try the sample CVE text or paste your own
2. **Document Upload**: Upload a DOCX file with CVE content
3. **Verify**: Check that translations preserve technical terms and formatting

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# If you get import errors, ensure services is a Python package:
touch services/__init__.py
```

#### 2. API Key Errors
```bash
# Verify environment variables are set:
echo $AZURE_OPENAI_KEY  # On Windows: echo %AZURE_OPENAI_KEY%
```

#### 3. Package Installation Issues
```bash
# Upgrade pip first:
pip install --upgrade pip

# Install packages one by one:
pip install streamlit
pip install openai
pip install python-docx
```

#### 4. Port Already in Use
```bash
# Use a different port:
streamlit run minimal_translator.py --server.port 8502
```

### Performance Tips

1. **Virtual Environment**: Always use a virtual environment to avoid conflicts
2. **API Rate Limits**: Be aware of Azure OpenAI rate limits for large documents
3. **Document Size**: Very large DOCX files may take longer to process
4. **Network**: Ensure stable internet connection for API calls

## Advanced Configuration

### Custom Streamlit Configuration
Create `.streamlit/config.toml`:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Production Deployment
For production deployment, consider:
- Using Docker containers
- Setting up reverse proxy (nginx)
- Implementing proper logging
- Adding authentication
- Using environment-specific configuration

## System Requirements

- **Minimum**: 4GB RAM, 2GB free disk space
- **Recommended**: 8GB RAM, 5GB free disk space
- **Network**: Stable internet connection for API calls
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)

The local setup provides the same functionality as the Replit version with full DOCX format preservation, translation quality validation, and technical term protection.