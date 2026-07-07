import google.generativeai as genai
import os
from backend.extensions import db
from backend.models.gews import DiseaseIncident
from backend.services.weather_service import WeatherService
from datetime import datetime
import logging
import base64

logger = logging.getLogger(__name__)


class AIDiseaseDetectionService:
    DISEASE_DATABASE = {
        "Tomato": {
            "Late Blight": {
                "symptoms": "Water-soaked lesions on leaves, brown spots, white mold on underside",
                "treatment": "Apply copper-based fungicides, remove infected leaves, improve air circulation",
                "severity": "HIGH",
            },
            "Early Blight": {
                "symptoms": "Dark brown circular spots with concentric rings on lower leaves",
                "treatment": "Use fungicides containing chlorothalonil or copper, crop rotation",
                "severity": "MEDIUM",
            },
            "Septoria Leaf Spot": {
                "symptoms": "Small circular spots with dark borders and gray centers on leaves",
                "treatment": "Apply fungicides, remove affected leaves, avoid overhead irrigation",
                "severity": "MEDIUM",
            },
            "Bacterial Spot": {
                "symptoms": "Small water-soaked spots on leaves, stems, and fruits",
                "treatment": "Use copper bactericides, avoid working with wet plants",
                "severity": "HIGH",
            },
        },
        "Wheat": {
            "Rust": {
                "symptoms": "Orange-brown pustules on leaves and stems",
                "treatment": "Apply fungicides, use resistant varieties, crop rotation",
                "severity": "HIGH",
            },
            "Powdery Mildew": {
                "symptoms": "White powdery growth on leaves and stems",
                "treatment": "Apply sulfur or fungicides, improve air circulation",
                "severity": "MEDIUM",
            },
        },
        "Rice": {
            "Blast": {
                "symptoms": "Diamond-shaped lesions on leaves, neck rot",
                "treatment": "Use fungicides like tricyclazole, resistant varieties, proper water management",
                "severity": "HIGH",
            },
            "Bacterial Leaf Blight": {
                "symptoms": "Yellowing along leaf margins, drying of leaves",
                "treatment": "Use resistant varieties, balanced fertilization, avoid excess nitrogen",
                "severity": "HIGH",
            },
        },
        "Cotton": {
            "Verticillium Wilt": {
                "symptoms": "Yellowing and wilting of leaves, vascular discoloration",
                "treatment": "Use resistant varieties, soil solarization, crop rotation",
                "severity": "HIGH",
            },
            "Boll Rot": {
                "symptoms": "Rotting of cotton bolls, wet spots",
                "treatment": "Use fungicides, improve drainage, avoid overhead irrigation",
                "severity": "HIGH",
            },
        },
        "Maize": {
            "Northern Corn Leaf Blight": {
                "symptoms": "Long gray-green lesions on leaves",
                "treatment": "Apply fungicides, use resistant hybrids, crop rotation",
                "severity": "MEDIUM",
            },
            "Gray Leaf Spot": {
                "symptoms": "Rectangular gray lesions on leaves",
                "treatment": "Apply fungicides, crop rotation, residue management",
                "severity": "MEDIUM",
            },
        },
    }

    ADVISORY_LIBRARY = {
        "Tomato": {
            "Late Blight": {
                "organic_solution": "Spray neem oil or copper-based biofungicides and remove infected foliage immediately.",
                "chemical_solution": "Apply copper oxychloride or mancozeb as directed on the label.",
                "preventive_measures": [
                    "Avoid overhead irrigation",
                    "Improve air circulation with proper spacing",
                    "Destroy infected plant debris",
                ],
                "suggested_fertilizers": ["Balanced NPK 19:19:19", "Potassium-rich foliar feed"],
            },
            "Early Blight": {
                "organic_solution": "Use copper sprays and compost tea; prune lower infected leaves.",
                "chemical_solution": "Use chlorothalonil or copper fungicide as per label instructions.",
                "preventive_measures": [
                    "Rotate crops for 2-3 seasons",
                    "Mulch to prevent soil splash",
                    "Avoid wetting leaves during irrigation",
                ],
                "suggested_fertilizers": ["Potassium sulfate", "Calcium nitrate"],
            },
        },
        "Wheat": {
            "Rust": {
                "organic_solution": "Remove volunteer wheat and use resistant varieties.",
                "chemical_solution": "Use triazole-based fungicides at early symptom onset.",
                "preventive_measures": ["Monitor humid periods closely", "Use certified seed", "Practice crop rotation"],
                "suggested_fertilizers": ["Balanced NPK", "Zinc sulfate"],
            },
            "Powdery Mildew": {
                "organic_solution": "Apply sulfur sprays and improve canopy ventilation.",
                "chemical_solution": "Use systemic fungicides if pressure increases.",
                "preventive_measures": ["Reduce overcrowding", "Avoid excess nitrogen", "Scout weekly"],
                "suggested_fertilizers": ["Split nitrogen doses", "Potash supplementation"],
            },
        },
        "Rice": {
            "Blast": {
                "organic_solution": "Use biocontrol agents and remove infected tillers early.",
                "chemical_solution": "Apply tricyclazole or compatible fungicides following local guidance.",
                "preventive_measures": ["Maintain balanced water levels", "Avoid excess nitrogen", "Use resistant varieties"],
                "suggested_fertilizers": ["Balanced NPK", "Silicon amendments"],
            }
        },
        "Cotton": {
            "Verticillium Wilt": {
                "organic_solution": "Solarize soil and use bio-fungicides around the root zone.",
                "chemical_solution": "Use recommended soil treatment products where permitted.",
                "preventive_measures": ["Rotate away from cotton", "Improve drainage", "Use clean seed"],
                "suggested_fertilizers": ["Potassium-rich fertilizer", "Humic acid"],
            }
        },
        "Maize": {
            "Northern Corn Leaf Blight": {
                "organic_solution": "Use compost-based sprays and remove crop residue after harvest.",
                "chemical_solution": "Apply fungicide at first symptom appearance.",
                "preventive_measures": ["Use resistant hybrids", "Rotate crops", "Avoid prolonged leaf wetness"],
                "suggested_fertilizers": ["Balanced NPK", "Magnesium sulfate"],
            }
        },
    }

    DEFAULT_ADVISORY = {
        "organic_solution": "Remove visibly affected leaves, improve drainage, and use neem-based sprays where appropriate.",
        "chemical_solution": "Consult a local agri-input dealer or extension officer for crop-safe fungicide guidance.",
        "preventive_measures": [
            "Inspect plants every 2-3 days",
            "Avoid overhead irrigation",
            "Keep tools and pruning blades disinfected",
        ],
        "suggested_fertilizers": ["Balanced NPK", "Potash supplement"],
    }

    @staticmethod
    def analyze_crop_image(image_base64, crop_type, location=None):
        api_key = os.environ.get("GEMINI_API_KEY")
        weather = WeatherService.get_latest_weather(location) if location else None

        try:
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")

                prompt = f"""
                Analyze this {crop_type} plant image for diseases.

                Identify:
                1. Disease name (if any)
                2. Symptoms observed
                3. Severity level (LOW, MEDIUM, HIGH)
                4. Affected plant parts
                5. Confidence level (0-100%)
                6. Treatment summary

                Local weather context: {AIDiseaseDetectionService._weather_summary(weather)}

                If healthy, state "No disease detected".

                Provide response in this exact JSON format:
                {{
                    "disease_name": "Disease Name or Healthy",
                    "symptoms": "description of symptoms",
                    "severity": "LOW/MEDIUM/HIGH",
                    "affected_parts": ["leaves", "stems"],
                    "confidence": 85,
                    "is_healthy": false,
                    "treatment": "short treatment summary"
                }}
                """

                image_data = {"mime_type": "image/jpeg", "data": image_base64}

                response = model.generate_content([prompt, image_data])

                import re

                json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
                if json_match:
                    import json

                    diagnosis = json.loads(json_match.group())
                    return AIDiseaseDetectionService.enhance_diagnosis(diagnosis, crop_type, weather)

            return AIDiseaseDetectionService.rule_based_diagnosis(crop_type, weather)

        except Exception as e:
            logger.error(f"AI disease detection error: {str(e)}")
            return AIDiseaseDetectionService.rule_based_diagnosis(crop_type, weather, error_message=str(e))

    @staticmethod
    def _weather_summary(weather):
        if not weather:
            return "Weather data unavailable"

        return f"{weather.temperature}°C, {weather.humidity}% humidity, rainfall {weather.rainfall}mm, {weather.weather_condition}"

    @staticmethod
    def rule_based_diagnosis(crop_type, weather=None, error_message=None):
        crop_diseases = AIDiseaseDetectionService.DISEASE_DATABASE.get(crop_type, {})
        if not crop_diseases:
            return {
                "disease_name": "Unknown",
                "symptoms": "No crop profile found for this crop type.",
                "severity": "LOW",
                "affected_parts": ["leaves"],
                "confidence": 35,
                "is_healthy": False,
                "treatment": "Use crop-specific diagnosis for better accuracy.",
                "recommendation": "Capture a clearer image and consult a local agronomist.",
                "organic_solution": AIDiseaseDetectionService.DEFAULT_ADVISORY["organic_solution"],
                "chemical_solution": AIDiseaseDetectionService.DEFAULT_ADVISORY["chemical_solution"],
                "preventive_measures": AIDiseaseDetectionService.DEFAULT_ADVISORY["preventive_measures"],
                "suggested_fertilizers": AIDiseaseDetectionService.DEFAULT_ADVISORY["suggested_fertilizers"],
                "weather_risk": AIDiseaseDetectionService._weather_risk(weather),
                "weather_summary": AIDiseaseDetectionService._weather_summary(weather),
                "fallback_used": True,
                "error": error_message,
            }

        disease_name, info = next(iter(crop_diseases.items()))
        diagnosis = {
            "disease_name": disease_name,
            "symptoms": info["symptoms"],
            "severity": info["severity"],
            "affected_parts": ["leaves"],
            "confidence": 72 if weather else 60,
            "is_healthy": False,
            "treatment": info["treatment"],
            "recommendation": "Apply the recommended treatment and monitor the crop daily.",
            "fallback_used": True,
        }
        return AIDiseaseDetectionService.enhance_diagnosis(diagnosis, crop_type, weather, error_message=error_message)

    @staticmethod
    def _weather_risk(weather):
        if not weather:
            return "Weather data unavailable"

        risk_points = 0
        if weather.humidity >= 80:
            risk_points += 2
        if weather.temperature >= 30:
            risk_points += 1
        if weather.rainfall >= 10:
            risk_points += 1

        if risk_points >= 3:
            return "High disease risk"
        if risk_points == 2:
            return "Moderate disease risk"
        return "Low disease risk"

    @staticmethod
    def enhance_diagnosis(diagnosis, crop_type, weather=None, error_message=None):
        if diagnosis.get("is_healthy", False):
            diagnosis["treatment"] = "No treatment needed. Continue regular care."
            diagnosis["recommendation"] = "Monitor plant health regularly."
            diagnosis["organic_solution"] = "Continue good hygiene, remove dead foliage, and monitor every 2-3 days."
            diagnosis["chemical_solution"] = "No chemical treatment needed unless symptoms develop."
            diagnosis["preventive_measures"] = ["Use clean tools", "Avoid waterlogging", "Inspect leaves routinely"]
            diagnosis["suggested_fertilizers"] = ["Balanced NPK"]
            diagnosis["weather_risk"] = AIDiseaseDetectionService._weather_risk(weather)
            diagnosis["weather_summary"] = AIDiseaseDetectionService._weather_summary(weather)
            if error_message:
                diagnosis["fallback_note"] = error_message
            return diagnosis

        disease_name = diagnosis.get("disease_name", "Unknown")
        crop_diseases = AIDiseaseDetectionService.DISEASE_DATABASE.get(crop_type, {})
        advisory = AIDiseaseDetectionService.ADVISORY_LIBRARY.get(crop_type, {}).get(disease_name, {})

        for disease, info in crop_diseases.items():
            if (
                disease_name.lower() in disease.lower()
                or disease.lower() in disease_name.lower()
            ):
                diagnosis["symptoms"] = info["symptoms"]
                diagnosis["treatment"] = info["treatment"]
                diagnosis["severity"] = info["severity"]
                diagnosis["database_match"] = True
                break

        if "treatment" not in diagnosis:
            diagnosis["treatment"] = (
                "Consult agricultural expert for specific treatment recommendations."
            )
            diagnosis["recommendation"] = "Isolate affected plants and prevent spread."

        if "recommendation" not in diagnosis:
            if diagnosis.get("severity") == "HIGH":
                diagnosis["recommendation"] = (
                    "Immediate action required. Consider contacting agricultural extension services."
                )
            elif diagnosis.get("severity") == "MEDIUM":
                diagnosis["recommendation"] = (
                    "Monitor closely and apply treatment as soon as possible."
                )
            else:
                diagnosis["recommendation"] = (
                    "Apply preventive measures and monitor plant health."
                )

        diagnosis["organic_solution"] = advisory.get("organic_solution", AIDiseaseDetectionService.DEFAULT_ADVISORY["organic_solution"])
        diagnosis["chemical_solution"] = advisory.get("chemical_solution", AIDiseaseDetectionService.DEFAULT_ADVISORY["chemical_solution"])
        diagnosis["preventive_measures"] = advisory.get("preventive_measures", AIDiseaseDetectionService.DEFAULT_ADVISORY["preventive_measures"])
        diagnosis["suggested_fertilizers"] = advisory.get("suggested_fertilizers", AIDiseaseDetectionService.DEFAULT_ADVISORY["suggested_fertilizers"])
        diagnosis["weather_risk"] = AIDiseaseDetectionService._weather_risk(weather)
        diagnosis["weather_summary"] = AIDiseaseDetectionService._weather_summary(weather)
        if error_message:
            diagnosis["fallback_note"] = error_message

        return diagnosis

    @staticmethod
    def save_diagnosis(user_id, crop_type, diagnosis, image_base64=None, location=None):
        incident = DiseaseIncident(
            incident_id=f"AI-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            user_id=user_id,
            disease_name=diagnosis.get("disease_name", "Unknown"),
            crop_affected=crop_type,
            severity_level=diagnosis.get("severity", "MEDIUM"),
            symptoms=diagnosis.get("symptoms", ""),
            latitude=location.get("latitude") if location else None,
            longitude=location.get("longitude") if location else None,
            detection_method="ai_image",
            verification_status="pending",
            images=[image_base64] if image_base64 else [],
            reported_at=datetime.utcnow(),
        )

        db.session.add(incident)
        db.session.commit()

        return incident

    @staticmethod
    def get_disease_history(user_id, crop_type=None, days=30):
        threshold = datetime.utcnow() - timedelta(days=days)
        query = DiseaseIncident.query.filter(
            DiseaseIncident.user_id == user_id, DiseaseIncident.reported_at >= threshold
        )

        if crop_type:
            query = query.filter_by(crop_affected=crop_type)

        return query.order_by(DiseaseIncident.reported_at.desc()).all()

    @staticmethod
    def get_treatment_recommendation(crop_type, disease_name):
        crop_diseases = AIDiseaseDetectionService.DISEASE_DATABASE.get(crop_type, {})

        for disease, info in crop_diseases.items():
            if (
                disease_name.lower() in disease.lower()
                or disease.lower() in disease_name.lower()
            ):
                return {
                    "disease": disease,
                    "treatment": info["treatment"],
                    "symptoms": info["symptoms"],
                    "severity": info["severity"],
                }

        return {
            "disease": disease_name,
            "treatment": "Consult agricultural expert for specific treatment recommendations.",
            "symptoms": "Not available in database",
            "severity": "UNKNOWN",
        }


from datetime import timedelta
