from providers.provider_registry import PROVIDER_CAPABILITIES

from providers.groq_provider import groq_chat
from providers.deepseek_provider import deepseek_chat
from providers.grok_provider import grok_chat
from providers.gemini_provider import gemini_chat, gemini_vision_chat
from providers.openai_provider import gpt4o_chat


def dispatch(
    provider: str,
    prompt: str,
    tier: str,
    image_bytes=None,
    mime_type=None
):
    config = PROVIDER_CAPABILITIES.get(provider)

    if not config:
        return groq_chat(prompt)

    if tier not in config["tiers"]:
        fallback = groq_chat(prompt)
        fallback["fallback_used"] = True
        fallback["fallback_reason"] = "tier restriction"
        return fallback

    try:
        if provider == "groq":
            return groq_chat(prompt)

        if provider == "deepseek":
            return deepseek_chat(prompt)

        if provider == "grok":
            return grok_chat(prompt)

        if provider == "gpt4o":
            return gpt4o_chat(prompt)

        if provider == "gemini":
            if image_bytes:
                return gemini_vision_chat(
                    prompt,
                    image_bytes,
                    mime_type
                )
            return gemini_chat(prompt)

    except Exception as e:
        fallback = groq_chat(prompt)
        fallback["fallback_used"] = True
        fallback["fallback_reason"] = str(e)
        fallback["original_provider"] = provider
        return fallback

    return groq_chat(prompt)
