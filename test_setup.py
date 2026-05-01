from app.services.parser import extract_text, clean_text
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
chat = client.chats.create(model="gemini-2.5-pro")
msg = chat.send_message("say ok")
print("Gemini connected:", msg.text.strip())
print("Setup complete!")
