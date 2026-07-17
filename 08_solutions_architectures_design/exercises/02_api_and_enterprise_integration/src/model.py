import torch
from transformers import ViTForImageClassification, ViTImageProcessor
from PIL import Image
import io
import os

# Define path to the model directory
# Assuming this file is in src/ and model/ is in the parent directory
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")

class PokemonClassifier:
    def __init__(self):
        print(f"Loading model from {MODEL_DIR}...")
        self.processor = ViTImageProcessor.from_pretrained(MODEL_DIR)
        self.model = ViTForImageClassification.from_pretrained(MODEL_DIR)
        self.model.eval()
        print("Model loaded successfully.")

    def predict(self, image_bytes: bytes):
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)
        
        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        
        # Calculate confidence
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        confidence = probabilities[0, predicted_class_idx].item()
        
        class_name = self.model.config.id2label[predicted_class_idx]
        
        return {
            "class_name": class_name,
            "confidence": confidence
        }

# Global instance
classifier = PokemonClassifier()
