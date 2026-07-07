"""
ML Model Configuration and Registry

Centralized configuration for all ML models used in the application.
Defines model types, versions, and their metadata.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path
import os


@dataclass
class ModelConfig:
    """Configuration for a single ML model"""
    
    name: str                  # e.g., 'crop_recommendation'
    description: str           # Human-readable description
    model_type: str            # 'sklearn', 'keras', 'pytorch', etc.
    active_version: str        # Currently active version (e.g., 'v1.0.0')
    created_at: str            # ISO format timestamp
    updated_at: str            # ISO format timestamp
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class ModelRegistry:
    """
    Central registry for all ML models in the application.
    
    This maintains a mapping of all models, their versions, and metadata.
    """
    
    # Define all models used in the application
    MODELS = {
        'crop_recommendation': {
            'description': 'Random Forest model for crop recommendation based on soil and climate',
            'model_type': 'sklearn',
            'artifacts': ['label_encoder'],  # Related artifacts to save with model
            'performance_metrics': ['accuracy', 'f1_score', 'precision', 'recall'],
            'input_features': ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'],
            'version_history': [
                {
                    'version': 'v1.0.0',
                    'date': '2026-01-15',
                    'description': 'Initial production model',
                    'performance': {'accuracy': 0.89, 'f1_score': 0.87},
                    'status': 'archived'
                },
                {
                    'version': 'v1.1.0',
                    'date': '2026-02-01',
                    'description': 'Improved features, better precision',
                    'performance': {'accuracy': 0.92, 'f1_score': 0.90},
                    'status': 'stable'
                },
                {
                    'version': 'v1.2.0',
                    'date': '2026-02-15',
                    'description': 'Added seasonal adjustments',
                    'performance': {'accuracy': 0.94, 'f1_score': 0.93},
                    'status': 'active'
                }
            ]
        },
        'disease_detection': {
            'description': 'CNN model for detecting crop diseases from leaf images',
            'model_type': 'keras',
            'artifacts': ['label_encoder', 'image_preprocessor'],
            'performance_metrics': ['accuracy', 'auc', 'precision', 'recall'],
            'input_features': ['image_array'],
            'version_history': [
                {
                    'version': 'v1.0.0',
                    'date': '2026-01-10',
                    'description': 'Initial CNN model',
                    'performance': {'accuracy': 0.85, 'auc': 0.91},
                    'status': 'archived'
                },
                {
                    'version': 'v1.1.0',
                    'date': '2026-02-05',
                    'description': 'Data augmentation improvements',
                    'performance': {'accuracy': 0.91, 'auc': 0.95},
                    'status': 'active'
                }
            ]
        },
        'yield_prediction': {
            'description': 'Regression model for predicting crop yield',
            'model_type': 'sklearn',
            'artifacts': ['feature_scaler', 'label_encoder'],
            'performance_metrics': ['mse', 'rmse', 'r2_score', 'mae'],
            'input_features': ['area', 'production', 'soil_ph', 'rainfall'],
            'version_history': [
                {
                    'version': 'v1.0.0',
                    'date': '2026-01-20',
                    'description': 'Initial yield prediction model',
                    'performance': {'r2_score': 0.87, 'rmse': 0.12},
                    'status': 'active'
                }
            ]
        },
        'pest_detection': {
            'description': 'Model for detecting pest infestations',
            'model_type': 'sklearn',
            'artifacts': ['label_encoder', 'feature_scaler'],
            'performance_metrics': ['accuracy', 'precision', 'recall', 'f1_score'],
            'input_features': ['leaf_color', 'texture', 'shape', 'size'],
            'version_history': []
        }
    }
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Optional[Dict]:
        """Get configuration for a specific model"""
        return cls.MODELS.get(model_name)
    
    @classmethod
    def get_all_models(cls) -> Dict[str, Dict]:
        """Get all model configurations"""
        return cls.MODELS.copy()
    
    @classmethod
    def list_model_names(cls) -> List[str]:
        """Get list of all model names"""
        return list(cls.MODELS.keys())
    
    @classmethod
    def is_model_registered(cls, model_name: str) -> bool:
        """Check if a model is registered"""
        return model_name in cls.MODELS
    
    @classmethod
    def add_model_to_registry(cls, model_name: str, config: Dict) -> None:
        """Add a new model to the registry"""
        if model_name not in cls.MODELS:
            cls.MODELS[model_name] = config
    
    @classmethod
    def export_registry(cls, filepath: str) -> bool:
        """Export registry to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(cls.MODELS, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to export registry: {str(e)}")
            return False
    
    @classmethod
    def import_registry(cls, filepath: str) -> bool:
        """Import registry from JSON file"""
        try:
            with open(filepath, 'r') as f:
                cls.MODELS = json.load(f)
            return True
        except Exception as e:
            print(f"Failed to import registry: {str(e)}")
            return False


# Default model configuration
DEFAULT_MODELS_CONFIG = {
    'crop_recommendation': ModelRegistry.MODELS.get('crop_recommendation'),
    'disease_detection': ModelRegistry.MODELS.get('disease_detection'),
    'yield_prediction': ModelRegistry.MODELS.get('yield_prediction'),
}


def get_model_config(model_name: str) -> Optional[Dict]:
    """Convenience function to get model config"""
    return ModelRegistry.get_model_config(model_name)


def list_all_models() -> Dict[str, Dict]:
    """Convenience function to list all models"""
    return ModelRegistry.get_all_models()
