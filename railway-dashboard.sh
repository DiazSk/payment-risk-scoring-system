#!/bin/bash
echo "🎨 FORCING DASHBOARD START"
echo "Current directory: $(pwd)"
echo "Files in directory: $(ls -la)"
cd /app
pip install streamlit
streamlit run dashboard/app.py --server.port ${PORT:-8080} --server.address 0.0.0.0