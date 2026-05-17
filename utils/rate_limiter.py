from datetime import datetime, timedelta, timezone
from db.supabase_client import supabase

LIMITS = {
    "free": 20,
    "pro": 500
}


def check_rate_limit(user_id: str, tier: str):
    limit = LIMITS.get(tier, 20)

    result = (
        supabase
        .table("rate_limits")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    now = datetime.now(timezone.utc)

    if not result.data:
        supabase.table("rate_limits").insert({
            "user_id": user_id,
            "request_count": 1,
            "reset_at": (now + timedelta(hours=1)).isoformat()
        }).execute()
        return True

    record = result.data[0]
    reset_at = datetime.fromisoformat(
        record["reset_at"].replace("Z", "+00:00")
    )

    if now > reset_at:
        supabase.table("rate_limits").update({
            "request_count": 1,
            "reset_at": (now + timedelta(hours=1)).isoformat()
        }).eq("user_id", user_id).execute()
        return True

    if record["request_count"] >= limit:
        return False

    supabase.table("rate_limits").update({
        "request_count": record["request_count"] + 1
    }).eq("user_id", user_id).execute()

    return True
