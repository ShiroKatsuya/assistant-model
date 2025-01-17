import google.generativeai as genai
import os
import random
from voice import voice, save_audio

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
client = genai.GenerativeModel('gemini-1.5-flash')

def random_teks():
    templates = [
        "Sorry I Don't Understand Your Voice",
        "I Cannot Understand What You Said",
        "Your Voice Is Not Clear Enough",
        "Could You Please Speak More Clearly",
        "I Didn't Catch Your Voice Well",
        "Your Voice Was Not Clear To Me",
        "I'm Having Trouble With Your Voice",
        "Would You Mind Speaking Up Again",
        "I Couldn't Hear Your Voice Clearly",
        "Your Voice Message Was Unclear"
    ]

    selected = random.choice(templates)
    
    prompt = f"Rewrite this phrase in a different way 5 words 1 sentences: {selected}"
    response = client.generate_content(prompt)
    reponse = response.text.replace('*', '').replace('\n\n', '\n')
    return reponse

# print(random_teks())
# voice(random_teks())
save_audio(random_teks())
print("done")