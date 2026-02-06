from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db import get_or_create_profile, upsert_profile

DECAY_RATES = {
    "hunger": 0.012,
    "energy": 0.009,
    "hygiene": 0.01,
    "fun": 0.011,
}

SHOP_ITEMS = [
    {
        "id": "hat_cap",
        "name": "Sky Cap",
        "type": "hat",
        "price": 50,
        "asset_url": "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f9e2.png",
        "icon_url": "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f9e2.png",
        "description": "A cool cap for your pet.",
    },
    {
        "id": "hat_top",
        "name": "Top Hat",
        "type": "hat",
        "price": 80,
        "asset_url": "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f3a9.png",
        "icon_url": "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f3a9.png",
        "description": "Fancy vibes for hackathon demo.",
    },
    {
        "id": "bg_sunset",
        "name": "Sunset Yard",
        "type": "background",
        "price": 120,
        "asset_url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
        "icon_url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=600&q=60",
        "description": "Warm sunset background.",
    },
]

SHOP_MAP = {item["id"]: item for item in SHOP_ITEMS}


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def compute_mood(profile: dict[str, Any]) -> float:
    stats = [
        profile["hunger"],
        profile["energy"],
        profile["hygiene"],
        profile["fun"],
    ]
    return round(sum(stats) / len(stats), 1)


def apply_decay(profile: dict[str, Any]) -> None:
    now = datetime.now(timezone.utc)
    last = datetime.fromisoformat(profile["last_updated"])
    delta = max(0.0, (now - last).total_seconds())
    if delta <= 0:
        return
    for key, rate in DECAY_RATES.items():
        profile[key] = clamp(profile[key] - delta * rate)
    profile["mood"] = compute_mood(profile)
    profile["last_updated"] = now.isoformat()


def apply_action(profile: dict[str, Any], action: str) -> None:
    if action == "feed":
        profile["hunger"] = clamp(profile["hunger"] + 30)
        profile["hygiene"] = clamp(profile["hygiene"] - 2)
    elif action == "sleep":
        profile["energy"] = clamp(profile["energy"] + 40)
        profile["hunger"] = clamp(profile["hunger"] - 8)
    elif action == "clean":
        profile["hygiene"] = clamp(profile["hygiene"] + 35)
        profile["fun"] = clamp(profile["fun"] - 5)
    elif action == "play":
        profile["fun"] = clamp(profile["fun"] + 35)
        profile["energy"] = clamp(profile["energy"] - 10)
        profile["hunger"] = clamp(profile["hunger"] - 5)
    else:
        raise ValueError("Unknown action")

    profile["xp"] += 12
    profile["coins"] += 6
    profile["level"] = 1 + profile["xp"] // 100
    profile["mood"] = compute_mood(profile)


def apply_minigame(profile: dict[str, Any], score: int, duration_ms: int | None) -> None:
    score = max(0, score)
    base = max(5, score // 3)
    bonus = 5 if duration_ms and duration_ms < 25000 else 0
    reward = min(120, base + bonus)
    profile["coins"] += reward
    profile["xp"] += max(8, score // 5)
    profile["level"] = 1 + profile["xp"] // 100
    profile["mood"] = compute_mood(profile)


def buy_item(profile: dict[str, Any], item_id: str) -> None:
    item = SHOP_MAP.get(item_id)
    if not item:
        raise ValueError("Item not found")
    if item_id in profile["owned_items"]:
        return
    if profile["coins"] < item["price"]:
        raise ValueError("Not enough coins")
    profile["coins"] -= item["price"]
    profile["owned_items"].append(item_id)
    profile["equipped_items"][item["type"]] = item_id
    profile["mood"] = compute_mood(profile)


def equip_item(profile: dict[str, Any], item_id: str) -> None:
    item = SHOP_MAP.get(item_id)
    if not item:
        raise ValueError("Item not found")
    if item_id not in profile["owned_items"]:
        raise ValueError("Item not owned")
    profile["equipped_items"][item["type"]] = item_id


def fetch_profile(conn) -> dict[str, Any]:
    profile = get_or_create_profile(conn)
    apply_decay(profile)
    upsert_profile(conn, profile)
    return profile


def update_action(conn, action: str) -> dict[str, Any]:
    profile = get_or_create_profile(conn)
    apply_decay(profile)
    apply_action(profile, action)
    upsert_profile(conn, profile)
    return profile


def update_minigame(conn, score: int, duration_ms: int | None) -> dict[str, Any]:
    profile = get_or_create_profile(conn)
    apply_decay(profile)
    apply_minigame(profile, score, duration_ms)
    upsert_profile(conn, profile)
    return profile


def update_buy(conn, item_id: str) -> dict[str, Any]:
    profile = get_or_create_profile(conn)
    apply_decay(profile)
    buy_item(profile, item_id)
    upsert_profile(conn, profile)
    return profile


def update_equip(conn, item_id: str) -> dict[str, Any]:
    profile = get_or_create_profile(conn)
    apply_decay(profile)
    equip_item(profile, item_id)
    upsert_profile(conn, profile)
    return profile


def get_shop_items() -> list[dict[str, Any]]:
    return SHOP_ITEMS
