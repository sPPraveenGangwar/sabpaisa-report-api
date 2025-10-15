"""
Logging utilities for consistent logging across the application
"""
import logging
import json
import traceback
from functools import wraps
from datetime import datetime
from django.utils import timezone


class LoggingMixin:
    """
    Mixin to add consistent logging to views and viewsets
    """

    @property
    def logger(self):
        """Get logger for the current module"""
        return logging.getLogger(self.__module__)

    @property
    def security_logger(self):
        """Get security logger"""
        return logging.getLogger('security')

    @property
    def performance_logger(self):
        """Get performance logger"""
        return logging.getLogger('performance')

    def log_request(self, request, action=None):
        """Log incoming request details"""
        user = getattr(request.user, 'username', 'Anonymous')
        client_ip = self.get_client_ip(request)
        method = request.method
        path = request.path
        action = action or f"{method} {path}"

        self.logger.info(
            f"Request | Action: {action} | User: {user} | IP: {client_ip} | "
            f"Method: {method} | Path: {path}"
        )

        # Log request data for POST/PUT/PATCH
        if method in ['POST', 'PUT', 'PATCH']:
            # Sanitize sensitive data
            data = self.sanitize_sensitive_data(request.data)
            self.logger.debug(f"Request data: {data}")

    def log_response(self, response, action=None, start_time=None):
        """Log response details"""
        status = response.status_code

        if start_time:
            elapsed = (timezone.now() - start_time).total_seconds()
            self.performance_logger.info(
                f"Response | Action: {action} | Status: {status} | Time: {elapsed:.3f}s"
            )

            # Log slow responses
            if elapsed > 1.0:
                self.logger.warning(
                    f"Slow response | Action: {action} | Time: {elapsed:.3f}s"
                )
        else:
            self.logger.info(f"Response | Action: {action} | Status: {status}")

    def log_error(self, error, action=None, request=None):
        """Log error with context"""
        user = 'Unknown'
        client_ip = 'Unknown'

        if request:
            user = getattr(request.user, 'username', 'Anonymous')
            client_ip = self.get_client_ip(request)

        error_details = {
            'action': action,
            'user': user,
            'ip': client_ip,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc()
        }

        self.logger.error(
            f"Error | Action: {action} | User: {user} | IP: {client_ip} | "
            f"Error: {error.__class__.__name__}: {str(error)}"
        )
        self.logger.debug(f"Error details: {json.dumps(error_details, indent=2)}")

    def log_security_event(self, event_type, message, request=None, severity='INFO'):
        """Log security-related events"""
        user = 'Unknown'
        client_ip = 'Unknown'

        if request:
            user = getattr(request.user, 'username', 'Anonymous')
            client_ip = self.get_client_ip(request)

        log_message = f"SECURITY_EVENT | Type: {event_type} | User: {user} | IP: {client_ip} | {message}"

        if severity == 'WARNING':
            self.security_logger.warning(log_message)
        elif severity == 'ERROR':
            self.security_logger.error(log_message)
        elif severity == 'CRITICAL':
            self.security_logger.critical(log_message)
        else:
            self.security_logger.info(log_message)

    def get_client_ip(self, request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def sanitize_sensitive_data(self, data):
        """Remove sensitive information from data before logging"""
        if not data:
            return data

        sensitive_fields = [
            'password', 'pass', 'pwd', 'secret', 'token', 'key',
            'authorization', 'auth', 'api_key', 'client_secret',
            'refresh', 'access', 'otp', 'pin'
        ]

        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(field in key.lower() for field in sensitive_fields):
                    sanitized[key] = '***REDACTED***'
                elif isinstance(value, dict):
                    sanitized[key] = self.sanitize_sensitive_data(value)
                else:
                    sanitized[key] = value
            return sanitized

        return data


def log_api_call(action=None):
    """
    Decorator to log API calls with timing

    Usage:
        @log_api_call(action="Get Transaction History")
        def get(self, request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            start_time = timezone.now()

            # Determine action name
            action_name = action or f"{request.method} {func.__name__}"

            # Get logger
            logger = logging.getLogger(self.__module__)
            performance_logger = logging.getLogger('performance')

            # Log request
            user = getattr(request.user, 'username', 'Anonymous')
            client_ip = request.META.get('REMOTE_ADDR', 'unknown')

            logger.info(
                f"API Call Start | Action: {action_name} | User: {user} | "
                f"IP: {client_ip} | Method: {request.method}"
            )

            try:
                # Execute the actual function
                response = func(self, request, *args, **kwargs)

                # Log successful response
                elapsed = (timezone.now() - start_time).total_seconds()

                logger.info(
                    f"API Call Success | Action: {action_name} | User: {user} | "
                    f"Status: {response.status_code} | Time: {elapsed:.3f}s"
                )

                performance_logger.info(
                    f"API Performance | Action: {action_name} | User: {user} | "
                    f"Time: {elapsed:.3f}s | Status: {response.status_code}"
                )

                # Log slow APIs
                if elapsed > 1.0:
                    logger.warning(
                        f"Slow API | Action: {action_name} | User: {user} | "
                        f"Time: {elapsed:.3f}s"
                    )

                return response

            except Exception as e:
                # Log error
                elapsed = (timezone.now() - start_time).total_seconds()

                logger.exception(
                    f"API Call Failed | Action: {action_name} | User: {user} | "
                    f"Error: {str(e)} | Time: {elapsed:.3f}s"
                )

                raise

        return wrapper
    return decorator


def log_database_query(query_type=None):
    """
    Decorator to log database queries with timing
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = timezone.now()
            logger = logging.getLogger('django.db')

            query_name = query_type or func.__name__

            try:
                result = func(*args, **kwargs)

                elapsed = (timezone.now() - start_time).total_seconds()

                if elapsed > 0.1:  # Log slow queries over 100ms
                    logger.warning(
                        f"Slow query | Type: {query_name} | Time: {elapsed:.3f}s"
                    )
                else:
                    logger.debug(
                        f"Query executed | Type: {query_name} | Time: {elapsed:.3f}s"
                    )

                return result

            except Exception as e:
                logger.error(
                    f"Query failed | Type: {query_name} | Error: {str(e)}"
                )
                raise

        return wrapper
    return decorator


class StructuredLogger:
    """
    Structured logging for better log parsing and analysis
    """

    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)

    def log_event(self, event_type, level='INFO', **kwargs):
        """
        Log a structured event

        Usage:
            logger.log_event(
                'transaction_search',
                user='john',
                filters={'date': 'today'},
                result_count=100
            )
        """
        # Create structured log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'level': level,
            **kwargs
        }

        # Convert to JSON string for structured logging
        log_message = json.dumps(log_entry)

        # Log at appropriate level
        if level == 'DEBUG':
            self.logger.debug(log_message)
        elif level == 'INFO':
            self.logger.info(log_message)
        elif level == 'WARNING':
            self.logger.warning(log_message)
        elif level == 'ERROR':
            self.logger.error(log_message)
        elif level == 'CRITICAL':
            self.logger.critical(log_message)

    def log_api_request(self, endpoint, method, user, ip, params=None, body=None):
        """Log API request in structured format"""
        self.log_event(
            'api_request',
            endpoint=endpoint,
            method=method,
            user=user,
            ip=ip,
            params=params,
            body=body
        )

    def log_api_response(self, endpoint, status_code, response_time, user):
        """Log API response in structured format"""
        self.log_event(
            'api_response',
            endpoint=endpoint,
            status_code=status_code,
            response_time=response_time,
            user=user
        )

    def log_error(self, error_type, message, user=None, context=None):
        """Log error in structured format"""
        self.log_event(
            'error',
            level='ERROR',
            error_type=error_type,
            message=message,
            user=user,
            context=context
        )

    def log_security_event(self, event_type, user, ip, details=None):
        """Log security event in structured format"""
        self.log_event(
            'security_event',
            level='WARNING',
            security_type=event_type,
            user=user,
            ip=ip,
            details=details
        )