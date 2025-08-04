# Local Setup Guide - CVE Translation System

## Prerequisites

- Python 3.11 or higher
- Git (for cloning the repository)
- Azure OpenAI API access
- OpenAI API access

## Step-by-Step Setup

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd cve-translation-system
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies using pyproject.toml

The project uses `pyproject.toml` for dependency management. Install using pip:

```bash
# Install all dependencies
pip install -e .

# Or if you prefer using the pyproject.toml directly:
pip install .
```

**Dependencies included:**
- `streamlit` - Web interface framework
- `openai` - OpenAI API client
- `python-docx` - DOCX document processing
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `numpy` - Numerical operations
- `aspose-words` - Advanced document processing

### Step 4: Set Environment Variables

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env  # On macOS/Linux
# or create manually on Windows
```

Add your API credentials to `.env`:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# OpenAI Configuration (for embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# Optional Configuration
AZURE_OPENAI_API_VERSION=2024-02-15-preview
MAX_TOKENS=2000
TEMPERATURE=0.1
```

**Setting Environment Variables (Alternative methods):**

**Option A: Using export (macOS/Linux)**
```bash
export AZURE_OPENAI_KEY="your_azure_openai_key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export OPENAI_API_KEY="your_openai_key"
```

**Option B: Using set (Windows CMD)**
```cmd
set AZURE_OPENAI_KEY=your_azure_openai_key
set AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
set OPENAI_API_KEY=your_openai_key
```

**Option C: Using $env (Windows PowerShell)**
```powershell
$env:AZURE_OPENAI_KEY="your_azure_openai_key"
$env:AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
$env:OPENAI_API_KEY="your_openai_key"
```

### Step 5: Verify Installation

Check if all dependencies are installed correctly:

```bash
# Verify Python and packages
python --version
pip list | grep streamlit
pip list | grep openai
pip list | grep python-docx
```

### Step 6: Run the Application

```bash
# Start the CVE Translation System
streamlit run modular_app.py --server.port 5000

# Alternative with specific host binding
streamlit run modular_app.py --server.address 0.0.0.0 --server.port 5000
```

### Step 7: Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

After setup, your project structure should look like:

```
cve-translation-system/
├── core/                    # Core interfaces and models
├── providers/               # AI service providers
├── processors/              # Document processing
├── orchestration/           # Translation workflow
├── validation/              # Quality assurance
├── config/                  # Configuration management
├── attached_assets/         # Sample files and outputs
├── modular_app.py          # Main Streamlit application
├── japanese_first_page_template.png  # Japanese template image
├── pyproject.toml          # Project configuration and dependencies
├── README.md               # Comprehensive documentation
├── LOCAL_SETUP.md          # This setup guide
├── replit.md               # Project documentation
├── .env                    # Environment variables (create this)
└── venv/                   # Virtual environment (created by you)
```

## Testing the Setup

### Quick Test

1. **Upload a Document**: Try uploading a sample DOCX file
2. **Check API Connection**: The app will validate your API keys on startup
3. **Run Translation**: Process a small document to verify everything works
4. **Download Result**: Ensure the translated document downloads properly

### Sample Test Document

Create a simple test DOCX file with content:
```
Test CVE Document

VMware ESXi Security Advisory

This document contains information about CVE-2025-12345.
The vulnerability affects vCenter Server versions 7.0 and later.
```

## Troubleshooting

### Common Issues

**Issue 1: Module Not Found**
```bash
# Solution: Reinstall in editable mode
pip install -e .
```

**Issue 2: API Key Not Found**
```bash
# Check environment variables are set
echo $AZURE_OPENAI_KEY  # Linux/macOS
echo %AZURE_OPENAI_KEY%  # Windows CMD
$env:AZURE_OPENAI_KEY    # Windows PowerShell
```

**Issue 3: Port Already in Use**
```bash
# Use different port
streamlit run modular_app.py --server.port 8501
```

**Issue 4: Virtual Environment Issues**
```bash
# Deactivate and recreate
deactivate
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
pip install -e .
```

### Debug Mode

Enable verbose logging:
```bash
export DEBUG_MODE=True  # Linux/macOS
set DEBUG_MODE=True     # Windows
streamlit run modular_app.py --server.port 5000
```

## API Key Setup

### Getting Azure OpenAI Keys

1. Go to [Azure Portal](https://portal.azure.com)
2. Create or navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint"
4. Copy "Key 1" and "Endpoint"

### Getting OpenAI Keys

1. Go to [OpenAI Platform](https://platform.openai.com)
2. Navigate to API Keys section
3. Create new secret key
4. Copy the key (save it securely)

## Production Considerations

For production deployment:

1. **Security**: Never commit `.env` file to version control
2. **Performance**: Consider using faster hardware for large documents
3. **Monitoring**: Set up logging and error tracking
4. **Scaling**: Use proper web server (not Streamlit's dev server)

## Getting Help

If you encounter issues:

1. Check the main [README.md](README.md) for detailed documentation
2. Verify all environment variables are set correctly
3. Ensure you have proper API access and quotas
4. Check the console output for specific error messages

---

**Ready to translate CVE documents locally!**