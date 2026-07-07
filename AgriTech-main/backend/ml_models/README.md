# ML Model Versioning and Rollback System

## Overview

The ML Model Versioning and Rollback System provides a robust mechanism for managing machine learning model versions in the AgriTech application. It enables safe deployments, easy rollbacks, and comprehensive audit trails for all model changes.

## Key Features

✅ **Semantic Versioning Support** - Version models using standard semantic versioning (v1.0.0, v1.1.0, etc.)
✅ **Date-based Tagging** - Alternative tagging with dates (2026_02_01, 2026_02_15, etc.)
✅ **Model Artifacts Management** - Store related artifacts like label encoders and preprocessors
✅ **Performance Metrics Tracking** - Record and monitor model performance metrics over versions
✅ **Safe Rollback Mechanism** - Quickly rollback to previous stable versions
✅ **Audit Logging** - Complete audit trail of all model operations
✅ **Multi-Format Support** - Support for sklearn, Keras, PyTorch, and custom model formats
✅ **Version Metadata** - Rich metadata for each version including descriptions and timestamps
✅ **Model Health Checks** - Verify model availability and loadability

## Directory Structure

```
backend/ml_models/
├── model_manager.py              # Core versioning system
├── model_registry.py             # Model registry and configuration
├── migrate_models.py             # Migration script for existing models
├── __init__.py                   # Package initialization
├── crop_recommendation/
│   ├── v1.0.0/
│   │   ├── model_sklearn.pkl
│   │   ├── metadata.json
│   │   └── artifacts/
│   │       ├── label_encoder.pkl
│   │       └── ...
│   ├── v1.1.0/
│   │   ├── model_sklearn.pkl
│   │   ├── metadata.json
│   │   └── artifacts/
│   ├── v1.2.0/
│   │   ├── model_sklearn.pkl
│   │   ├── metadata.json
│   │   └── artifacts/
│   ├── active_version.json       # Points to current active version
│   └── changelog.md              # Version changelog
├── disease_detection/
│   ├── v1.0.0/
│   │   ├── model_keras.h5
│   │   ├── metadata.json
│   │   └── artifacts/
│   ├── v1.1.0/
│   │   ├── model_keras.h5
│   │   ├── metadata.json
│   │   └── artifacts/
│   ├── active_version.json
│   └── changelog.md
└── versioning_logs/
    ├── crop_recommendation_usage.log
    ├── disease_detection_usage.log
    └── ...
```

## Quick Start

### 1. Creating a New Model Version

```python
from backend.ml_models import get_model_manager, ModelType

# Get the model manager
model_manager = get_model_manager()

# Create a new version
model_manager.create_version(
    model_name='crop_recommendation',
    model=trained_model,
    version='v1.2.0',
    model_type=ModelType.SKLEARN,
    metadata={
        'training_date': '2026-02-15',
        'training_samples': 5000,
        'features_used': ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    },
    artifacts={
        'label_encoder': label_encoder,
        'feature_scaler': scaler
    },
    description='Added seasonal adjustments for better accuracy'
)
```

### 2. Loading a Model

```python
# Load the active version
model = model_manager.load_model('crop_recommendation')

# Load a specific version
model = model_manager.load_model('crop_recommendation', 'v1.1.0')

# Load model with artifacts
model, artifacts = model_manager.load_model(
    'crop_recommendation',
    return_artifacts=True
)
label_encoder = artifacts['label_encoder']
```

### 3. Making a Version Active

```python
# Set a specific version as active
model_manager.set_active_version('crop_recommendation', 'v1.2.0')

# Verify it's now active
active = model_manager.get_active_version('crop_recommendation')
print(f"Active version: {active}")  # Output: v1.2.0
```

### 4. Rolling Back to a Previous Version

```python
# Rollback to a previous version
model_manager.rollback_to_version('crop_recommendation', 'v1.1.0')

# All future predictions will use v1.1.0 until another version is activated
```

### 5. Listing All Versions

