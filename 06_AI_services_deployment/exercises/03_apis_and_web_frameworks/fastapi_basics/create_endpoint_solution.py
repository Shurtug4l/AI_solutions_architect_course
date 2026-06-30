from datetime import datetime
import uuid

from fastapi import FastAPI
from pydantic import BaseModel, Field


class Item(BaseModel):
    nome: str = Field(..., description='Nome del prodotto', example='Vite')
    scaffale: int = Field(default=10)
    data_registrazione: datetime = Field(..., description='Data di registrazione')


app = FastAPI()


@app.post("/load_item")
def load_item(item: Item):
    # add to db
    # ...
    return uuid.uuid4()


@app.get("/get_item")
def get_item(item_id: str):
    current_item = Item(nome='Bullone', scaffale=30, data_registrazione=datetime.today())
    return {'message': f'{item_id} ricevuto', 'item': current_item}
