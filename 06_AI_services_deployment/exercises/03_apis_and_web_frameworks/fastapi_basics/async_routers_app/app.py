from fastapi import FastAPI
from .routers import student, teacher

app = FastAPI(title='My example API', description='xxx', version='1.0.0', include_in_schema=True)


app.include_router(student.router)
app.include_router(teacher.router)


@app.get("/")
def root_endpoint():
    return "Hello"
