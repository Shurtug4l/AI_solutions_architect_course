from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)