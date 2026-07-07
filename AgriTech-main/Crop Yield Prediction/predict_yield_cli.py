import os
import sys
import joblib
import numpy as np

# Set up paths relative to the script directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "yield_predictor_model.pkl")
AREA_ENC_PATH = os.path.join(MODEL_DIR, "area_encoder.pkl")
ITEM_ENC_PATH = os.path.join(MODEL_DIR, "item_encoder.pkl")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_closest_matches(query, choices, limit=5):
    """Find simple case-insensitive matching string choices."""
    query_lower = query.lower()
    matches = [c for c in choices if query_lower in c.lower()]
    return matches[:limit]

def main():
    clear_screen()
    print("=" * 60)
    print("      AgriPredict: ML-Based Crop Yield Predictor CLI      ")
    print("=" * 60)
    
    # Check if model files exist
    if not (os.path.exists(MODEL_PATH) and os.path.exists(AREA_ENC_PATH) and os.path.exists(ITEM_ENC_PATH)):
        print("\nError: Trained model files not found in the 'models/' directory.")
        print("Please train the model first by running:")
        print("   python crop_yield_predictor.py")
        sys.exit(1)
        
    print("\nLoading machine learning assets...")
    try:
        model = joblib.load(MODEL_PATH)
        le_area = joblib.load(AREA_ENC_PATH)
        le_item = joblib.load(ITEM_ENC_PATH)
        print("Models and Encoders loaded successfully.")
    except Exception as e:
        print(f"Critical error loading model assets: {e}")
        sys.exit(1)

    print("\nEnter the following environmental and location parameters:")
    
    # 1. Location / Area
    while True:
        area_input = input("\nEnter Country/Region Name (e.g. India, Albania): ").strip()
        if not area_input:
            print("Warning: Country name cannot be empty.")
            continue
            
        if area_input in le_area.classes_:
            area = area_input
            break
            
        # Try finding closest match
        matches = get_closest_matches(area_input, le_area.classes_)
        if matches:
            print(f"Warning: Region '{area_input}' not found. Did you mean one of these?")
            for i, match in enumerate(matches, 1):
                print(f"   [{i}] {match}")
            choice = input("Enter option number or press Enter to type again: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(matches):
                area = matches[int(choice) - 1]
                print(f"Selected: {area}")
                break
        else:
            print("Warning: Country/Region not recognized by the model training set.")
            print("Valid examples: Albania, India, Algeria, Argentina, Brazil, Canada, France, etc.")

    # 2. Crop Type / Item
    while True:
        crop_input = input("\nEnter Crop Type (e.g. Maize, Wheat, Potatoes): ").strip()
        if not crop_input:
            print("Warning: Crop type cannot be empty.")
            continue
            
        if crop_input in le_item.classes_:
            crop = crop_input
            break
            
        # Try finding closest match
        matches = get_closest_matches(crop_input, le_item.classes_)
        if matches:
            print(f"Warning: Crop '{crop_input}' not found. Did you mean one of these?")
            for i, match in enumerate(matches, 1):
                print(f"   [{i}] {match}")
            choice = input("Enter option number or press Enter to type again: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(matches):
                crop = matches[int(choice) - 1]
                print(f"Selected: {crop}")
                break
        else:
            print("Warning: Crop type not recognized by the model training set.")
            print(f"Valid classes: {', '.join(le_item.classes_[:10])}...")

    # 3. Average Rainfall
    while True:
        try:
            rainfall_str = input("\nEnter Average Rainfall (mm/year) [e.g. 1200]: ").strip()
            rainfall = float(rainfall_str)
            if rainfall < 0:
                print("Warning: Rainfall cannot be negative.")
                continue
            break
        except ValueError:
            print("Warning: Invalid input. Please enter a valid number.")

    # 4. Pesticides
    while True:
        try:
            pesticide_str = input("\nEnter Pesticide Usage (tonnes) [e.g. 50]: ").strip()
            pesticide = float(pesticide_str)
            if pesticide < 0:
                print("Warning: Pesticide usage cannot be negative.")
                continue
            break
        except ValueError:
            print("Warning: Invalid input. Please enter a valid number.")

    # 5. Temperature
    while True:
        try:
            temp_str = input("\nEnter Average Temperature (C) [e.g. 25]: ").strip()
            temperature = float(temp_str)
            if not (-30 <= temperature <= 60):
                print("Warning: Temperature must be in range -30C to 60C.")
                continue
            break
        except ValueError:
            print("Warning: Invalid input. Please enter a valid number.")

    # Inference logic
    print("\nRunning Random Forest Regressor Prediction...")
    try:
        import pandas as pd
        # Encode inputs
        area_encoded = le_area.transform([area])[0]
        item_encoded = le_item.transform([crop])[0]
        
        # Feature DataFrame with matching column names
        input_data = pd.DataFrame(
            [[area_encoded, item_encoded, rainfall, pesticide, temperature]],
            columns=['area_encoded', 'item_encoded', 'average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp']
        )
        
        # Predict
        prediction = model.predict(input_data)[0]
        
        print("\n" + "=" * 50)
        print("          PREDICTION RESULT          ")
        print("=" * 50)
        print(f"Location      : {area}")
        print(f"Crop Type     : {crop}")
        print(f"Rainfall      : {rainfall:,.1f} mm/year")
        print(f"Pesticides    : {pesticide:,.1f} tonnes")
        print(f"Temperature   : {temperature:.1f} C")
        print("-" * 50)
        print(f"Predicted Yield: {prediction:,.2f} hg/ha")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nError during prediction calculation: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
