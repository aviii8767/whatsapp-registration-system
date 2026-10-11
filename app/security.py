import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .config import settings

security = HTTPBasic()


def require_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if not settings.ADMIN_USER or not settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=500, detail="Admin login is not configured.")

    user_ok = secrets.compare_digest(
        credentials.username.encode(), settings.ADMIN_USER.encode()
    )
    pass_ok = secrets.compare_digest(
        credentials.password.encode(), settings.ADMIN_PASSWORD.encode()
    )
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )