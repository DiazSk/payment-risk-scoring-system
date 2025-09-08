"""
Simplified Streamlit Dashboard for Fraud Detection API
Minimal version without heavy dependencies
"""

import streamlit as st
import requests
from datetime import datetime
from typing import Dict

# Configuration
API_BASE_URL = "https://fraud-api.onrender.com"  # Your deployed API URL

st.set_page_config(
    page_title="Payment Risk Scoring Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def call_api(endpoint: str, method: str = "GET", data=None) -> Dict:
    """Make API calls with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
            
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main():
    st.title("🛡️ Payment Risk Scoring Dashboard")
    st.markdown("Real-time fraud detection monitoring and testing")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Overview", "🔍 Single Prediction", "📊 Batch Testing", "📈 API Stats"]
    )
    
    if page == "🏠 Overview":
        show_overview()
    elif page == "🔍 Single Prediction":
        show_single_prediction()
    elif page == "📊 Batch Testing":
        show_batch_testing()
    elif page == "📈 API Stats":
        show_api_stats()

def show_overview():
    st.header("System Overview")
    
    # API Health Check
    health_data = call_api("/health")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if "error" not in health_data:
            st.success("✅ API Status: Healthy")
            st.metric("Environment", health_data.get("environment", "unknown"))
        else:
            st.error("❌ API Status: Error")
            st.error(health_data["error"])
    
    with col2:
        st.metric("API Version", "v2.0")
        st.metric("Response Time", "~10ms")
    
    with col3:
        st.metric("Detection Method", "Rule-Based")
        st.metric("Accuracy", "85%")
    
    # Recent Activity Simulation
    st.subheader("Recent Transaction Activity")
    
    # Sample data for demonstration
    sample_transactions = [
        {"time": "10:45 AM", "amount": "$1,250", "risk": "LOW", "status": "✅ Approved"},
        {"time": "10:44 AM", "amount": "$15,000", "risk": "HIGH", "status": "🚨 Flagged"},
        {"time": "10:43 AM", "amount": "$89", "risk": "LOW", "status": "✅ Approved"},
        {"time": "10:42 AM", "amount": "$7,500", "risk": "MEDIUM", "status": "⚠️ Review"},
        {"time": "10:41 AM", "amount": "$234", "risk": "LOW", "status": "✅ Approved"},
    ]
    
    for txn in sample_transactions:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.text(txn["time"])
        with col2:
            st.text(txn["amount"])
        with col3:
            if txn["risk"] == "HIGH":
                st.error(txn["risk"])
            elif txn["risk"] == "MEDIUM":
                st.warning(txn["risk"])
            else:
                st.success(txn["risk"])
        with col4:
            st.text(txn["status"])

def show_single_prediction():
    st.header("🔍 Single Transaction Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Transaction Details")
        
        transaction_id = st.text_input("Transaction ID", value=f"TXN_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        amount = st.number_input("Amount ($)", min_value=0.01, value=100.0, step=0.01)
        customer_id = st.text_input("Customer ID", value="CUST_12345")
        merchant = st.text_input("Merchant", value="Amazon")
        
        if st.button("🔍 Analyze Transaction", type="primary"):
            # Prepare transaction data
            transaction_data = {
                "transaction_id": transaction_id,
                "amount": amount,
                "customer_id": customer_id,
                "merchant": merchant,
                "timestamp": datetime.now().isoformat()
            }
            
            # Call API
            result = call_api("/predict", "POST", transaction_data)
            
            if "error" not in result:
                with col2:
                    st.subheader("Fraud Analysis Results")
                    
                    # Risk Level
                    risk_level = result.get("risk_level", "UNKNOWN")
                    if risk_level == "HIGH":
                        st.error(f"🚨 Risk Level: {risk_level}")
                    elif risk_level == "MEDIUM":
                        st.warning(f"⚠️ Risk Level: {risk_level}")
                    else:
                        st.success(f"✅ Risk Level: {risk_level}")
                    
                    # Fraud Probability
                    fraud_prob = result.get("fraud_probability", 0)
                    st.metric("Fraud Probability", f"{fraud_prob:.1%}")
                    
                    # Fraud Prediction
                    is_fraud = result.get("fraud_prediction", False)
                    if is_fraud:
                        st.error("🚨 FRAUD DETECTED")
                    else:
                        st.success("✅ Transaction Approved")
                    
                    # Risk Factors
                    risk_factors = result.get("risk_factors", [])
                    if risk_factors:
                        st.subheader("Risk Factors")
                        for factor in risk_factors:
                            st.warning(f"• {factor}")
                    
                    # Technical Details
                    with st.expander("Technical Details"):
                        st.json(result)
            else:
                st.error(f"API Error: {result['error']}")

def show_batch_testing():
    st.header("📊 Batch Transaction Testing")
    
    st.markdown("Test multiple transactions at once")
    
    # Sample batch data
    if st.button("🧪 Run Sample Batch Test"):
        sample_transactions = [
            {"transaction_id": "TXN_001", "amount": 50, "customer_id": "CUST_001"},
            {"transaction_id": "TXN_002", "amount": 15000, "customer_id": "CUST_002"},
            {"transaction_id": "TXN_003", "amount": 750, "customer_id": "CUST_003"},
            {"transaction_id": "TXN_004", "amount": 25, "customer_id": "CUST_004"},
            {"transaction_id": "TXN_005", "amount": 8500, "customer_id": "CUST_005"},
        ]
        
        result = call_api("/batch_predict", "POST", sample_transactions)
        
        if "error" not in result:
            st.success(f"✅ Batch processed: {result.get('total_transactions', 0)} transactions")
            
            # Results table
            results = result.get("results", [])
            
            col1, col2, col3 = st.columns(3)
            
            high_risk = sum(1 for r in results if r.get("risk_level") == "HIGH")
            medium_risk = sum(1 for r in results if r.get("risk_level") == "MEDIUM")
            low_risk = sum(1 for r in results if r.get("risk_level") == "LOW")
            
            with col1:
                st.metric("🚨 High Risk", high_risk)
            with col2:
                st.metric("⚠️ Medium Risk", medium_risk)
            with col3:
                st.metric("✅ Low Risk", low_risk)
            
            # Detailed results
            st.subheader("Detailed Results")
            for result_item in results:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.text(result_item.get("transaction_id", ""))
                with col2:
                    st.text(f"${result_item.get('amount', 0):,.2f}")
                with col3:
                    risk = result_item.get("risk_level", "UNKNOWN")
                    if risk == "HIGH":
                        st.error(risk)
                    elif risk == "MEDIUM":
                        st.warning(risk)
                    else:
                        st.success(risk)
                with col4:
                    st.text(f"{result_item.get('fraud_probability', 0):.1%}")
        else:
            st.error(f"Batch processing failed: {result['error']}")

def show_api_stats():
    st.header("📈 API Statistics")
    
    stats_data = call_api("/stats")
    
    if "error" not in stats_data:
        # Model Info
        st.subheader("Model Information")
        model_info = stats_data.get("model_info", {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Model Type", model_info.get("type", "unknown"))
            st.metric("Version", model_info.get("version", "unknown"))
        with col2:
            st.metric("Accuracy", model_info.get("accuracy", "unknown"))
            st.metric("Features", len(model_info.get("features", [])))
        
        # API Stats
        st.subheader("API Performance")
        api_stats = stats_data.get("api_stats", {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Predictions", api_stats.get("total_predictions", 0))
        with col2:
            st.metric("Avg Response Time", f"{api_stats.get('avg_response_time_ms', 0)}ms")
        with col3:
            st.metric("Status", api_stats.get("uptime", "unknown"))
        
        # Raw data
        with st.expander("Raw Statistics Data"):
            st.json(stats_data)
    else:
        st.error(f"Failed to load statistics: {stats_data['error']}")

if __name__ == "__main__":
    main()
