"""
Redis caching service for intelligent cache management
"""
from django.core.cache import cache
from django.conf import settings
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class RedisService:
    """
    Intelligent Redis caching service with predictive warming
    """

    @staticmethod
    def generate_cache_key(*args, **kwargs):
        """
        Generate a unique cache key based on arguments
        """
        key_parts = list(args)
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")

        key_string = ":".join(str(part) for part in key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()

        return f"sabpaisa:{key_hash}"

    @staticmethod
    def get(key, default=None):
        """
        Get value from cache
        """
        try:
            value = cache.get(key, default)
            if value is not None:
                logger.debug(f"Cache hit: {key}")
            else:
                logger.debug(f"Cache miss: {key}")
            return value
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return default

    @staticmethod
    def set(key, value, timeout=None):
        """
        Set value in cache
        """
        try:
            if timeout is None:
                # Safely get timeout from settings
                default_cache = settings.CACHES.get('default', {})
                timeout = default_cache.get('TIMEOUT', 3600) if isinstance(default_cache, dict) else 3600

            cache.set(key, value, timeout)
            logger.debug(f"Cache set: {key} (timeout: {timeout}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    @staticmethod
    def delete(key):
        """
        Delete key from cache
        """
        try:
            cache.delete(key)
            logger.debug(f"Cache delete: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    @staticmethod
    def delete_pattern(pattern):
        """
        Delete all keys matching a pattern
        """
        try:
            cache.delete_pattern(pattern)
            logger.debug(f"Cache delete pattern: {pattern}")
            return True
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return False

    @staticmethod
    def get_or_set(key, func, timeout=None):
        """
        Get from cache or compute and set
        """
        value = RedisService.get(key)
        if value is None:
            value = func()
            RedisService.set(key, value, timeout)
        return value

    @staticmethod
    def invalidate_merchant_cache(merchant_id):
        """
        Invalidate all cache entries for a specific merchant
        """
        patterns = [
            f"*merchant:{merchant_id}:*",
            f"*client_code:{merchant_id}:*"
        ]
        for pattern in patterns:
            RedisService.delete_pattern(pattern)

    @staticmethod
    def warm_cache_for_merchant(merchant_id):
        """
        Predictive cache warming for merchant data
        """
        # This would be called by a Celery task
        logger.info(f"Warming cache for merchant: {merchant_id}")
        # Implementation would preload frequently accessed data


class CacheDecorator:
    """
    Decorator for caching function results (Enhanced for DRF views)
    """

    @staticmethod
    def cache_result(timeout=3600, key_prefix=None):
        """
        Decorator to cache function results - handles DRF requests

        Args:
            timeout: Cache TTL in seconds
            key_prefix: Optional prefix for cache key
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Extract request object (DRF views pass 'self' and 'request')
                request = None
                if len(args) > 1 and hasattr(args[1], 'query_params'):
                    request = args[1]

                # Generate cache key
                if key_prefix:
                    cache_key = f"{key_prefix}:{func.__name__}"
                else:
                    cache_key = func.__name__

                # Add arguments to cache key
                key_parts = [cache_key]

                # Add request query parameters if available
                if request:
                    query_params = dict(request.query_params)
                    # Add user ID if authenticated
                    if hasattr(request, 'user') and request.user.is_authenticated:
                        query_params['user_id'] = request.user.id
                    key_parts.extend(f"{k}:{v}" for k, v in sorted(query_params.items()))
                else:
                    # Fallback to args/kwargs
                    key_parts.extend(str(arg) for arg in args[1:])  # Skip 'self'
                    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))

                final_key = RedisService.generate_cache_key(*key_parts)

                # Try to get from cache
                result = RedisService.get(final_key)
                if result is not None:
                    logger.info(f"✓ Cache HIT: {func.__name__} (key: {final_key[:20]}...)")
                    return result

                logger.info(f"✗ Cache MISS: {func.__name__} - Computing fresh data...")

                # Compute result
                result = func(*args, **kwargs)

                # Store in cache (only cache successful responses)
                if hasattr(result, 'status_code') and result.status_code == 200:
                    RedisService.set(final_key, result, timeout)
                    logger.info(f"✓ Cached: {func.__name__} (TTL: {timeout}s)")

                return result
            return wrapper
        return decorator