from flask import Blueprint, request, jsonify
from server.Utils.soil_analysis_logic import SoilRecoveryEngine
import json
import os

rotation_bp = Blueprint('rotation', __name__)

# Correctly locate the JSON database relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'models', 'crop_database.json')

def load_crop_data():
    with open(DB_PATH, 'r') as f:
        return json.load(f)

@rotation_bp.route('/api/analyze-rotation', methods=['POST'])
def analyze():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"status": "error", "message": "Request body must be a JSON object"}), 400

        soil = data.get('soil_status') or {}
        crop = data.get('selected_crop')

        if not isinstance(soil, dict):
            return jsonify({"status": "error", "message": "soil_status must be an object"}), 400

        normalized_soil = {
            'n': soil.get('n', soil.get('nitrogen')),
            'p': soil.get('p', soil.get('phosphorus')),
            'k': soil.get('k', soil.get('potassium'))
        }

        missing_soil_fields = [field for field, value in normalized_soil.items() if value is None]
        if missing_soil_fields:
            return jsonify({
                "status": "error",
                "message": f"Missing soil_status fields: {', '.join(missing_soil_fields)}"
            }), 400

        try:
            normalized_soil = {key: float(value) for key, value in normalized_soil.items()}
        except (TypeError, ValueError):
            return jsonify({"status": "error", "message": "soil_status values must be numeric"}), 400

        if not isinstance(crop, str) or not crop.strip():
            return jsonify({"status": "error", "message": "selected_crop is required"}), 400

        crop = crop.strip()
        
        # Initialize engine with fresh data
        engine = SoilRecoveryEngine(load_crop_data())
        
        analysis = engine.calculate_soil_impact(normalized_soil, crop)
        if analysis is None:
            return jsonify({"status": "error", "message": f"Unknown crop: {crop}"}), 400

        suggestion = engine.suggest_recovery_crop(analysis) if analysis["is_depleted"] else None
        
        return jsonify({
            "status": "success",
            "analysis": analysis,
            "recommendation": suggestion
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500