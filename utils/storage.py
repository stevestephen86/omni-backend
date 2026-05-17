import uuid
from db.supabase_client import supabase


def upload_file(file_bytes: bytes, filename: str, mime_type: str):
    unique_name = f"{uuid.uuid4()}_{filename}"

    supabase.storage.from_("uploads").upload(
        path=unique_name,
        file=file_bytes,
        file_options={
            "content-type": mime_type
        }
    )

    public_url = supabase.storage.from_("uploads").get_public_url(
        unique_name
    )

    return {
        "path": unique_name,
        "url": public_url
    }
