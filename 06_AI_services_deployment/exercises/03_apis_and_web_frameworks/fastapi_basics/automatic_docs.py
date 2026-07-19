from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Student(BaseModel):
    first_name: str = Field(..., description="The student's first name", example='Mario')
    last_name: str = Field(..., description="The student's last name", example='Rossi')


class Address(BaseModel):
    street: str = Field(..., description='Street of an address')
    zip_code: str = Field(..., example='00100')


class School(BaseModel):
    name: str = Field(..., example='Istituto XXX')
    address: Address = Field(..., description='Address of the school')


@app.post("/add_student",
          description='A POST endpoint that adds a student',
          response_description='Id of the record added to the database')
def add_student(item: Student) -> Dict[str, int]:
    """
    This endpoint takes a student as input and adds it to the database.
    :param item: student to add
    """
    return {"id": 1234}


@app.get("/find_school")
def find_school(student: Student) -> School:
    """
    Endpoint that finds the school of a student
    :param student:
    :return: the school of the input student
    """
    return School(name='istituto yyy', address=Address(street='via Roma', zip_code='00100'))
