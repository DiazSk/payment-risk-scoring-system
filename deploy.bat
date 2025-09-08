@echo off
REM 🚀 Quick Deployment Script for Render.com & Vercel (Windows)
REM This script helps you deploy the fraud detection system quickly

echo 🛡️ Fraud Detection System - Quick Deploy Script
echo ================================================
echo.

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is required but not installed.
    pause
    exit /b 1
)

REM Check if we're in a git repository
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo ❌ This script must be run from the project's git repository.
    pause
    exit /b 1
)

echo ✅ Git repository detected
echo.

:menu
echo 📋 Deployment Options:
echo =====================
echo 1. Deploy API to Render.com
echo 2. Deploy Dashboard to Streamlit Cloud (Recommended)
echo 3. Deploy Dashboard to Vercel
echo 4. Test Deployment
echo 5. View Full Documentation
echo 6. Exit
echo.

set /p choice="Choose an option (1-6): "

if "%choice%"=="1" goto render_deploy
if "%choice%"=="2" goto streamlit_deploy
if "%choice%"=="3" goto vercel_deploy
if "%choice%"=="4" goto test_deploy
if "%choice%"=="5" goto view_docs
if "%choice%"=="6" goto exit_script
echo ❌ Invalid option. Please choose 1-6.
echo.
goto menu

:render_deploy
echo.
echo 🔧 Deploying API to Render.com...
echo =================================
echo.
if not exist "render.yaml" (
    echo ❌ render.yaml not found but should exist from setup
) else (
    echo ✅ render.yaml found
)
echo.
echo 📋 Steps to complete deployment:
echo 1. Go to https://render.com/deploy
echo 2. Connect your GitHub repository
echo 3. Render will auto-detect render.yaml
echo 4. Click 'Apply' to deploy both services
echo.
echo 🔗 After deployment, your API will be available at:
echo    https://fraud-api.onrender.com
echo    https://fraud-api.onrender.com/docs (API documentation)
echo    https://fraud-api.onrender.com/health (Health check)
echo.
pause
goto menu

:streamlit_deploy
echo.
echo 📊 Deploying Dashboard to Streamlit Cloud...
echo ===========================================
echo.
echo 📋 Steps to complete deployment:
echo 1. Go to https://share.streamlit.io
echo 2. Click 'Deploy an app'
echo 3. Connect your GitHub repository
echo 4. Set main file path: dashboard/app.py
echo 5. Add environment variable:
echo    API_URL=https://fraud-api.onrender.com
echo.
echo 🔗 Recommended for dashboard deployment (easier for Streamlit apps)
echo.
pause
goto menu

:vercel_deploy
echo.
echo 📊 Deploying Dashboard to Vercel...
echo ===================================
echo.
if not exist "vercel.json" (
    echo ❌ vercel.json not found but should exist from setup
) else (
    echo ✅ vercel.json found
)
echo.
echo 📋 Steps to complete deployment:
echo 1. Install Vercel CLI: npm install -g vercel
echo 2. Run: vercel login
echo 3. Run: vercel
echo 4. Follow prompts to deploy
echo.
echo 🔗 Alternative: Use GitHub integration at vercel.com/import
echo.
echo ⚠️  Note: Vercel has limitations for Streamlit apps.
echo    Consider Streamlit Cloud for better compatibility.
echo.
pause
goto menu

:test_deploy
echo.
echo 🧪 Testing Deployment...
echo =======================
echo.
set /p API_URL="Enter your API URL (e.g., https://fraud-api.onrender.com): "

if "%API_URL%"=="" (
    echo ❌ API URL is required for testing
    pause
    goto menu
)

echo Testing health endpoint...
curl --version >nul 2>&1
if errorlevel 1 (
    echo 💡 Visit these URLs to test manually:
    echo    %API_URL%/health
    echo    %API_URL%/docs
) else (
    echo 📡 Testing: %API_URL%/health
    curl -s "%API_URL%/health"
    echo.
    echo 📡 Testing prediction endpoint...
    curl -X POST "%API_URL%/predict" -H "Content-Type: application/json" -d "{\"transaction_amount\": 500, \"transaction_hour\": 23, \"merchant_risk_score\": 0.8, \"customer_id\": \"TEST_001\"}"
    echo.
)
pause
goto menu

:view_docs
echo.
echo 📖 Full Documentation:
echo =====================
echo 📁 docs\RENDER_VERCEL_DEPLOYMENT.md - Complete deployment guide
echo 📁 render.yaml - Render configuration
echo 📁 vercel.json - Vercel configuration
echo.
if exist "docs\RENDER_VERCEL_DEPLOYMENT.md" (
    echo Opening deployment guide...
    start "" "docs\RENDER_VERCEL_DEPLOYMENT.md"
) else (
    echo Please open docs\RENDER_VERCEL_DEPLOYMENT.md manually
)
pause
goto menu

:exit_script
echo.
echo 👋 Goodbye! Your fraud detection system is ready for deployment.
echo.
echo 🎯 Quick Summary:
echo - API: Deploy to Render.com using render.yaml
echo - Dashboard: Deploy to Streamlit Cloud (recommended)
echo - Cost: $0/month on free tiers
echo - Documentation: docs\RENDER_VERCEL_DEPLOYMENT.md
echo.
pause
exit /b 0
