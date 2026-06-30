import requests

url = "http://localhost:8000/inference"

data = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
}

response = requests.post(url, json=data)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Errore: {response.json()}")