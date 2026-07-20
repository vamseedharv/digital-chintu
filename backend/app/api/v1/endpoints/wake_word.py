"""Wake-word introspection and the push-to-talk fallback. See
docs/features/011_Wake_Word.md — `POST /trigger` always works regardless of
whether real audio-driven detection is available, by design."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.voice.events import WakeWordEvent
from app.core.voice.runtime import WakeWordRuntime

router = APIRouter()


class WakeWordStatusResponse(BaseModel):
    enabled: bool
    listening: bool
    model: str | None
    reason: str | None


class WakeWordEventResponse(BaseModel):
    model: str | None
    confidence: float
    trigger: str
    detected_at: str


def _to_event_response(event: WakeWordEvent) -> WakeWordEventResponse:
    return WakeWordEventResponse(
        model=event.model,
        confidence=event.confidence,
        trigger=event.trigger,
        detected_at=event.detected_at.isoformat(),
    )


@router.get("/wake-word/status", response_model=WakeWordStatusResponse)
def get_wake_word_status(request: Request) -> WakeWordStatusResponse:
    runtime: WakeWordRuntime = request.app.state.wake_word_runtime
    status = runtime.status
    return WakeWordStatusResponse(
        enabled=status.enabled,
        listening=status.listening,
        model=status.model,
        reason=status.reason,
    )


@router.post("/wake-word/trigger", response_model=WakeWordEventResponse)
async def trigger_wake_word(request: Request) -> WakeWordEventResponse:
    runtime: WakeWordRuntime = request.app.state.wake_word_runtime
    event = await runtime.trigger_manual()
    return _to_event_response(event)
