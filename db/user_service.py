from db.supabase_client import supabase


def get_subscription_tier(user_id: str):
    result = (
        supabase
        .table("subscriptions")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "active")
        .execute()
    )

    if result.data:
        return result.data[0]["tier"]

    return "free"


def ensure_user_exists(user: dict):
    existing = (
        supabase
        .table("users")
        .select("id")
        .eq("id", user["id"])
        .execute()
    )

    if existing.data:
        return

    supabase.table("users").insert({
        "id": user["id"],
        "email": user.get("email"),
        "name": user.get("email", "User").split("@")[0]
    }).execute()