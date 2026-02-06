from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.db import get_conn, init_db
from app.models import (
    ActionResponse,
    BuyRequest,
    ChatRequest,
    ChatResponse,
    EquipRequest,
    MiniGameResult,
    ProfileOut,
    ShopResponse,
)
from app.services import chat as chat_service
from app.services.chat import ChatServiceError
from app.services import game

logger = logging.getLogger(__name__)
app = FastAPI(title="Talking Tom Hackathon API")

_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env", override=False)
load_dotenv(_ROOT / "backend" / ".env", override=False)

_ANIMATIONS_DIR = _ROOT / "external_assets" / "animations_cat"
if _ANIMATIONS_DIR.exists():
    app.mount(
        "/assets/animations_cat",
        StaticFiles(directory=str(_ANIMATIONS_DIR)),
        name="animations-cat",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/profile", response_model=ProfileOut)
def get_profile() -> ProfileOut:
    with get_conn() as conn:
        profile = game.fetch_profile(conn)
    return ProfileOut(**profile)


@app.get("/api/shop", response_model=ShopResponse)
def get_shop() -> ShopResponse:
    return ShopResponse(items=game.get_shop_items())


@app.post("/api/actions/{action}", response_model=ActionResponse)
def take_action(action: str) -> ActionResponse:
    allowed = {"feed", "sleep", "clean", "play"}
    if action not in allowed:
        raise HTTPException(status_code=400, detail="Unknown action")
    with get_conn() as conn:
        profile = game.update_action(conn, action)
    return ActionResponse(profile=ProfileOut(**profile), message=f"Action {action} applied.")


@app.post("/api/shop/buy", response_model=ActionResponse)
def buy_item(payload: BuyRequest) -> ActionResponse:
    try:
        with get_conn() as conn:
            profile = game.update_buy(conn, payload.item_id)
        return ActionResponse(profile=ProfileOut(**profile), message="Item purchased.")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/shop/equip", response_model=ActionResponse)
def equip_item(payload: EquipRequest) -> ActionResponse:
    try:
        with get_conn() as conn:
            profile = game.update_equip(conn, payload.item_id)
        return ActionResponse(profile=ProfileOut(**profile), message="Item equipped.")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/minigame/result", response_model=ActionResponse)
def submit_minigame(payload: MiniGameResult) -> ActionResponse:
    with get_conn() as conn:
        profile = game.update_minigame(conn, payload.score, payload.duration_ms)
    return ActionResponse(profile=ProfileOut(**profile), message="Mini-game rewards applied.")


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    with get_conn() as conn:
        profile = game.fetch_profile(conn)
        shop_items = game.get_shop_items()
        hat_ids = [item["id"] for item in shop_items if item["type"] == "hat"]
        background_ids = [
            item["id"] for item in shop_items if item["type"] == "background"
        ]
        item_map = {item["id"]: item for item in shop_items}

        try:
            result = chat_service.chat_with_cat(
                messages=payload.messages[-12:],
                profile=profile,
                hat_ids=hat_ids,
                background_ids=background_ids,
            )
        except ChatServiceError as exc:
            logger.info("Chat service error: %s", exc)
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except Exception as exc:
            logger.exception("Chat request failed")
            raise HTTPException(
                status_code=500,
                detail=f"Chat failed: {str(exc)}",
            ) from exc

        if result.action != "none":
            profile = game.update_action(conn, result.action)

        equip = result.equip
        if equip:
            for item_id in [equip.hat_id, equip.background_id]:
                if not item_id or item_id not in item_map:
                    continue
                if item_id not in profile["owned_items"]:
                    try:
                        profile = game.update_buy(conn, item_id)
                    except ValueError:
                        continue
                if item_id in profile["owned_items"]:
                    profile = game.update_equip(conn, item_id)

    return ChatResponse(response=result, profile=ProfileOut(**profile))
