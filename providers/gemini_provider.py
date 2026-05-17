import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")


def normalize(message: str):
    return {
        "provider": "gemini",
        "status": "live",
        "fallback_used": False,
        "message": message,
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }


def gemini_chat(prompt: str):
    response = model.generate_content(prompt)
    return normalize(response.text)


def gemini_vision_chat(prompt: str, image_bytes: bytes, mime_type: str):
    response = model.generate_content([
        prompt,
        {
            "mime_type": mime_type,
            "data": image_bytes
        }
    ])

    return normalize(response.text)
