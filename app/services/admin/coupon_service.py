from fastapi import (
    HTTPException,
    status
)

from app.models.models import Coupon

from app.repositories.coupon_repository import (
    CouponRepository
)

from app.utils.exception_handler import (
    handle_service_exceptions
)


class CouponService:

    @staticmethod
    @handle_service_exceptions(
        "creating coupon"
    )
    async def create_coupon(
        db,
        payload
    ):

        existing = await CouponRepository.get_by_code(
            db,
            payload.code.upper()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Coupon code already exists"
            )

        if payload.discount_value <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount value must be greater than 0"
            )

        if payload.minimum_order_amount < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum order amount cannot be negative"
            )

        if (
            payload.max_discount_amount is not None
            and payload.max_discount_amount < 0
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum discount amount cannot be negative"
            )

        if payload.usage_limit <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usage limit must be greater than 0"
            )

        if payload.valid_from >= payload.valid_until:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid from date must be before valid until date"
            )

        coupon = Coupon(
            code=payload.code.upper(),
            title=payload.title,
            description=payload.description,
            coupon_type=(
                payload.coupon_type.value
                if hasattr(payload.coupon_type, "value")
                else payload.coupon_type
            ),
            discount_value=payload.discount_value,
            max_discount_amount=payload.max_discount_amount,
            minimum_order_amount=payload.minimum_order_amount,
            usage_limit=payload.usage_limit,
            is_first_order_only=payload.is_first_order_only,
            valid_from=payload.valid_from,
            valid_until=payload.valid_until
        )

        coupon = await CouponRepository.create(
            db,
            coupon
        )

        return {
            "success": True,
            "status_code": 201,
            "message": "Coupon created successfully",
            "data": {
                "id": str(coupon.id),
                "code": coupon.code,
                "coupon_type": coupon.coupon_type
            }
        }

    @staticmethod
    @handle_service_exceptions(
        "fetching coupons"
    )
    async def get_coupons(
        db
    ):

        coupons = await CouponRepository.get_all(
            db
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Coupons fetched successfully",
            "data": coupons
        }

    @staticmethod
    @handle_service_exceptions(
        "fetching coupon"
    )
    async def get_coupon(
        db,
        coupon_id
    ):

        coupon = await CouponRepository.get_by_id(
            db,
            coupon_id
        )

        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found"
            )

        return {
            "success": True,
            "status_code": 200,
            "message": "Coupon fetched successfully",
            "data": coupon
        }

    @staticmethod
    @handle_service_exceptions(
        "updating coupon"
    )
    async def update_coupon(
        db,
        coupon_id,
        payload
    ):

        coupon = await CouponRepository.get_by_id(
            db,
            coupon_id
        )

        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found"
            )

        update_data = payload.model_dump(
            exclude_unset=True
        )

        if (
            "discount_value" in update_data
            and update_data["discount_value"] <= 0
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount value must be greater than 0"
            )

        if (
            "minimum_order_amount" in update_data
            and update_data["minimum_order_amount"] < 0
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum order amount cannot be negative"
            )

        if (
            "max_discount_amount" in update_data
            and update_data["max_discount_amount"] is not None
            and update_data["max_discount_amount"] < 0
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum discount amount cannot be negative"
            )

        if (
            "usage_limit" in update_data
            and update_data["usage_limit"] <= 0
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usage limit must be greater than 0"
            )

        if (
            "valid_from" in update_data
            and "valid_until" in update_data
            and update_data["valid_from"]
            >= update_data["valid_until"]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid from date must be before valid until date"
            )

        if "coupon_type" in update_data:

            coupon_type = update_data["coupon_type"]

            update_data["coupon_type"] = (
                coupon_type.value
                if hasattr(coupon_type, "value")
                else coupon_type
            )

        for key, value in update_data.items():

            setattr(
                coupon,
                key,
                value
            )

        await CouponRepository.update(
            db,
            coupon
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Coupon updated successfully"
        }

    @staticmethod
    @handle_service_exceptions(
        "deleting coupon"
    )
    async def delete_coupon(
        db,
        coupon_id
    ):

        coupon = await CouponRepository.get_by_id(
            db,
            coupon_id
        )

        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found"
            )

        await CouponRepository.delete(
            db,
            coupon
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Coupon deleted successfully"
        }

    @staticmethod
    @handle_service_exceptions(
        "updating coupon status"
    )
    async def update_coupon_status(
        db,
        coupon_id,
        is_active
    ):

        coupon = await CouponRepository.get_by_id(
            db,
            coupon_id
        )

        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found"
            )

        if not isinstance(
            is_active,
            bool
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status value"
            )

        coupon.is_active = is_active

        await CouponRepository.update(
            db,
            coupon
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Coupon status updated successfully"
        }