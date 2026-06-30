import requests

# inserimento token
API_TOKEN = "hf_..."

API_URL = "https://api-inference.huggingface.co/models/neuraly/bert-base-italian-cased-sentiment"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# utilizzo
output = query({
    "inputs": "Questo corso è molto interessante!",
})

print(output)