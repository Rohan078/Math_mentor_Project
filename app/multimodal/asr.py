"""Audio input: ASR using Whisper. Returns transcript and confidence proxy."""
import traceback
import wave
from pathlib import Path
from typing import Tuple

import numpy as np

from app.config import ASR_CONFIDENCE_THRESHOLD

_model = None
WHISPER_SAMPLE_RATE = 16000


def _get_model():
    global _model
    if _model is None:
        import whisper
        _model = whisper.load_model("base")  # tiny/base/small for speed vs accuracy
    return _model


def _load_wav_without_ffmpeg(path: Path) -> Tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as wav:
        nch = wav.getnchannels()
        sampwidth = wav.getsampwidth()
        framerate = wav.getframerate()
        nframes = wav.getnframes()
        raw = wav.readframes(nframes)
    if sampwidth == 2:
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 1:
        audio = (np.frombuffer(raw, dtype=np.uint8) - 128).astype(np.float32) / 128.0
    else:
        raise ValueError(f"Unsupported WAV sample width: {sampwidth}")
    if nch == 2:
        audio = audio.reshape(-1, 2).mean(axis=1)
    if framerate != WHISPER_SAMPLE_RATE:
        n_new = int(len(audio) * WHISPER_SAMPLE_RATE / framerate)
        ix = np.linspace(0, len(audio) - 1, n_new)
        audio = np.interp(ix, np.arange(len(audio)), audio).astype(np.float32)
    return audio, WHISPER_SAMPLE_RATE


def transcribe_audio(audio_path: str | Path) -> Tuple[str, float]:
    path = Path(audio_path)
    if not path.exists():
        return "", 0.0
    if path.stat().st_size < 100:
        return "", 0.0
    if path.suffix.lower() in (".wav", ".wave"):
        try:
            model = _get_model()
            audio, _ = _load_wav_without_ffmpeg(path)
            result = model.transcribe(audio, fp16=False, language="en")
            return _result_to_text_conf(result)
        except Exception as e:
            traceback.print_exc()
            return f"[Transcription failed: {e!s}. You can type your question below.]", 0.0

    return (
        "[Only WAV is supported (no ffmpeg). Use 'Record from microphone' or upload a .wav file. "
        "Or type your question below.]",
        0.0,
    )


def _result_to_text_conf(result: dict) -> Tuple[str, float]:
    text = (result.get("text") or "").strip()
    segments = result.get("segments") or []
    if not text:
        return "", 0.0
    conf = 0.85 if len(segments) > 0 and len(text) > 3 else 0.7
    text = _normalize_math_phrases(text)
    return text, conf


def _normalize_math_phrases(s: str) -> str:
    s = s.replace(" square root of ", " sqrt ")
    s = s.replace(" squared ", " ^2 ")
    s = s.replace(" raised to ", " ^ ")
    s = s.replace(" divided by ", " / ")
    s = s.replace(" multiplied by ", " * ")
    s = s.replace(" plus ", " + ")
    s = s.replace(" minus ", " - ")
    s = s.replace(" integral ", " ∫ ")
    s = s.replace(" summation ", " Σ ")
    s = s.replace(" product ", " Π ")
    s = s.replace(" derivative ", " ′ ")
    s = s.replace(" quotient ", " / ")
    s = s.replace(" logarithm ", " log ")
    s = s.replace(" exponential ", " exp ")
    s = s.replace(" trigonometric ", " trig ")
    s= s.replace("determinant", "det")
    return s


def asr_confidence_low(confidence: float) -> bool:
    return confidence < ASR_CONFIDENCE_THRESHOLD
