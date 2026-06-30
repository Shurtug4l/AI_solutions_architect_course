import requests
import io
import PIL.Image as Image

response = requests.get('https://cataas.com/cat')

print(response)

print(type(response.content))

image = Image.open(io.BytesIO(response.content))
image.save("cat.jpeg")