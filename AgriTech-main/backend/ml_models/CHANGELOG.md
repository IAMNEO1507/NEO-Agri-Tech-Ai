# Model Versioning CHANGELOG

This file documents the version history of all ML models used in the AgriTech application.

## Crop Recommendation Model

### v1.2.0 (2026-02-15)
**Status**: Active

**Changes**:
- Added seasonal adjustment factors
- Improved soil pH normalization
- Fine-tuned hyperparameters for better F1-score
- Added rainfall pattern recognition

**Performance Improvements**:
- Accuracy: 0.92 → 0.94 (+2%)
- F1-Score: 0.90 → 0.93 (+3%)
- Precision: 0.92 → 0.95 (+3%)
- Recall: 0.88 → 0.92 (+4%)

**Tested on**:
- 1,000 validation samples
- 10 different crop types
- Multiple soil and climate conditions

**Breaking Changes**: None

**Migration Notes**: Safe to upgrade directly from v1.1.0

---

### v1.1.0 (2026-02-01)
**Status**: Stable

**Changes**:
- Improved feature scaling
- Fixed data normalization issues
- Enhanced error handling for edge cases
- Updated label encoder

**Performance Improvements**:
- Accuracy: 0.89 → 0.92 (+3%)
- F1-Score: 0.87 → 0.90 (+3%)

**Tested on**:
- 500 validation samples
- 8 different crop types

**Breaking Changes**: None

**Migration Notes**: Recommended upgrade path from v1.0.0

---

### v1.0.0 (2026-01-15)
**Status**: Archived

**Description**:
- Initial production release
- Random Forest Classifier with 100 estimators
- Basic feature scaling and encoding

**Performance**:
- Accuracy: 0.89
- F1-Score: 0.87

**Known Issues**:
- Poor performance with extreme weather conditions
- Limited seasonal adjustment

**End of Life**: 2026-03-01 (recommended to upgrade)

---

## Disease Detection Model

### v1.1.0 (2026-02-05)
**Status**: Active

**Changes**:
- Added data augmentation (rotation, flip, zoom)
- Improved preprocessing pipeline
- Better handling of different lighting conditions
- Updated label encoder

**Performance Improvements**:
- Accuracy: 0.85 → 0.91 (+6%)
- AUC: 0.91 → 0.95 (+4%)
- Precision: 0.84 → 0.90 (+6%)
- Recall: 0.86 → 0.92 (+6%)

**Tested on**:
- 2,000 test images
- 15 different plant diseases
- Varying image qualities and angles

**Breaking Changes**: None

**Migration Notes**: Recommended for production deployment

---

### v1.0.0 (2026-01-10)
**Status**: Archived

**Description**:
- Initial CNN-based disease detection model
- Basic image preprocessing
- Limited training data

**Performance**:
- Accuracy: 0.85
- AUC: 0.91

**Known Issues**:
- Sensitive to image angle and lighting
- Limited disease types supported (10)
- Requires high image resolution

**End of Life**: 2026-03-01 (recommended to upgrade)

---

## Yield Prediction Model

### v1.0.0 (2026-01-20)
**Status**: Active

**Description**:
- Random Forest Regressor for crop yield prediction
- 100 estimators with max_depth=15
- Feature scaling for numerical inputs

**Performance**:
- R² Score: 0.87
- RMSE: 0.12
- MAE: 0.08

**Tested on**:
- 500 training samples
- 100 test samples

**Known Issues**: None

---

## Version Comparison Matrix

| Model | v1.0.0 Acc | Latest Acc | Improvement | Status |
|-------|-----------|-----------|------------|--------|
| Crop Recommendation | 0.89 | 0.94 | +5% | Active (v1.2.0) |
| Disease Detection | 0.85 | 0.91 | +6% | Active (v1.1.0) |
| Yield Prediction | 0.87 | 0.87 | - | Active (v1.0.0) |

---

## Rollback Guide

### When to Rollback

- Performance metrics degradation > 2%
- Systematic prediction errors detected
- Integration issues in production
- Data distribution changes detected

### Quick Rollback Steps

```bash
# Via API
curl -X POST http://localhost:5000/api/v1/models/crop_recommendation/rollback \
  -H "Content-Type: application/json" \
  -d '{
    "target_version": "v1.1.0",
    "reason": "Detected prediction anomalies in v1.2.0"
  }'

# Via Python
from backend.ml_models import get_model_manager
model_manager = get_model_manager()
model_manager.rollback_to_version('crop_recommendation', 'v1.1.0')
```

---

## Version Release Schedule

**Regular Updates**: First Monday of every month
**Security Patches**: As needed
**Major Releases**: Quarterly

Next Scheduled Release: 2026-03-01

---

## Performance Tracking

### Crop Recommendation - v1.2.0

**Date**: 2026-02-15 12:00:00 UTC

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Accuracy | 0.94 | > 0.90 | ✅ Pass |
| F1-Score | 0.93 | > 0.90 | ✅ Pass |
| Precision | 0.95 | > 0.90 | ✅ Pass |
| Recall | 0.92 | > 0.88 | ✅ Pass |
| Inference Time | 45ms | < 100ms | ✅ Pass |
| Memory Usage | 234MB | < 500MB | ✅ Pass |

---

## Dependencies and Requirements

### Crop Recommendation
- scikit-learn >= 0.24.0
- numpy >= 1.19.0
- joblib >= 1.0.0

### Disease Detection
- tensorflow >= 2.5.0
- keras >= 2.4.0
- opencv-python >= 4.5.0

### Yield Prediction
- scikit-learn >= 0.24.0
- numpy >= 1.19.0
- joblib >= 1.0.0

---

## Notes

- All versions are tested on production-like environments
- Performance metrics are measured on validation sets
- Models are regularly monitored for drift
- Users are notified before major version updates
