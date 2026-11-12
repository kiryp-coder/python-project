from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.config import ACCESS_TOKEN_MINUTES, ALGORITHM, SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id):
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def read_user_id(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return int(payload["sub"])
