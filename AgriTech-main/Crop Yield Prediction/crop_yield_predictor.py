import os
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split 
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# --- 1. CONFIGURATION & LOAD ---
# Use absolute or relative paths from the script's directory for safety
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "crop_yield_dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

try:
    df = pd.read_csv(DATA_PATH)
    # Clean column names: strip spaces, lowercase, replace spaces with underscores
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    print(f"Dataset loaded. Shape: {df.shape}")
except FileNotFoundError:
    print(f"Error: {DATA_PATH} not found. Please check the file path.")
    exit()

# --- 2. ENCODING & PREPROCESSING ---
encoders = {}
categorical_cols = ['area', 'item']

for col in categorical_cols:
    le = LabelEncoder()
    df[f'{col}_encoded'] = le.fit_transform(df[col])
    encoders[col] = le

# Define Features and Target
features = ['area_encoded', 'item_encoded', 'average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp']
target = 'hg/ha_yield'

# Ensure all feature columns exist before training
if not all(col in df.columns for col in features + [target]):
    missing = [col for col in features + [target] if col not in df.columns]
    print(f"Missing columns in CSV: {missing}")
    exit()

X = df[features]
y = df[target]

# --- 3. TRAIN/TEST SPLIT ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)

# --- 4. MODEL TRAINING ---
print("Training Random Forest Regressor...")
model = RandomForestRegressor(
    n_estimators=100, 
    max_depth=15,       # Prevents extreme overfitting
    n_jobs=-1,          # Uses all CPU cores for faster training
    random_state=42
)
model.fit(X_train, y_train)

# --- 5. EVALUATION ---
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("-" * 40)
print(f"Model Performance:")
print(f"R2 Score (Accuracy): {r2 * 100:.2f}%")
print(f"Mean Absolute Error: {mae:.2f} hg/ha")
print(f"Root Mean Squared Error: {rmse:.2f} hg/ha")
print("-" * 40)

# --- 6. SAVE ARTIFACTS ---
joblib.dump(model, os.path.join(MODEL_DIR, 'yield_predictor_model.pkl'))
joblib.dump(encoders['area'], os.path.join(MODEL_DIR, 'area_encoder.pkl'))
joblib.dump(encoders['item'], os.path.join(MODEL_DIR, 'item_encoder.pkl'))
print(f"Model and encoders saved successfully in '{MODEL_DIR}/'")

# --- 7. VISUALIZATIONS ---
print("Generating plots and saving to assets...")

# Feature Importance Plot
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]
clean_feature_names = ['Region/Area', 'Crop/Item', 'Rainfall (mm/year)', 'Pesticides (tonnes)', 'Avg Temperature (C)']
sorted_feature_names = [clean_feature_names[i] for i in indices]

plt.figure(figsize=(10, 6))
sns.set_theme(style="whitegrid")
sns.barplot(x=importances[indices], y=sorted_feature_names, palette="viridis", hue=sorted_feature_names, legend=False)
plt.title("Feature Importance in Crop Yield Prediction Model", fontsize=14, pad=15)
plt.xlabel("Relative Importance Score", fontsize=12)
plt.ylabel("Features", fontsize=12)
plt.tight_layout()
feat_importance_path = os.path.join(ASSETS_DIR, "feature_importance.png")
plt.savefig(feat_importance_path, dpi=300)
plt.close()
print(f"Feature Importance plot saved as '{feat_importance_path}'")

# Actual vs Predicted Plot
plt.figure(figsize=(10, 6))
# Sample data for scatter plot to avoid sluggish rendering with huge datasets
sample_indices = np.random.choice(len(y_test), min(len(y_test), 2000), replace=False)
plt.scatter(y_test.iloc[sample_indices], y_pred[sample_indices], alpha=0.4, color="#2e8b57", label="Predicted vs Actual")
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "k--", lw=2, label="Perfect Fit Line")
plt.xlabel("Actual Yield (hg/ha)", fontsize=12)
plt.ylabel("Predicted Yield (hg/ha)", fontsize=12)
plt.title("Actual vs Predicted Crop Yield (Sampled Test Set)", fontsize=14, pad=15)
plt.legend()
plt.tight_layout()
act_vs_pred_path = os.path.join(ASSETS_DIR, "actual_vs_predicted.png")
plt.savefig(act_vs_pred_path, dpi=300)
plt.close()
print(f"Performance plot saved as '{act_vs_pred_path}'")
print("Training pipeline complete!")