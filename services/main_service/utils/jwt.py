import os
from datetime import UTC, datetime, timedelta

import jwt


def issue_member_token(member_id: int, account: str) -> str:
    secret_key = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))

    payload = {
        "sub": str(member_id),
        "account": account,
        "exp": datetime.now(UTC) + timedelta(minutes=expire_minutes),
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)
