import google.generativeai as genai
import os
from monsterapi import client
import requests
from PIL import Image
import io

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

os.environ['MONSTER_API_KEY']
monster_client = client()

# Define the question prompt
question = "Give me a list of 3 points, each consisting of 3 words, based on the following sentence:"

# Input text for analysis
input_text = """
There is no universally defined 'three-star system'. This term generally refers to a star system consisting of three stars, but the arrangement and dynamics of these stars can vary greatly, resulting in various types of triple star systems. Each system has its own uniqueness, so a single explanation cannot cover them all. However, we can discuss common types and their characteristics.

Types and General Characteristics:

1. Hierarchical Triple Star System
   This is the most common type of triple star system. This system involves a hierarchical arrangement where two stars orbit each other closely as a binary pair, and this binary pair then orbits a third, more distant star. Just imagine a smaller 'planet' of binary stars orbiting a larger star. These systems are generally simpler to model due to less complicated stellar interactions.

2. Trapezium System
   Although usually consisting of four stars, trapezium systems often resemble triple star systems in terms of dynamics. These systems are arranged in more complex configurations, such as two nearby binary star pairs. Despite having four stars, their gravitational interactions can sometimes resemble those in three-star systems.

3. Non-Hierarchical Triple Star System
   These systems are rarer and significantly more chaotic. In such systems, there is no clear binary pair, but rather all three stars orbit each other in an intricate and interconnected dance. Their gravitational interactions are very strong and unpredictable, often leading to unstable orbits, close encounters, or even the ejection of one star from the system.
"""

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

# Generate response and print result
response = model.generate_content([question, input_text])
cleaned_response = response.text.replace('*', '').replace('\n\n', '\n')
print(cleaned_response)

# Split the response into lines and generate normalized images for each point
response_lines = cleaned_response.split('\n')
for line in response_lines:
    if line.strip():  # Check if line is not empty
        # Add context to the prompt for better image generation
        enhanced_prompt = f"Create a realistic and contextually accurate visualization of: {line} in the context"
        
        response_monster = monster_client.generate(model='txt2img', data={
            "prompt": enhanced_prompt,
            "negative_prompt": "cartoon, abstract, unrealistic, distorted",  # Avoid non-realistic elements
            "samples": 1,
            "steps": 30,  # Increase steps for better quality
            "guidance_scale": 7.5  # Adjust guidance scale for better adherence to prompt
        })
        
        print(f"Generated image for: {line}")
        print(response_monster)
        
        image_url = response_monster['output'][0]
        image_bytes = requests.get(image_url).content
        image = Image.open(io.BytesIO(image_bytes))
        
        # Normalize image dimensions while maintaining aspect ratio
        base_width = 1920
        w_percent = base_width / float(image.size[0])
        h_size = int(float(image.size[1]) * float(w_percent))
        image = image.resize((base_width, h_size), Image.Resampling.LANCZOS)
        
        image.show()