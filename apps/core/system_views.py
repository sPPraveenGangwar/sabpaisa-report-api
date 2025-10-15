"""
System monitoring and health check views
NEW ENDPOINTS - No impact on existing APIs
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.db import connections
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import psutil
import logging
import time

from apps.core.permissions import IsAdmin

logger = logging.getLogger(__name__)


class SystemHealthView(APIView):
    """
    Comprehensive health check endpoint
    GET /api/v1/system/health/

    NEW ENDPOINT - Does not modify any existing APIs
    """
    permission_classes = [AllowAny]  # Public endpoint for monitoring tools

    def get(self, request):
        """
        Check health of all system dependencies
        Returns overall status and individual service statuses
        """
        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0',
            'services': {}
        }

        overall_healthy = True

        # Check all databases
        for db_name in ['default', 'legacy', 'user_management', 'qwikforms_db']:
            db_status = self._check_database(db_name)
            health_data['services'][f'database_{db_name}'] = db_status
            if db_status['status'] != 'healthy':
                overall_healthy = False

        # Check Redis cache
        cache_status = self._check_redis()
        health_data['services']['redis_cache'] = cache_status
        if cache_status['status'] != 'healthy':
            overall_healthy = False

        # System resources
        try:
            health_data['system'] = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        except Exception as e:
            logger.error(f"Error getting system resources: {e}")
            health_data['system'] = {'status': 'unavailable'}

        # Set overall status
        health_data['status'] = 'healthy' if overall_healthy else 'unhealthy'

        response_status = status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

        return Response(health_data, status=response_status)

    def _check_database(self, db_name):
        """Check database connection and response time"""
        try:
            start_time = time.time()
            with connections[db_name].cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            response_time = (time.time() - start_time) * 1000  # Convert to ms

            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2)
            }
        except Exception as e:
            logger.error(f"Database {db_name} health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def _check_redis(self):
        """Check Redis cache connection"""
        try:
            start_time = time.time()
            cache.set('health_check', 'ok', timeout=10)
            result = cache.get('health_check')
            response_time = (time.time() - start_time) * 1000

            if result == 'ok':
                # Get cache stats if available
                try:
                    from django_redis import get_redis_connection
                    redis_conn = get_redis_connection("default")
                    info = redis_conn.info('memory')
                    memory_used = info.get('used_memory_human', 'N/A')
                except:
                    memory_used = 'N/A'

                return {
                    'status': 'healthy',
                    'response_time_ms': round(response_time, 2),
                    'memory_used': memory_used
                }
            else:
                return {'status': 'unhealthy', 'error': 'Cache test failed'}
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


class SystemMetricsView(APIView):
    """
    System metrics and statistics
    GET /api/v1/system/metrics/

    NEW ENDPOINT - Admin only, does not modify existing APIs
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        """
        Get system-wide metrics and statistics
        """
        metrics = {
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'data': {}
        }

        # API request statistics
        metrics['data']['api_stats'] = self._get_api_stats()

        # Transaction statistics
        metrics['data']['transaction_stats'] = self._get_transaction_stats()

        # Cache statistics
        metrics['data']['cache_stats'] = self._get_cache_stats()

        # Database statistics
        metrics['data']['database_stats'] = self._get_database_stats()

        return Response(metrics)

    def _get_api_stats(self):
        """Get API request statistics from cache"""
        try:
            # Get cached metrics (these would be tracked by middleware)
            total_requests = cache.get('metrics:total_requests_today', 0)
            avg_response_time = cache.get('metrics:avg_response_time', 0)
            error_count = cache.get('metrics:error_count_today', 0)
            slow_requests = cache.get('metrics:slow_requests_today', 0)

            error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0

            return {
                'total_requests_today': total_requests,
                'avg_response_time_ms': round(avg_response_time, 2),
                'error_rate_percent': round(error_rate, 2),
                'slow_requests': slow_requests
            }
        except Exception as e:
            logger.error(f"Error getting API stats: {e}")
            return {'error': 'Unable to fetch API statistics'}

    def _get_transaction_stats(self):
        """Get today's transaction statistics"""
        try:
            from apps.transactions.models import TransactionDetail
            from django.db.models import Count, Q

            today = timezone.now().date()
            today_transactions = TransactionDetail.objects.filter(
                trans_date__date=today
            )

            total = today_transactions.count()
            successful = today_transactions.filter(status='SUCCESS').count()
            failed = today_transactions.filter(status='FAILED').count()
            success_rate = (successful / total * 100) if total > 0 else 0

            return {
                'total_today': total,
                'successful': successful,
                'failed': failed,
                'success_rate': round(success_rate, 2)
            }
        except Exception as e:
            logger.error(f"Error getting transaction stats: {e}")
            return {'error': 'Unable to fetch transaction statistics'}

    def _get_cache_stats(self):
        """Get cache performance statistics"""
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            info = redis_conn.info('stats')

            hits = int(info.get('keyspace_hits', 0))
            misses = int(info.get('keyspace_misses', 0))
            total = hits + misses

            hit_rate = (hits / total * 100) if total > 0 else 0
            miss_rate = (misses / total * 100) if total > 0 else 0

            # Memory info
            memory_info = redis_conn.info('memory')
            memory_used = memory_info.get('used_memory_human', 'N/A')

            return {
                'hit_rate': round(hit_rate, 2),
                'miss_rate': round(miss_rate, 2),
                'memory_used': memory_used
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'error': 'Unable to fetch cache statistics'}

    def _get_database_stats(self):
        """Get database connection statistics"""
        try:
            stats = {}
            for db_name in ['default', 'legacy', 'user_management', 'qwikforms_db']:
                try:
                    with connections[db_name].cursor() as cursor:
                        # Get connection status
                        cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
                        result = cursor.fetchone()
                        connections_count = int(result[1]) if result else 0

                        stats[db_name] = {
                            'active_connections': connections_count,
                            'status': 'connected'
                        }
                except Exception as e:
                    stats[db_name] = {
                        'status': 'error',
                        'error': str(e)
                    }

            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {'error': 'Unable to fetch database statistics'}


