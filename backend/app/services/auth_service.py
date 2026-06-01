from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
    verify_token_type,
)
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import PasswordChange, TokenResponse, UserLogin, UserRegister, UserUpdate


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)

    async def register(self, data: UserRegister) -> User:
        if await self.users.get_by_email(data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user = User(
            email=data.email.lower(),
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            role=UserRole.STAFF,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def login(self, data: UserLogin) -> TokenResponse:
        user = await self.users.get_by_email(data.email.lower())
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account inactive")
        return TokenResponse(
            access_token=create_access_token(user.id, extra={"role": user.role.value}),
            refresh_token=create_refresh_token(user.id),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if not verify_token_type(payload, "refresh"):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
            from uuid import UUID

            user = await self.users.get_by_id(UUID(payload["sub"]))
            if not user or not user.is_active:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc
        return TokenResponse(
            access_token=create_access_token(user.id, extra={"role": user.role.value}),
            refresh_token=create_refresh_token(user.id),
        )

    async def update_profile(self, user: User, data: UserUpdate) -> User:
        if data.email and data.email.lower() != user.email:
            existing = await self.users.get_by_email(data.email.lower())
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
            user.email = data.email.lower()
        if data.full_name:
            user.full_name = data.full_name
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def change_password(self, user: User, data: PasswordChange) -> None:
        if not verify_password(data.current_password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password incorrect")
        user.hashed_password = get_password_hash(data.new_password)
        await self.session.flush()
