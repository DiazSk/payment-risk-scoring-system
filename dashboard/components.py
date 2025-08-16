"""
Dashboard Components for Fraud Detection System
Reusable Streamlit components for visualizations and metrics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Literal
import warnings
warnings.filterwarnings('ignore')

def create_metric_card(title: str, value: str, delta: Optional[str] = None, 
                      delta_color: Literal["normal", "inverse", "off"] = "normal", 
                      help_text: Optional[str] = None):
    """
    Create a styled metric card
    
    Args:
        title: Metric title
        value: Metric value
        delta: Change indicator (optional)
        delta_color: Color of delta ('normal', 'inverse', 'off')
        help_text: Help tooltip text
    """
    with st.container():
        if help_text:
            st.metric(label=title, value=value, delta=delta, 
                     delta_color=delta_color, help=help_text)
        else:
            st.metric(label=title, value=value, delta=delta, delta_color=delta_color)

def create_status_indicator(status: str, label: str = "Status"):
    """
    Create a status indicator with appropriate colors
    
    Args:
        status: Status value ('healthy', 'warning', 'error', 'unknown')
        label: Status label
    """
    status_config = {
        'healthy': ('🟢', 'Healthy', '#28a745'),
        'warning': ('🟡', 'Warning', '#ffc107'),
        'error': ('🔴', 'Error', '#dc3545'),
        'unknown': ('⚪', 'Unknown', '#6c757d')
    }
    
    icon, text, color = status_config.get(status.lower(), status_config['unknown'])
    
    st.markdown(f"""
        <div style="
            display: flex; 
            align-items: center; 
            padding: 0.5rem; 
            background-color: {color}20; 
            border-radius: 8px;
            border-left: 4px solid {color};
        ">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
            <strong>{label}:</strong> {text}
        </div>
    """, unsafe_allow_html=True)

def create_model_performance_chart(performance_data: Dict[str, Dict[str, float]], 
                                 title: str = "Model Performance Comparison"):
    """
    Create a model performance comparison chart
    
    Args:
        performance_data: Dictionary with model names as keys and metrics as values
        title: Chart title
    """
    if not performance_data:
        st.warning("No performance data available")
        return
    
    # Convert to DataFrame for easier plotting
    df = pd.DataFrame(performance_data).T
    
    # Create subplots for different metrics
    metrics = ['accuracy', 'precision', 'recall', 'f1_score']
    available_metrics = [m for m in metrics if m in df.columns]
    
    if not available_metrics:
        st.warning("No recognized performance metrics found")
        return
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[m.replace('_', ' ').title() for m in available_metrics[:4]]
    )
    
    colors = px.colors.qualitative.Set3
    
    for i, metric in enumerate(available_metrics[:4]):
        row = (i // 2) + 1
        col = (i % 2) + 1
        
        models = df.index.tolist()
        values = df[metric].values
        
        fig.add_trace(
            go.Bar(
                x=models,
                y=values,
                name=metric.title(),
                text=[f"{v:.3f}" for v in values],
                textposition='auto',
                marker_color=colors[i % len(colors)],
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Update y-axis to show 0-1 range for most metrics
        fig.update_yaxes(range=[0, 1], row=row, col=col)
    
    fig.update_layout(
        title_text=title,
        height=600,
        template="plotly_white"
    )
    
    return fig

def create_fraud_trend_chart(dates: List, fraud_counts: List[int], 
                           legitimate_counts: Optional[List[int]] = None,
                           title: str = "Fraud Detection Trends"):
    """
    Create a fraud trend chart over time
    
    Args:
        dates: List of dates
        fraud_counts: List of fraud counts
        legitimate_counts: List of legitimate transaction counts (optional)
        title: Chart title
    """
    fig = go.Figure()
    
    # Add fraud trend
    fig.add_trace(go.Scatter(
        x=dates,
        y=fraud_counts,
        mode='lines+markers',
        name='Fraudulent Transactions',
        line=dict(color='red', width=3),
        marker=dict(size=6)
    ))
    
    # Add legitimate trend if provided
    if legitimate_counts:
        fig.add_trace(go.Scatter(
            x=dates,
            y=legitimate_counts,
            mode='lines+markers',
            name='Legitimate Transactions',
            line=dict(color='green', width=2),
            marker=dict(size=4)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Transaction Count",
        template="plotly_white",
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_feature_importance_chart(features: List[str], importance_scores: List[float],
                                  title: str = "Feature Importance",
                                  top_n: int = 15):
    """
    Create a feature importance chart
    
    Args:
        features: List of feature names
        importance_scores: List of importance scores
        title: Chart title
        top_n: Number of top features to show
    """
    # Create DataFrame and sort by importance
    df = pd.DataFrame({
        'Feature': features,
        'Importance': importance_scores
    })
    df = df.sort_values('Importance', ascending=True).tail(top_n)
    
    # Create horizontal bar chart
    fig = px.bar(
        df,
        x='Importance',
        y='Feature',
        orientation='h',
        title=title,
        labels={'Importance': 'Importance Score', 'Feature': 'Features'},
        template="plotly_white"
    )
    
    fig.update_layout(
        height=max(400, top_n * 25),
        margin=dict(l=150)  # Left margin for feature names
    )
    
    return fig

def create_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, 
                          labels: Optional[List[str]] = None, title: str = "Confusion Matrix"):
    """
    Create an interactive confusion matrix
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        labels: Label names
        title: Chart title
    """
    from sklearn.metrics import confusion_matrix
    
    cm = confusion_matrix(y_true, y_pred)
    
    if labels is None:
        labels = ['Legitimate', 'Fraudulent']
    
    # Calculate percentages
    cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=labels,
        y=labels,
        colorscale='Blues',
        text=[[f'{cm[i,j]}<br>({cm_percent[i,j]:.1f}%)' 
               for j in range(len(labels))] 
              for i in range(len(labels))],
        texttemplate="%{text}",
        textfont={"size": 14},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Predicted",
        yaxis_title="Actual",
        template="plotly_white",
        height=400,
        width=500
    )
    
    return fig

def create_risk_distribution_pie(risk_levels: List[str], counts: List[int],
                               title: str = "Risk Level Distribution"):
    """
    Create a pie chart for risk level distribution
    
    Args:
        risk_levels: List of risk levels
        counts: Corresponding counts
        title: Chart title
    """
    # Define colors for risk levels
    color_map = {
        'VERY_LOW': '#28a745',    # Green
        'LOW': '#ffc107',         # Yellow
        'MEDIUM': '#fd7e14',      # Orange
        'HIGH': '#dc3545',        # Red
        'CRITICAL': '#6f42c1'     # Purple
    }
    
    colors = [color_map.get(level, '#6c757d') for level in risk_levels]
    
    fig = px.pie(
        values=counts,
        names=risk_levels,
        title=title,
        color_discrete_sequence=colors
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=12
    )
    
    fig.update_layout(
        template="plotly_white",
        height=400
    )
    
    return fig

def create_performance_gauge(value: float, title: str, 
                           min_val: float = 0, max_val: float = 100,
                           thresholds: Optional[Dict] = None):
    """
    Create a performance gauge chart
    
    Args:
        value: Current value
        title: Gauge title
        min_val: Minimum value
        max_val: Maximum value
        thresholds: Dictionary with threshold levels
    """
    if thresholds is None:
        thresholds = {
            'poor': 50,
            'fair': 70,
            'good': 85,
            'excellent': 95
        }
    
    # Create steps for the gauge
    steps = [
        {'range': [min_val, thresholds['poor']], 'color': "#ff4444"},
        {'range': [thresholds['poor'], thresholds['fair']], 'color': "#ffaa00"},
        {'range': [thresholds['fair'], thresholds['good']], 'color': "#ffff00"},
        {'range': [thresholds['good'], thresholds['excellent']], 'color': "#00ff00"},
        {'range': [thresholds['excellent'], max_val], 'color': "#00aa00"}
    ]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': thresholds['good']},
        gauge={
            'axis': {'range': [None, max_val]},
            'bar': {'color': "darkblue"},
            'steps': steps,
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': thresholds['excellent']
            }
        }
    ))
    
    fig.update_layout(height=300, template="plotly_white")
    
    return fig

def create_time_series_chart(df: pd.DataFrame, x_col: str, y_col: str,
                           title: str = "Time Series", color_col: Optional[str] = None):
    """
    Create a time series chart
    
    Args:
        df: DataFrame with time series data
        x_col: X-axis column (time)
        y_col: Y-axis column (values)
        title: Chart title
        color_col: Column for color coding (optional)
    """
    if color_col and color_col in df.columns:
        fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title)
    else:
        fig = px.line(df, x=x_col, y=y_col, title=title)
    
    fig.update_layout(
        template="plotly_white",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def load_model_metadata(metadata_path: str = "models/model_metadata.json") -> Optional[Dict]:
    """
    Load model metadata from file
    
    Args:
        metadata_path: Path to metadata file
        
    Returns:
        Dictionary with metadata or None if file doesn't exist
    """
    try:
        metadata_file = Path(metadata_path)
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading metadata: {e}")
    
    return None

def display_model_metrics_table(performance_data: Dict[str, Dict[str, float]]):
    """
    Display model performance metrics in a formatted table with improved readability
    
    Args:
        performance_data: Dictionary with model performance metrics
    """
    if not performance_data:
        st.warning("No performance data available")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(performance_data).T
    
    # Round values for better display
    df = df.round(4)
    
    # Define improved highlighting function with better colors and contrast
    def highlight_best_readable(s):
        """Highlight the best value in each column with better readability"""
        is_max = s == s.max()
        return ['background-color: #e8f5e8; color: #155724; font-weight: bold; border: 2px solid #28a745;' if v else 'background-color: white; color: #333;' for v in is_max]
    
    # Apply performance tier coloring - simplified approach for compatibility
    def style_performance_cells(val):
        """Apply styling based on performance value"""
        if pd.isna(val):
            return 'background-color: #f8f9fa; color: #6c757d;'
        
        try:
            num_val = float(val)
            if num_val >= 0.95:  # Excellent
                return 'background-color: #d4edda; color: #155724; font-weight: bold;'
            elif num_val >= 0.85:  # Good
                return 'background-color: #fff3cd; color: #856404;'
            elif num_val >= 0.70:  # Fair
                return 'background-color: #ffeaa7; color: #6c5701;'
            else:  # Poor
                return 'background-color: #f8d7da; color: #721c24;'
        except (ValueError, TypeError):
            return 'background-color: #f8f9fa; color: #333;'
    
    # Apply styling to the entire dataframe
    performance_metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
    
    # Create styled dataframe with comprehensive error handling
    try:
        # Start with basic style
        styled_df = df.style
        
        # Try to apply formatting
        try:
            styled_df = styled_df.format(precision=3)
        except Exception:
            pass  # Skip formatting if it fails
        
        # Apply performance styling to relevant columns
        for col in df.columns:
            if any(metric in col.lower() for metric in performance_metrics):
                try:
                    styled_df = styled_df.apply(lambda s: s.map(style_performance_cells), subset=[col])
                except Exception:
                    # If styling fails, just use basic formatting
                    pass
    except Exception:
        # Fallback to basic styling if anything fails
        styled_df = df.style
    
    # Display styled DataFrame with custom CSS
    st.markdown("""
    <style>
    .stDataFrame {
        font-family: 'Courier New', monospace;
    }
    .stDataFrame th {
        background-color: #343a40 !important;
        color: white !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 12px !important;
    }
    .stDataFrame td {
        text-align: center !important;
        padding: 8px 12px !important;
        border: 1px solid #dee2e6 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=300
    )
    
    # Add legend for color coding
    st.markdown("""
    **🎨 Performance Legend:**
    - 🟢 **Excellent** (≥95%): Dark green background
    - 🟡 **Good** (≥85%): Yellow background  
    - 🟠 **Fair** (≥70%): Orange background
    - 🔴 **Poor** (<70%): Red background
    """)
    
    # Add interpretation with more detailed analysis
    if len(df) > 0:
        # Calculate overall best model with safer operations
        weights = {'accuracy': 0.2, 'precision': 0.2, 'recall': 0.4, 'f1_score': 0.2}
        
        weighted_scores = {}
        for model in df.index:
            score = 0.0
            total_weight = 0.0
            for metric, weight in weights.items():
                if metric in df.columns:
                    metric_value = df.loc[model, metric]
                    # Only attempt to convert to float if the value is int or float (not string, bool, or datetime)
                    if pd.notna(metric_value) and isinstance(metric_value, (int, float, np.integer, np.floating)):
                        numeric_value = float(metric_value)
                        score += numeric_value * weight
                        total_weight += weight

            weighted_scores[model] = score / total_weight if total_weight > 0 else 0.0
        # Find best model safely
        if weighted_scores:
            best_model = max(weighted_scores.keys(), key=lambda k: weighted_scores[k])
            best_score = weighted_scores[best_model]
        else:
            best_model = df.index[0] if len(df) > 0 else "Unknown"
            best_score = 0.0
        
        # Create performance summary
        col1, col2 = st.columns(2)
        
        with col1:
            best_model_name = str(best_model).replace('_', ' ').title()
            st.success(f"""
            🏆 **Champion Model: {best_model_name}**
            
            **Weighted Score: {best_score:.3f}**
            
            *Optimized for fraud detection (recall weighted 40%)*
            """)
        
        with col2:
            # Show top 3 models with safe sorting
            st.markdown("**🥇 Model Ranking:**")
            
            try:
                sorted_models = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)
                medals = ["🥇", "🥈", "🥉"]
                
                for i, (model, score) in enumerate(sorted_models[:3]):
                    medal = medals[i] if i < len(medals) else "🏅"
                    model_display_name = str(model).replace('_', ' ').title()
                    st.markdown(f"{medal} **{model_display_name}**: {score:.3f}")
                    
            except Exception:
                # Fallback if sorting fails
                st.markdown("Model ranking temporarily unavailable")
        
        # Performance insights with error handling
        st.markdown("### 📊 Key Insights")
        insights = []
        
        # Find best performing metrics with safer operations
        for metric in ['accuracy', 'precision', 'recall', 'f1_score']:
            if metric in df.columns:
                try:
                    best_model_for_metric = df[metric].idxmax()
                    best_value = df[metric].max()
                    model_display_name = str(best_model_for_metric).replace('_', ' ').title()
                    
                    if pd.notna(best_value):
                        best_value_float = float(best_value)
                        insights.append(f"**{metric.title()}**: {model_display_name} leads with {best_value_float:.1%}")
                    else:
                        insights.append(f"**{metric.title()}**: {model_display_name} leads")
                except (ValueError, TypeError, KeyError):
                    continue  # Skip metrics with issues
        
        for insight in insights[:3]:  # Show top 3 insights
            st.markdown(f"• {insight}")
        
        # Alert for poor performance
        poor_performers = []
        for model in df.index:
            for metric in ['accuracy', 'recall']:  # Critical metrics
                if metric in df.columns:
                    metric_value = df.loc[model, metric]
                    if pd.notna(metric_value):
                        try:
                            # Only attempt to convert if it's a number or string that looks like a number
                            if isinstance(metric_value, (int, float, str)):
                                numeric_value = float(metric_value)
                                if numeric_value < 0.70:
                                    poor_performers.append((model, metric, numeric_value))
                        except (ValueError, TypeError):
                            continue  # Skip non-numeric values
        
        if poor_performers:
            st.warning("⚠️ **Performance Alerts:**")
            for model, metric, value in poor_performers:
                model_display_name = str(model).replace('_', ' ').title()
                st.markdown(f"• {model_display_name}: {metric} is {value:.1%} (below 70% threshold)")
        else:
            st.success("✅ **All models meet minimum performance thresholds!**")

