"""
Custom middleware for request processing and monitoring
"""
import time
import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.cache import cache

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Logs all incoming requests with relevant information
    """
    def process_request(self, request):
        request.start_time = time.time()

        # Log request details
        logger.info(f"Request: {request.method} {request.path}")

        # Add request ID for tracking
        import uuid
        request.id = str(uuid.uuid4())

        return None

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"Response: {request.method} {request.path} "
                f"Status: {response.status_code} "
                f"Duration: {duration:.3f}s"
            )

            # Add performance headers
            response['X-Request-ID'] = getattr(request, 'id', 'unknown')
            response['X-Response-Time'] = f"{duration:.3f}"

        return response


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Monitors API performance and tracks slow requests
    """
    SLOW_REQUEST_THRESHOLD = 0.150  # 150ms threshold

    def process_request(self, request):
        request._start_time = time.time()
        return None

    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time

            # Track slow requests
            if duration > self.SLOW_REQUEST_THRESHOLD:
                logger.warning(
                    f"Slow request detected: {request.method} {request.path} "
                    f"took {duration:.3f}s (threshold: {self.SLOW_REQUEST_THRESHOLD}s)"
                )

                # Cache slow request info for analytics
                cache_key = f"slow_request_{request.path}_{int(time.time())}"
                cache.set(cache_key, {
                    'method': request.method,
                    'path': request.path,
                    'duration': duration,
                    'user': str(getattr(request.user, 'id', 'anonymous')),
                    'timestamp': time.time()
                }, timeout=3600)  # Keep for 1 hour

            # Add performance classification header
            if duration < 0.100:
                performance = 'excellent'
            elif duration < 0.150:
                performance = 'good'
            elif duration < 0.300:
                performance = 'acceptable'
            else:
                performance = 'slow'

            response['X-Performance'] = performance

        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Adds security headers to all responses
    """
    def process_response(self, request, response):
        # Security headers for production
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Remove server header for security
        if 'Server' in response:
            del response['Server']

        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Global rate limiting middleware
    """
    def process_request(self, request):
        # Get client IP
        ip = self.get_client_ip(request)

        # Check global rate limit
        cache_key = f"rate_limit_{ip}"
        requests_count = cache.get(cache_key, 0)

        # 10000 requests per hour per IP (global limit)
        if requests_count > 10000:
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return JsonResponse(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=429
            )

        # Increment counter
        cache.set(cache_key, requests_count + 1, timeout=3600)

        return None

    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# ===== NEW FEATURE ENHANCEMENTS - Response Headers Only =====
# These middleware classes ADD headers without changing response body
# ZERO impact on existing API responses

class RequestCorrelationMiddleware(MiddlewareMixin):
    """
    ENHANCEMENT: Adds Request Correlation ID and Response Time headers

    NEW FEATURE - Adds headers only, does NOT modify response body
    Headers Added:
    - X-Request-ID: Unique identifier for request tracing
    - X-Response-Time: Response time in seconds

    Response body: UNCHANGED
    """
    def process_request(self, request):
        """Generate unique request ID"""
        import uuid
        request.correlation_id = str(uuid.uuid4())
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        """Add correlation ID and response time headers"""
        # Add Request ID header
        if hasattr(request, 'correlation_id'):
            response['X-Request-ID'] = request.correlation_id

        # Add Response Time header
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response['X-Response-Time'] = f"{duration:.3f}s"

        return response


class PerformanceHeaderMiddleware(MiddlewareMixin):
    """
    ENHANCEMENT: Adds Performance Classification header

    NEW FEATURE - Adds header only, does NOT modify response body
    Header Added:
    - X-Performance: excellent|good|acceptable|slow

    Response body: UNCHANGED
    """
    def process_request(self, request):
        """Track request start time"""
        if not hasattr(request, 'start_time'):
            request.start_time = time.time()
        return None

    def process_response(self, request, response):
        """Add performance classification header"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time

            # Classify performance
            if duration < 0.100:
                performance = 'excellent'
            elif duration < 0.200:
                performance = 'good'
            elif duration < 0.500:
                performance = 'acceptable'
            else:
                performance = 'slow'

            response['X-Performance'] = performance

        return response


class RateLimitHeaderMiddleware(MiddlewareMixin):
    """
    ENHANCEMENT: Adds Rate Limit Information headers

    NEW FEATURE - Adds headers only, does NOT modify response body
    Headers Added:
    - X-RateLimit-Limit: Maximum requests allowed
    - X-RateLimit-Remaining: Remaining requests in current window
    - X-RateLimit-Reset: Unix timestamp when limit resets

    Response body: UNCHANGED
    """
    def process_response(self, request, response):
        """Add rate limit information headers"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Get user's rate limit info from cache
            user_id = getattr(request.user, 'id', 'unknown')
            cache_key = f"rate_limit_{user_id}"

            # Get current request count
            current_count = cache.get(cache_key, 0)

            # Determine limit based on user role
            if hasattr(request.user, 'role_id'):
                if request.user.role_id == 1:  # Admin
                    limit = 10000
                else:  # Merchant
                    limit = 5000
            else:
                limit = 1000

            remaining = max(0, limit - current_count)

            # Reset time (1 hour from now)
            reset_time = int(time.time()) + 3600

            # Add headers
            response['X-RateLimit-Limit'] = str(limit)
            response['X-RateLimit-Remaining'] = str(remaining)
            response['X-RateLimit-Reset'] = str(reset_time)
        else:
            # Anonymous user
            response['X-RateLimit-Limit'] = '100'
            response['X-RateLimit-Remaining'] = '100'
            response['X-RateLimit-Reset'] = str(int(time.time()) + 3600)

        return response