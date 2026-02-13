import numpy as np
from PIL import Image
import io
from typing import Tuple, Dict

class SoilDetectionModel:
    def __init__(self):
        """
        Initialize soil type detection model
        Using pretrained model for soil classification
        """
        self.model = None
        self.soil_types = [
            "Clay",
            "Sandy",
            "Loamy",
            "Silty",
            "Peaty",
            "Chalky",
            "Red Soil",
            "Black Soil",
            "Alluvial",
            "Laterite"
        ]
        
        # Soil characteristics database
        self.soil_characteristics = {
            "Clay": {
                "texture": "Very fine particles",
                "water_retention": "High",
                "drainage": "Poor",
                "nutrients": "High",
                "best_for": ["Rice", "Wheat", "Pulses"]
            },
            "Sandy": {
                "texture": "Coarse particles",
                "water_retention": "Low",
                "drainage": "Excellent",
                "nutrients": "Low",
                "best_for": ["Millet", "Groundnut", "Watermelon"]
            },
            "Loamy": {
                "texture": "Well-balanced mix",
                "water_retention": "Good",
                "drainage": "Good",
                "nutrients": "High",
                "best_for": ["Most vegetables", "Fruits", "Grains"]
            },
            "Silty": {
                "texture": "Smooth, fine particles",
                "water_retention": "Good",
                "drainage": "Moderate",
                "nutrients": "Moderate to High",
                "best_for": ["Vegetables", "Grass crops"]
            },
            "Black Soil": {
                "texture": "Fine, cotton soil",
                "water_retention": "Very High",
                "drainage": "Poor when wet",
                "nutrients": "High in calcium, potassium",
                "best_for": ["Cotton", "Sugarcane", "Jowar"]
            },
            "Red Soil": {
                "texture": "Sandy to clay",
                "water_retention": "Moderate",
                "drainage": "Good",
                "nutrients": "Rich in iron",
                "best_for": ["Groundnut", "Millets", "Tobacco"]
            },
            "Alluvial": {
                "texture": "Deposited by rivers",
                "water_retention": "Good",
                "drainage": "Good",
                "nutrients": "Very High",
                "best_for": ["Rice", "Wheat", "Sugarcane", "Cotton"]
            }
        }
        
        # Load model (mock for now)
        self.model = self._create_mock_model()
    
    def _create_mock_model(self):
        """Create mock model for development"""
        return "mock_soil_model"
    
    def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """Preprocess soil image"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            image = image.resize((224, 224))
            img_array = np.array(image) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
        except Exception as e:
            print(f"Soil image preprocessing error: {e}")
            raise ValueError("Invalid image format")
    
    def predict(self, image_bytes: bytes) -> Tuple[str, float, Dict]:
        """
        Predict soil type from image
        
        Returns:
            Tuple of (soil_type, confidence, characteristics)
        """
        try:
            img_array = self.preprocess_image(image_bytes)
            
            if self.model == "mock_soil_model":
                return self._mock_prediction()
            
            # Actual model prediction would go here
            
        except Exception as e:
            print(f"Soil prediction error: {e}")
            raise ValueError(f"Prediction failed: {str(e)}")
    
    def _mock_prediction(self) -> Tuple[str, float, Dict]:
        """Generate mock soil prediction"""
        soil_idx = np.random.randint(0, len(self.soil_types))
        soil_type = self.soil_types[soil_idx]
        confidence = np.random.uniform(0.80, 0.98)
        
        characteristics = self.soil_characteristics.get(
            soil_type,
            {
                "texture": "Unknown",
                "water_retention": "Unknown",
                "drainage": "Unknown",
                "nutrients": "Unknown",
                "best_for": []
            }
        )
        
        return soil_type, confidence, characteristics

# Global instance
soil_model = SoilDetectionModel()

def detect_soil_type(image_bytes: bytes) -> dict:
    """
    Detect soil type from image
    
    Returns:
        Dict with soil_type, confidence, and characteristics
    """
    soil_type, confidence, characteristics = soil_model.predict(image_bytes)
    
    return {
        "soil_type": soil_type,
        "confidence": confidence,
        "characteristics": characteristics
    }
