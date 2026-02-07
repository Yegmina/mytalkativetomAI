from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ProfileOut(BaseModel):
    id: int
    name: str
    coins: int
    level: int
    xp: int
    hunger: float
    energy: float
    hygiene: float
    fun: float
    mood: float
    last_updated: str
    owned_items: list[str]
    equipped_items: dict[str, str]


class ShopItem(BaseModel):
    id: str
    name: str
    type: str
    price: int
    asset_url: str
    icon_url: str
    description: str


class ShopResponse(BaseModel):
    items: list[ShopItem]


class BuyRequest(BaseModel):
    item_id: str = Field(..., min_length=1)


class EquipRequest(BaseModel):
    item_id: str = Field(..., min_length=1)


class MiniGameResult(BaseModel):
    score: int = Field(..., ge=0)
    duration_ms: int | None = Field(default=None, ge=0)


class ErrorResponse(BaseModel):
    detail: str


class ActionResponse(BaseModel):
    profile: ProfileOut
    message: str | None = None
    extra: dict[str, Any] | None = None


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatEquip(BaseModel):
    hat_id: str | None = None
    background_id: str | None = None


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatResult(BaseModel):
    reply: str
    mood: Literal["happy", "neutral", "sad", "angry", "tired"]
    action: Literal["feed", "sleep", "clean", "play", "none"]
    equip: ChatEquip | None = None
    animation: str | None = None
    sfx_prompt: str | None = None


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1)


class SFXRequest(BaseModel):
    prompt: str = Field(..., min_length=1)


class ActionFeedbackRequest(BaseModel):
    action: Literal["feed", "sleep", "clean", "play"]


class STTResponse(BaseModel):
    text: str


class ChatResponse(BaseModel):
    response: ChatResult
    profile: ProfileOut
