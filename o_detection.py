import requests

api_url = 'https://api.api-ninjas.com/v1/objectdetection'
headers = {'X-Api-Key': 'U3x7lYsAaOZKqDN4sHQQTA==a5xr9L4nI4EpaZEt'}

image_file_descriptor = open('images.jpg', 'rb')
files = {'image': image_file_descriptor}
r = requests.post(api_url, headers=headers, files=files)
print(r.json())
