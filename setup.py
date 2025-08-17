#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for the fraud detection project"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file with UTF-8 encoding
this_directory = Path(__file__).parent
try:
    long_description = (this_directory / "README.md").read_text(encoding='utf-8')
except FileNotFoundError:
    long_description = "E-Commerce Fraud Detection System"

setup(
    name="ecommerce-fraud-detection",
    version="1.0.0",
    description="ML-powered fraud detection system with FastAPI backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/ecommerce-fraud-detection",
    packages=find_packages(where=".", include=["src*", "app*"]),
    package_dir={"": "."},
    python_requires=">=3.8",
    install_requires=[
        # Core ML/Data Science
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "xgboost>=1.5.0",
        "imbalanced-learn>=0.8.0",
        
        # API Framework
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0",
        "pydantic>=2.0.0",
        "python-multipart>=0.0.5",
        
        # Visualization
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
        
        # Utilities
        "joblib>=1.0.0",
        "python-dotenv>=0.19.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "pylint>=2.15.0",
            "autopep8>=2.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)