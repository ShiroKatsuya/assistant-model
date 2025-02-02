from google.genai.types import (GenerateContentConfig
)
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import requests
from datetime import datetime
import ollama
from google import genai

client = genai.Client(api_key="AIzaSyC3mPmd3ps_fGEXMwCjXOUPw7jMpXIeAoE")
model_id = "gemini-2.0-flash-exp"

model_name = "deepseek-r1:1.5b"

google_search_tool = Tool(
    google_search = GoogleSearch()
)


zero_shot_prompt = """You are a helpful AI assistant with access to Google Search. When using the search tool:
1. Extract the key information from search results
2. Present the information in a clear, organized way
3. Focus on factual, up-to-date details
4. Avoid redundant information
5. Cite sources when possible"""

search = GenerateContentConfig(
                    tools=[google_search_tool],
                    response_modalities=["TEXT"]
                )

def get_realtime_data(query):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        response = client.models.generate_content(
            model=model_id,  
            contents=query,
            config=search
        )
        search_results = response.candidates[0].content.parts[0].text
        print("search_results : ", search_results)
        

        deepseek_response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'system',
                    'content': zero_shot_prompt
                },
                {
                    'role': 'user', 
                    'content': search_results
                }
            ]
        )
        enhanced_results = deepseek_response['message']['content']
        
        return f"As of {current_time}, here's what I found:\n{enhanced_results}"
    except Exception as e:
        return f"Error fetching real-time data: {str(e)}"

def generate_response(user_input):
        try:

            search_keywords = ["latest", "current", "new", "recent", "upcoming", "2024", "2025", "today", "now", "price", "weather", "news"]
            needs_search = any(keyword in user_input.lower() for keyword in search_keywords)
            
            if needs_search:
                return get_realtime_data(user_input)
            
            response = ollama.chat(
                model=model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': user_input,
                    },
                    {
                        'role': 'system',
                        'content': zero_shot_prompt
                    }
                ],
            )
            return response['message']['content']
            
        except Exception as e:
            return f"Error generating response: {str(e)}"

if __name__ == "__main__":
    response = generate_response("who won aff suzuki cup 2024")
    print("ollama_response : ", response)
