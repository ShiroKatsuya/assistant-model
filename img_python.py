import os
import google.generativeai as genai

genai.configure(api_key = os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

chat = model.start_chat(history=[])

response = chat.send_message("Now explain it like I a Physics PhD student")
print(response.text)
