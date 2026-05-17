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
