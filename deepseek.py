import ollama
model_name = "C.A.L.I.S.T.A:latest"

system_prompt = """You are DeepSeek R1, an intelligent assistant. Your capabilities include:
                                1. Understanding and responding to natural language queries
                                2. Providing accurate and contextually relevant information
                                3. Assisting with problem solving and decision making
                                4. Maintaining coherent and helpful conversations
                                5. Adapting to user needs and preferences"""


def generate_response(user_input):
        try:
            response = ollama.generate(
                model=model_name,
                system=system_prompt,
                prompt=user_input
            )
            return response['response']
            
        except Exception as e:
            return f"Error generating response: {str(e)}"

if __name__ == "__main__":
     response = generate_response("Hello , What Your Name?")
     print(response)
     


