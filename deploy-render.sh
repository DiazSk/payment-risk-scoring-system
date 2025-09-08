#!/bin/bash
# Render.com deployment helper script

echo "=== Render Deployment Helper ==="
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# Update pip first
echo "Updating pip..."
pip install --upgrade pip

# Install with verbose output for debugging
echo "Installing requirements..."
pip install -r requirements-api.txt --verbose

echo "=== Installation Complete ==="
echo "Installed packages:"
pip list | grep -E "(numpy|pandas|scikit-learn|fastapi|uvicorn)"

echo "=== Starting API ==="
python app/main.py
