# utils.py
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os
import logging

logger = logging.getLogger(__name__)

# Class labels (update if needed)
class_names = [
    'Apple___Black_rot', 'Apple___healthy',
    'Corn___Cercospora_leaf_spot', 'Corn___Common_rust',
    'Corn___healthy', 'Grape___Black_rot', 'Grape___Esca',
    'Grape___healthy', 'Potato___Early_blight', 'Potato___Late_blight',
    'Potato___healthy', 'Tomato___Bacterial_spot', 'Tomato___Early_blight',
    'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites', 'Tomato___Target_Spot', 'Tomato___Yellow_Leaf_Curl_Virus',
    'Tomato___mosaic_virus', 'Tomato___healthy'
]

# Add this in utils.py
class_descriptions = {
    'Apple___Black_rot': 'Black rot is a fungal disease. Remove affected fruit and apply fungicide.',
    'Apple___healthy': 'The apple plant is healthy.',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': 'Gray leaf spot detected. Use resistant varieties and rotate crops.',
    'Corn_(maize)___Common_rust_': 'Common rust detected. Remove infected leaves and apply fungicide.',
    'Corn_(maize)___healthy': 'The corn plant is healthy.',
    'Grape___Black_rot': 'Black rot detected on grapes. Remove infected parts.',
    'Grape___Esca_(Black_Measles)': 'Esca disease detected. Prune and burn affected wood.',
    'Grape___healthy': 'The grape plant is healthy.',
    'Potato___Early_blight': 'Early blight detected. Use certified disease-free seeds.',
    'Potato___Late_blight': 'Late blight detected. Avoid overhead irrigation and apply fungicide.',
    'Potato___healthy': 'The potato plant is healthy.',
    'Tomato___Bacterial_spot': 'Bacterial spot found. Use copper-based sprays.',
    'Tomato___Early_blight': 'Early blight detected. Improve air circulation and remove infected leaves.',
    'Tomato___Late_blight': 'Late blight found. Remove and destroy infected plants.',
    'Tomato___Leaf_Mold': 'Leaf mold detected. Reduce humidity and ensure ventilation.',
    'Tomato___Septoria_leaf_spot': 'Septoria leaf spot detected. Remove lower leaves and apply fungicide.',
    'Tomato___Spider_mites Two-spotted_spider_mite': 'Spider mites present. Use insecticidal soap.',
    'Tomato___Target_Spot': 'Target spot found. Use proper spacing and apply fungicide.',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': 'Viral infection found. Remove infected plants.',
    'Tomato___Tomato_mosaic_virus': 'Mosaic virus detected. Control aphid population.',
    'Tomato___healthy': 'The tomato plant is healthy.'
}

def load_keras_model(model_path):
    try:
        if not os.path.exists(model_path):
            logger.error(f"Model file does not exist at path: {model_path}")
            return None
        model = load_model(model_path)
        return model
    except Exception as e:
        logger.error(f"Failed to load Keras model from {model_path}: {str(e)}")
        return None

def predict_image_keras(model, img_path):
    if model is None:
        logger.error("Prediction failed: model is None")
        return "Model unavailable", "The classification model is currently unavailable."
    try:
        if not os.path.exists(img_path):
            logger.error(f"Image file does not exist at path: {img_path}")
            return "Image not found", "The uploaded image file could not be found."
        img = image.load_img(img_path, target_size=(160, 160))  # Match your training size
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        predictions = model.predict(img_array)
        predicted_index = np.argmax(predictions)
        predicted_class = class_names[predicted_index]
        description = class_descriptions.get(predicted_class, "No description available.")

        return predicted_class, description
    except Exception as e:
        logger.error(f"Error predicting image {img_path}: {str(e)}")
        return "Model unavailable", f"An error occurred during prediction: {str(e)}"