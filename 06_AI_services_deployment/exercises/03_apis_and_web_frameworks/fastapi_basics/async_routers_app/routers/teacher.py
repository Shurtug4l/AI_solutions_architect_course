from fastapi import APIRouter

router = APIRouter(prefix='/teacher', include_in_schema=False)


@router.get("/get_teacher_name")
def get_teacher_name():
    return "Maria"


@router.delete("/teacher")
def remove_teacher(name: str):
    return f"Teacher {name} removed"
