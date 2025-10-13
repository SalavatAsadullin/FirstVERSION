from datetime import datetime, timedelta, timezone
from typing import Any, Dict
import hmac
import hashlib
from urllib.parse import parse_qsl, unquote_plus

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.security import get_current_user

router = APIRouter()


class TelegramAuthPayload(BaseModel):
    init_data: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _validate_telegram_init_data(init_data: str, bot_token: str) -> Dict[str, Any]:
    # Spec: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    # 1) init_data is a query-string-like payload
    # 2) We must validate hash using secret key derived from bot token
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    if "hash" not in parsed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing hash")

    received_hash = parsed.pop("hash")

    # Build data_check_string sorted by key
    data_check_pairs = [f"{k}={unquote_plus(v)}" for k, v in parsed.items() if k != "hash"]
    data_check_pairs.sort()
    data_check_string = "\n".join(data_check_pairs)

    # Compute secret key = HMAC_SHA256("WebAppData", bot_token)
    secret_key = hmac.new(key=b"WebAppData", msg=bot_token.encode(), digestmod=hashlib.sha256).digest()
    computed_hash = hmac.new(key=secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()

    if computed_hash != received_hash:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid init data")

    # Check auth_date freshness (<= 1 day)
    try:
        auth_date = int(parsed.get("auth_date", "0"))
    except ValueError:
        auth_date = 0
    if auth_date:
        now_ts = int(datetime.now(tz=timezone.utc).timestamp())
        if now_ts - auth_date > 24 * 3600:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="init data expired")

    return parsed


@router.post("/telegram", response_model=TokenResponse)
async def exchange_telegram_auth(payload: TelegramAuthPayload, db: Session = Depends(get_db)) -> TokenResponse:
    settings = get_settings()

    parsed = _validate_telegram_init_data(payload.init_data, settings.bot_token)
    user_info = {}
    if "user" in parsed:
        import json
        user_info = json.loads(parsed["user"]) if isinstance(parsed["user"], str) else parsed["user"]
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No user in init data")

    # build JWT
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    # upsert user
    telegram_id = str(user_info.get("id"))
    first_name = user_info.get("first_name")
    last_name = user_info.get("last_name")

    user = db.query(User).filter(User.telegram_id == telegram_id).one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id, first_name=first_name, last_name=last_name)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        dirty = False
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            dirty = True
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            dirty = True
        if dirty:
            db.add(user)
            db.commit()

    to_encode = {"sub": str(user.id), "role": user.role, "exp": expire}
    encoded = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return TokenResponse(access_token=encoded)


class UpgradeRolePayload(BaseModel):
    secret: str
    role: UserRole


@router.post("/upgrade_role", response_model=TokenResponse)
async def upgrade_role(
    payload: UpgradeRolePayload,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TokenResponse:
    settings = get_settings()
    if payload.secret != settings.operator_bootstrap_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bad secret")

    if payload.role not in (UserRole.OPERATOR, UserRole.COURIER):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not allowed")

    user.role = payload.role.value
    db.add(user)
    db.commit()
    db.refresh(user)

    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": str(user.id), "role": user.role, "exp": expire}
    encoded = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return TokenResponse(access_token=encoded)
