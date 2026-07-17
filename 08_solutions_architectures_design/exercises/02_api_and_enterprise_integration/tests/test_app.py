from fastapi.testclient import TestClient
from src.main import app
from PIL import Image
import io

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Pokemon Classifier API! use POST /predict to classify images."}

def test_predict_image():
    # Create a dummy image (red square)
    image = Image.new("RGB", (224, 224), color="red")
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    files = {"file": ("test.png", img_byte_arr, "image/png")}
    response = client.post("/predict", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "class_name" in data
    assert "confidence" in data
    assert isinstance(data["class_name"], str)
    assert isinstance(data["confidence"], float)

def test_predict_invalid_file():
    files = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
