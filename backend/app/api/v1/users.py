from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AdminUser
from app.core.security import get_password_hash
from app.database.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import UserOut
from app.utils.responses import APIResponse

router = APIRouter()


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    role: UserRole = UserRole.STAFF


@router.get("", response_model=APIResponse[list[UserOut]])
async def list_users(_: AdminUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.deleted_at.is_(None)).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return APIResponse(data=[UserOut.model_validate(u) for u in users])


@router.post("", response_model=APIResponse[UserOut])
async def create_user(data: AdminUserCreate, _: AdminUser, db: Annotated[AsyncSession, Depends(get_db)]):
    repo = UserRepository(db)
    if await repo.get_by_email(data.email.lower()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email exists")
    user = User(
        email=data.email.lower(),
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return APIResponse(data=UserOut.model_validate(user))
