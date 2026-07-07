import time
import re
import numpy as np
from flask import Flask, render_template, request, jsonify, flash
from functools import wraps
from dataclasses import dataclass
import joblib
from pathlib import Path

app = Flask(__name__)
app.secret_key = "super_secret_agricultural_key" # Required for flash messages

# Real Backend Artifacts
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "xgb_crop_model.pkl"
CROP_ENCODER_PATH = MODEL_DIR / "Crop_encoder.pkl"
SEASON_ENCODER_PATH = MODEL_DIR / "Season_encoder.pkl"
STATE_ENCODER_PATH = MODEL_DIR / "State_encoder.pkl"


def load_artifacts():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Missing model file: {MODEL_PATH}")
    if not CROP_ENCODER_PATH.exists():
        raise FileNotFoundError(f"Missing encoder file: {CROP_ENCODER_PATH}")
    if not SEASON_ENCODER_PATH.exists():
        raise FileNotFoundError(f"Missing encoder file: {SEASON_ENCODER_PATH}")
    if not STATE_ENCODER_PATH.exists():
        raise FileNotFoundError(f"Missing encoder file: {STATE_ENCODER_PATH}")

    loaded_model = joblib.load(MODEL_PATH)
    loaded_crop_enc = joblib.load(CROP_ENCODER_PATH)
    loaded_season_enc = joblib.load(SEASON_ENCODER_PATH)
    loaded_state_enc = joblib.load(STATE_ENCODER_PATH)
    return loaded_model, loaded_crop_enc, loaded_season_enc, loaded_state_enc


model, crop_enc, season_enc, state_enc = load_artifacts()

# --- UTILITIES & VALIDATION ---

@dataclass
class PredictionParams:
    crop: str
    year: int
    season: str
    state: str
    area: float
    production: float
    rainfall: float
    temperature: float = 25.0
    humidity: float = 60.0
    ph: float = 6.5

def validate_and_sanitize(form):
    """Centralized validation logic to keep routes clean."""
    try:
        # Sanitize text
        crop = form.get('crop', '').strip()
        season = form.get('season', '').strip()
        state = form.get('state', '').strip()
        
        # Validate against encoders
        if crop not in crop_enc.classes_: raise ValueError(f"Unsupported crop: {crop}")
        if season not in season_enc.classes_: raise ValueError(f"Unsupported season: {season}")
        if state not in state_enc.classes_: raise ValueError(f"Unsupported state: {state}")

        # Sanitize and validate numbers
        def to_float(val, name, min_v=0):
            clean = re.sub(r'[^0-9.-]', '', str(val))
            f_val = float(clean)
            if f_val < min_v: raise ValueError(f"{name} cannot be negative")
            return f_val

        year = int(form.get('year', 0))
        if not (1900 <= year <= 2100): raise ValueError("Year must be between 1900-2100")

        return PredictionParams(
            crop=crop,
            year=year,
            season=season,
            state=state,
            area=to_float(form.get('area'), "Area"),
            production=to_float(form.get('production'), "Production"),
            rainfall=to_float(form.get('rainfall'), "Rainfall")
        )
    except (TypeError, ValueError) as e:
        raise ValueError(str(e))

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('input.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 1. Validation & Sanitization
        params = validate_and_sanitize(request.form)

        # 2. Encoding
        features = np.array([[
            crop_enc.transform([params.crop])[0],
            params.year,
            season_enc.transform([params.season])[0],
            state_enc.transform([params.state])[0],
            params.area,
            params.rainfall,
            params.production
        ]])

        # 3. Inference
        prediction_raw = model.predict(features)[0]
        prediction = round(float(prediction_raw), 2)

        # 4. Success Response
        return render_template('index.html', 
                               crop=params.crop, 
                               prediction=prediction, 
                               params=params.__dict__)

    except ValueError as e:
        # User input error
        return render_template('input.html', error=str(e))
    except Exception as e:
        # System error
        app.logger.error(f"Prediction Crash: {e}")
        return render_template('input.html', error="An internal error occurred. Please try again.")

# --- ERROR HANDLERS ---

@app.errorhandler(404)
def not_found(e):
    return render_template('input.html', error="Page not found"), 404

if __name__ == '__main__':
    # Using '0.0.0.0' makes it accessible on your local network
    app.run(debug=True, port=5502, host='0.0.0.0')
    