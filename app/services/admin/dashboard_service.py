from fastapi import (
    HTTPException,
    status
)

from app.repositories.dashboard_repository import (
    DashboardRepository
)

from app.utils.exception_handler import (
    handle_service_exceptions
)


class DashboardService:

    @staticmethod
    @handle_service_exceptions(
        "fetching dashboard data"
    )
    async def get_dashboard(
        db
    ):

        summary = await DashboardRepository.get_summary(
            db
        )

        revenue_trend = (
            await DashboardRepository.get_revenue_trend(
                db
            )
        )

        orders_by_category = (
            await DashboardRepository.get_orders_by_category(
                db
            )
        )

        peak_shopping_hours = (
            await DashboardRepository.get_peak_shopping_hours(
                db
            )
        )

        top_selling_products = (
            await DashboardRepository.get_top_selling_products(
                db
            )
        )

        recent_orders = (
            await DashboardRepository.get_recent_orders(
                db
            )
        )

        abandoned_carts = (
            await DashboardRepository.get_abandoned_carts(
                db
            )
        )

        if summary is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard summary not found"
            )

        return {
            "summary": summary,

            "revenue_trend":
                revenue_trend or [],

            "orders_by_category":
                orders_by_category or [],

            "peak_shopping_hours":
                peak_shopping_hours or [],

            "top_selling_products":
                top_selling_products or [],

            "recent_orders":
                recent_orders or [],

            "abandoned_carts":
                abandoned_carts or []
        }