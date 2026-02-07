from __future__ import annotations

import io
import logging
import os
from typing import Any

from elevenlabs.client import ElevenLabs
from elevenlabs.core.api_error import ApiError

logger = logging.getLogger(__name__)


DEFAULT_VOICE_ID = "ucLUcBEXNVEmKfy5PhkX"
FALLBACK_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
DEFAULT_TTS_MODEL = "eleven_multilingual_v2"
DEFAULT_TTS_FORMAT = "mp3_44100_128"
DEFAULT_STT_MODEL = "scribe_v2"
DEFAULT_STT_LANGUAGE = "eng"


def _client() -> ElevenLabs:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is not set")
    return ElevenLabs(api_key=api_key)


def _coerce_audio_bytes(audio: Any) -> bytes:
    if isinstance(audio, (bytes, bytearray)):
        return bytes(audio)
    if hasattr(audio, "__iter__"):
        return b"".join(audio)
    if hasattr(audio, "read"):
        return audio.read()
    raise TypeError("Unsupported audio response type")


def text_to_speech(text: str) -> bytes:
    if not text or not text.strip():
        raise ValueError("Text is empty")
    client = _client()
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
    model_id = os.getenv("ELEVENLABS_TTS_MODEL", DEFAULT_TTS_MODEL)
    output_format = os.getenv("ELEVENLABS_TTS_FORMAT", DEFAULT_TTS_FORMAT)
    try:
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format,
        )
        logger.info("TTS: voice_id=%s", voice_id)
        return _coerce_audio_bytes(audio)
    except ApiError as exc:
        detail = exc.body.get("detail", {}) if isinstance(exc.body, dict) else {}
        status = detail.get("status")
        if status == "voice_not_found":
            fallback = os.getenv("ELEVENLABS_FALLBACK_VOICE_ID", FALLBACK_VOICE_ID)
            if voice_id != fallback:
                logger.info(
                    "TTS: voice_id=%s not found, using fallback voice_id=%s",
                    voice_id,
                    fallback,
                )
                audio = client.text_to_speech.convert(
                    text=text,
                    voice_id=fallback,
                    model_id=model_id,
                    output_format=output_format,
                )
                return _coerce_audio_bytes(audio)
        raise


def text_to_sound_effects(prompt: str) -> bytes:
    if not prompt or not prompt.strip():
        raise ValueError("Sound effect prompt is empty")
    client = _client()
    audio = client.text_to_sound_effects.convert(text=prompt.strip())
    logger.info("SFX: prompt=%s", prompt)
    return _coerce_audio_bytes(audio)


def speech_to_text(audio_bytes: bytes, filename: str | None = None) -> str:
    if not audio_bytes:
        raise ValueError("Audio is empty")
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename or "audio.webm"
    client = _client()
    transcription = client.speech_to_text.convert(
        file=audio_file,
        model_id=os.getenv("ELEVENLABS_STT_MODEL", DEFAULT_STT_MODEL),
        language_code=os.getenv("ELEVENLABS_STT_LANGUAGE", DEFAULT_STT_LANGUAGE),
        diarize=False,
        tag_audio_events=False,
    )
    if isinstance(transcription, str):
        return transcription
    if hasattr(transcription, "text"):
        return transcription.text
    if isinstance(transcription, dict):
        text = transcription.get("text") or transcription.get("transcript")
        if text:
            return text
    raise RuntimeError("Unable to parse speech-to-text response")
