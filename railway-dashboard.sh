#!/bin/bash
echo "🎨 FORCING DASHBOARD START"
echo "Current directory: $(pwd)"
echo "Files in directory: $(ls -la)"
# Don't cd to /app, already there in Railway
streamlit run dashboard/app.py --server.port ${PORT:-8080} --server.address 0.0.0.0