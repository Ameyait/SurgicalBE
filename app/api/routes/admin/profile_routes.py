from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.schemas.admin.profile_schema import (
    ProfileResponse,
    UpdateProfileRequest
)

from app.services.admin.profile_service import (
    ProfileService
)

router = APIRouter(
    prefix="/admin/profile",
    tags=["Profile"]
)


@router.get(
    "",
    response_model=ProfileResponse
)
async def get_profile(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    user_id = current_user["sub"]

    user = await ProfileService.get_profile(
        db=db,
        user_id=user_id
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.put(
    "",
    response_model=ProfileResponse
)
async def update_profile(
    payload: UpdateProfileRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    user_id = current_user["sub"]

    user = await ProfileService.update_profile(
        db=db,
        user_id=user_id,
        payload=payload
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user