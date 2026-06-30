from fastapi import APIRouter

router = APIRouter(prefix='/student')


@router.get("/get_student_name")
def get_student_name():
    return "Francesca"


@router.delete("/student")
def remove_student(name: str):
    return f"Student {name} removed"