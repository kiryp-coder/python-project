from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import LOGIN_RATE_LIMIT
from app.database import get_session
from app.dependencies import get_current_user
from app.limiter import limiter
from app.models import User, UserRole
from app.schemas import ErrorResponse, Token, UserRegister
from app.schemas import User as UserSchema
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post(
    "/register",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse, "description": "Email уже зарегистрирован"}},
    summary="Регистрация",
    description=(
        "Создаёт пользователя с ролью **user**. Пароль сохраняется только в виде хэша bcrypt. "
        "Email уникален без учёта регистра: повторная регистрация вернёт **409**."
    ),
)
def register(data: UserRegister, session: Session = Depends(get_session)):
    email = data.email.lower()
    if session.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email уже зарегистрирован")

    user = User(name=data.name, email=email, hashed_password=hash_password(data.password), role=UserRole.USER.value)
    session.add(user)
    session.commit()
    return user


@router.post(
    "/login",
    response_model=Token,
    responses={
        401: {"model": ErrorResponse, "description": "Неверный email или пароль"},
        429: {"description": "Больше 5 попыток входа в минуту с одного адреса"},
    },
    summary="Вход (получить JWT)",
    description=(
        "Стандартная форма OAuth2: поля `username` (сюда вводится **email**) и `password`, "
        "формат `application/x-www-form-urlencoded`. Возвращает access-токен. "
        "Не больше **5 попыток в минуту** с одного IP — шестая получит **429**."
    ),
)
@limiter.limit(LOGIN_RATE_LIMIT)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username.lower()))

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserSchema,
    responses={401: {"model": ErrorResponse, "description": "Нет токена или он недействителен"}},
    summary="Текущий пользователь",
)
def me(current_user: User = Depends(get_current_user)):
    return current_user
