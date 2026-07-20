"""Speech-to-text introspection — no dedicated trigger endpoint: STT is
driven purely by the wake-word handoff (POST /api/v1/wake-word/trigger
already reaches it, since SttRuntime just subscribes to the same bus). See
docs/features/012_Speech_To_Text.md."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.voice.stt_runtime import SttRuntime

router = APIRouter()


class SttStatusResponse(BaseModel):
    enabled: bool
    available: bool
    model: str | None
    reason: str | None
    last_transcription: str | None
    last_transcribed_at: str | None


@router.get("/stt/status", response_model=SttStatusResponse)
def get_stt_status(request: Request) -> SttStatusResponse:
    runtime: SttRuntime = request.app.state.stt_runtime
    status = runtime.status
    return SttStatusResponse(
        enabled=status.enabled,
        available=status.available,
        model=status.model,
        reason=status.reason,
        last_transcription=status.last_transcription,
        last_transcribed_at=(
            status.last_transcribed_at.isoformat() if status.last_transcribed_at else None
        ),
    )
