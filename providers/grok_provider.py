import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)


def grok_chat(prompt: str):
    response = client.chat.completions.create(
        model="grok-2-latest",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    usage = response.usage

    return {
        "provider": "grok",
        "status": "live",
        "fallback_used": False,
        "message": response.choices[0].message.content,
        "usage": {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens
        }
    }
