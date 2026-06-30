from fastapi import APIRouter, status, FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse


class Studente(BaseModel):
    nome: str
    cognome: str
    student_id: int

router = FastAPI()

@router.get("/get_student/{student_id}")
def get_student(student_id: int):
    try:
        my_student = Studente(nome='Mario',
                              cognome='Rossi', student_id=student_id)
    except Exception as e:
        return JSONResponse(
            content={"error": 'Error msg'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JSONResponse(content={'value': my_student.model_dump()},
                        status_code=status.HTTP_200_OK)
