# Pokemon Image Classifier API

This project provides a FastAPI-based backend for classifying Pokemon images using a fine-tuned Vision Transformer (ViT) model.

## Features

- **FastAPI**: High-performance, easy-to-use web framework.
- **Transformers & Torch**: State-of-the-art machine learning capabilities.
- **Image Processing**: Automatic resizing and normalization of input images.
- **JSON Output**: Returns predicted class and confidence score.

## Prerequisites

- Python 3.12+
- `uv` (for dependency management)

## Installation

From this exercise folder:

```bash
uv sync
```

## Model weights (not versioned)

The API expects a `model/` directory at the project root with the fine-tuned ViT
checkpoint and processor files (`save_pretrained` layout). The weights are not
committed: they are heavy and were produced during the lesson. Any ViT
image-classification checkpoint saved with `save_pretrained("model")` works as a
stand-in (e.g. `google/vit-base-patch16-224`), with generic ImageNet classes instead
of Pokemon ones.

## Usage

### Running the Server

Start the FastAPI application using `uvicorn`:

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

### API Documentation

Once the server is running, you can access the interactive API docs:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Endpoints

#### `GET /`
Returns a welcome message.

#### `POST /predict`
Upload an image file to get the Pokemon prediction.

**Example using `curl`:**
```bash
curl -X POST "http://localhost:8000/predict" -F "file=@path/to/image.png"
```

**Response Example:**
```json
{
  "class_name": "Pikachu",
  "confidence": 0.98
}
```

## Testing

You can verify the model and integration using the provided test script:

```bash
uv run python test_model.py
```

This script attempts to load the local model from `model/` and classify the `test_image.png` file in the root directory.

API tests (root endpoint, prediction happy path, invalid file rejection) run with:

```bash
uv run pytest
```

## Docker

The lesson's end state is the containerized microservice:

```bash
docker build -t pokemon-classifier .
docker run -p 8000:8000 pokemon-classifier
```

The Dockerfile copies `model/` into the image, so the weights must be present before
building. Port mapping exposes the isolated service on the host network; the same
Postman/curl request used against the local server must return the same prediction.

## Project Structure

- `src/`: Source code for the API and model inference.
    - `main.py`: FastAPI application entry point.
    - `model.py`: Model loader and prediction logic.
- `model/`: Directory containing the fine-tuned model and processor files (not versioned).
- `tests/test_app.py`: API tests via FastAPI TestClient.
- `test_model.py`: Standalone script to test model inference without the API.
- `Dockerfile`, `.dockerignore`: container build for the service.
