from uuid import UUID

from fastapi import (
    HTTPException,
    UploadFile,
    status
)
from app.utils.exception_handler import handle_service_exceptions
from app.core.storage import local_storage
from sqlalchemy.ext.asyncio import AsyncSession

from slugify import slugify

from app.models.models import (
    Product,
    ProductImage,
    ReviewStatus
)

from app.repositories.product_repository import (
    ProductRepository
)

from app.repositories.category_repository import (
    CategoryRepository
)

from app.repositories.product_image_repository import (
    ProductImageRepository
)


class ProductService:

    @staticmethod
    def get_stock_status(stock_qty: int):
        if stock_qty <= 0:
            return "Out of Stock"
        if stock_qty <= 10:
            return "Limited Stock"
        return "In Stock"

    @staticmethod
    def calculate_discount(mrp, sale_price):
        if float(mrp) <= 0:
            return 0
        return round((float(mrp) - float(sale_price)) / float(mrp) * 100)

    @staticmethod
    @handle_service_exceptions("creating product")
    async def create_product(db: AsyncSession, payload, images: list[UploadFile]):
        category = await CategoryRepository.get_by_id(db, payload.category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        existing_sku = await ProductRepository.get_by_sku(db, payload.sku)

        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="SKU already exists"
            )

        if not payload.name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product name is required"
            )

        if payload.mrp <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MRP must be greater than 0"
            )

        if payload.sale_price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sale price must be greater than 0"
            )

        if payload.sale_price > payload.mrp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sale price cannot be greater than MRP"
            )

        if payload.stock_qty < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock quantity cannot be negative"
            )

        if len(images) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one image required"
            )

        if len(images) > 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 6 images allowed"
            )

        slug = slugify(payload.name)

        product = Product(
            category_id=payload.category_id,
            name=payload.name,
            slug=slug,
            sku=payload.sku,
            brand=payload.brand,
            description=payload.description,
            short_description=payload.short_description,
            mrp=payload.mrp,
            sale_price=payload.sale_price,
            stock_qty=payload.stock_qty,
            manufacturer=payload.manufacturer,
            hsn_code=payload.hsn_code,
            is_featured=payload.is_featured,
            is_bestseller=payload.is_bestseller,
            is_new_arrival=payload.is_new_arrival
        )

        product = await ProductRepository.create(db, product)

        image_records = []
        thumbnail_url = None

        for index, image in enumerate(images):
            image_url = await local_storage.upload_product_image(image)

            if index == 0:
                thumbnail_url = image_url

            image_records.append(
                ProductImage(
                    product_id=product.id,
                    image_url=image_url,
                    is_primary=(index == 0),
                    sort_order=index
                )
            )

        await ProductImageRepository.bulk_create(db, image_records)

        product.thumbnail_url = thumbnail_url

        await ProductRepository.update(db, product)

        return {
            "success": True,
            "status_code": 201,
            "message": "Product created successfully",
            "data": {
                "id": str(product.id),
                "name": product.name,
                "sku": product.sku
            }
        }

    @staticmethod
    @handle_service_exceptions("fetching products")
    async def get_products(
        db: AsyncSession,
        page: int,
        page_size: int,
        search: str | None = None,
        category_id: UUID | None = None
    ):
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page number must be greater than 0"
            )

        if page_size < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page size must be greater than 0"
            )

        if category_id:
            category = await CategoryRepository.get_by_id(db, category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )

        products, total_records = await ProductRepository.get_products(
            db=db,
            page=page,
            page_size=page_size,
            search=search,
            category_id=category_id
        )

        total_pages = ((total_records + page_size - 1) // page_size) if total_records else 0

        data = []
        for product in products:
            data.append(
                {
                    "id": str(product.id),
                    "category_id": (str(product.category_id) if product.category_id else None),
                    "category_name": (product.category.name if product.category else None),
                    "name": product.name,
                    "slug": product.slug,
                    "sku": product.sku,
                    "brand": product.brand,
                    "short_description": product.short_description,
                    "mrp": str(product.mrp),
                    "sale_price": str(product.sale_price),
                    "discount_percentage": ProductService.calculate_discount(product.mrp, product.sale_price),
                    "stock_qty": product.stock_qty,
                    "stock_status": ProductService.get_stock_status(product.stock_qty),
                    "thumbnail_url": product.thumbnail_url,
                    "rating": 0,
                    "review_count": 0,
                    "is_featured": product.is_featured,
                    "is_bestseller": product.is_bestseller,
                    "is_new_arrival": product.is_new_arrival,
                    "created_at": product.created_at,
                    "images": [
                        {
                            "id": str(img.id),
                            "image_url": img.image_url,
                            "is_primary": img.is_primary,
                            "sort_order": img.sort_order
                        }
                        for img in product.images
                    ]
                }
            )

        return {
            "success": True,
            "status_code": 200,
            "message": "Products fetched successfully",
            "filters": {
                "search": search,
                "category_id": (str(category_id) if category_id else None)
            },
            "data": data,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }

    @staticmethod
    @handle_service_exceptions("fetching product")
    async def get_product(db: AsyncSession, product_id: UUID):
        product = await ProductRepository.get_product_by_id(db=db, product_id=product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        approved_reviews = [review for review in product.reviews if review.status == ReviewStatus.APPROVED]
        review_count = len(approved_reviews)

        rating = (
            round(sum(review.rating for review in approved_reviews) / review_count, 2)
            if review_count > 0
            else 0
        )

        discount_percentage = ProductService.calculate_discount(product.mrp, product.sale_price)

        return {
            "success": True,
            "status_code": 200,
            "message": "Product fetched successfully",
            "data": {
                "id": str(product.id),
                "category": {
                    "id": (str(product.category.id) if product.category else None),
                    "name": (product.category.name if product.category else None)
                },
                "name": product.name,
                "slug": product.slug,
                "sku": product.sku,
                "brand": product.brand,
                "description": product.description,
                "short_description": product.short_description,
                "mrp": float(product.mrp),
                "sale_price": float(product.sale_price),
                "discount_percentage": discount_percentage,
                "stock_qty": product.stock_qty,
                "stock_status": ProductService.get_stock_status(product.stock_qty),
                "thumbnail_url": product.thumbnail_url,
                "manufacturer": product.manufacturer,
                "hsn_code": product.hsn_code,
                "rating": rating,
                "review_count": review_count,
                "is_featured": product.is_featured,
                "is_bestseller": product.is_bestseller,
                "is_new_arrival": product.is_new_arrival,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                "images": [
                    {
                        "id": str(image.id),
                        "image_url": image.image_url,
                        "is_primary": image.is_primary,
                        "sort_order": image.sort_order
                    }
                    for image in product.images
                ],
                "reviews": [
                    {
                        "id": str(review.id),
                        "rating": review.rating,
                        "review_text": review.review_text,
                        "user_name": (review.user.full_name if review.user else None),
                        "created_at": review.created_at
                    }
                    for review in approved_reviews
                ]
            }
        }

    @staticmethod
    @handle_service_exceptions("updating product")
    async def update_product(
        db: AsyncSession,
        product_id: UUID,
        payload,
        images: list[UploadFile] | None = None
        ):
            product = await ProductRepository.get_by_id(
            db,
            product_id
        )

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )

            update_data = payload.model_dump(
                exclude_unset=True
            )

            if (
                "name" in update_data
                and not update_data["name"].strip()
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product name cannot be empty"
                )

            if (
                "mrp" in update_data
                and update_data["mrp"] <= 0
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="MRP must be greater than 0"
                )

            if (
                "sale_price" in update_data
                and update_data["sale_price"] <= 0
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sale price must be greater than 0"
                )

            if (
                "stock_qty" in update_data
                and update_data["stock_qty"] < 0
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Stock quantity cannot be negative"
                )

            if (
                "category_id" in update_data
            ):

                category = await CategoryRepository.get_by_id(
                    db,
                    update_data["category_id"]
                )

                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Category not found"
                    )

            new_mrp = update_data.get(
                "mrp",
                product.mrp
            )

            new_sale_price = update_data.get(
                "sale_price",
                product.sale_price
            )

            if new_sale_price > new_mrp:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sale price cannot be greater than MRP"
                )

            if "name" in update_data:

                product.name = update_data["name"]

                product.slug = slugify(
                    update_data["name"]
                )

            for key, value in update_data.items():

                setattr(
                    product,
                    key,
                    value
                )

            
            if images:

                if len(images) > 6:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Maximum 6 images allowed"
                    )

                await ProductImageRepository.delete_product_images(
                    db,
                    product.id
                )

                image_records = []

                thumbnail_url = None

                for index, image in enumerate(
                    images
                ):

                    image_url = await local_storage.upload_product_image(
                        image
                    )

                    if index == 0:
                        thumbnail_url = image_url

                    image_records.append(
                        ProductImage(
                            product_id=product.id,
                            image_url=image_url,
                            is_primary=(index == 0),
                            sort_order=index
                        )
                    )

                await ProductImageRepository.bulk_create(
                    db,
                    image_records
                )

                product.thumbnail_url = thumbnail_url

            await ProductRepository.update(
                db,
                product
            )

            return {
                "success": True,
                "status_code": 200,
                "message": "Product updated successfully"
        }

    @staticmethod
    @handle_service_exceptions("deleting product")
    async def delete_product(
        db: AsyncSession,
        product_id: UUID
    ):
        product = await ProductRepository.get_by_id(
            db,
            product_id
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        await ProductRepository.delete(
            db,
            product
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Product deleted successfully"
        }
