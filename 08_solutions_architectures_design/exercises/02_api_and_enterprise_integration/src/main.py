from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from src.model import classifier

app = FastAPI(title="Pokemon Classifier API", description="API to classify Pokemon images using a fine-tuned ViT model.")

class PredictionResponse(BaseModel):
    class_name: str
    confidence: float

@app.get("/")
def read_root():
    return {"message": "Welcome to the Pokemon Classifier API! use POST /predict to classify images."}

@app.post("/predict", response_model=PredictionResponse)
async def predict_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    try:
        contents = await file.read()
        prediction = classifier.predict(contents)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