def create_alert_panel(alerts: List[Dict[str, Any]], title: str = "System Alerts"):
    """
    Create an alerts panel
    
    Args:
        alerts: List of alert dictionaries
        title: Panel title
    """
    st.subheader(title)
    
    if not alerts:
        st.success("✅ No active alerts")
        return
    
    alert_types = {
        'info': ('ℹ️', 'info'),
        'warning': ('⚠️', 'warning'), 
        'error': ('❌', 'error'),
        'success': ('✅', 'success')
    }
    
    for alert in alerts:
        alert_type = alert.get('type', 'info')
        icon, st_type = alert_types.get(alert_type, ('ℹ️', 'info'))
        
        message = f"{icon} **{alert.get('title', 'Alert')}**: {alert.get('message', '')}"
        
        if alert.get('timestamp'):
            message += f"\n\n*Time: {alert['timestamp']}*"
        
        getattr(st, st_type)(message)

def format_number(value: float, format_type: str = 'decimal') -> str:
    """
    Format numbers for display
    
    Args:
        value: Number to format
        format_type: Type of formatting ('decimal', 'percent', 'currency', 'integer')
        
    Returns:
        Formatted string
    """
    if format_type == 'percent':
        return f"{value:.1%}"
    elif format_type == 'currency':
        return f"${value:,.2f}"
    elif format_type == 'integer':
        return f"{int(value):,}"
    else:  # decimal
        return f"{value:.3f}"

