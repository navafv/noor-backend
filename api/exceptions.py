from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler that standardizes error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # If the exception was handled by DRF
    if response is not None:
        # Add a standard "status" field
        response.data['status'] = 'error'
        
        # If the error is a simple detail string, wrap it
        if 'detail' in response.data:
            response.data['message'] = response.data['detail']
            del response.data['detail']
        else:
            # If it's a validation error dictionary, keep it generally as is,
            # but maybe add a generic message.
            if response.status_code == 400:
                 response.data['message'] = "Validation error"

    # If response is None, it's an unhandled server error (500)
    else:
        logger.error(f"Unhandled Exception: {exc}", exc_info=True)
        
        # In production, hide details. In debug, show them.
        # For this app, we'll return a generic 500 json.
        return Response(
            {
                "status": "error",
                "message": "An unexpected error occurred. Please contact support."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response