from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
def get_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Handle the case where requirements.txt might not exist
try:
    install_requires = get_requirements()
except FileNotFoundError:
    install_requires = [
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
    ]

setup(
    name="FAST_API",
    version="0.1.0",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.8",
)