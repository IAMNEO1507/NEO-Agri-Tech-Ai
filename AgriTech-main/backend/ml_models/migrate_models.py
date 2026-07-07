#!/usr/bin/env python
"""
Model Migration Script

Migrates existing ML models to the new versioning system.
This script helps import models from legacy locations into the versioned model storage.

Usage:
    python migrate_models.py --migrate-crop
    python migrate_models.py --migrate-disease
    python migrate_models.py --migrate-all
"""

import os
import sys
import json
import joblib
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.ml_models import ModelVersioning, ModelType
from backend.ml_models.model_registry import ModelRegistry


class ModelMigration:
    """Handles migration of models to versioned storage"""
    
    def __init__(self, base_models_path=None):
        """Initialize migration handler"""
        self.versioning = ModelVersioning(base_models_path)
        self.project_root = Path(__file__).parent.parent.parent
    
    def migrate_crop_recommendation(self):
        """Migrate crop recommendation model from legacy location"""
        logger.info("="*60)
        logger.info("Migrating Crop Recommendation Model...")
        logger.info("="*60)
        
        try:
            # Look for legacy model files
            legacy_model_path = self.project_root / 'crop_recommendation' / 'model' / 'rf_model.pkl'
            legacy_encoder_path = self.project_root / 'crop_recommendation' / 'model' / 'label_encoder.pkl'
            
            if not legacy_model_path.exists():
                logger.error(f"Legacy model not found at: {legacy_model_path}")
                return False
            
            logger.info(f"Found legacy model at: {legacy_model_path}")
            
            # Load the models
            logger.info("Loading legacy model and encoder...")
            model = joblib.load(str(legacy_model_path))
            
            artifacts = {}
            if legacy_encoder_path.exists():
                artifacts['label_encoder'] = joblib.load(str(legacy_encoder_path))
                logger.info("Loaded label encoder")
            
            # Create versioned model
            version = "v1.0.0"
            metadata = {
                'description': 'Initial production model - migrated from legacy storage',
                'source': 'legacy',
                'migrated_from': str(legacy_model_path),
                'migration_date': datetime.utcnow().isoformat()
            }
            
            success = self.versioning.create_version(
                'crop_recommendation',
                model,
                version,
                ModelType.SKLEARN,
                metadata=metadata,
                artifacts=artifacts,
                description="Initial production model from legacy storage"
            )
            
            if success:
                logger.info(f"✓ Successfully created version {version}")
                
                # Set as active version
                if self.versioning.set_active_version('crop_recommendation', version):
                    logger.info(f"✓ Set {version} as active version")
                else:
                    logger.error("Failed to set as active version")
                    return False
                
                return True
            else:
                logger.error("Failed to create versioned model")
                return False
        
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            return False
    
    def migrate_disease_detection(self):
        """Migrate disease detection model from legacy location"""
        logger.info("="*60)
        logger.info("Migrating Disease Detection Model...")
        logger.info("="*60)
        
        try:
            # Look for legacy disease model
            legacy_model_path = self.project_root / 'face_vs_nonface_model.h5'
            
            if not legacy_model_path.exists():
                logger.warning(f"Legacy disease model not found at: {legacy_model_path}")
                logger.info("Skipping disease detection migration (model not found)")
                return True
            
            logger.info(f"Found legacy disease model at: {legacy_model_path}")
            
            # For h5 models, we need to handle loading differently
            try:
                from tensorflow import keras
                logger.info("Loading legacy Keras model...")
                model = keras.models.load_model(str(legacy_model_path))
            except Exception as e:
                logger.error(f"Failed to load Keras model: {str(e)}")
                return False
            
            # Create versioned model
            version = "v1.0.0"
            metadata = {
                'description': 'Initial disease detection model - migrated from legacy storage',
                'source': 'legacy',
                'migrated_from': str(legacy_model_path),
                'migration_date': datetime.utcnow().isoformat()
            }
            
            success = self.versioning.create_version(
                'disease_detection',
                model,
                version,
                ModelType.KERAS,
                metadata=metadata,
                description="Initial disease detection model from legacy storage"
            )
            
            if success:
                logger.info(f"✓ Successfully created version {version}")
                
                # Set as active version
                if self.versioning.set_active_version('disease_detection', version):
                    logger.info(f"✓ Set {version} as active version")
                else:
                    logger.error("Failed to set as active version")
                    return False
                
                return True
            else:
                logger.error("Failed to create versioned disease model")
                return False
        
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            return False
    
    def verify_migration(self):
        """Verify that migration was successful"""
        logger.info("="*60)
        logger.info("Verifying Migration...")
        logger.info("="*60)
        
        success = True
        
        for model_name in ['crop_recommendation', 'disease_detection']:
            try:
                active_version = self.versioning.get_active_version(model_name)
                
                if active_version:
                    logger.info(f"✓ {model_name}: Active version = {active_version}")
                    
                    # Try to load the model
                    model = self.versioning.load_model(model_name)
                    if model:
                        logger.info(f"✓ {model_name}: Model successfully loaded")
                    else:
                        logger.warning(f"⚠ {model_name}: Failed to load model")
                        success = False
                else:
                    logger.warning(f"⚠ {model_name}: No active version found")
            
            except Exception as e:
                logger.warning(f"⚠ {model_name}: Verification failed - {str(e)}")
        
        return success
    
    def show_migration_summary(self):
        """Display migration summary"""
        logger.info("="*60)
        logger.info("Migration Summary")
        logger.info("="*60)
        
        all_models = ModelRegistry.get_all_models()
        
        for model_name, config in all_models.items():
            try:
                versions = self.versioning.list_versions(model_name)
                active_version = self.versioning.get_active_version(model_name)
                
                logger.info(f"\n{model_name}:")
                logger.info(f"  Description: {config.get('description', 'N/A')}")
                logger.info(f"  Total versions: {len(versions)}")
                logger.info(f"  Active version: {active_version}")
                
                if versions:
                    for v in versions:
                        status = "ACTIVE" if v.get('is_active') else "archived"
                        logger.info(f"    - {v.get('version', 'N/A')} [{status}]")
                        if v.get('description'):
                            logger.info(f"      {v['description']}")
            
            except Exception as e:
                logger.warning(f"  Error retrieving versions: {str(e)}")


