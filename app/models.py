"""
Model Management for FastAPI Application
This file handles model loading and serving for the API
"""

import os
import sys
import json
import joblib
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add src to path for imports
sys.path.append('src')
sys.path.append('.')

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages loading and serving of trained ML models"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.metadata = {}
        self.model_loaded = False
        self.best_model_name = None
        
    def load_models(self):
        """Load all trained models and metadata"""
        try:
            models_dir = Path("models")
            
            # Load metadata
            metadata_path = models_dir / "model_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                logger.info("✅ Model metadata loaded")
            
            # Load scalers
            scalers_path = models_dir / "scalers.pkl"
            if scalers_path.exists():
                self.scalers = joblib.load(scalers_path)
                logger.info("✅ Scalers loaded")
            
            # Load individual models
            model_count = 0
            for model_name, model_info in self.metadata.get('models', {}).items():
                model_path = models_dir / model_info['file_path']
                if model_path.exists():
                    try:
                        self.models[model_name] = joblib.load(model_path)
                        logger.info(f"✅ Loaded {model_name}")
                        model_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to load {model_name}: {e}")
            
            # Determine best model
            if self.models:
                performance_summary = self.metadata.get('performance_summary', {})
                if performance_summary:
                    self.best_model_name = max(
                        performance_summary.keys(),
                        key=lambda x: performance_summary[x].get('f1_score', 0)
                    )
                else:
                    self.best_model_name = list(self.models.keys())[0]
                
                logger.info(f"🏆 Best model selected: {self.best_model_name}")
                self.model_loaded = True
                return True
            
            logger.error("❌ No models loaded successfully")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}")
            return False
    
    def predict_fraud(self, features: np.ndarray, model_name: Optional[str] = None) -> Dict:
        """Make fraud prediction using specified model or best model"""
        if not self.model_loaded:
            raise RuntimeError("Models not loaded")
        
        # Use specified model or best model
        if model_name is None:
            model_name = self.best_model_name
        
        if not model_name or model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not available")
        
        model = self.models[model_name]
        
        try:
            # Prepare features based on model type
            if model_name in ['logistic_regression', 'ensemble']:
                if 'standard' in self.scalers:
                    features_processed = self.scalers['standard'].transform(features)
                else:
                    features_processed = features
            else:
                features_processed = features
            
            # Make predictions
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(features_processed)
                fraud_probability = float(probabilities[0][1])
                threshold = self.metadata.get('models', {}).get(model_name, {}).get('threshold', 0.5)
                is_fraud = fraud_probability >= threshold
                
            elif model_name == 'isolation_forest':
                anomaly_score = model.predict(features_processed)
                is_fraud = anomaly_score[0] == -1
                raw_scores = model.score_samples(features_processed)
                fraud_probability = float(1 / (1 + np.exp(raw_scores[0])))
                
            else:
                prediction = model.predict(features_processed)
                is_fraud = bool(prediction[0])
                fraud_probability = float(prediction[0])
            
            # Determine risk level
            if fraud_probability >= 0.8:
                risk_level = "HIGH"
            elif fraud_probability >= 0.5:
                risk_level = "MEDIUM"
            elif fraud_probability >= 0.2:
                risk_level = "LOW"
            else:
                risk_level = "VERY_LOW"
            
            return {
                "is_fraud": bool(is_fraud),
                "fraud_probability": fraud_probability,
                "risk_level": risk_level,
                "model_used": model_name,
                "confidence": abs(fraud_probability - 0.5) * 2,
                "prediction_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction error: {str(e)}")

# This can be imported by main.py
model_manager = ModelManager()