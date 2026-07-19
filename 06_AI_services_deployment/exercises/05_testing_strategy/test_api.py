from fastapi.testclient import TestClient
from app import app 

client = TestClient(app)

def test_root_endpoint():

    response = client.get("/")

    assert response.status_code == 200, "Expected status code 200"

    assert "text/html" in response.headers["content-type"], "Expected HTML response"

    assert "<h1>This is not an endpoint for PyTest </h1>" in response.text, "Expected HTML content"