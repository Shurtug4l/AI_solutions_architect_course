from fastapi import FastAPI
from pydantic import BaseModel
import pickle

app = FastAPI()

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

class IrisData(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

@app.post("/inference")
async def predict(data: IrisData):
    
    features = [[
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width
    ]]
    
    
    prediction = model.predict(features)[0]
    return {"prediction": prediction}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)