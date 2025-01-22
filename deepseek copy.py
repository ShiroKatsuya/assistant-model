import ollama

class DeepSeekR1:
    def __init__(self):
        self.model_name = "deepseek-r1:1.5b"
        self.system_prompt = """You are DeepSeek R1, an intelligent assistant. Your capabilities include:
                                1. Understanding and responding to natural language queries
                                2. Providing accurate and contextually relevant information
                                3. Assisting with problem solving and decision making
                                4. Maintaining coherent and helpful conversations
                                5. Adapting to user needs and preferences"""

    def generate_response(self, user_input):
        try:
            response = ollama.generate(
                model=self.model_name,
                system=self.system_prompt,
                prompt=user_input
            )
            return response['response']
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def chat(self):
        print("DeepSeek R1 initialized. Type 'exit' to end the conversation.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break
            response = self.generate_response(user_input)
            print(f"DeepSeek: {response}")

if __name__ == "__main__":
    assistant = DeepSeekR1()
    assistant.chat()
