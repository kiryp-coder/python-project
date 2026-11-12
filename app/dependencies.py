from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import User, UserRole
from app.security import read_user_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        user_id = read_user_id(token)
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(*allowed_roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in [role.value for role in allowed_roles]:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")
        return current_user

    return role_checker


def ensure_owner_or_admin(current_user, owner_id):
    if current_user.role != UserRole.ADMIN.value and current_user.id != owner_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Можно смотреть только свои данные")
