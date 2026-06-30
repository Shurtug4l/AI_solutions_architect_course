import requests
import io
import PIL.Image as Image

response_filter = requests.get("https://cataas.com/cat?filter=mono")
print(response_filter)

image = Image.open(io.BytesIO(response_filter.content))
image.save("cat_with_filter.jpeg")