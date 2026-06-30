from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field


class Student(BaseModel):
    nome: str = Field(..., description="Nome dello studente")
    cognome: str = Field(..., description="cognome dello studente")
    student_id: int = Field(..., description="ID dello studente")
    genere: Optional[str] = Field(default='ND', description="GENERE dello studente")


app = FastAPI()


@app.post("/add_student")
def add_student(student: Student):
    # add to database
    # ...
    return student