class DatabaseStatusView(APIView):
    """
    Detailed database connection status
    GET /api/v1/system/database/status/

    NEW ENDPOINT - Admin only, does not modify existing APIs
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        """
        Test all database connections and return detailed status
        """
        database_status = {
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'databases': {}
        }

        for db_name in ['default', 'legacy', 'user_management', 'qwikforms_db']:
            database_status['databases'][db_name] = self._test_database(db_name)

        return Response(database_status)

    def _test_database(self, db_name):
        """Test individual database connection"""
        try:
            start_time = time.time()
            with connections[db_name].cursor() as cursor:
                # Test query
                cursor.execute("SELECT 1")
                cursor.fetchone()

                # Get database info
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]

                # Get connection info
                cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
                threads = cursor.fetchone()
                active_connections = int(threads[1]) if threads else 0

            response_time = (time.time() - start_time) * 1000

            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'version': version,
                'active_connections': active_connections
            }
        except Exception as e:
            logger.error(f"Database {db_name} test failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


class AuditLogView(APIView):
    """
    View audit logs for sensitive operations
    GET /api/v1/system/audit-logs/

    NEW ENDPOINT - Admin only, read-only view of logs
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        """
        Get audit logs with filtering options
        """
        # Get query parameters
        action_filter = request.query_params.get('action')
        user_filter = request.query_params.get('user')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        limit = int(request.query_params.get('limit', 100))

        # Get logs from cache (these are populated by security logger)
        logs = self._get_audit_logs(
            action_filter=action_filter,
            user_filter=user_filter,
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )

        return Response({
            'success': True,
            'count': len(logs),
            'data': logs
        })

    def _get_audit_logs(self, action_filter=None, user_filter=None,
                        date_from=None, date_to=None, limit=100):
        """
        Get audit logs from cache/database
        In production, this would query an audit_logs table
        For now, returns sample structure
        """
        try:
            # This is a placeholder - in production, query actual audit log table
            logs = []

            # Get recent security events from cache
            cache_keys = cache.keys('audit:*')[:limit]
            for key in cache_keys:
                log_entry = cache.get(key)
                if log_entry:
                    # Apply filters
                    if action_filter and log_entry.get('action') != action_filter:
                        continue
                    if user_filter and log_entry.get('user') != user_filter:
                        continue

                    logs.append(log_entry)

            # Sort by timestamp descending
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            return logs[:limit]
        except Exception as e:
            logger.error(f"Error fetching audit logs: {e}")
            return []
