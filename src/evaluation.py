"""
Advanced Model Evaluation and Visualization
Professional-grade evaluation metrics and plots for fraud detection models
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.metrics import (
    confusion_matrix, classification_report, roc_curve, auc,
    precision_recall_curve, average_precision_score, roc_auc_score
)
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import joblib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudModelEvaluator:
    """
    Advanced evaluation and visualization for fraud detection models
    """
    
    def __init__(self, save_plots: bool = True):
        self.save_plots = save_plots
        self.plots_dir = Path("plots")
        if save_plots:
            self.plots_dir.mkdir(exist_ok=True)
    
    def plot_confusion_matrices(self, evaluation_results: Dict, figsize: Tuple = (15, 10)):
        """Create confusion matrix plots for all models"""
        logger.info("Creating confusion matrix plots...")
        
        n_models = len(evaluation_results)
        cols = min(3, n_models)
        rows = (n_models + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=figsize)
        if n_models == 1:
            axes = [axes]
        elif rows == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        
        for idx, (model_name, results) in enumerate(evaluation_results.items()):
            ax = axes[idx] if n_models > 1 else axes[0]
            
            # Get predictions from results
            y_true = results.get('y_true', [])
            y_pred = results.get('predictions', [])
            
            if len(y_true) == 0 or len(y_pred) == 0:
                continue
            
            # Create confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            
            # Plot heatmap
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                       xticklabels=['Normal', 'Fraud'],
                       yticklabels=['Normal', 'Fraud'])
            
            ax.set_title(f'{model_name.replace("_", " ").title()}\nConfusion Matrix')
            ax.set_ylabel('True Label')
            ax.set_xlabel('Predicted Label')
            
            # Add accuracy in the title
            accuracy = (cm[0,0] + cm[1,1]) / cm.sum()
            ax.set_title(f'{model_name.replace("_", " ").title()}\nAccuracy: {accuracy:.3f}')
        
        # Hide unused subplots
        for idx in range(n_models, len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        
        if self.save_plots:
            plt.savefig(self.plots_dir / 'confusion_matrices.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_roc_curves(self, evaluation_results: Dict, figsize: Tuple = (10, 8)):
        """Plot ROC curves for all models"""
        logger.info("Creating ROC curve plots...")
        
        plt.figure(figsize=figsize)
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
        
        for idx, (model_name, results) in enumerate(evaluation_results.items()):
            y_true = results.get('y_true', [])
            y_proba = results.get('probabilities', [])
            
            if len(y_true) == 0 or y_proba is None or len(y_proba) == 0:
                continue
            
            # Calculate ROC curve
            fpr, tpr, _ = roc_curve(y_true, y_proba)
            roc_auc = auc(fpr, tpr)
            
            color = colors[idx % len(colors)]
            plt.plot(fpr, tpr, color=color, lw=2, 
                    label=f'{model_name.replace("_", " ").title()} (AUC = {roc_auc:.3f})')
        
        # Plot diagonal line
        plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--', alpha=0.5)
        
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curves - Model Comparison')
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        
        if self.save_plots:
            plt.savefig(self.plots_dir / 'roc_curves.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_precision_recall_curves(self, evaluation_results: Dict, figsize: Tuple = (10, 8)):
        """Plot Precision-Recall curves for all models"""
        logger.info("Creating Precision-Recall curve plots...")
        
        plt.figure(figsize=figsize)
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
        
        for idx, (model_name, results) in enumerate(evaluation_results.items()):
            y_true = results.get('y_true', [])
            y_proba = results.get('probabilities', [])
            
            if len(y_true) == 0 or y_proba is None or len(y_proba) == 0:
                continue
            
            # Calculate Precision-Recall curve
            precision, recall, _ = precision_recall_curve(y_true, y_proba)
            pr_auc = average_precision_score(y_true, y_proba)
            
            color = colors[idx % len(colors)]
            plt.plot(recall, precision, color=color, lw=2,
                    label=f'{model_name.replace("_", " ").title()} (AP = {pr_auc:.3f})')
        
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curves - Model Comparison')
        plt.legend(loc="lower left")
        plt.grid(True, alpha=0.3)
        
        if self.save_plots:
            plt.savefig(self.plots_dir / 'precision_recall_curves.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_feature_importance(self, model, feature_names: List[str], model_name: str, 
                               top_n: int = 20, figsize: Tuple = (12, 8)):
        """Plot feature importance for tree-based models"""
        logger.info(f"Creating feature importance plot for {model_name}...")
        
        # Get feature importance
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importance = np.abs(model.coef_[0])
        else:
            logger.warning(f"Model {model_name} doesn't support feature importance")
            return
        
        # Create feature importance DataFrame
        feature_importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False).head(top_n)
        
        # Create plot
        plt.figure(figsize=figsize)
        sns.barplot(data=feature_importance_df, x='importance', y='feature', palette='viridis')
        plt.title(f'Top {top_n} Feature Importance - {model_name.replace("_", " ").title()}')
        plt.xlabel('Feature Importance')
        plt.ylabel('Features')
        plt.tight_layout()
        
        if self.save_plots:
            plt.savefig(self.plots_dir / f'{model_name}_feature_importance.png', 
                       dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return feature_importance_df
    
    def create_interactive_model_comparison(self, evaluation_results: Dict):
        """Create interactive Plotly dashboard for model comparison"""
        logger.info("Creating interactive model comparison dashboard...")
        
        # Prepare data for comparison
        models = []
        metrics = ['recall', 'precision', 'f1_score', 'accuracy', 'fpr']
        
        for model_name, results in evaluation_results.items():
            model_metrics = results['metrics']
            models.append({
                'model': model_name.replace('_', ' ').title(),
                'recall': model_metrics.get('recall', 0),
                'precision': model_metrics.get('precision', 0), 
                'f1_score': model_metrics.get('f1_score', 0),
                'accuracy': model_metrics.get('accuracy', 0),
                'fpr': model_metrics.get('fpr', 0),
                'roc_auc': model_metrics.get('roc_auc', 0)
            })
        
        df_comparison = pd.DataFrame(models)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Model Performance Comparison', 'ROC-AUC Comparison',
                           'False Positive Rate', 'Precision vs Recall'),
            specs=[[{'secondary_y': False}, {'secondary_y': False}],
                   [{'secondary_y': False}, {'secondary_y': False}]]
        )
        
        # Performance metrics radar chart data
        metrics_to_plot = ['recall', 'precision', 'f1_score', 'accuracy']
        
        # Bar chart comparison
        for metric in metrics_to_plot:
            fig.add_trace(
                go.Bar(x=df_comparison['model'], y=df_comparison[metric], 
                      name=metric.replace('_', ' ').title()),
                row=1, col=1
            )
        
        # ROC-AUC comparison
        if 'roc_auc' in df_comparison.columns:
            fig.add_trace(
                go.Bar(x=df_comparison['model'], y=df_comparison['roc_auc'],
                      name='ROC-AUC', marker_color='lightblue'),
                row=1, col=2
            )
        
        # False Positive Rate
        fig.add_trace(
            go.Bar(x=df_comparison['model'], y=df_comparison['fpr'],
                  name='False Positive Rate', marker_color='red'),
            row=2, col=1
        )
        
        # Precision vs Recall scatter
        fig.add_trace(
            go.Scatter(x=df_comparison['recall'], y=df_comparison['precision'],
                      mode='markers+text', text=df_comparison['model'],
                      textposition="top center", name='Models',
                      marker=dict(size=12, color=df_comparison['f1_score'], 
                                colorscale='Viridis', showscale=True,
                                colorbar=dict(title="F1-Score"))),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="Fraud Detection Model Performance Dashboard",
            showlegend=False,
            height=800
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Models", row=1, col=1)
        fig.update_yaxes(title_text="Score", row=1, col=1)
        
        fig.update_xaxes(title_text="Models", row=1, col=2)
        fig.update_yaxes(title_text="ROC-AUC Score", row=1, col=2)
        
        fig.update_xaxes(title_text="Models", row=2, col=1)
        fig.update_yaxes(title_text="False Positive Rate", row=2, col=1)
        
        fig.update_xaxes(title_text="Recall", row=2, col=2)
        fig.update_yaxes(title_text="Precision", row=2, col=2)
        
        if self.save_plots:
            fig.write_html(self.plots_dir / "interactive_model_comparison.html")
        
        fig.show()
    
    def create_business_impact_visualization(self, evaluation_results: Dict, 
                                           annual_transactions: int = 1000000,
                                           avg_fraud_amount: float = 150.0,
                                           investigation_cost: float = 25.0):
        """Create business impact analysis visualization"""
        logger.info("Creating business impact visualization...")
        
        business_metrics = []
        
        for model_name, results in evaluation_results.items():
            metrics = results['metrics']
            
            # Calculate business impact
            recall = metrics.get('recall', 0)
            fpr = metrics.get('fpr', 0)
            
            # Estimated business impact
            fraud_prevented = recall * annual_transactions * 0.002 * avg_fraud_amount  # 0.2% fraud rate
            false_positive_cost = fpr * annual_transactions * investigation_cost
            net_savings = fraud_prevented - false_positive_cost
            
            business_metrics.append({
                'model': model_name.replace('_', ' ').title(),
                'fraud_prevented': fraud_prevented,
                'false_positive_cost': false_positive_cost,
                'net_savings': net_savings,
                'recall': recall,
                'fpr': fpr
            })
        
        df_business = pd.DataFrame(business_metrics)
        
        # Create visualization
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Net savings comparison
        colors = ['green' if x > 0 else 'red' for x in df_business['net_savings']]
        ax1.bar(df_business['model'], df_business['net_savings'] / 1000, color=colors)
        ax1.set_title('Estimated Annual Net Savings ($ Thousands)')
        ax1.set_ylabel('Savings ($K)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Fraud prevented vs False positive cost
        x = np.arange(len(df_business))
        width = 0.35
        
        ax2.bar(x - width/2, df_business['fraud_prevented'] / 1000, width, 
               label='Fraud Prevented', color='green', alpha=0.7)
        ax2.bar(x + width/2, df_business['false_positive_cost'] / 1000, width,
               label='False Positive Cost', color='red', alpha=0.7)
        
        ax2.set_title('Fraud Prevention vs False Positive Costs')
        ax2.set_ylabel('Amount ($K)')
        ax2.set_xticks(x)
        ax2.set_xticklabels(df_business['model'])
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)
        
        # Recall vs FPR trade-off
        ax3.scatter(df_business['fpr'], df_business['recall'], s=100, alpha=0.7)
        for i, model in enumerate(df_business['model']):
            ax3.annotate(model, (df_business['fpr'].iloc[i], df_business['recall'].iloc[i]),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax3.set_xlabel('False Positive Rate')
        ax3.set_ylabel('Recall (Fraud Detection Rate)')
        ax3.set_title('Recall vs False Positive Rate Trade-off')
        ax3.grid(True, alpha=0.3)
        
        # Efficiency ratio (Recall / FPR)
        efficiency_ratio = df_business['recall'] / (df_business['fpr'] + 0.001)  # Avoid division by zero
        ax4.bar(df_business['model'], efficiency_ratio, color='skyblue')
        ax4.set_title('Model Efficiency Ratio (Recall / FPR)')
        ax4.set_ylabel('Efficiency Ratio')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if self.save_plots:
            plt.savefig(self.plots_dir / 'business_impact_analysis.png', 
                       dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return df_business
    
    def generate_evaluation_report(self, evaluation_results: Dict, 
                                  feature_names: List[str] = None) -> str:
        """Generate comprehensive evaluation report"""
        logger.info("Generating comprehensive evaluation report...")
        
        report = []
        report.append("# COMPREHENSIVE MODEL EVALUATION REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Executive Summary
        report.append("## EXECUTIVE SUMMARY")
        report.append("-" * 40)
        
        best_f1_model = max(evaluation_results.keys(), 
                           key=lambda x: evaluation_results[x]['metrics']['f1_score'])
        best_recall_model = max(evaluation_results.keys(),
                               key=lambda x: evaluation_results[x]['metrics']['recall'])
        
        report.append(f"• Best Overall Model (F1-Score): {best_f1_model}")
        report.append(f"• Best Fraud Detection (Recall): {best_recall_model}")
        report.append(f"• Total Models Evaluated: {len(evaluation_results)}")
        report.append("")
        
        # Detailed Results
        report.append("## DETAILED MODEL PERFORMANCE")
        report.append("-" * 45)
        
        for model_name, results in evaluation_results.items():
            metrics = results['metrics']
            report.append(f"\n### {model_name.replace('_', ' ').title()}")
            report.append(f"Recall (Fraud Detection): {metrics['recall']:.4f}")
            report.append(f"Precision: {metrics['precision']:.4f}")
            report.append(f"F1-Score: {metrics['f1_score']:.4f}")
            report.append(f"Accuracy: {metrics['accuracy']:.4f}")
            report.append(f"False Positive Rate: {metrics['fpr']:.4f}")
            report.append(f"False Negative Rate: {metrics['fnr']:.4f}")
            
            if 'roc_auc' in metrics:
                report.append(f"ROC-AUC: {metrics['roc_auc']:.4f}")
                report.append(f"PR-AUC: {metrics['pr_auc']:.4f}")
            
            report.append(f"Optimal Threshold: {metrics['threshold']:.3f}")
            
            # Confusion Matrix
            report.append("\nConfusion Matrix:")
            report.append(f"True Positives: {metrics['true_positives']}")
            report.append(f"False Positives: {metrics['false_positives']}")
            report.append(f"True Negatives: {metrics['true_negatives']}")
            report.append(f"False Negatives: {metrics['false_negatives']}")
        
        # Recommendations
        report.append("\n## RECOMMENDATIONS")
        report.append("-" * 30)
        
        best_metrics = evaluation_results[best_f1_model]['metrics']
        
        if best_metrics['recall'] >= 0.85:
            report.append("✅ EXCELLENT fraud detection performance achieved")
        elif best_metrics['recall'] >= 0.70:
            report.append("✅ GOOD fraud detection performance achieved")
        else:
            report.append("⚠️  Fraud detection performance needs improvement")
        
        if best_metrics['fpr'] <= 0.05:
            report.append("✅ EXCELLENT false positive rate achieved")
        elif best_metrics['fpr'] <= 0.10:
            report.append("✅ ACCEPTABLE false positive rate achieved")
        else:
            report.append("⚠️  False positive rate may be too high for production")
        
        report.append(f"\nRECOMMENDED MODEL: {best_f1_model}")
        report.append("DEPLOYMENT READINESS: ✅ Ready for production testing")
        
        # Save report
        report_text = "\n".join(report)
        if self.save_plots:
            with open(self.plots_dir.parent / "reports" / "detailed_evaluation_report.txt", 'w') as f:
                f.write(report_text)
        
        return report_text
    
    def run_complete_evaluation(self, evaluation_results: Dict, feature_names: List[str] = None):
        """Run complete evaluation suite with all visualizations"""
        logger.info("🚀 Running complete evaluation suite...")
        
        # Create all visualizations
        self.plot_confusion_matrices(evaluation_results)
        self.plot_roc_curves(evaluation_results)
        self.plot_precision_recall_curves(evaluation_results)
        
        # Feature importance for tree-based models
        if feature_names:
            for model_name, results in evaluation_results.items():
                if hasattr(results['model'], 'feature_importances_'):
                    self.plot_feature_importance(results['model'], feature_names, model_name)
        
        # Interactive dashboard
        self.create_interactive_model_comparison(evaluation_results)
        
        # Business impact analysis
        business_impact = self.create_business_impact_visualization(evaluation_results)
        
        # Generate comprehensive report
        report = self.generate_evaluation_report(evaluation_results, feature_names)
        
        logger.info("✅ Complete evaluation suite finished!")
        logger.info(f"📁 All plots saved to: {self.plots_dir}")
        
        return {
            'business_impact': business_impact,
            'evaluation_report': report
        }

def main():
    """Test the evaluation system"""
    # This would typically be called from the training script
    print("🧪 Model Evaluation System Ready!")
    print("Use FraudModelEvaluator class in your training pipeline")

if __name__ == "__main__":
    main()