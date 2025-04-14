from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.utils.auth import decode_jwt_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_jwt_token(token)
    return {"user_id": payload.get("sub"), "role": payload.get("role")}


async def get_current_employee_or_moderator(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["employee", "moderator"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return current_user


async def check_if_moderator(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "moderator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only moderators can perform this action"
        )
    return current_user


async def check_if_employee(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only employees can perform this action"
        )
    return current_user
