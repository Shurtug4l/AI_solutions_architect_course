import time
from typing import Optional
import logging

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s: %(asctime)s - %(message)s")


class Student(BaseModel):
    nome: str = Field(..., description="Nome dello studente")
    cognome: str = Field(..., description="cognome dello studente")
    student_id: int = Field(..., description="ID dello studente")
    genere: Optional[str] = Field(default='ND', description="GENERE dello studente")


app = FastAPI()


def expansive_function():
    logger.info("Start expansive function")
    time.sleep(5)
    logger.info("End expansive function")


@app.post("/add_student")
async def add_student(student: Student, background_task: BackgroundTasks):
    logger.info("Start request")
    background_task.add_task(expansive_function)
    logger.info("End request")
    return student
