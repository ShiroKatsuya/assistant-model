from google import genai
from PIL import Image
import requests
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from google.genai.types import (GenerateContentConfig
)

from IPython.display import Markdown, display


client = genai.Client(api_key="AIzaSyC3mPmd3ps_fGEXMwCjXOUPw7jMpXIeAoE")
model_id = "gemini-2.0-flash-exp"


# video_import = "sample.mp4"

# response = client.models.generate_content(
#     model=model_id,
#     contents=[video_import, "Do You Know In This Video One Person Is Doing Something Wrong?"],
# )
# print(response.text)

#basic text generation

response = client.models.generate_content(model='gemini-2.0-flash-exp', contents='How does AI work?')
print(response.text)


#web search

# google_search_tool = Tool(
#     google_search = GoogleSearch()
# )

# response = client.models.generate_content(
#     model=model_id,
#     contents="Dune Propency Sinopsis",
#     config=GenerateContentConfig(
#         tools=[google_search_tool],
#         response_modalities=["TEXT"],
#     )
# )

# for each in response.candidates[0].content.parts:
#     print(each.text)
# Example response:
# The next total solar eclipse visible in the contiguous United States will be on ...

# To get grounding metadata as web content.
# print(response.candidates[0].grounding_metadata.search_entry_point.rendered_content)


#Image Sentiment Analysis

# image = Image.open(
# requests.get(
# "https://storage.googleapis.com/cloud-samples-data/generative-ai/image/meal.png",
# stream=True,
# ).raw
# )


# response = client.models.generate_content(
# model=model_id,
# contents=[
# image,
# "Write a short and engaging blog post based on this picture.",
# ]
# )

# print(response.text)


#setting paramters for the model

# gemini_config = GenerateContentConfig(
# temperature=0.2,
# top_p=0.95,
# top_k=20,
# candidate_count=1,
# seed=5,
# max_output_tokens=100,
# stop_sequences=["STOP!"],
# )