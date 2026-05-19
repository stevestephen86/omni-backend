from db.supabase_client import supabase


def ensure_user_exists(user):
    existing = supabase.table("users").select("id").eq("id", user["id"]).execute()

    if existing.data:
        return

    supabase.table("users").insert({
        "id": user["id"],
        "email": user["email"],
        "full_name": user.get("email", "").split("@")[0],
        "tier": "free"
    }).execute()


def get_subscription_tier(user_id):
    result = supabase.table("subscriptions") \
        .select("tier,status") \
        .eq("user_id", user_id) \
        .eq("status", "active") \
        .limit(1) \
        .execute()

    if result.data:
        return result.data[0]["tier"]

    return "free"