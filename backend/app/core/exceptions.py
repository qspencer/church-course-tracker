"""
Custom exception classes for better error handling

This module defines application-specific exceptions that provide
better context and handling than generic Python exceptions.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class PlanningCenterAPIError(Exception):
    """
    Base exception for Planning Center API errors

    Attributes:
        message: Error message describing what went wrong
        status_code: HTTP status code from Planning Center (if applicable)
        response: Raw response data from Planning Center (if available)
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class PlanningCenterAuthenticationError(PlanningCenterAPIError):
    """
    Planning Center authentication failed

    Raised when API credentials are invalid or expired.
    """
    pass


class PlanningCenterRateLimitError(PlanningCenterAPIError):
    """
    Planning Center rate limit exceeded

    Raised when too many requests have been made to Planning Center API.
    Clients should retry after a delay.
    """
    pass


class PlanningCenterNotFoundError(PlanningCenterAPIError):
    """
    Planning Center resource not found

    Raised when a requested resource (person, event, etc.) doesn't exist.
    """
    pass


class DatabaseTransactionError(Exception):
    """
    Database transaction failed

    Raised when a database transaction cannot be completed successfully.
    The transaction should be rolled back when this is raised.
    """
    pass


class AuditLogError(Exception):
    """
    Audit logging failed

    Raised when audit log creation fails. Depending on context,
    this may or may not fail the main operation.
    """
    pass


class ValidationError(Exception):
    """
    Data validation failed

    Raised when input data doesn't meet validation requirements.
    Should result in a 400 Bad Request response to the client.
    """
    pass


def planning_center_exception_handler(func):
    """
    Decorator to handle Planning Center API errors consistently

    This decorator wraps endpoint functions and converts Planning Center
    exceptions into appropriate HTTP responses.

    Example:
        @router.get("/sync")
        @planning_center_exception_handler
        async def sync_people():
            # Planning Center API calls
            pass
    """
    from functools import wraps
    import logging

    logger = logging.getLogger(__name__)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except PlanningCenterAuthenticationError as e:
            logger.error(f"PC Authentication failed: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Planning Center authentication failed. Please check credentials."
            )
        except PlanningCenterRateLimitError as e:
            logger.warning(f"PC Rate limit exceeded: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Planning Center rate limit exceeded. Please try again later."
            )
        except PlanningCenterNotFoundError as e:
            logger.warning(f"PC Resource not found: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planning Center resource not found."
            )
        except PlanningCenterAPIError as e:
            logger.error(f"PC API error: {e.message}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Planning Center service error. Please try again."
            )
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except DatabaseTransactionError as e:
            logger.error(f"Database transaction error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed. Please try again."
            )

    return wrapper


def planning_center_exception_handler_sync(func):
    """
    Synchronous version of planning_center_exception_handler

    Use this for non-async functions that need Planning Center error handling.
    """
    from functools import wraps
    import logging

    logger = logging.getLogger(__name__)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PlanningCenterAuthenticationError as e:
            logger.error(f"PC Authentication failed: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Planning Center authentication failed. Please check credentials."
            )
        except PlanningCenterRateLimitError as e:
            logger.warning(f"PC Rate limit exceeded: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Planning Center rate limit exceeded. Please try again later."
            )
        except PlanningCenterNotFoundError as e:
            logger.warning(f"PC Resource not found: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planning Center resource not found."
            )
        except PlanningCenterAPIError as e:
            logger.error(f"PC API error: {e.message}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Planning Center service error. Please try again."
            )
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except DatabaseTransactionError as e:
            logger.error(f"Database transaction error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed. Please try again."
            )

    return wrapper
