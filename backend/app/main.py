from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.db import get_conn, init_db
from app.models import (
    ActionResponse,
    BuyRequest,
    EquipRequest,
    MiniGameResult,
    ProfileOut,
    ShopResponse,
)
from app.services import game

app = FastAPI(title="Talking Tom Hackathon API")

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
