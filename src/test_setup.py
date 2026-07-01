from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

print("✓ All libraries installed correctly")
print(f"✓ Groq API key loaded: {api_key[:10]}...")

client = Groq(api_key=api_key)
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": "You are a secure banking assistant for National Digital Bank India."
        },
        {
            "role": "user",
            "content": "Say hello in one sentence as a banking assistant."
        }
    ]
)

print(f"✓ Groq API working: {response.choices[0].message.content}")
print("✓ Day 1 complete. Ready to build.")