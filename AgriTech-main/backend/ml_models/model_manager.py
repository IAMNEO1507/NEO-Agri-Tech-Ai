"""
ML Model Versioning and Management System

This module provides a unified interface for managing ML model versions,
including loading, versioning, logging, and rollback capabilities.

Features:
- Semantic versioning support (v1.0.0, v1.1.0, etc.)
- Date-based tagging (2026_02_01, 2026_02_02, etc.)
- Model metadata tracking (creation time, performance metrics, etc.)
- Automatic version logging for audit trails
- Safe rollback to previous stable versions
- Model performance tracking
"""

import os
import json
import logging
import joblib
import pickle
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Supported model types"""
    SKLEARN = "sklearn"  # joblib format
    KERAS = "keras"      # h5 format
    PYTORCH = "pytorch"  # pth format
    PICKLE = "pickle"    # pickle format
    CUSTOM = "custom"    # Custom format


class ModelVersioning:
    """
    Main class for managing ML model versions and rollbacks.
    
    Directory structure:
    backend/ml_models/
    ├── {model_name}/
    │   ├── v1.0.0/
    │   │   ├── model.pkl
    │   │   ├── metadata.json
    │   │   └── artifacts/
    │   ├── v1.1.0/
    │   │   ├── model.pkl
    │   │   ├── metadata.json
    │   │   └── artifacts/
    │   ├── active_version.json
    │   └── changelog.md
    ├── versioning_logs/
    │   └── {model_name}_usage.log
    """
    
    def __init__(self, base_models_path: str = None):
        """
        Initialize the model versioning system.
        
        Args:
            base_models_path: Base path where models are stored.
                            Defaults to backend/ml_models/
        """
        if base_models_path is None:
            base_models_path = os.path.join(
                os.path.dirname(__file__)
            )
        
        self.base_path = Path(base_models_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.logs_path = self.base_path / "versioning_logs"
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ModelVersioning initialized with base path: {self.base_path}")
    
    def create_version(
        self,
        model_name: str,
        model: Any,
        version: str,
        model_type: ModelType = ModelType.SKLEARN,
        metadata: Dict[str, Any] = None,
        artifacts: Dict[str, Any] = None,
        description: str = ""
    ) -> bool:
        """
        Create a new version of a model.
        
        Args:
            model_name: Name of the model (e.g., 'crop_recommendation')
            model: The model object to save
            version: Version string (e.g., 'v1.0.0' or '2026_02_01')
            model_type: Type of model (from ModelType enum)
            metadata: Additional metadata (dict)
            artifacts: Related artifacts like label encoders, scalers, etc.
            description: Description of changes in this version
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create version directory
            model_dir = self.base_path / model_name
            version_dir = model_dir / version
            version_dir.mkdir(parents=True, exist_ok=True)
            
            # Save model based on type
            model_path = version_dir / f"model_{model_type.value}"
            self._save_model(model, model_path, model_type)
            
            # Save artifacts if provided
            if artifacts:
                artifacts_dir = version_dir / "artifacts"
                artifacts_dir.mkdir(exist_ok=True)
                for artifact_name, artifact_obj in artifacts.items():
                    artifact_path = artifacts_dir / f"{artifact_name}.pkl"
                    joblib.dump(artifact_obj, artifact_path)
                    logger.info(f"Saved artifact: {artifact_name}")
            
            # Create and save metadata
            metadata_path = version_dir / "metadata.json"
            version_metadata = self._create_metadata(
                version, model_type, metadata, description
            )
            with open(metadata_path, 'w') as f:
                json.dump(version_metadata, f, indent=2, default=str)
            
            logger.info(
                f"Created model version: {model_name}/{version}"
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to create model version: {str(e)}")
            return False
    
    def load_model(
        self,
        model_name: str,
        version: str = None,
        return_artifacts: bool = False
    ) -> Union[Any, tuple]:
        """
        Load a specific version of a model.
        
        Args:
            model_name: Name of the model
            version: Version to load (if None, loads active version)
            return_artifacts: If True, returns (model, artifacts_dict)
        
        Returns:
            Loaded model object, or tuple of (model, artifacts) if return_artifacts=True
        """
        try:
            # Get version if not specified
            if version is None:
                version = self.get_active_version(model_name)
                if version is None:
                    logger.warning(f"No active version found for {model_name}")
                    return None
            
            version_dir = self.base_path / model_name / version
            
            if not version_dir.exists():
                logger.error(f"Version not found: {model_name}/{version}")
                return None
            
            # Log the model usage
            self._log_model_usage(model_name, version, "load")
            
            # Find and load model file
            model_path = self._find_model_file(version_dir)
            if not model_path:
                logger.error(f"Model file not found in {version_dir}")
                return None
            
            model = self._load_model_file(model_path)
            
            # Load artifacts if requested
            if return_artifacts:
                artifacts = self._load_artifacts(version_dir)
                logger.info(f"Loaded model {model_name}/{version} with artifacts")
                return model, artifacts
            
            logger.info(f"Loaded model {model_name}/{version}")
            return model
        
        except Exception as e:
            logger.error(
                f"Failed to load model {model_name}/{version}: {str(e)}"
            )
            return None
    
    def set_active_version(self, model_name: str, version: str) -> bool:
        """
        Set the active version for a model.
        
        Args:
            model_name: Name of the model
            version: Version to set as active
        
        Returns:
            bool: True if successful
        """
        try:
            model_dir = self.base_path / model_name
            version_dir = model_dir / version
            
            if not version_dir.exists():
                logger.error(f"Version not found: {model_name}/{version}")
                return False
            
            # Save active version
            active_version_path = model_dir / "active_version.json"
            active_config = {
                "active_version": version,
                "activated_at": datetime.utcnow().isoformat(),
                "activated_by": "system"
            }
            
            with open(active_version_path, 'w') as f:
                json.dump(active_config, f, indent=2)
            
            # Log the version switch
            self._log_version_switch(model_name, version)
            
            logger.info(f"Set active version for {model_name}: {version}")
            return True
        
        except Exception as e:
            logger.error(
                f"Failed to set active version: {str(e)}"
            )
            return False
    
    def get_active_version(self, model_name: str) -> Optional[str]:
        """
        Get the currently active version of a model.
        
        Args:
            model_name: Name of the model
        
        Returns:
            Active version string, or None if not found
        """
        try:
            model_dir = self.base_path / model_name
            active_version_path = model_dir / "active_version.json"
            
            if not active_version_path.exists():
                logger.warning(
                    f"No active version config found for {model_name}"
                )
                return None
            
            with open(active_version_path, 'r') as f:
                config = json.load(f)
                return config.get("active_version")
        
        except Exception as e:
            logger.error(f"Failed to get active version: {str(e)}")
            return None
    
    def rollback_to_version(self, model_name: str, version: str) -> bool:
        """
        Rollback to a previous version of a model.
        
        Args:
            model_name: Name of the model
            version: Version to rollback to
        
        Returns:
            bool: True if successful
        """
        try:
            model_dir = self.base_path / model_name
            version_dir = model_dir / version
            
            if not version_dir.exists():
                logger.error(f"Cannot rollback: Version not found {model_name}/{version}")
                return False
            
            # Test loading the model before rollback
            test_load = self._find_model_file(version_dir)
            if not test_load:
                logger.error(f"Cannot rollback: Model file not accessible {model_name}/{version}")
                return False
            
            # Get current active version for backup
            current_version = self.get_active_version(model_name)
            
            # Set the new active version
            if not self.set_active_version(model_name, version):
                logger.error("Failed to set active version during rollback")
                return False
            
            logger.warning(
                f"Rolled back {model_name} from {current_version} to {version}"
            )
            
            # Log rollback event
            self._log_rollback(model_name, current_version, version)
            
            return True
        
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return False
    
    def list_versions(self, model_name: str) -> List[Dict[str, Any]]:
        """
        List all available versions of a model.
        
        Args:
            model_name: Name of the model
        
        Returns:
            List of version info dicts
        """
        try:
            model_dir = self.base_path / model_name
            
            if not model_dir.exists():
                logger.warning(f"Model not found: {model_name}")
                return []
            
            versions = []
            active_version = self.get_active_version(model_name)
            
            for version_dir in sorted(model_dir.iterdir()):
                if version_dir.name.startswith('active_version') or version_dir.name == 'changelog.md':
                    continue
                
                metadata_path = version_dir / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        metadata['is_active'] = (version_dir.name == active_version)
                        versions.append(metadata)
            
            return sorted(versions, key=lambda x: x.get('created_at'), reverse=True)
        
        except Exception as e:
            logger.error(f"Failed to list versions: {str(e)}")
            return []
    
    def get_version_metadata(
        self,
        model_name: str,
        version: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific model version.
        
        Args:
            model_name: Name of the model
            version: Version identifier
        
        Returns:
            Metadata dict or None if not found
        """
        try:
            metadata_path = self.base_path / model_name / version / "metadata.json"
            
            if not metadata_path.exists():
                logger.warning(f"Metadata not found: {model_name}/{version}")
                return None
            
            with open(metadata_path, 'r') as f:
                return json.load(f)
        
        except Exception as e:
            logger.error(f"Failed to get version metadata: {str(e)}")
            return None
    
    def add_performance_metrics(
        self,
        model_name: str,
        version: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """
        Add or update performance metrics for a model version.
        
        Args:
            model_name: Name of the model
            version: Version identifier
            metrics: Performance metrics dict
                    (e.g., {'accuracy': 0.95, 'f1_score': 0.92})
        
        Returns:
            bool: True if successful
        """
        try:
            metadata_path = self.base_path / model_name / version / "metadata.json"
            
            if not metadata_path.exists():
                logger.warning(f"Metadata not found: {model_name}/{version}")
                return False
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Update or create performance_metrics section
            if 'performance_metrics' not in metadata:
                metadata['performance_metrics'] = {}
            
            metadata['performance_metrics'].update(metrics)
            metadata['metrics_updated_at'] = datetime.utcnow().isoformat()
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            logger.info(
                f"Updated performance metrics for {model_name}/{version}"
            )
            return True
        
        except Exception as e:
            logger.error(f"Failed to add performance metrics: {str(e)}")
            return False
    
    def delete_version(self, model_name: str, version: str) -> bool:
        """
        Delete a specific model version.
        
        Args:
            model_name: Name of the model
            version: Version to delete
        
        Returns:
            bool: True if successful
        """
        try:
            version_dir = self.base_path / model_name / version
            
            if not version_dir.exists():
                logger.error(f"Version not found: {model_name}/{version}")
                return False
            
            # Don't allow deleting active version
            if version == self.get_active_version(model_name):
                logger.error(
                    f"Cannot delete active version: {model_name}/{version}"
                )
                return False
            
            shutil.rmtree(version_dir)
            logger.info(f"Deleted model version: {model_name}/{version}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete version: {str(e)}")
            return False
    
    # ==================== Private Helper Methods ====================
    
    def _save_model(
        self,
        model: Any,
        model_path: Path,
        model_type: ModelType
    ) -> None:
        """Save model based on its type"""
        if model_type == ModelType.SKLEARN or model_type == ModelType.PICKLE:
            joblib.dump(model, f"{model_path}.pkl")
        elif model_type == ModelType.KERAS:
            model.save(f"{model_path}.h5")
        elif model_type == ModelType.PYTORCH:
            import torch
            torch.save(model, f"{model_path}.pth")
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def _load_model_file(self, model_path: Path) -> Any:
        """Load model file based on its extension"""
        model_path_str = str(model_path)
        
        if model_path_str.endswith('.pkl'):
            return joblib.load(model_path_str)
        elif model_path_str.endswith('.h5'):
            from tensorflow import keras
            return keras.models.load_model(model_path_str)
        elif model_path_str.endswith('.pth'):
            import torch
            return torch.load(model_path_str)
        else:
            raise ValueError(f"Unsupported model format: {model_path}")
    
    def _find_model_file(self, version_dir: Path) -> Optional[Path]:
        """Find the model file in a version directory"""
        for extension in ['.pkl', '.h5', '.pth']:
            for file in version_dir.glob(f"*model*{extension}"):
                return file
        return None
    
    def _load_artifacts(self, version_dir: Path) -> Dict[str, Any]:
        """Load all artifacts from a version directory"""
        artifacts = {}
        artifacts_dir = version_dir / "artifacts"
        
        if artifacts_dir.exists():
            for artifact_file in artifacts_dir.glob("*.pkl"):
                artifact_name = artifact_file.stem
                artifacts[artifact_name] = joblib.load(str(artifact_file))
        
        return artifacts
    
    def _create_metadata(
        self,
        version: str,
        model_type: ModelType,
        metadata: Dict[str, Any] = None,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create metadata JSON for a model version"""
        meta = {
            "version": version,
            "model_type": model_type.value,
            "created_at": datetime.utcnow().isoformat(),
            "description": description,
            "performance_metrics": {}
        }
        
        if metadata:
            meta.update(metadata)
        
        return meta
    
    def _log_model_usage(
        self,
        model_name: str,
        version: str,
        action: str
    ) -> None:
        """Log model usage for audit trail"""
        try:
            log_path = self.logs_path / f"{model_name}_usage.log"
            
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "model_name": model_name,
                "version": version,
                "action": action
            }
            
            with open(log_path, 'a') as f:
                json.dump(log_entry, f)
                f.write('\n')
        
        except Exception as e:
            logger.error(f"Failed to log model usage: {str(e)}")
    
    def _log_version_switch(self, model_name: str, version: str) -> None:
        """Log version switch event"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "model_name": model_name,
            "new_version": version,
            "action": "version_switch"
        }
        
        log_path = self.logs_path / f"{model_name}_usage.log"
        with open(log_path, 'a') as f:
            json.dump(log_entry, f)
            f.write('\n')
    
    def _log_rollback(
        self,
        model_name: str,
        from_version: str,
        to_version: str
    ) -> None:
        """Log rollback event"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "model_name": model_name,
            "from_version": from_version,
            "to_version": to_version,
            "action": "rollback"
        }
        
        log_path = self.logs_path / f"{model_name}_usage.log"
        with open(log_path, 'a') as f:
            json.dump(log_entry, f)
            f.write('\n')


# Global instance for easy access
_model_versioning = None

def get_model_manager() -> ModelVersioning:
    """Get or create the global model manager instance"""
    global _model_versioning
    
    if _model_versioning is None:
        _model_versioning = ModelVersioning()
    
    return _model_versioning
