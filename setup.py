from setuptools import setup, find_packages
import os

# Fallback dependencies if requirements.txt can't be read
default_requires = [
    "fastapi>=0.68.0",
    "uvicorn>=0.15.0",
]

# Read requirements from requirements.txt with robust error handling
def get_requirements():
    try:
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open('requirements.txt', 'r', encoding=encoding) as f:
                    return [line.strip() for line in f 
                            if line.strip() and not line.startswith('#')]
            except UnicodeDecodeError:
                continue  # Try next encoding
        
        # If we get here, none of the encodings worked
        print("Warning: Could not decode requirements.txt with standard encodings")
        return default_requires
    except FileNotFoundError:
        print("Warning: requirements.txt not found")
        return default_requires
    except Exception as e:
        print(f"Error reading requirements: {e}")
        return default_requires

setup(
    name="your-package-name",
    version="0.1.0",
    packages=find_packages(exclude=["tests*"]) or ['.'],  # Fallback to current directory if no packages found
    install_requires=get_requirements(),
    python_requires=">=3.8",
)