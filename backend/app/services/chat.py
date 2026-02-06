from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Iterable, Literal

from google import genai
from google.genai import errors, types
from openai import OpenAI

from app.models import ChatMessage, ChatResult


DEFAULT_OPENAI_MODEL = "gpt-5"
DEFAULT_REASONING_EFFORT = "medium"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


class ChatServiceError(RuntimeError):
    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.status_code = status_code


logger = logging.getLogger(__name__)


def _animation_options() -> list[dict[str, str]]:
    root = Path(__file__).resolve().parents[3]
    path = root / "external_assets" / "animations_cat" / "cat_videos.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    cats = data.get("cats", [])
    return [
        {"video": item.get("video", ""), "description": item.get("description", "")}
        for item in cats
        if item.get("video")
    ]


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)


def _provider() -> Literal["openai", "gemini"]:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "gemini":
        if not os.getenv("GEMINI_API_KEY"):
            raise RuntimeError("GEMINI_API_KEY is not set")
        return "gemini"
    return "openai"


def _system_prompt(
    profile: dict,
    hat_ids: Iterable[str],
    background_ids: Iterable[str],
) -> str:
    hats = ", ".join(hat_ids) if hat_ids else "none"
    backgrounds = ", ".join(background_ids) if background_ids else "none"
    animations = _animation_options()
    if animations:
        animation_list = "; ".join(
            f"{item['video']} ({item['description']})" for item in animations
        )
    else:
        animation_list = "none"
    return (
        "You are Kit the cat in a virtual pet game. Keep replies short, playful, and kind. "
        "You MUST respond in JSON that matches the provided schema. "
        "Pick a mood, an action, and optional equip item based on the user's message. "
        "Choose an animation video that fits the mood/action; if unsure use chilling_cat.mp4. "
        "If the user asks to change a hat/background, select from the allowed ids. "
        "If unsure, use action 'none' and mood 'neutral'. "
        "All stats are on a 0-100 scale. Lower hunger means more full; higher hunger means more hungry. "
        "Higher energy, hygiene, and fun are better. Mood is 0-100 where higher is happier. "
        f"Current stats: hunger={profile['hunger']:.0f}, energy={profile['energy']:.0f}, "
        f"hygiene={profile['hygiene']:.0f}, fun={profile['fun']:.0f}, mood={profile['mood']:.0f}. "
        f"Allowed hat_ids: {hats}. Allowed background_ids: {backgrounds}. "
        f"Allowed animation videos: {animation_list}."
    )


def _chat_openai(
    messages: list[ChatMessage],
    profile: dict,
    hat_ids: Iterable[str],
    background_ids: Iterable[str],
) -> ChatResult:
    model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    reasoning_effort = os.getenv("OPENAI_REASONING_EFFORT", DEFAULT_REASONING_EFFORT)
    allowed_animations = [item["video"] for item in _animation_options()]
    animation_enum = allowed_animations + [None]
    system_message = {
        "role": "system",
        "content": _system_prompt(profile, hat_ids, background_ids),
    }
    input_messages = [system_message] + [
        {"role": msg.role, "content": msg.content} for msg in messages
    ]

    response = _client().responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "cat_response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "reply": {"type": "string"},
                        "mood": {
                            "type": "string",
                            "enum": ["happy", "neutral", "sad", "angry", "tired"],
                        },
                        "action": {
                            "type": "string",
                            "enum": ["feed", "sleep", "clean", "play", "none"],
                        },
                        "equip": {
                            "type": "object",
                            "properties": {
                                "hat_id": {"type": "string"},
                                "background_id": {"type": "string"},
                            },
                            "required": [],
                            "additionalProperties": False,
                        },
                        "animation": {
                            "type": ["string", "null"],
                            "enum": animation_enum,
                        },
                    },
                    "required": ["reply", "mood", "action"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        },
        input=input_messages,
    )

    data = json.loads(response.output_text)
    return ChatResult(**data)


def _extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output")
    return json.loads(text[start : end + 1])


def _chat_gemini(
    messages: list[ChatMessage],
    profile: dict,
    hat_ids: Iterable[str],
    background_ids: Iterable[str],
) -> ChatResult:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    contents: list[types.Content] = []
    for msg in messages:
        role = "user" if msg.role == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg.content)],
            )
        )

    system_prompt_text = _system_prompt(profile, hat_ids, background_ids)
    config = types.GenerateContentConfig(
        system_instruction=system_prompt_text,
        response_mime_type="application/json",
        response_schema=ChatResult,
    )

    response = None
    for attempt in range(3):
        try:
            with genai.Client(api_key=api_key) as client:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )
            break
        except errors.APIError as exc:
            code = exc.code
            if code in {429, 503} and attempt < 2:
                time.sleep(0.5 * (2**attempt))
                continue
            if code == 429:
                raise ChatServiceError(
                    "Gemini rate limit exceeded. Please try again shortly.",
                    status_code=429,
                ) from exc
            if code in {401, 403}:
                raise ChatServiceError(
                    "Gemini authentication failed. Check GEMINI_API_KEY.",
                    status_code=401,
                ) from exc
            raise ChatServiceError(
                f"Gemini API error (HTTP {code}).",
                status_code=502,
            ) from exc
        except Exception as exc:
            raise ChatServiceError(
                "Gemini API request failed.",
                status_code=502,
            ) from exc

    if response is None:
        raise ChatServiceError("Gemini API request failed.", status_code=502)
    parsed_obj = getattr(response, "parsed", None)
    if parsed_obj is not None:
        if isinstance(parsed_obj, ChatResult):
            return parsed_obj
        if isinstance(parsed_obj, dict):
            return ChatResult(**parsed_obj)
        model_dump = getattr(parsed_obj, "model_dump", None)
        if callable(model_dump):
            return ChatResult(**model_dump())

    text = getattr(response, "text", None)
    if isinstance(text, dict):
        return ChatResult(**text)
    if not text:
        candidates = getattr(response, "candidates", None)
        if candidates:
            parts: list[str] = []
            for candidate in candidates:
                content = getattr(candidate, "content", None)
                candidate_parts = getattr(content, "parts", None) if content else None
                if not candidate_parts:
                    continue
                for part in candidate_parts:
                    part_text = getattr(part, "text", None)
                    if part_text:
                        parts.append(part_text)
            text = "".join(parts) if parts else None

    if not text:
        raise ChatServiceError("Gemini returned empty content.", status_code=502)

    try:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = _extract_json(text)
        return ChatResult(**parsed)
    except Exception as exc:
        logger.exception("Gemini parse failure. Raw text: %s", text)
        raise ChatServiceError(
            "Gemini response parsing failed.",
            status_code=502,
        ) from exc


def _normalize_animation(selection: str | None) -> str | None:
    if not selection:
        return None
    allowed = {item["video"] for item in _animation_options()}
    if selection in allowed:
        return selection
    if selection.endswith(".mp4"):
        candidate = f"{selection[:-4]}.webm"
        if candidate in allowed:
            return candidate
    if "." not in selection:
        candidate = f"{selection}.webm"
        if candidate in allowed:
            return candidate
    return None


def chat_with_cat(
    messages: list[ChatMessage],
    profile: dict,
    hat_ids: Iterable[str],
    background_ids: Iterable[str],
) -> ChatResult:
    provider = _provider()
    if provider == "gemini":
        result = _chat_gemini(messages, profile, hat_ids, background_ids)
    else:
        result = _chat_openai(messages, profile, hat_ids, background_ids)

    result.animation = _normalize_animation(result.animation)
    return result
