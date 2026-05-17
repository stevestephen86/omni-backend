import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ROUTER_PROMPT = """
You are OMNI's routing intelligence.

Your ONLY job is to choose the BEST provider.

AVAILABLE PROVIDERS ONLY:

groq
Use for:
- casual chat
- greetings
- simple questions
- quick math
- lightweight reasoning
- general fast responses

deepseek
Use for:
- coding
- debugging
- algorithms
- software engineering
- backend/frontend coding
- SQL/database issues
- technical implementation

gemini
Use for:
- screenshots
- images
- PDFs
- document analysis
- OCR
- visual comparison
- multimodal tasks

grok
Use for:
- latest news
- live information
- realtime web-aware questions
- current events
- trending topics
- crypto prices
- stock/live market info

gpt4o
Use for:
- business strategy
- startup advice
- pricing strategy
- product thinking
- deep reasoning
- planning
- nuanced recommendations

IMPORTANT:
If attachments include image/pdf/document/screenshot, strongly prefer gemini.

Return STRICT JSON ONLY:

{
  "provider": "groq|deepseek|gemini|grok|gpt4o",
  "confidence": 1,
  "reason": "short explanation"
}
"""

def route_prompt(user_prompt, attachments=None):
    attachment_context = ""

    if attachments:
        attachment_types = []

        for a in attachments:
            if hasattr(a, "type"):
                attachment_types.append(a.type)
            elif isinstance(a, dict):
                attachment_types.append(a["type"])

        attachment_context = f"\nAttachments present: {', '.join(attachment_types)}"

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": ROUTER_PROMPT},
            {
                "role": "user",
                "content": user_prompt + attachment_context
            }
        ],
        temperature=0
    )

    response = completion.choices[0].message.content.strip()
    response = response.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(response)

        allowed = ["groq", "deepseek", "gemini", "grok", "gpt4o"]

        if parsed.get("provider") not in allowed:
            return {
                "provider": "groq",
                "confidence": 50,
                "reason": "Invalid provider returned"
            }

        return parsed

    except Exception:
        return {
            "provider": "groq",
            "confidence": 60,
            "reason": "Fallback due to parse issue"
        }