def main():
    """Main migration entry point"""
    parser = argparse.ArgumentParser(
        description='Migrate ML models to versioned storage'
    )
    parser.add_argument(
        '--migrate-crop',
        action='store_true',
        help='Migrate crop recommendation model'
    )
    parser.add_argument(
        '--migrate-disease',
        action='store_true',
        help='Migrate disease detection model'
    )
    parser.add_argument(
        '--migrate-all',
        action='store_true',
        help='Migrate all available models'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify existing migrations without migrating'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show migration summary'
    )
    
    args = parser.parse_args()
    
    migration = ModelMigration()
    
    # Handle verify-only mode
    if args.verify_only:
        logger.info("Running verification only...")
        migration.verify_migration()
        migration.show_migration_summary()
        return 0
    
    # Handle summary mode
    if args.summary:
        migration.show_migration_summary()
        return 0
    
    # Default to migrate all if no specific option selected
    if not (args.migrate_crop or args.migrate_disease or args.migrate_all):
        args.migrate_all = True
    
    success_count = 0
    
    if args.migrate_crop or args.migrate_all:
        if migration.migrate_crop_recommendation():
            success_count += 1
    
    if args.migrate_disease or args.migrate_all:
        if migration.migrate_disease_detection():
            success_count += 1
    
    # Verify migrations
    logger.info("")
    if migration.verify_migration():
        logger.info("✓ All migrations verified successfully!")
    else:
        logger.warning("⚠ Some migrations could not be verified")
    
    # Show summary
    migration.show_migration_summary()
    
    logger.info("")
    logger.info("="*60)
    logger.info("Migration Complete")
    logger.info("="*60)
    
    return 0 if success_count > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
