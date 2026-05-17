from db.supabase_client import supabase


def create_conversation(user_id: str, title: str = "New Chat"):
    result = supabase.table("conversations").insert({
        "user_id": user_id,
        "title": title
    }).execute()

    return result.data[0]["id"]


def get_conversation(conversation_id: str, user_id: str):
    result = (
        supabase
        .table("conversations")
        .select("*")
        .eq("id", conversation_id)
        .eq("user_id", user_id)
        .execute()
    )

    return result.data


def save_message(conversation_id: str, role: str, content: str):
    supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "role": role,
        "content": content
    }).execute()


def get_recent_messages(conversation_id: str, limit: int = 10):
    result = (
        supabase
        .table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .limit(limit)
        .execute()
    )

    return result.data
