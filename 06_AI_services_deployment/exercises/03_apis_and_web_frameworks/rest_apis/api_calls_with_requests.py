import requests
import json

url = "https://google.com"
res = requests.get(url)
print(res.status_code)
print(res.text)


url = 'http://ip.jsontest.com/'
res = requests.get(url)
print(res.status_code)
print(res.json())


url_for_post = 'https://jsonplaceholder.typicode.com/posts'
payload = json.dumps(
    {"nome": "Andrea",
     "cognome": "Rossi"}
    )

headers = {
  'Content-Type': 'application/json'
}

res = requests.post(url_for_post, data=payload, headers=headers)
print(res.status_code)
res.json()