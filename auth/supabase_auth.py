from db.supabase_client import supabase


def verify_token(token: str):
    try:
        user_response = supabase.auth.get_user(token)

        if user_response.user:
            return {
                "email": user_response.user.email,
                "id": user_response.user.id
            }

        return None

    except Exception:
        return None


def get_user_by_email(email: str):
    result = supabase.table("users").select("*").eq("email", email).execute()

    if result.data:
        return result.data[0]

    return None


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
