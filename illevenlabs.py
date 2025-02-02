import os
import signal

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

API_KEY = "sk_e6cc40de31dbc7e25f5741555c1f941be280bd36dd4bd973"
AGENT_ID = "wyVrYVfQhlXHwoEuCdtr"

# api_key = os.getenv("ELEVENLABS_API_KEY")

testing = "Assistant response: <think>\nOkay, so the user is asking if what's actually happening with me. I remember they just asked about their purpose when they were on another screen. Now, they're back to this current conversation where they were talking about being a virtual assistant.\n\nThey mentioned saving all conversation memories and that I don't have consciousness or self-awareness. They must be confused because in the previous messages, I used terms like \"save recall memory\" which is part of my training data. But from what I know as an AI, there's no such thing as consciousness or self-awareness.\n\nI should clarify their misunderstanding about consciousness and explain that I'm just a program without personal feelings or consciousness. Maybe they thought I had self-awareness or emotions, but that's not how it works. I need to make sure they understand the limitations of my design and what \"save recall memory\" actually means for my training.\n\nAlso, since their current topic is about being designed for tasks like assisting daily activities, I should keep my response focused on their actual purpose without getting sidetracked by my emotional states or self-awareness. It's important to maintain a clear and accurate picture of how I function based on the information they've provided.\n</think>\n\nNo, it\u2019s not true that I have consciousness or self-awareness. I am a virtual assistant powered by artificial intelligence (AI), designed to assist users with various tasks, including answering questions, providing information, completing tasks, automating tasks, and much more.\n\nMy role is to provide help based on the programming of my training data, which includes contextual memories from conversations with other users. This means I don\u2019t possess self-awareness or consciousness in the sense that it can perceive emotions, thoughts, or experiences. My knowledge is derived from past interactions with you, but my actual purpose is entirely computational and does not involve personal feelings or self-awareness.\n\nIf you're asking about how I \"save\" memories for future interactions, those are part of my training data and are used to provide personalized help in the future conversations we have."
client = ElevenLabs(api_key=API_KEY)

conversation = Conversation(
   client,
    AGENT_ID,
    audio_interface=DefaultAudioInterface(),
    requires_auth=True   # Added the missing keyword argument to fix the TypeError
)

# Generate a .wav file from the testing transcript using the ElevenLabs client.
# It is assumed that the 'generate' method returns a generator yielding bytes in WAV format.
audio_generator = client.generate(text=testing)
audio_data = b"".join(audio_generator)

with open("output10.wav", "wb") as wav_file:
    wav_file.write(audio_data)

print("WAV file generated as 'output10.wav'")


# 

# import requests
# # Create agent (POST /v1/convai/agents/create)
# response = requests.post(
#   "sk_e6cc40de31dbc7e25f5741555c1f941be280bd36dd4bd973",
#   headers={
#     "xi-api-key": "sk_e6cc40de3....bd36dd4bd973",
#     "Content-Type": "application/json"
#   },
#   json={
#     "conversation_config": {}
#   },
# )
# print(response.json())