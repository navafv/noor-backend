from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied, NotAuthenticated
from django.http import Http404
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Global exception handler for a consistent API response format.
    Format:
    {
        "success": False,
        "status_code": 4xx/5xx,
        "message": "Human readable error",
        "code": "internal_code",
        "details": { ... } (optional field errors)
    }
    """
    # Call DRF's default handler first to get the standard response
    response = exception_handler(exc, context)

    # Default error details
    success = False
    message = "An unexpected error occurred."
    code = "server_error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    details = None

    if response is not None:
        # DRF handled the exception (e.g., ValidationError, PermissionDenied)
        status_code = response.status_code
        
        if isinstance(exc, ValidationError):
            message = "Validation failed."
            code = "validation_error"
            details = response.data
        elif isinstance(exc, (PermissionDenied, NotAuthenticated)):
            message = "You do not have permission to perform this action."
            code = "permission_denied"
        elif isinstance(exc, Http404):
            message = "The requested resource was not found."
            code = "not_found"
        else:
            # Extract message from DRF response if available
            message = response.data.get('detail', str(exc))
            code = "client_error"
    
    else:
        # Handle unexpected errors (500) that DRF didn't catch
        logger.error(f"Unhandled Exception in {context['view'].__class__.__name__}: {exc}", exc_info=True)
        # In production, keep the message generic. In debug, you might show str(exc)
        message = "Internal Server Error. Please contact support."

    # Construct the standardized response
    data = {
        "success": success,
        "status_code": status_code,
        "message": message,
        "code": code,
    }
    
    if details:
        data["details"] = details

    return Response(data, status=status_code)