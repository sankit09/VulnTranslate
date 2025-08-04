#!/bin/bash

# CVE Translation System - Local Setup Script
# This script automates the local setup process

echo "🚀 CVE Translation System - Local Setup"
echo "======================================="

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
if [[ $(echo "$python_version >= 3.11" | bc) -eq 1 ]]; then
    echo "✅ Python $python_version detected (>=3.11 required)"
else
    echo "❌ Python 3.11+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install dependencies
echo "📥 Installing dependencies from pyproject.toml..."
pip install --upgrade pip
pip install -e .
echo "✅ Dependencies installed"

# Check if .env file exists
echo "🔑 Checking environment variables..."
if [ ! -f ".env" ]; then
    echo "📝 Creating .env template..."
    cat > .env << EOL
# Azure OpenAI Configuration
AZURE_OPENAI_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# OpenAI Configuration (for embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# Optional Configuration
AZURE_OPENAI_API_VERSION=2024-02-15-preview
MAX_TOKENS=2000
TEMPERATURE=0.1
EOL
    echo "✅ .env template created"
    echo "⚠️  Please edit .env file with your actual API keys"
else
    echo "✅ .env file already exists"
fi

# Verify installation
echo "🔍 Verifying installation..."
pip list | grep -E "(streamlit|openai|python-docx)" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Key packages installed successfully"
else
    echo "❌ Some packages may not be installed correctly"
    exit 1
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the application:"
echo "   streamlit run modular_app.py --server.port 5000"
echo ""
echo "4. Open browser to: http://localhost:5000"
echo ""
echo "For detailed instructions, see: LOCAL_SETUP.md"
echo ""