import ollama

response_ollama = ollama.generate(model="deepseek-r1:1.5b", prompt="Hello, how are you?")
response = response_ollama['response']
print(response)
