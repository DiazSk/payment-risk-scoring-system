"""
Setup configuration for E-Commerce Fraud Detection System
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

# Read requirements from requirements.txt
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    # Fallback requirements if file doesn't exist
    requirements = [
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "xgboost>=1.4.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "streamlit>=1.10.0",
        "plotly>=5.0.0",
        "pydantic>=1.8.0",
        "joblib>=1.0.0",
        "requests>=2.25.0",
        "python-multipart>=0.0.5",
        "imbalanced-learn>=0.8.0",
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0"
    ]

setup(
    name="credit-card-fraud-detection-system",
    version="1.0.0",
    author="Credit Card Fraud Detection Team",
    author_email="team@creditcardfrauddetection.com",
    description="Advanced ML-powered fraud detection system for credit card transactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/credit-card-fraud-detection-system",
    project_urls={
        "Bug Tracker": "https://github.com/your-username/credit-card-fraud-detection-system/issues",
        "Documentation": "https://credit-card-fraud-detection-docs.readthedocs.io/",
        "Source Code": "https://github.com/your-username/credit-card-fraud-detection-system",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Financial :: Point-Of-Sale",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
            "pre-commit>=2.10.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
            "sphinxcontrib-napoleon>=0.7",
        ],
        "deployment": [
            "docker>=5.0.0",
            "gunicorn>=20.0.0",
            "psycopg2-binary>=2.8.0",  # PostgreSQL support
            "redis>=3.5.0",            # Caching support
        ],
        "monitoring": [
            "prometheus-client>=0.11.0",
            "grafana-api>=1.0.0",
            "sentry-sdk>=1.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "credit-card-fraud-detector=app.main:main",
            "credit-card-fraud-train=src.train_models:main",
            "credit-card-fraud-dashboard=dashboard.app:main",
            "credit-card-fraud-api=app.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.txt", "*.md"],
        "models": ["*.pkl", "*.json"],
        "data": ["*.csv", "*.json"],
        "configs": ["*.yaml", "*.json"],
    },
    zip_safe=False,
    keywords=[
        "credit card fraud detection",
        "fraud detection",
        "machine learning",
        "credit card security",
        "payment fraud",
        "anomaly detection", 
        "financial technology",
        "risk management",
        "payment processing",
        "artificial intelligence",
        "data science",
        "cybersecurity",
        "fintech"
    ],
    platforms=["any"],
    license="MIT",
    test_suite="tests",
    cmdclass={},
    # Additional metadata for PyPI
    maintainer="Credit Card Fraud Detection Team",
    maintainer_email="maintainer@creditcardfrauddetection.com",
    download_url="https://github.com/your-username/credit-card-fraud-detection-system/archive/v1.0.0.tar.gz",
)

# Setup configuration for different environments
if __name__ == "__main__":
    print("🚀 Setting up Credit Card Fraud Detection System...")
    print("📦 Package: credit-card-fraud-detection-system v1.0.0")
    print("🐍 Python: >=3.8 required")
    print("📋 Installing dependencies...")
    print("\n✅ Setup configuration loaded successfully!")
    print("\nTo install in development mode:")
    print("  pip install -e .")
    print("\nTo install with all extras:")
    print("  pip install -e .[dev,docs,deployment,monitoring]")
    print("\nTo build distribution packages:")
    print("  python setup.py sdist bdist_wheel")
    print("\nTo upload to PyPI:")
    print("  twine upload dist/*")