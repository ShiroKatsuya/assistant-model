import google.generativeai as genai
import os
import random
from voice import voice, save_audio

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
client = genai.GenerativeModel('gemini-1.5-flash')

def random_teks():
    templates = [
        "Ready to start recording now",
        "Let's begin the recording session", 
        "Recording can commence now",
        "All set for recording",
        "Time to start recording",
        "Recording system initialized",
        "Microphone is ready now",
        "Begin recording sequence",
        "Recording mode activated",
        "System primed for recording"
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