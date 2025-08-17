#!/bin/bash
if [[ "$RAILWAY_PUBLIC_DOMAIN" == *"dashboard"* ]]; then
    echo "Starting Dashboard..."
    streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0
else
    echo "Starting API..."
    python app/main.py
fi
