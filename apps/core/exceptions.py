"""
Custom exception handling for the API
"""
from rest_framework.views import exception_handler
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import DatabaseError
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'success': False,
            'error': {
                'message': get_error_message(exc),
                'code': get_error_code(exc),
                'details': response.data
            }
        }

        # Log the error
        logger.error(
            f"API Error: {exc.__class__.__name__} - {str(exc)} "
            f"Path: {context['request'].path}"
        )

        response.data = custom_response_data

    # Handle database errors
    elif isinstance(exc, DatabaseError):
        logger.error(f"Database Error: {str(exc)}")
        from rest_framework.response import Response
        return Response({
            'success': False,
            'error': {
                'message': 'Database error occurred. Please try again later.',
                'code': 'DATABASE_ERROR',
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handle validation errors
    elif isinstance(exc, ValidationError):
        from rest_framework.response import Response
        return Response({
            'success': False,
            'error': {
                'message': 'Validation error occurred.',
                'code': 'VALIDATION_ERROR',
                'details': exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    return response


def get_error_message(exc):
    """
    Get user-friendly error message
    """
    error_messages = {
        'NotAuthenticated': 'Authentication credentials were not provided.',
        'AuthenticationFailed': 'Invalid authentication credentials.',
        'PermissionDenied': 'You do not have permission to perform this action.',
        'NotFound': 'The requested resource was not found.',
        'MethodNotAllowed': 'Method not allowed for this endpoint.',
        'Throttled': 'Request was throttled. Please try again later.',
    }

    exc_class_name = exc.__class__.__name__
    return error_messages.get(exc_class_name, str(exc))


def get_error_code(exc):
    """
    Get error code for the exception
    """
    error_codes = {
        'NotAuthenticated': 'NOT_AUTHENTICATED',
        'AuthenticationFailed': 'AUTHENTICATION_FAILED',
        'PermissionDenied': 'PERMISSION_DENIED',
        'NotFound': 'NOT_FOUND',
        'MethodNotAllowed': 'METHOD_NOT_ALLOWED',
        'Throttled': 'THROTTLED',
        'ValidationError': 'VALIDATION_ERROR',
    }

    exc_class_name = exc.__class__.__name__
    return error_codes.get(exc_class_name, 'UNKNOWN_ERROR')