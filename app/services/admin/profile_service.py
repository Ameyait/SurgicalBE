from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User
from app.core.security import (
    verify_password,
    hash_password
)


class ProfileService:

    @staticmethod
    async def get_profile(
        db: AsyncSession,
        user_id: str
    ):
        result = await db.execute(
            select(User).where(
                User.id == UUID(user_id)
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user_id: str,
        payload
    ):

        result = await db.execute(
            select(User).where(
                User.id == UUID(user_id)
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return None

        # Update Profile Details

        if payload.full_name is not None:
            user.full_name = payload.full_name

        if payload.email is not None:
            user.email = payload.email

        if payload.phone is not None:
            user.phone = payload.phone

        # Password Change Validation

        if payload.current_password and not payload.new_password:
            raise HTTPException(
                status_code=400,
                detail="New password is required"
            )

        if payload.new_password:

            if not payload.current_password:
                raise HTTPException(
                    status_code=400,
                    detail="Current password is required"
                )

            if not verify_password(
                payload.current_password,
                user.password_hash
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Current password is incorrect"
                )

            user.password_hash = hash_password(
                payload.new_password
            )

        await db.commit()
        await db.refresh(user)

        return user