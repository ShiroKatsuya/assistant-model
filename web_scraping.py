import requests
from bs4 import BeautifulSoup

url = "https://id.wikipedia.org/wiki/Politeknik_Negeri_Indramayu"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Ekstrak data spesifik, misalnya body
# Mengambil judul utama
title = soup.find('h1', {'class': 'firstHeading'}).text


infobox = soup.find('table', {'class': 'infobox'})
info_penting = {}
if infobox:
    rows = infobox.find_all('tr')
    for row in rows:
        header = row.find('th')
        data = row.find('td')
        if header and data:
            info_penting[header.text.strip()] = data.text.strip()


important_paragraphs = [p.text for p in soup.find('div', {'class': 'mw-parser-output'}).find_all('p', recursive=False)]

title = f"""
Judul: {title}

Informasi Penting:
{'-'*50}

"""
for key, value in info_penting.items():
    title += f"{key}: {value}\n"
title += f"\nRingkasan:\n{important_paragraphs}"
print(title)
