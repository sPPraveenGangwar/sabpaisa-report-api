"""
Redis Cache Utilities for SabPaisa Reports API
Provides consistent caching across all modules
"""

import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


def generate_cache_key(prefix: str, **kwargs) -> str:
    """
    Generate a consistent cache key based on prefix and parameters

    Args:
        prefix: Module prefix (e.g., 'analytics', 'transactions')
        **kwargs: Filter parameters to include in cache key

    Returns:
        Hashed cache key string
    """
    # Sort parameters for consistency
    params = sorted(kwargs.items())
    param_str = json.dumps(params, sort_keys=True, default=str)

    # Generate hash for long parameter strings
    param_hash = hashlib.md5(param_str.encode()).hexdigest()[:12]

    return f"{prefix}_{param_hash}"


def cache_response(timeout: int = 300, key_prefix: str = 'api'):
    """
    Decorator to cache API responses with Redis

    Usage:
        @cache_response(timeout=300, key_prefix='transactions')
        def get(self, request):
            ...

    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            # Extract cache key parameters from request
            cache_params = {}

            # Add query parameters
            if hasattr(request, 'query_params'):
                cache_params.update(request.query_params.dict())
            elif hasattr(request, 'GET'):
                cache_params.update(request.GET.dict())

            # Add user information
            if hasattr(request, 'user') and request.user.is_authenticated:
                cache_params['user_id'] = request.user.id

            # Add URL path parameters
            if args:
                cache_params['args'] = str(args)
            if kwargs:
                cache_params.update(kwargs)

            # Generate cache key
            cache_key = generate_cache_key(key_prefix, **cache_params)

            # Try to get from cache
            try:
                cached_data = cache.get(cache_key)
                if cached_data is not None:
                    logger.info(f"Cache HIT: {cache_key}")
                    return Response(cached_data)
            except Exception as e:
                logger.warning(f"Cache GET error: {e}")

            # Cache miss - execute view
            logger.info(f"Cache MISS: {cache_key}")
            response = view_func(self, request, *args, **kwargs)

            # Cache the response if successful
            if isinstance(response, Response) and response.status_code == 200:
                try:
                    cache.set(cache_key, response.data, timeout)
                    logger.info(f"Cached response: {cache_key} (TTL: {timeout}s)")
                except Exception as e:
                    logger.warning(f"Cache SET error: {e}")

            return response

        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate all cache keys matching a pattern

    Args:
        pattern: Cache key pattern (e.g., 'transactions_*')

    Returns:
        Number of keys deleted
    """
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")

        # Get all keys matching pattern
        keys = redis_conn.keys(f"sabpaisa:{pattern}")

        if keys:
            count = redis_conn.delete(*keys)
            logger.info(f"Invalidated {count} cache keys matching '{pattern}'")
            return count
        return 0
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")
        return 0


def clear_user_cache(user_id: int) -> int:
    """
    Clear all cache entries for a specific user

    Args:
        user_id: User ID

    Returns:
        Number of keys deleted
    """
    return invalidate_cache_pattern(f"*user_id*{user_id}*")


def get_cache_stats() -> dict:
    """
    Get Redis cache statistics

    Returns:
        Dictionary with cache stats
    """
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")

        info = redis_conn.info()

        return {
            'connected': True,
            'total_keys': redis_conn.dbsize(),
            'used_memory': info.get('used_memory_human', 'N/A'),
            'connected_clients': info.get('connected_clients', 0),
            'uptime_days': info.get('uptime_in_days', 0),
            'hit_rate': info.get('keyspace_hits', 0) / max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1), 1) * 100
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {'connected': False, 'error': str(e)}