```python
# Get all versions of a model
versions = model_manager.list_versions('crop_recommendation')

for version_info in versions:
    print(f"Version: {version_info['version']}")
    print(f"Active: {version_info.get('is_active', False)}")
    print(f"Created: {version_info['created_at']}")
    print(f"Description: {version_info['description']}")
    print()
```

### 6. Updating Performance Metrics

```python
# Add or update performance metrics
model_manager.add_performance_metrics(
    'crop_recommendation',
    'v1.2.0',
    {
        'accuracy': 0.94,
        'f1_score': 0.93,
        'precision': 0.95,
        'recall': 0.92,
        'test_samples': 1000
    }
)
```

## REST API Endpoints

### Get Model Registry
```
GET /api/v1/models/registry
```

### List Model Versions
```
GET /api/v1/models/{model_name}/versions
```

Example:
```bash
curl http://localhost:5000/api/v1/models/crop_recommendation/versions
```

### Get Active Version
```
GET /api/v1/models/{model_name}/active
```

### Get Version Metadata
```
GET /api/v1/models/{model_name}/{version}/metadata
```

### Set Active Version
```
POST /api/v1/models/{model_name}/set-active
Content-Type: application/json

{
    "version": "v1.2.0"
}
```

### Rollback Model
```
POST /api/v1/models/{model_name}/rollback
Content-Type: application/json

{
    "target_version": "v1.1.0",
    "reason": "Latest version causing poor predictions"
}
```

### Update Performance Metrics
```
POST /api/v1/models/{model_name}/performance
Content-Type: application/json

{
    "version": "v1.2.0",
    "metrics": {
        "accuracy": 0.94,
        "f1_score": 0.93,
        "precision": 0.95,
        "recall": 0.92
    }
}
```

### Check Model Health
```
GET /api/v1/models/{model_name}/health
```

### Delete a Version
```
DELETE /api/v1/models/{model_name}/{version}/delete
```

## Migration from Legacy System

### Step 1: Run Migration Script

```bash
# Migrate all models
python backend/ml_models/migrate_models.py --migrate-all

# Migrate specific model
python backend/ml_models/migrate_models.py --migrate-crop

# Verify migration without making changes
python backend/ml_models/migrate_models.py --verify-only

# Show summary of current migrations
python backend/ml_models/migrate_models.py --summary
```

### Step 2: Verify Migration

The script will:
1. Load models from legacy locations
2. Create versioned storage structure
3. Set initial versions as active
4. Verify all models are loadable
5. Display summary of migrated models

## Supported Model Types

| Type | Format | Extension | Framework |
|------|--------|-----------|-----------|
| **SKLEARN** | Joblib | .pkl | scikit-learn |
| **KERAS** | H5 | .h5 | TensorFlow/Keras |
| **PYTORCH** | PyTorch | .pth | PyTorch |
| **PICKLE** | Pickle | .pkl | Python pickle |
| **CUSTOM** | Custom | varies | Custom format |

## Version Naming Conventions

### Semantic Versioning (Recommended)
- **v1.0.0** - Major.Minor.Patch
- **v1.0.0-beta** - Pre-release versions
- **v1.0.0+metadata** - Build metadata

### Date-based Versioning
- **2026_02_15** - YYYY_MM_DD format
- **2026_02_15_v1** - Date with version counter

## Metadata Structure

Each version includes metadata in `metadata.json`:

```json
{
  "version": "v1.2.0",
  "model_type": "sklearn",
  "created_at": "2026-02-15T10:30:45.123456",
  "description": "Added seasonal adjustments for better accuracy",
  "performance_metrics": {
    "accuracy": 0.94,
    "f1_score": 0.93,
    "precision": 0.95,
    "recall": 0.92,
    "test_samples": 1000
  },
  "metrics_updated_at": "2026-02-15T11:00:00.123456"
}
```

## Audit Logging

All model operations are logged to `versioning_logs/{model_name}_usage.log`:

