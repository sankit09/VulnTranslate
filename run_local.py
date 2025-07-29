#!/usr/bin/env python3
"""
CVE Translation System - Local Runner
Quick setup script for running the application locally
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_required_packages():
    """Check if required packages are installed"""
    required_packages = {
        'streamlit': 'streamlit',
        'openai': 'openai', 
        'numpy': 'numpy',
        'docx': 'python-docx',
        'bs4': 'beautifulsoup4'
    }
    
    missing_packages = []
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name} installed")
        except ImportError:
            print(f"❌ {package_name} not found")
            missing_packages.append(package_name)
    
    return missing_packages

def install_packages(packages):
    """Install missing packages"""
    if not packages:
        return True
    
    print(f"\n📦 Installing missing packages: {', '.join(packages)}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = {
        'AZURE_OPENAI_KEY': 'Azure OpenAI API Key',
        'AZURE_OPENAI_ENDPOINT': 'Azure OpenAI Endpoint',
        'OPENAI_API_KEY': 'OpenAI API Key (optional for validation)'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        if os.getenv(var):
            print(f"✅ {description} configured")
        else:
            print(f"❌ {description} missing")
            missing_vars.append(var)
    
    return missing_vars

def create_env_file_template():
    """Create a .env template file"""
    env_template = """# CVE Translation System Environment Variables
# Copy this file to .env and fill in your actual API keys

# Azure OpenAI Configuration (Required)
AZURE_OPENAI_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# OpenAI Configuration (Optional - for translation validation)
OPENAI_API_KEY=your_openai_key_here
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("📝 Created .env.template file")
    print("   Copy it to .env and add your API keys")

def setup_project_structure():
    """Ensure proper project structure"""
    services_dir = Path('services')
    if not services_dir.exists():
        print("❌ services/ directory not found")
        return False
    
    init_file = services_dir / '__init__.py'
    if not init_file.exists():
        init_file.touch()
        print("✅ Created services/__init__.py")
    
    return True

def run_application():
    """Start the Streamlit application"""
    print("\n🚀 Starting CVE Translation System...")
    print("   The application will open in your browser")
    print("   Press Ctrl+C to stop the application")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "minimal_translator.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except FileNotFoundError:
        print("❌ minimal_translator.py not found")
        return False
    
    return True

def main():
    """Main setup and run function"""
    print("🔒 CVE Translation System - Local Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check project structure
    if not setup_project_structure():
        return False
    
    # Check packages
    missing_packages = check_required_packages()
    if missing_packages:
        install_choice = input(f"\nInstall missing packages? (y/n): ")
        if install_choice.lower() == 'y':
            if not install_packages(missing_packages):
                return False
        else:
            print("❌ Cannot run without required packages")
            return False
    
    # Check environment variables
    missing_vars = check_environment_variables()
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        create_env_file_template()
        print("\nOptions:")
        print("1. Set environment variables in your system")
        print("2. Create .env file from template")
        print("3. Install python-dotenv and use .env file")
        
        choice = input("\nContinue anyway? (y/n): ")
        if choice.lower() != 'y':
            return False
    
    # Run the application
    print("\n" + "=" * 40)
    return run_application()

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)