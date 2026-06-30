from fastapi import FastAPI, HTTPException, Query
from fastapi import FastAPI, Query
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

app = FastAPI()

class City(BaseModel):
    city: str
    country: str

data = [
    City(city="Napoli", country="Italy"),
    City(city="Pisa", country="Italy"),
    City(city="Reykjavik", country="Iceland"),
    City(city="Bali", country="Indonesia")
]

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <link rel="shortcut icon" href="#">
    <head>
        <meta charset="UTF-8">
        <title>Congratulazioni</title>
    </head>
    <body>
        <div style="text-align: center; margin-top: 100px;">
            <h1>Congratulazioni, questo è il tuo primo endpoint con FastAPI!</h1>
        </div>
    </body>
    </html>
    """

@app.get("/cities")
async def get_cities(city: Optional[str] = Query(None), country: Optional[str] = Query(None)):
    if city and country:
        filtered_cities = [c for c in data if c.city == city and c.country == country]
    elif city:
        filtered_cities = [c for c in data if c.city == city]
    elif country:
        filtered_cities = [c for c in data if c.country == country]
    else:
        filtered_cities = data
    return filtered_cities

@app.post("/cities")
async def add_city(new_city: City):
    for existing_city in data:
        if existing_city.city == new_city.city and existing_city.country == new_city.country:
            raise HTTPException(status_code=400, detail="City already exists.")
    data.append(new_city)
    return {"message": f"City {new_city.city} added successfully."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
