from setuptools import setup, find_packages

setup(
    name="vulntranslate",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=[
        "streamlit",
        "python-docx",
        "python-dotenv",
        "openai",
        "aspose-words",  # if you're using Aspose
        # Add any other libraries you're using
    ],
)
