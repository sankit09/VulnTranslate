@echo off
REM CVE Translation System - Windows Setup Script

echo 🚀 CVE Translation System - Local Setup (Windows)
echo ===================================================

REM Check Python version
echo 📋 Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3.11+ required. Please upgrade Python.
    pause
    exit /b 1
)
echo ✅ Python version check passed

REM Create virtual environment
echo 📦 Creating virtual environment...
if exist "venv" (
    echo ⚠️  Virtual environment already exists. Removing...
    rmdir /s /q venv
)

python -m venv venv
echo ✅ Virtual environment created

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated

REM Install dependencies
echo 📥 Installing dependencies from pyproject.toml...
python -m pip install --upgrade pip
pip install -e .
echo ✅ Dependencies installed

REM Check if .env file exists
echo 🔑 Checking environment variables...
if not exist ".env" (
    echo 📝 Creating .env template...
    (
        echo # Azure OpenAI Configuration
        echo AZURE_OPENAI_KEY=your_azure_openai_api_key_here
        echo AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
        echo.
        echo # OpenAI Configuration ^(for embeddings^)
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo.
        echo # Optional Configuration
        echo AZURE_OPENAI_API_VERSION=2024-02-15-preview
        echo MAX_TOKENS=2000
        echo TEMPERATURE=0.1
    ) > .env
    echo ✅ .env template created
    echo ⚠️  Please edit .env file with your actual API keys
) else (
    echo ✅ .env file already exists
)

REM Verify installation
echo 🔍 Verifying installation...
pip list | findstr "streamlit openai python-docx" >nul
if errorlevel 1 (
    echo ❌ Some packages may not be installed correctly
    pause
    exit /b 1
)
echo ✅ Key packages installed successfully

echo.
echo 🎉 Setup Complete!
echo ==================
echo.
echo Next steps:
echo 1. Edit .env file with your API keys:
echo    notepad .env
echo.
echo 2. Activate virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 3. Run the application:
echo    streamlit run modular_app.py --server.port 5000
echo.
echo 4. Open browser to: http://localhost:5000
echo.
echo For detailed instructions, see: LOCAL_SETUP.md
echo.

pause