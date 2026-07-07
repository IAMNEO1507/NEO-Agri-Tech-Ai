"""
ML Model Versioning API

Flask Blueprint for managing model versions, performing rollbacks,
and retrieving model metadata.
"""

from flask import Blueprint, request, jsonify
from backend.ml_models.model_manager import get_model_manager, ModelType
from backend.ml_models.model_registry import ModelRegistry
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

model_versioning_bp = Blueprint(
    'model_versioning',
    __name__,
    url_prefix='/api/v1/models'
)


@model_versioning_bp.route('/registry', methods=['GET'])
def get_registry():
    """
    Get the complete model registry with all registered models.
    
    Returns:
        List of all registered models with their metadata
    """
    try:
        all_models = ModelRegistry.get_all_models()
        return jsonify({
            'success': True,
            'total_models': len(all_models),
            'models': all_models
        }), 200
    except Exception as e:
        logger.error(f"Failed to get model registry: {str(e)}")
        return jsonify({'error': 'Failed to retrieve registry'}), 500


@model_versioning_bp.route('/<model_name>/versions', methods=['GET'])
def list_model_versions(model_name):
    """
    List all available versions for a specific model.
    
    Args:
        model_name: Name of the model
    
    Returns:
        List of all versions with metadata
    """
    try:
        # Check if model is registered
        if not ModelRegistry.is_model_registered(model_name):
            return jsonify({
                'error': f'Model not registered: {model_name}'
            }), 404
        
        model_manager = get_model_manager()
        versions = model_manager.list_versions(model_name)
        active_version = model_manager.get_active_version(model_name)
        
        return jsonify({
            'success': True,
            'model_name': model_name,
            'total_versions': len(versions),
            'active_version': active_version,
            'versions': versions
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to list model versions: {str(e)}")
        return jsonify({'error': 'Failed to list versions'}), 500


@model_versioning_bp.route('/<model_name>/active', methods=['GET'])
def get_active_model_version(model_name):
    """
    Get the currently active version of a model.
    
    Args:
        model_name: Name of the model
    
    Returns:
        Active version information
    """
    try:
        if not ModelRegistry.is_model_registered(model_name):
            return jsonify({
                'error': f'Model not registered: {model_name}'
            }), 404
        
        model_manager = get_model_manager()
        active_version = model_manager.get_active_version(model_name)
        
        if not active_version:
            return jsonify({
                'error': f'No active version found for {model_name}'
            }), 404
        
        metadata = model_manager.get_version_metadata(model_name, active_version)
        
        return jsonify({
            'success': True,
            'model_name': model_name,
            'active_version': active_version,
            'metadata': metadata
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get active model version: {str(e)}")
        return jsonify({'error': 'Failed to get active version'}), 500


@model_versioning_bp.route('/<model_name>/<version>/metadata', methods=['GET'])
def get_model_version_metadata(model_name, version):
    """
    Get metadata for a specific model version.
    
    Args:
        model_name: Name of the model
        version: Version identifier
    
    Returns:
        Version metadata including performance metrics
    """
    try:
        if not ModelRegistry.is_model_registered(model_name):
            return jsonify({
                'error': f'Model not registered: {model_name}'
            }), 404
        
        model_manager = get_model_manager()
        metadata = model_manager.get_version_metadata(model_name, version)
        
        if not metadata:
            return jsonify({
                'error': f'Version not found: {model_name}/{version}'
            }), 404
        
        return jsonify({
            'success': True,
            'model_name': model_name,
            'version': version,
            'metadata': metadata
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get version metadata: {str(e)}")
        return jsonify({'error': 'Failed to retrieve metadata'}), 500


@model_versioning_bp.route('/<model_name>/set-active', methods=['POST'])
def set_active_version(model_name):
    """
    Set a specific version as the active version for a model.
    
    Args:
        model_name: Name of the model
    
    Request JSON:
        {
            "version": "v1.2.0"
        }
    
    Returns:
        Success or error response
    """
    try:
        data = request.get_json()
        
        if not data or 'version' not in data:
            return jsonify({
                'error': 'Missing required field: version'
            }), 400
        
        version = data['version']
        
        if not ModelRegistry.is_model_registered(model_name):
            return jsonify({
                'error': f'Model not registered: {model_name}'
            }), 404
        
        model_manager = get_model_manager()
        
        # Test load the model to ensure it's valid
        test_model = model_manager.load_model(model_name, version)
        if test_model is None:
            return jsonify({
                'error': f'Failed to load model version: {model_name}/{version}'
            }), 400
        
        # Set as active
        if not model_manager.set_active_version(model_name, version):
            return jsonify({
                'error': f'Failed to set active version'
            }), 500
        
        return jsonify({
            'success': True,
            'message': f'Set {model_name} active version to {version}',
            'model_name': model_name,
            'new_active_version': version
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to set active version: {str(e)}")
        return jsonify({'error': 'Failed to set active version'}), 500


@model_versioning_bp.route('/<model_name>/rollback', methods=['POST'])
def rollback_model_version(model_name):
    """
    Rollback a model to a previous version.
    
    Args:
        model_name: Name of the model
    
    Request JSON:
        {
            "target_version": "v1.1.0",
            "reason": "Latest version causing poor predictions"  // optional
        }
    
    Returns:
        Success or error response
    """
    try:
        data = request.get_json()
        
        if not data or 'target_version' not in data:
            return jsonify({
                'error': 'Missing required field: target_version'
            }), 400
        
        target_version = data['target_version']
        reason = data.get('reason', 'User initiated rollback')
        
        if not ModelRegistry.is_model_registered(model_name):
            return jsonify({
                'error': f'Model not registered: {model_name}'
            }), 404
        
        model_manager = get_model_manager()
        current_version = model_manager.get_active_version(model_name)
        
        if current_version == target_version:
            return jsonify({
                'error': f'Model is already at version {target_version}'
            }), 400
        
        # Perform rollback
        if not model_manager.rollback_to_version(model_name, target_version):
            return jsonify({
                'error': f'Failed to rollback {model_name} to {target_version}'
            }), 500
        
        logger.warning(
            f"Model {model_name} rolled back from {current_version} to "
            f"{target_version}. Reason: {reason}"
        )
        
        return jsonify({
            'success': True,
            'message': f'Successfully rolled back {model_name}',
            'model_name': model_name,
            'previous_version': current_version,
            'new_version': target_version,
            'reason': reason
        }), 200
    
    except Exception as e:
        logger.error(f"Rollback operation failed: {str(e)}")
        return jsonify({'error': 'Rollback operation failed'}), 500


@model_versioning_bp.route('/<model_name>/performance', methods=['POST'])
def update_model_performance(model_name):
    """
    Add or update performance metrics for a model version.
    
    Args:
        model_name: Name of the model
    
    Request JSON:
        {
            "version": "v1.2.0",
            "metrics": {
                "accuracy": 0.94,
                "f1_score": 0.93,
                "precision": 0.95,
                "recall": 0.92
            }
        }
    
    Returns:
        Success or error response
    """
    try:
        data = request.get_json()
        
        required_fields = ['version', 'metrics']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        version = data['version']
        metrics = data['metrics']
        
        if not isinstance(metrics, dict):
            return jsonify({
                'error': 'Metrics must be a dictionary'
            }), 400
        
        if not ModelRegistry.is_model_registered(model_name):
            return jsonify({
                'error': f'Model not registered: {model_name}'
            }), 404
        
        model_manager = get_model_manager()
        
        if not model_manager.add_performance_metrics(model_name, version, metrics):
            return jsonify({
                'error': f'Failed to update metrics for {model_name}/{version}'
            }), 500
        
        return jsonify({
            'success': True,
            'message': f'Updated performance metrics for {model_name}/{version}',
            'model_name': model_name,
            'version': version,
            'metrics': metrics
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to update performance metrics: {str(e)}")
        return jsonify({'error': 'Failed to update metrics'}), 500


@model_versioning_bp.route('/<model_name>/<version>/delete', methods=['DELETE'])
def delete_model_version(model_name, version):
    """
    Delete a specific model version (cannot delete active version).
    
    Args:
        model_name: Name of the model
        version: Version to delete
    
    Returns:
        Success or error response
    """
    try:
        if not ModelRegistry.is_model_registered(model_name):
            return jsonify({
                'error': f'Model not registered: {model_name}'
            }), 404
        
        model_manager = get_model_manager()
        
        if not model_manager.delete_version(model_name, version):
            return jsonify({
                'error': f'Failed to delete {model_name}/{version}'
            }), 500
        
        logger.info(f"Deleted model version: {model_name}/{version}")
        
        return jsonify({
            'success': True,
            'message': f'Deleted model version {model_name}/{version}',
            'model_name': model_name,
            'deleted_version': version
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to delete model version: {str(e)}")
        return jsonify({'error': 'Failed to delete version'}), 500


@model_versioning_bp.route('/<model_name>/health', methods=['GET'])
def check_model_health(model_name):
    """
    Check the health status of a model.
    
    Args:
        model_name: Name of the model
    
    Returns:
        Health status and diagnostics
    """
    try:
        if not ModelRegistry.is_model_registered(model_name):
            return jsonify({
                'error': f'Model not registered: {model_name}'
            }), 404
        
        model_manager = get_model_manager()
        active_version = model_manager.get_active_version(model_name)
        
        if not active_version:
            return jsonify({
                'model_name': model_name,
                'status': 'unhealthy',
                'reason': 'No active version set'
            }), 503
        
        # Try to load the active model
        model = model_manager.load_model(model_name, active_version)
        
        if model is None:
            return jsonify({
                'model_name': model_name,
                'status': 'unhealthy',
                'active_version': active_version,
                'reason': 'Failed to load active model'
            }), 503
        
        metadata = model_manager.get_version_metadata(model_name, active_version)
        
        return jsonify({
            'model_name': model_name,
            'status': 'healthy',
            'active_version': active_version,
            'loadable': True,
            'metadata': metadata
        }), 200
    
    except Exception as e:
        logger.error(f"Health check failed for {model_name}: {str(e)}")
        return jsonify({
            'model_name': model_name,
            'status': 'error',
            'error': str(e)
        }), 500
