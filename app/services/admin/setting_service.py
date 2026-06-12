from fastapi import (
    HTTPException,
    status
)

from app.repositories.setting_repository import (
    SettingRepository
)

from app.utils.exception_handler import (
    handle_service_exceptions
)


class SettingService:

    @staticmethod
    @handle_service_exceptions(
        "fetching general settings"
    )
    async def get_general_settings(
        db
    ):

        settings = await SettingRepository.get_settings(
            db
        )

        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Settings not found"
            )

        return {
            "admin_display_name":
                settings.company_name,

            "support_email":
                settings.support_email,

            "timezone":
                settings.timezone
        }

    @staticmethod
    @handle_service_exceptions(
        "updating general settings"
    )
    async def update_general_settings(
        db,
        request
    ):

        settings = await SettingRepository.get_settings(
            db
        )

        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Settings not found"
            )

        settings.company_name = (
            request.admin_display_name
        )

        settings.support_email = (
            request.support_email
        )

        settings.timezone = (
            request.timezone
        )

        await SettingRepository.save(
            db,
            settings
        )

        return settings

    @staticmethod
    @handle_service_exceptions(
        "fetching store settings"
    )
    async def get_store_settings(
        db
    ):

        settings = await SettingRepository.get_settings(
            db
        )

        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Settings not found"
            )

        return {
            "business_name":
                settings.company_name,

            "phone":
                settings.support_phone,

            "gst_number":
                settings.gst_number,

            "address":
                settings.address
        }

    @staticmethod
    @handle_service_exceptions(
        "updating store settings"
    )
    async def update_store_settings(
        db,
        request
    ):

        settings = await SettingRepository.get_settings(
            db
        )

        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Settings not found"
            )

        settings.company_name = (
            request.business_name
        )

        settings.support_phone = (
            request.phone
        )

        settings.gst_number = (
            request.gst_number
        )

        settings.address = (
            request.address
        )

        await SettingRepository.save(
            db,
            settings
        )

        return settings

    @staticmethod
    @handle_service_exceptions(
        "fetching delivery settings"
    )
    async def get_delivery_settings(
        db
    ):

        settings = await SettingRepository.get_settings(
            db
        )

        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Settings not found"
            )

        return {
            "delivery_charge":
                settings.delivery_charge,

            "free_shipping_threshold":
                settings.free_shipping_threshold,

            "cod_charge":
                settings.cod_charge
        }

    @staticmethod
    @handle_service_exceptions(
        "updating delivery settings"
    )
    async def update_delivery_settings(
        db,
        request
    ):

        settings = await SettingRepository.get_settings(
            db
        )

        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Settings not found"
            )

        if request.delivery_charge < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery charge cannot be negative"
            )

        if request.free_shipping_threshold < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Free shipping threshold cannot be negative"
            )

        if request.cod_charge < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="COD charge cannot be negative"
            )

        settings.delivery_charge = (
            request.delivery_charge
        )

        settings.free_shipping_threshold = (
            request.free_shipping_threshold
        )

        settings.cod_charge = (
            request.cod_charge
        )

        await SettingRepository.save(
            db,
            settings
        )

        return settings