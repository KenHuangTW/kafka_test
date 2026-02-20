import os

import jwt
from fastapi import HTTPException, status


def decode_member_token(token: str) -> int:
    secret_key = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token") from exc

    subject = payload.get("sub")
    try:
        member_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token") from exc

    return member_id