```json
{"timestamp": "2026-02-15T10:30:45.123456", "model_name": "crop_recommendation", "version": "v1.2.0", "action": "version_created"}
{"timestamp": "2026-02-15T11:00:00.123456", "model_name": "crop_recommendation", "version": "v1.2.0", "action": "set_active"}
{"timestamp": "2026-02-15T12:15:30.123456", "model_name": "crop_recommendation", "version": "v1.2.0", "action": "load"}
{"timestamp": "2026-02-15T13:45:00.123456", "model_name": "crop_recommendation", "from_version": "v1.2.0", "to_version": "v1.1.0", "action": "rollback"}
```

## Best Practices

### 1. Versioning Strategy

```
v1.0.0 - Initial production release
v1.1.0 - Bug fixes and improvements
v1.2.0 - New features or major improvements
v2.0.0 - Breaking changes or architecture redesign
```

### 2. Always Test Before Rolling Back

```python
# Load the target version
test_model = model_manager.load_model('crop_recommendation', 'v1.1.0')

# Run quick validation
assert test_model is not None, "Failed to load model"
print("✓ Model loaded successfully")

# Only then perform rollback
model_manager.rollback_to_version('crop_recommendation', 'v1.1.0')
```

### 3. Document Changes in Descriptions

```python
model_manager.create_version(
    model_name='crop_recommendation',
    model=trained_model,
    version='v1.2.0',
    model_type=ModelType.SKLEARN,
    description="""
    v1.2.0 - Improved Seasonal Adjustments
    - Added temperature normalization
    - Fixed humidity scaling issue
    - Improved F1-score from 0.90 to 0.93
    - Tested on 1000 new samples
    """,
    ...
)
```

### 4. Monitor Performance Metrics

```python
# Regularly track performance
metrics = {
    'accuracy': 0.94,
    'f1_score': 0.93,
    'precision': 0.95,
    'recall': 0.92,
    'inference_time_ms': 45.2,
    'memory_usage_mb': 234.5
}

model_manager.add_performance_metrics(
    'crop_recommendation',
    'v1.2.0',
    metrics
)
```

### 5. Clean Up Old Versions

```python
# Remove old versions after confirming new version is stable
# (never delete the active version)
model_manager.delete_version('crop_recommendation', 'v1.0.0')
```

## Troubleshooting

### Model Not Loading

```python
# Check if version exists
versions = model_manager.list_versions('crop_recommendation')
print("Available versions:", [v['version'] for v in versions])

# Check metadata
metadata = model_manager.get_version_metadata('crop_recommendation', 'v1.2.0')
print(metadata)

# Verify model file exists
import os
version_dir = 'backend/ml_models/crop_recommendation/v1.2.0'
print("Files:", os.listdir(version_dir))
```

### Migration Errors

```bash
# Run migration with verbose output
python backend/ml_models/migrate_models.py --migrate-all

# Check logs for detailed error messages
# Check versioning_logs/crop_recommendation_usage.log
```

## Performance Considerations

- **Model Size**: Keep individual model files < 1GB for optimal performance
- **Artifacts**: Store only essential artifacts with each model version
- **Cleanup**: Regularly remove old versions to save disk space
- **Concurrency**: The system is thread-safe for read operations

## Future Enhancements

- [ ] Model compression and optimization
- [ ] A/B testing support (deploy multiple versions simultaneously)
- [ ] Automatic version rollback on performance degradation
- [ ] Model comparison and diff utilities
- [ ] Integration with model serving frameworks (TensorFlow Serving, MLflow)

## Support and Debugging

For detailed logs, check:
- `backend/ml_models/versioning_logs/{model_name}_usage.log` - Operation logs
- Application logs - Error and warning messages

Enable debug logging:
```python
import logging
logging.getLogger('backend.ml_models').setLevel(logging.DEBUG)
```

## Related Documentation

- [Model Registry Configuration](model_registry.py)
- [Model Manager API Reference](model_manager.py)
- [REST API Endpoints](../../api/v1/model_versioning.py)
- [Migration Guide](migrate_models.py)
