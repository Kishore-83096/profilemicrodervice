from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


def custom_exception_handler(exc, context):
    """
    Global exception handler for Profile_MS.
    Ensures consistent error response format.
    """

    response = exception_handler(exc, context)

    error_response = {
        "success": False,
        "message": "Something went wrong. Please try again later."
    }

    # -------------------------------
    # Validation Errors → 400
    # -------------------------------
    if isinstance(exc, ValidationError):
        error_response["message"] = (
            exc.detail if isinstance(exc.detail, str)
            else "Invalid input. Please check your data."
        )
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------
    # Authentication Errors → 401
    # -------------------------------
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        error_response["message"] = "Authentication failed. Please login again."
        return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

    # -------------------------------
    # Permission Errors → 403
    # -------------------------------
    if isinstance(exc, PermissionDenied):
        error_response["message"] = (
            "You do not have permission to perform this action."
        )
        return Response(error_response, status=status.HTTP_403_FORBIDDEN)

    # -------------------------------
    # JWT Errors → 401
    # -------------------------------
    if isinstance(exc, (InvalidToken, TokenError)):
        error_response["message"] = "Session expired. Please login again."
        return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

    # -------------------------------
    # Unhandled Server Errors → 500
    # -------------------------------
    if response is None:
        return Response(
            {
                "success": False,
                "message": "Internal server error. Please contact support."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # If DRF already created a response, wrap it
    response.data = error_response
    return response
