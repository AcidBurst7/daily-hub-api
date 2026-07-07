import os
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)
from errors import Missing
from model.user import User


if os.getenv("DAILYHUB_USER_UNIT_TEST"):
    from fake import user as service
else:
    from service import user as service

ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter(prefix="/users")

# Эта зависимость создает сообщение в каталоге 
# "/users/token" (из формы с именем пользователя и паролем)
# и возвращает токен доступа
oauth2_dep = OAuth2PasswordBearer(tokenUrl="token")

def unauthed():
    raise HTTPException(
        status_code=401,
        detail="Некорректный логин или пароль",
        headers={"WWW-Authenticate": "Bearer"},
    )

# К этой конечной точке направляется любой вызов,
# содаержащий зависимость oauth2_dep()
@router.post("/token")
async def create_access_token(
    form_data: OAuth2PasswordRequestForm
):
    """Получение имени пользователя и пароля
        из формы OAuth, возврат токена доступа"""
    user = service.auth_user(
        form_data.username,
        form_data.password
    )
    if not user:
        unauthed()
    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = service.create_access_token(
        data={"sub": user.username},
        expires=expires
    )
    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }

@router.get("/token")
def get_access_token(token: str = Depends(oauth2_dep)) -> dict:
    """Возврат текущего токена доступа"""
    return {"token": token}

@router.get("/")
def get_all() -> list[User]:
    return service.get_all()

@router.get("/{name}")
def get_one(username: str) -> User | None:
    try:
        return service.get_one(username)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.post("/", status_code=201)
def create(user: User) -> User | None:
    try:
        return service.create(user)
    except Missing as exc:
        raise HTTPException(status_code=409, detail=exc.msg)
    
@router.patch("/")
def modify(user: User) -> User | None:
    try:
        return service.modify(user)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
    
    
@router.delete("/")
def delete(id: int) -> User | None:
    try:
        return service.delete(id)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)