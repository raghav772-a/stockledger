from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.database.session import get_db
from app.schemas.auth import (
    PasswordChange,
    RefreshRequest,
    TokenResponse,
    UserLogin,
    UserOut,
    UserRegister,
    UserUpdate,
)
from app.services.auth_service import AuthService
from app.utils.responses import APIResponse

router = APIRouter()


@router.post("/register", response_model=APIResponse[UserOut])
async def register(data: UserRegister, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await AuthService(db).register(data)
    return APIResponse(data=UserOut.model_validate(user), message="Registered successfully")


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(data: UserLogin, db: Annotated[AsyncSession, Depends(get_db)]):
    tokens = await AuthService(db).login(data)
    return APIResponse(data=tokens)


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh(data: RefreshRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    tokens = await AuthService(db).refresh(data.refresh_token)
    return APIResponse(data=tokens)


@router.get("/me", response_model=APIResponse[UserOut])
async def me(current_user: CurrentUser):
    return APIResponse(data=UserOut.model_validate(current_user))


@router.patch("/me", response_model=APIResponse[UserOut])
async def update_me(
    data: UserUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await AuthService(db).update_profile(current_user, data)
    return APIResponse(data=UserOut.model_validate(user))


@router.post("/change-password", response_model=APIResponse[None])
async def change_password(
    data: PasswordChange,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await AuthService(db).change_password(current_user, data)
    return APIResponse(message="Password updated")
