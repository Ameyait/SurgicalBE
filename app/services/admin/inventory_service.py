from fastapi import (
    HTTPException,
    status
)

from app.repositories.inventory_repository import (
    InventoryRepository
)

from app.utils.exception_handler import (
    handle_service_exceptions
)


class InventoryService:

    @staticmethod
    @handle_service_exceptions(
        "fetching inventory dashboard"
    )
    async def get_inventory_dashboard(
        db
    ):

        result = await InventoryRepository.get_inventory_dashboard(
            db
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory data not found"
            )

        (
            total_stock,
            low_stock,
            out_of_stock,
            movements_today,
            products
        ) = result

        inventory_products = []

        for product in products:

            if product.stock_qty == 0:
                product_status = "out_of_stock"

            elif product.stock_qty <= 25:
                product_status = "low"

            else:
                product_status = "healthy"

            inventory_products.append(
                {
                    "product_id": str(product.id),
                    "product_name": product.name,
                    "sku": product.sku,
                    "stock_qty": product.stock_qty,
                    "status": product_status,
                    "stock_percentage": min(
                        max(product.stock_qty, 0),
                        100
                    )
                }
            )

        return {
            "summary": {
                "units_in_stock": total_stock,
                "low_stock": low_stock,
                "out_of_stock": out_of_stock,
                "stock_movements_today": movements_today
            },
            "products": inventory_products
        }