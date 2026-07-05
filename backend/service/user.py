from datetime import timedelta, datetime
import os
from jose import jwt
from model.user import User


if os.getenv("DAILYHUN_USER_UNIT_TEST"):
    from fake import user as user_data
else:
    from data import user as user_data

from passlib.context import CryptContext

SECRET_KEY = "keep-it-secret-keep-it-safe"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hash: str) -> bool:
    """Хэширование строки <plain> и сравнение с записью <hash>
    из базы данных"""
    return pwd_context.verify(plain, hash)

def get_hash(plain: str) -> str:
    """Возврат хеша строки <plain>"""
    return pwd_context.hash(plain)

def get_jwt_username(token: str) -> str | None:
    """Возврат имени пользователя из JWT-доступа <token>"""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        if not (username := payload.get("sub")):
            return None
    except jwt.JWTError:
        return None
    return username

def current_user(token: str):
    """Декодирование токена <token> доступа OAuth 
    и возврат объекта User"""
    if not (username := get_jwt_username(token)):
        return None
    if (user := lookup_user(username)):
        return user
    return None

def lookup_user(username: str) -> User | None:
    """Возврат совпадающего пользователя из базы данных
    для строки <name>"""
    if (user := user_data.get_one_by_username(username)):
        return user
    return None

def auth_user(username: str, plain: str) -> User | None:
    """Аутентификация пользователя <name> и <plain> пароль"""
    if not (user := lookup_user(username)):
        return None
    if not verify_password(plain, user.hash):
        return None
    return user

def create_access_token(data: dict, expires: timedelta | None = None):
    """Возвращение токена доступа JWT"""
    src = data.copy()
    now = datetime.now(datetime.timezone.utc)
    if not expires:
        expires = timedelta(minutes=15)
    src.update({"exp": now + expires})
    encoded_jwt = jwt.encode(src, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- CRUD

def get_all() -> list[User]:
    return user_data.get_all()

def get_one(username) -> User:
    return user_data.get_one_by_username(username)

def create(user: User) -> User:
    return user_data.create(user)

def modify(user: User) -> User:
    return user_data.modify(user)

def delete(id: int) -> None:
    return user_data.delete(id)
