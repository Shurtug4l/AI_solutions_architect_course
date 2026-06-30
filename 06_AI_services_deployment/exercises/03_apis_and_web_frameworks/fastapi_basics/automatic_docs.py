from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Studente(BaseModel):
    nome: str = Field(..., description="Il nome dello studente", example='Mario')
    cognome: str = Field(..., description='Il cognome dello studente', example='Rossi')


class Indirizzo(BaseModel):
    via: str = Field(..., description='Via di un indirizzo')
    cap: str = Field(..., example='00100')


class School(BaseModel):
    nome: str = Field(..., example='Istituto XXX')
    indirizzo: Indirizzo = Field(..., description='Indirizzo della scuola')


@app.post("/add_student",
          description='Un endpoint POST per aggiungere uno studente',
          response_description='Id del record aggiunto al database')
def add_student(item: Studente) -> Dict[str, int]:
    """
    Questo endpoint accetta uno studente in input e lo aggiunge al database.
    :param item: studente da aggiungere
    """
    return {"id": 1234}


@app.get("/find_school")
def find_school(student: Studente) -> School:
    """
    Endpoint per trovare la scuola di uno studente
    :param student:
    :return: la scuola dello studente di input
    """
    return School(nome='istituto yyy', indirizzo=Indirizzo(via='via Roma', cap='00100'))

