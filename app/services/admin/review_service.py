from fastapi import (
    HTTPException,
    status
)

from app.models.models import (
    ReviewStatus
)

from app.repositories.review_repository import (
    ReviewRepository
)

from app.utils.exception_handler import (
    handle_service_exceptions
)


class AdminReviewService:

    @staticmethod
    @handle_service_exceptions(
        "fetching reviews"
    )
    async def get_reviews(
        db,
        status_filter=None,
        page: int = 1,
        page_size: int = 20
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

        reviews = await ReviewRepository.get_all_reviews(
            db=db,
            status=status_filter
        )

        start = (page - 1) * page_size
        end = start + page_size

        paginated_reviews = reviews[start:end]

        return {
            "success": True,
            "status_code": 200,
            "data": [
                {
                    "id": str(review.id),

                    "product_id": str(review.product.id),
                    "product_name": review.product.name,

                    "user_id": str(review.user.id),
                    "user_name": review.user.full_name,

                    "rating": review.rating,
                    "review_text": review.review_text,

                    "image_url": review.image_url,

                    "verified_purchase":
                        review.is_verified_purchase,

                    "status":
                        review.status.value,

                    "admin_note":
                        review.admin_note,

                    "created_at":
                        review.created_at
                }
                for review in paginated_reviews
            ],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": len(reviews),
                "total_pages": (
                    len(reviews) + page_size - 1
                ) // page_size
            }
        }

    @staticmethod
    @handle_service_exceptions(
        "fetching review"
    )
    async def get_review(
        db,
        review_id
    ):

        review = await ReviewRepository.get_by_id(
            db,
            review_id
        )

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "id": str(review.id),

                "product_id": str(review.product.id),
                "product_name": review.product.name,

                "user_id": str(review.user.id),
                "user_name": review.user.full_name,

                "rating": review.rating,
                "review_text": review.review_text,

                "image_url": review.image_url,

                "verified_purchase":
                    review.is_verified_purchase,

                "status":
                    review.status.value,

                "admin_note":
                    review.admin_note,

                "created_at":
                    review.created_at
            }
        }

    @staticmethod
    @handle_service_exceptions(
        "approving review"
    )
    async def approve_review(
        db,
        review_id,
        admin_note
    ):

        review = await ReviewRepository.get_by_id(
            db,
            review_id
        )

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        review.status = ReviewStatus.APPROVED
        review.admin_note = admin_note

        await ReviewRepository.save(
            db,
            review
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Review approved successfully"
        }

    @staticmethod
    @handle_service_exceptions(
        "rejecting review"
    )
    async def reject_review(
        db,
        review_id,
        admin_note
    ):

        review = await ReviewRepository.get_by_id(
            db,
            review_id
        )

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        review.status = ReviewStatus.REJECTED
        review.admin_note = admin_note

        await ReviewRepository.save(
            db,
            review
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Review rejected successfully"
        }

    @staticmethod
    @handle_service_exceptions(
        "flagging review"
    )
    async def flag_review(
        db,
        review_id,
        admin_note
    ):

        review = await ReviewRepository.get_by_id(
            db,
            review_id
        )

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        review.status = ReviewStatus.FLAGGED
        review.admin_note = admin_note

        await ReviewRepository.save(
            db,
            review
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Review flagged successfully"
        }

    @staticmethod
    @handle_service_exceptions(
        "fetching review dashboard"
    )
    async def dashboard(
        db
    ):

        stats = await ReviewRepository.get_dashboard_stats(
            db
        )

        return {
            "success": True,
            "status_code": 200,
            "data": stats
        }