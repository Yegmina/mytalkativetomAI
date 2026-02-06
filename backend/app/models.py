from __future__ import annotations

from typing import Any

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
