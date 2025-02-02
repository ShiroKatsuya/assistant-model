import ollama

def generate_response(user_input):
    response = ollama.generate(
        model="",
        prompt=user_input
    )
    return response['response']


if __name__ == "__main__":
    user_input = "distance from earth to moon"
    response = generate_response(user_input)
    print(response)






