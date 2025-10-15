"""
Custom throttling classes for intelligent rate limiting
"""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core.cache import cache


class CustomAnonThrottle(AnonRateThrottle):
    """
    Custom anonymous throttle with intelligent rate limiting
    """
    scope = 'anon_custom'

    def get_cache_key(self, request, view):
        """
        Override to include additional factors in rate limiting
        """
        if self.get_ident(request) is None:
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class MerchantRateThrottle(UserRateThrottle):
    """
    Merchant-specific rate limiting
    """
    scope = 'merchant'

    def get_cache_key(self, request, view):
        """
        Rate limit based on merchant ID
        """
        if request.user.is_authenticated:
            merchant_id = getattr(request.user, 'merchant_id', None)
            if merchant_id:
                ident = f"merchant_{merchant_id}"
            else:
                ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class ReportGenerationThrottle(UserRateThrottle):
    """
    Special throttle for report generation endpoints
    """
    scope = 'report_generation'
    rate = '10/hour'  # Allow 10 report generations per hour per user

    def allow_request(self, request, view):
        """
        Check if the request should be throttled for report generation
        """
        if request.user.is_staff:
            return True  # Don't throttle staff users

        return super().allow_request(request, view)