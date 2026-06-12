import logging
from functools import wraps

from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def handle_service_exceptions(
    operation_name: str
):
    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            try:
                return await func(
                    *args,
                    **kwargs
                )

            except HTTPException:
                raise

            except SQLAlchemyError:

                logger.exception(
                    f"Database error while {operation_name}"
                )

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database operation failed"
                )

            except Exception:

                logger.exception(
                    f"Unexpected error while {operation_name}"
                )

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )

        return wrapper

    return decorator