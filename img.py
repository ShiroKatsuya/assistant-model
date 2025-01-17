import os
from monsterapi import client
from PIL import Image
import io
import requests
import google.generativeai as genai


#Set the Monster API key as an environment variable
os.environ['MONSTER_API_KEY']
genai.configure(api_key = os.getenv("GEMINI_API_KEY"))

#Initialize the Monster API client
monster_client = client()

prompt = "create image black hole ultra hd 4k reference gargantua"

if prompt.startswith("create image" or "create images" or "buatkan saya gambar" or "gambar" or "image" or "buatkan gambar"):
    #Fetch a response from the Monster API
    response = monster_client.generate(model='txt2img', data={
        "prompt": prompt})
    print(response)

    # Convert response to PIL Image and open
    image_url = response['output'][0]  # Get first URL from output list
    image_bytes = requests.get(image_url).content
    image = Image.open(io.BytesIO(image_bytes))
    image.show()
    sentiment = image
    model = genai.GenerativeModel('gemini-1.5-flash')

    response = model.generate_content(["describe the image in detail", sentiment])
    print(response.text)
else:
    print("Please enter a prompt first like this: create image in first teks")


