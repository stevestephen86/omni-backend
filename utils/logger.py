from db.supabase_client import supabase


def log_usage(
    user_id: str,
    conversation_id: str,
    prompt: str,
    selected_provider: str,
    response_provider: str,
    fallback_used: bool,
    fallback_reason: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    latency_ms: int,
    tier: str,
    had_upload: bool
):
    supabase.table("usage_logs").insert({
        "user_id": user_id,
        "conversation_id": conversation_id,
        "prompt": prompt,
        "selected_provider": selected_provider,
        "response_provider": response_provider,
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "latency_ms": latency_ms,
        "tier": tier,
        "had_upload": had_upload
    }).execute()
