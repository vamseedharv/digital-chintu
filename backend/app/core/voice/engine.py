"""Wraps openWakeWord model inference. Lazily imports `openwakeword` (an
optional `voice` extra, see backend/pyproject.toml) so importing this
module never fails on a machine without it installed — see
docs/features/011_Wake_Word.md."""

from dataclasses import dataclass

from app.core.voice.audio import FRAME_SAMPLES


@dataclass(frozen=True)
class Detection:
    model: str
    confidence: float


class ModelUnavailable(Exception):
    """Raised when the detection engine can't be constructed — library not
    installed, or the model files couldn't be downloaded/loaded (e.g. no
    network on first run). Always caught one level up
    (WakeWordRuntime.start()); must never crash the backend."""


class WakeWordEngine:
    """Loads a single openWakeWord model and scores incoming audio frames
    against it."""

    def __init__(self, model_name: str, sensitivity: float) -> None:
        try:
            import openwakeword
            from openwakeword.model import Model
        except ImportError as exc:
            raise ModelUnavailable(
                "openwakeword/onnxruntime are not installed — run "
                "`pip install '.[voice]'` to enable wake-word detection"
            ) from exc

        try:
            openwakeword.utils.download_models([model_name])
            self._model = Model(wakeword_models=[model_name], inference_framework="onnx")
        except Exception as exc:
            raise ModelUnavailable(
                f"could not load wake-word model '{model_name}': {exc}"
            ) from exc

        self._model_name = model_name
        self._sensitivity = sensitivity

    def detect(self, frame: bytes) -> list[Detection]:
        import numpy as np

        pcm = np.frombuffer(frame, dtype=np.int16)
        if pcm.shape[0] != FRAME_SAMPLES:
            return []
        scores = self._model.predict(pcm)
        return [
            Detection(model=name, confidence=float(score))
            for name, score in scores.items()
            if score >= self._sensitivity
        ]
