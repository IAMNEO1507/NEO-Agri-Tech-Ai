"""
Unit Tests for ML Model Versioning System

Tests for model creation, loading, versioning, rollback, and metadata management.
"""

import unittest
import tempfile
import shutil
import json
import os
from pathlib import Path
from datetime import datetime
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Import versioning system
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.ml_models.model_manager import ModelVersioning, ModelType
from backend.ml_models.model_registry import ModelRegistry


class TestModelVersioning(unittest.TestCase):
    """Test cases for ModelVersioning class"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.test_dir = tempfile.mkdtemp()
        cls.versioning = ModelVersioning(base_models_path=cls.test_dir)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        shutil.rmtree(cls.test_dir)
    
    def create_dummy_model(self):
        """Create a dummy sklearn model for testing"""
        X = np.random.randn(100, 4)
        y = np.random.randint(0, 3, 100)
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        return model
    
    def create_dummy_encoder(self):
        """Create a dummy label encoder"""
        encoder = LabelEncoder()
        encoder.fit(['crop1', 'crop2', 'crop3'])
        return encoder
    
    # ==================== Creation Tests ====================
    
    def test_create_version_sklearn(self):
        """Test creating a new sklearn model version"""
        model = self.create_dummy_model()
        encoder = self.create_dummy_encoder()
        
        success = self.versioning.create_version(
            'test_model',
            model,
            'v1.0.0',
            ModelType.SKLEARN,
            metadata={'test': True},
            artifacts={'encoder': encoder},
            description='Test version'
        )
        
        self.assertTrue(success)
        
        # Verify files were created
        version_dir = Path(self.test_dir) / 'test_model' / 'v1.0.0'
        self.assertTrue(version_dir.exists())
        self.assertTrue((version_dir / 'model_sklearn.pkl').exists())
        self.assertTrue((version_dir / 'metadata.json').exists())
        self.assertTrue((version_dir / 'artifacts' / 'encoder.pkl').exists())
    
    def test_create_version_with_metadata(self):
        """Test that metadata is correctly saved"""
        model = self.create_dummy_model()
        metadata_input = {
            'author': 'test_user',
            'description': 'Test model version'
        }
        
        self.versioning.create_version(
            'test_model2',
            model,
            'v1.0.0',
            ModelType.SKLEARN,
            metadata=metadata_input,
            description='Test version'
        )
        
        # Read and verify metadata
        metadata_path = Path(self.test_dir) / 'test_model2' / 'v1.0.0' / 'metadata.json'
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata['version'], 'v1.0.0')
        self.assertEqual(metadata['model_type'], 'sklearn')
        self.assertIn('created_at', metadata)
    
    # ==================== Loading Tests ====================
    
    def test_load_model_latest_version(self):
        """Test loading the latest active version"""
        model = self.create_dummy_model()
        
        # Create version
        self.versioning.create_version(
            'test_model3',
            model,
            'v1.0.0',
            ModelType.SKLEARN,
            description='Test version'
        )
        
        # Set as active
        self.versioning.set_active_version('test_model3', 'v1.0.0')
        
        # Load without specifying version
        loaded_model = self.versioning.load_model('test_model3')
        self.assertIsNotNone(loaded_model)
    
    def test_load_model_specific_version(self):
        """Test loading a specific version"""
        model = self.create_dummy_model()
        encoder = self.create_dummy_encoder()
        
        # Create version
        self.versioning.create_version(
            'test_model4',
            model,
            'v1.0.0',
            ModelType.SKLEARN,
            artifacts={'encoder': encoder},
            description='Test version'
        )
        
        # Load specific version
        loaded_model, artifacts = self.versioning.load_model(
            'test_model4',
            'v1.0.0',
            return_artifacts=True
        )
        
        self.assertIsNotNone(loaded_model)
        self.assertIn('encoder', artifacts)
    
    def test_load_nonexistent_version(self):
        """Test loading a non-existent version"""
        loaded_model = self.versioning.load_model(
            'nonexistent_model',
            'v1.0.0'
        )
        self.assertIsNone(loaded_model)
    
    # ==================== Version Management Tests ====================
    
    def test_set_active_version(self):
        """Test setting active version"""
        model = self.create_dummy_model()
        
        # Create two versions
        self.versioning.create_version(
            'test_model5',
            model,
            'v1.0.0',
            ModelType.SKLEARN,
            description='Version 1'
        )
        self.versioning.create_version(
            'test_model5',
            model,
            'v1.1.0',
            ModelType.SKLEARN,
            description='Version 2'
        )
        
        # Set v1.1.0 as active
        success = self.versioning.set_active_version('test_model5', 'v1.1.0')
        self.assertTrue(success)
        
        # Verify active version
        active = self.versioning.get_active_version('test_model5')
        self.assertEqual(active, 'v1.1.0')
    
    def test_get_active_version(self):
        """Test getting active version"""
        model = self.create_dummy_model()
        
        # Create and set active
        self.versioning.create_version(
            'test_model6',
            model,
            'v1.0.0',
            ModelType.SKLEARN
        )
        self.versioning.set_active_version('test_model6', 'v1.0.0')
        
        active = self.versioning.get_active_version('test_model6')
        self.assertEqual(active, 'v1.0.0')
    
    def test_list_versions(self):
        """Test listing all versions"""
        model = self.create_dummy_model()
        
        # Create multiple versions
        for i in range(3):
            version = f'v1.{i}.0'
            self.versioning.create_version(
                'test_model7',
                model,
                version,
                ModelType.SKLEARN,
                description=f'Version {i}'
            )
        
        versions = self.versioning.list_versions('test_model7')
        self.assertEqual(len(versions), 3)
        
        # Verify version info
        version_numbers = [v['version'] for v in versions]
        self.assertIn('v1.0.0', version_numbers)
        self.assertIn('v1.1.0', version_numbers)
        self.assertIn('v1.2.0', version_numbers)
    
    # ==================== Rollback Tests ====================
    
    def test_rollback_to_version(self):
        """Test rolling back to a previous version"""
        model = self.create_dummy_model()
        
        # Create two versions
        self.versioning.create_version(
            'test_model8',
            model,
            'v1.0.0',
            ModelType.SKLEARN
        )
        self.versioning.create_version(
            'test_model8',
            model,
            'v1.1.0',
            ModelType.SKLEARN
        )
        
        # Set v1.1.0 as active
        self.versioning.set_active_version('test_model8', 'v1.1.0')
        self.assertEqual(self.versioning.get_active_version('test_model8'), 'v1.1.0')
        
        # Rollback to v1.0.0
        success = self.versioning.rollback_to_version('test_model8', 'v1.0.0')
        self.assertTrue(success)
        
        # Verify rollback
        self.assertEqual(self.versioning.get_active_version('test_model8'), 'v1.0.0')
    
    def test_rollback_nonexistent_version(self):
        """Test rolling back to non-existent version"""
        model = self.create_dummy_model()
        
        self.versioning.create_version(
            'test_model9',
            model,
            'v1.0.0',
            ModelType.SKLEARN
        )
        self.versioning.set_active_version('test_model9', 'v1.0.0')
        
        # Try to rollback to non-existent version
        success = self.versioning.rollback_to_version('test_model9', 'v1.999.0')
        self.assertFalse(success)
    
    # ==================== Metadata Tests ====================
    
    def test_get_version_metadata(self):
        """Test retrieving version metadata"""
        model = self.create_dummy_model()
        
        self.versioning.create_version(
            'test_model10',
            model,
            'v1.0.0',
            ModelType.SKLEARN,
            metadata={'custom_field': 'test_value'},
            description='Test model'
        )
        
        metadata = self.versioning.get_version_metadata('test_model10', 'v1.0.0')
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['version'], 'v1.0.0')
        self.assertEqual(metadata['custom_field'], 'test_value')
        self.assertEqual(metadata['description'], 'Test model')
    
    def test_add_performance_metrics(self):
        """Test adding performance metrics"""
        model = self.create_dummy_model()
        
        self.versioning.create_version(
            'test_model11',
            model,
            'v1.0.0',
            ModelType.SKLEARN
        )
        
        # Add metrics
        metrics = {
            'accuracy': 0.95,
            'f1_score': 0.92,
            'precision': 0.94
        }
        
        success = self.versioning.add_performance_metrics(
            'test_model11',
            'v1.0.0',
            metrics
        )
        
        self.assertTrue(success)
        
        # Verify metrics were saved
        metadata = self.versioning.get_version_metadata('test_model11', 'v1.0.0')
        self.assertEqual(metadata['performance_metrics']['accuracy'], 0.95)
        self.assertEqual(metadata['performance_metrics']['f1_score'], 0.92)
    
    # ==================== Deletion Tests ====================
    
    def test_delete_version(self):
        """Test deleting a non-active version"""
        model = self.create_dummy_model()
        
        # Create two versions
        self.versioning.create_version(
            'test_model12',
            model,
            'v1.0.0',
            ModelType.SKLEARN
        )
        self.versioning.create_version(
            'test_model12',
            model,
            'v1.1.0',
            ModelType.SKLEARN
        )
        
        # Set v1.1.0 as active
        self.versioning.set_active_version('test_model12', 'v1.1.0')
        
        # Delete v1.0.0
        success = self.versioning.delete_version('test_model12', 'v1.0.0')
        self.assertTrue(success)
        
        # Verify v1.0.0 is deleted
        versions = self.versioning.list_versions('test_model12')
        version_numbers = [v['version'] for v in versions]
        self.assertNotIn('v1.0.0', version_numbers)
    
    def test_cannot_delete_active_version(self):
        """Test that active version cannot be deleted"""
        model = self.create_dummy_model()
        
        self.versioning.create_version(
            'test_model13',
            model,
            'v1.0.0',
            ModelType.SKLEARN
        )
        self.versioning.set_active_version('test_model13', 'v1.0.0')
        
        # Try to delete active version
        success = self.versioning.delete_version('test_model13', 'v1.0.0')
        self.assertFalse(success)


class TestModelRegistry(unittest.TestCase):
    """Test cases for ModelRegistry"""
    
    def test_get_model_config(self):
        """Test getting model configuration"""
        config = ModelRegistry.get_model_config('crop_recommendation')
        self.assertIsNotNone(config)
        self.assertIn('description', config)
        self.assertIn('model_type', config)
    
    def test_list_model_names(self):
        """Test listing all model names"""
        models = ModelRegistry.list_model_names()
        self.assertIn('crop_recommendation', models)
        self.assertIn('disease_detection', models)
    
    def test_is_model_registered(self):
        """Test checking if model is registered"""
        self.assertTrue(ModelRegistry.is_model_registered('crop_recommendation'))
        self.assertFalse(ModelRegistry.is_model_registered('nonexistent_model'))
    
    def test_get_all_models(self):
        """Test getting all models"""
        all_models = ModelRegistry.get_all_models()
        self.assertIsInstance(all_models, dict)
        self.assertGreater(len(all_models), 0)


if __name__ == '__main__':
    unittest.main()
