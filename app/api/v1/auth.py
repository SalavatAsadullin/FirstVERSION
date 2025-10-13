from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter()


class TelegramAuthPayload(BaseModel):
    init_data: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _validate_telegram_init_data(init_data: str, bot_token: str) -> dict[str, Any]:
    # TODO: implement Telegram Mini App initData validation using HMAC-SHA256
    # For now it is a stub that trusts payload
    return {"user": {"id": 0, "first_name": "stub"}}


@router.post("/telegram", response_model=TokenResponse)
async def exchange_telegram_auth(payload: TelegramAuthPayload) -> TokenResponse:
    settings = get_settings()

    user_info = _validate_telegram_init_data(payload.init_data, settings.bot_token)

    # build JWT
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": str(user_info["user"]["id"]), "exp": expire}
    encoded = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return TokenResponse(access_token=encoded)
