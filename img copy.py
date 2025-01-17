import requests

url = "https://api.monsterapi.ai/v1/generate/txt2img"

headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

response = requests.post(url, headers=headers)

print(response.text)