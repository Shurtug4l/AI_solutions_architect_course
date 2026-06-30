import requests

url = "http://127.0.0.1:8000/cities"

data = {
    "city": "Sorong",
    "country": "Indonesia"
}

response = requests.post(url, json=data)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Errore: {response.status_code} - {response.json()}")