import requests

# paste your Hugging Face token here
API_TOKEN = "hf_..."

API_URL = "https://api-inference.huggingface.co/models/neuraly/bert-base-italian-cased-sentiment"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# usage (Italian input by design: the model is an Italian sentiment classifier)
output = query({
    "inputs": "Questo corso è molto interessante!",
})

print(output)