def create_summary_cards(metrics: Dict[str, Any], columns: int = 4):
    """
    Create a row of summary metric cards
    
    Args:
        metrics: Dictionary with metric name as key and dict with 'value', 'delta', 'help' as value
        columns: Number of columns
    """
    cols = st.columns(columns)
    
    for i, (metric_name, metric_data) in enumerate(metrics.items()):
        with cols[i % columns]:
            value = metric_data.get('value', 'N/A')
            delta = metric_data.get('delta')
            help_text = metric_data.get('help')
            delta_color = metric_data.get('delta_color', 'normal')
            
            # Ensure delta_color is valid
            valid_delta_color = delta_color if delta_color in ['normal', 'inverse', 'off'] else 'normal'
            
            create_metric_card(
                title=metric_name,
                value=str(value),
                delta=delta,
                delta_color=valid_delta_color,  # type: ignore
                help_text=help_text
            )

def create_data_quality_report(df: pd.DataFrame, title: str = "Data Quality Report"):
    """
    Create a data quality assessment report
    
    Args:
        df: DataFrame to assess
        title: Report title
    """
    st.subheader(title)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Basic statistics
        st.markdown("**Dataset Overview**")
        st.write(f"• **Rows:** {len(df):,}")
        st.write(f"• **Columns:** {len(df.columns)}")
        st.write(f"• **Memory Usage:** {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    with col2:
        # Data quality metrics
        st.markdown("**Data Quality**")
        missing_percent = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        st.write(f"• **Missing Values:** {missing_percent:.2f}%")
        st.write(f"• **Duplicate Rows:** {df.duplicated().sum():,}")
        
        if df.select_dtypes(include=[np.number]).shape[1] > 0:
            numeric_df = df.select_dtypes(include=[np.number])
            inf_count = np.isinf(numeric_df).sum().sum()
            st.write(f"• **Infinite Values:** {inf_count}")
    
    # Missing values heatmap for columns with missing data
    missing_data = df.isnull().sum()
    missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
    
    if len(missing_data) > 0:
        st.markdown("**Missing Data by Column**")
        fig = px.bar(
            x=missing_data.values,
            y=missing_data.index,
            orientation='h',
            title="Missing Values Count by Column"
        )
        fig.update_layout(height=max(300, len(missing_data) * 25))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No missing values detected!")

# Utility functions for dashboard styling
def apply_custom_css():
    """Apply custom CSS for better dashboard styling"""
    st.markdown("""
    <style>
    .reportview-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%)
    }
    .metric-container {
        background-color: white;
        border: 1px solid #ddd;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stAlert > div {
        padding: 1rem;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

def create_download_button(data: Any, filename: str, label: str, 
                         file_format: str = 'csv'):
    """
    Create a download button for data
    
    Args:
        data: Data to download
        filename: Name of the file
        label: Button label
        file_format: File format ('csv', 'json', 'xlsx')
    """
    if file_format == 'csv' and isinstance(data, pd.DataFrame):
        csv = data.to_csv(index=False)
        st.download_button(
            label=label,
            data=csv,
            file_name=f"{filename}.csv",
            mime="text/csv"
        )
    elif file_format == 'json':
        if isinstance(data, pd.DataFrame):
            json_data = data.to_json(orient='records')
        else:
            json_data = json.dumps(data)
        
        st.download_button(
            label=label,
            data=json_data,
            file_name=f"{filename}.json",
            mime="application/json"
        )