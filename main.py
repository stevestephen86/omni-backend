from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Header, UploadFile, File, Form
from pydantic import BaseModel
import time

from routers.groq_router import route_prompt
from providers.provider_dispatcher import dispatch

from auth.supabase_auth import verify_token
from db.user_service import get_subscription_tier

from utils.rate_limiter import check_rate_limit
from utils.memory import (
    create_conversation,
    get_conversation,
    save_message,
    get_recent_messages
)
from utils.storage import upload_file
from utils.logger import log_usage

# Create FastAPI app instance before applying middleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str
    attachments: list = []
    conversation_id: str | None = None


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "omni-backend"
    }


@app.post("/route")
def route(req: ChatRequest):
    return route_prompt(req.prompt, req.attachments)




@app.post("/chat")
async def chat(
    prompt: str = Form(...),
    conversation_id: str = Form(None),
    file: UploadFile = File(None),
    authorization: str | None = Header(None)
):
    if not authorization:
        return {"error": "missing authorization"}

    token = authorization.replace("Bearer ", "")
    user = verify_token(token)

    if not user:
        return {"error": "invalid token"}

    tier = get_subscription_tier(user["id"])

    if not check_rate_limit(user["id"], tier):
        return {
            "error": "rate limit exceeded",
            "tier": tier
        }

    attachments = []
    image_bytes = None
    mime_type = None

    if file:
        image_bytes = await file.read()
        mime_type = file.content_type

        uploaded = upload_file(
            image_bytes,
            file.filename,
            mime_type
        )

        attachments.append({
            "type": "image",
            "filename": file.filename,
            "url": uploaded["url"]
        })

    if conversation_id:
        convo = get_conversation(
            conversation_id,
            user["id"]
        )

        if not convo:
            return {
                "error": "unauthorized conversation access"
            }

    else:
        conversation_id = create_conversation(
            user["id"],
            prompt[:40]
        )

    history = get_recent_messages(conversation_id)

    context_prompt = ""

    for msg in history:
        context_prompt += f"{msg['role']}: {msg['content']}\n"

    context_prompt += f"user: {prompt}"

    save_message(
        conversation_id,
        "user",
        prompt
    )

    routing = route_prompt(
        context_prompt,
        attachments
    )

    start = time.time()

    result = dispatch(
        provider=routing["provider"],
        prompt=context_prompt,
        tier=tier,
        image_bytes=image_bytes,
        mime_type=mime_type
    )

    latency_ms = int((time.time() - start) * 1000)

    usage = result.get("usage", {})

    log_usage(
        user_id=user["id"],
        conversation_id=conversation_id,
        prompt=prompt,
        selected_provider=routing["provider"],
        response_provider=result.get("provider"),
        fallback_used=result.get("fallback_used", False),
        fallback_reason=result.get("fallback_reason", ""),
        prompt_tokens=usage.get("prompt_tokens", 0),
        completion_tokens=usage.get("completion_tokens", 0),
        total_tokens=usage.get("total_tokens", 0),
        latency_ms=latency_ms,
        tier=tier,
        had_upload=bool(file)
    )

    save_message(
        conversation_id,
        "assistant",
        result["message"]
    )

    return {
        "user": user["email"],
        "tier": tier,
        "conversation_id": conversation_id,
        "routing": routing,
        "response": result,
        "uploaded_file": attachments if file else None
    }
