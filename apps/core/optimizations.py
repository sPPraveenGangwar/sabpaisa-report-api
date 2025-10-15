"""
Performance optimization utilities for views
"""
from django.core.cache import cache
from django.db.models import Prefetch
from functools import wraps
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def cache_view_queryset(timeout=300, key_prefix='view'):
    """
    Decorator to cache view queryset results
    Usage: @cache_view_queryset(timeout=300)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(view_instance, request, *args, **kwargs):
            # Generate cache key from request params
            cache_key_parts = [
                key_prefix,
                view_func.__name__,
                request.user.username if hasattr(request.user, 'username') else 'anon',
                request.GET.urlencode()
            ]
            cache_key_str = ':'.join(str(p) for p in cache_key_parts)
            cache_key = hashlib.md5(cache_key_str.encode()).hexdigest()
            cache_key = f'sabpaisa:view:{cache_key}'

            # Try cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache HIT for {view_func.__name__}")
                return cached_result

            # Execute view
            logger.debug(f"Cache MISS for {view_func.__name__}")
            result = view_func(view_instance, request, *args, **kwargs)

            # Cache the result
            cache.set(cache_key, result, timeout)
            return result

        return wrapper
    return decorator


def optimize_queryset_fields(queryset, fields_list):
    """
    Optimize queryset by selecting only required fields
    """
    try:
        return queryset.only(*fields_list)
    except Exception as e:
        logger.warning(f"Field optimization failed: {e}")
        return queryset


def add_select_related(queryset, related_fields):
    """
    Add select_related for foreign key optimization
    """
    try:
        return queryset.select_related(*related_fields)
    except Exception as e:
        logger.warning(f"select_related failed: {e}")
        return queryset


def add_prefetch_related(queryset, prefetch_fields):
    """
    Add prefetch_related for many-to-many optimization
    """
    try:
        return queryset.prefetch_related(*prefetch_fields)
    except Exception as e:
        logger.warning(f"prefetch_related failed: {e}")
        return queryset
