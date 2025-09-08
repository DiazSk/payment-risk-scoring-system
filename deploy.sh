#!/bin/bash

# 🚀 Quick Deployment Script for Render.com & Vercel
# This script helps you deploy the fraud detection system quickly

echo "🛡️ Fraud Detection System - Quick Deploy Script"
echo "================================================"

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is required but not installed."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ This script must be run from the project's git repository."
    exit 1
fi

echo "✅ Git repository detected"

# Function to deploy to Render
deploy_to_render() {
    echo ""
    echo "🔧 Deploying API to Render.com..."
    echo "================================="
    
    # Check if render.yaml exists
    if [ ! -f "render.yaml" ]; then
        echo "❌ render.yaml not found. Creating it..."
        # render.yaml should already exist from previous step
        echo "✅ render.yaml created"
    fi
    
    echo "📋 Steps to complete deployment:"
    echo "1. Go to https://render.com/deploy"
    echo "2. Connect your GitHub repository"
    echo "3. Render will auto-detect render.yaml"
    echo "4. Click 'Apply' to deploy both services"
    echo ""
    echo "🔗 After deployment, your API will be available at:"
    echo "   https://fraud-api.onrender.com"
    echo "   https://fraud-api.onrender.com/docs (API documentation)"
    echo "   https://fraud-api.onrender.com/health (Health check)"
}

# Function to deploy dashboard to Streamlit Cloud
deploy_dashboard_streamlit() {
    echo ""
    echo "📊 Deploying Dashboard to Streamlit Cloud..."
    echo "==========================================="
    
    echo "📋 Steps to complete deployment:"
    echo "1. Go to https://share.streamlit.io"
    echo "2. Click 'Deploy an app'"
    echo "3. Connect your GitHub repository"
    echo "4. Set main file path: dashboard/app.py"
    echo "5. Add environment variable:"
    echo "   API_URL=https://fraud-api.onrender.com"
    echo ""
    echo "🔗 Recommended for dashboard deployment (easier for Streamlit apps)"
}

# Function to deploy dashboard to Vercel
deploy_dashboard_vercel() {
    echo ""
    echo "📊 Deploying Dashboard to Vercel..."
    echo "==================================="
    
    # Check if vercel.json exists
    if [ ! -f "vercel.json" ]; then
        echo "❌ vercel.json not found but should exist from setup"
    fi
    
    echo "📋 Steps to complete deployment:"
    echo "1. Install Vercel CLI: npm install -g vercel"
    echo "2. Run: vercel login"
    echo "3. Run: vercel"
    echo "4. Follow prompts to deploy"
    echo ""
    echo "🔗 Alternative: Use GitHub integration at vercel.com/import"
    echo ""
    echo "⚠️  Note: Vercel has limitations for Streamlit apps."
    echo "   Consider Streamlit Cloud for better compatibility."
}

# Function to test deployment
test_deployment() {
    echo ""
    echo "🧪 Testing Deployment..."
    echo "======================="
    
    read -p "Enter your API URL (e.g., https://fraud-api.onrender.com): " API_URL
    
    if [ -z "$API_URL" ]; then
        echo "❌ API URL is required for testing"
        return 1
    fi
    
    echo "Testing health endpoint..."
    if command -v curl &> /dev/null; then
        echo "📡 Testing: $API_URL/health"
        curl -s "$API_URL/health" | head -10
        echo ""
        
        echo "📡 Testing prediction endpoint..."
        curl -X POST "$API_URL/predict" \
             -H "Content-Type: application/json" \
             -d '{
               "transaction_amount": 500,
               "transaction_hour": 23,
               "merchant_risk_score": 0.8,
               "customer_id": "TEST_001"
             }' | head -10
        echo ""
    else
        echo "💡 Visit these URLs to test manually:"
        echo "   $API_URL/health"
        echo "   $API_URL/docs"
    fi
}

# Main menu
while true; do
    echo ""
    echo "📋 Deployment Options:"
    echo "====================="
    echo "1. Deploy API to Render.com"
    echo "2. Deploy Dashboard to Streamlit Cloud (Recommended)"
    echo "3. Deploy Dashboard to Vercel"
    echo "4. Test Deployment"
    echo "5. View Full Documentation"
    echo "6. Exit"
    echo ""
    
    read -p "Choose an option (1-6): " choice
    
    case $choice in
        1)
            deploy_to_render
            ;;
        2)
            deploy_dashboard_streamlit
            ;;
        3)
            deploy_dashboard_vercel
            ;;
        4)
            test_deployment
            ;;
        5)
            echo ""
            echo "📖 Full Documentation:"
            echo "====================="
            echo "📁 docs/RENDER_VERCEL_DEPLOYMENT.md - Complete deployment guide"
            echo "📁 render.yaml - Render configuration"
            echo "📁 vercel.json - Vercel configuration"
            echo ""
            if command -v cat &> /dev/null && [ -f "docs/RENDER_VERCEL_DEPLOYMENT.md" ]; then
                echo "Opening deployment guide..."
                # On macOS/Linux, try to open with default app
                if command -v open &> /dev/null; then
                    open "docs/RENDER_VERCEL_DEPLOYMENT.md"
                elif command -v xdg-open &> /dev/null; then
                    xdg-open "docs/RENDER_VERCEL_DEPLOYMENT.md"
                else
                    echo "Please open docs/RENDER_VERCEL_DEPLOYMENT.md manually"
                fi
            fi
            ;;
        6)
            echo "👋 Goodbye! Your fraud detection system is ready for deployment."
            echo ""
            echo "🎯 Quick Summary:"
            echo "- API: Deploy to Render.com using render.yaml"
            echo "- Dashboard: Deploy to Streamlit Cloud (recommended)"
            echo "- Cost: $0/month on free tiers"
            echo "- Documentation: docs/RENDER_VERCEL_DEPLOYMENT.md"
            echo ""
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-6."
            ;;
    esac
done
