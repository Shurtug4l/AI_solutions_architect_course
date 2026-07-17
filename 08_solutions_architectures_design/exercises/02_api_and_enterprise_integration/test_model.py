from transformers import AutoModelForImageClassification, AutoImageProcessor
from PIL import Image
import torch
import os

def test_model():
    model_path = "./model"
    image_path = "test_image.png"

    print(f"Loading model from {model_path}...")
    try:
        model = AutoModelForImageClassification.from_pretrained(model_path)
        processor = AutoImageProcessor.from_pretrained(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    print(f"Loading image from {image_path}...")
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return
        
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    print("Running inference...")
    inputs = processor(image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
    
    logits = outputs.logits
    probs = torch.nn.functional.softmax(logits, dim=-1)
    
    # Get top 5 predictions
    top5_prob, top5_indices = torch.topk(probs, 5)
    
    print("\nTop 5 Predictions:")
    for i in range(5):
        class_idx = top5_indices[0][i].item()
        probability = top5_prob[0][i].item()
        # Try string key first, then integer key, then default to index
        label = model.config.id2label.get(str(class_idx)) or model.config.id2label.get(class_idx) or f"Class {class_idx}"
        print(f"{i+1}. {label}: {probability:.4f}")

if __name__ == "__main__":
    test_model()
