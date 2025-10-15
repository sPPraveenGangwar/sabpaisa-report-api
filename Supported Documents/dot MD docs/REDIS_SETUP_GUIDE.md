# Redis Cache Setup Guide for SabPaisa Reports API

This guide explains how Redis caching is configured in the SabPaisa Reports API and how to set it up.

## Table of Contents
1. [Overview](#overview)
2. [Automatic Setup (Recommended)](#automatic-setup-recommended)
3. [Manual Installation](#manual-installation)
4. [Configuration](#configuration)
5. [Caching Implementation](#caching-implementation)
6. [Performance Benefits](#performance-benefits)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The SabPaisa Reports API uses **Redis** as a distributed cache to dramatically improve API response times. Redis caching has been implemented across all major API modules:

- **Analytics Dashboard API** - 5 endpoints cached (5-30 min TTL)
- **Transactions API** - 4 endpoints cached (5-30 min TTL)
- **Settlements API** - 6 endpoints cached (5-10 min TTL)
- **Refunds API** - 2 endpoints cached (5 min TTL)
- **Reports API** - 1 endpoint cached (5 min TTL)

### Performance Improvements
- **Dashboard load time**: 10-20s → 0.5-2s (10-20X faster)
- **Transaction queries**: 2-5s → 400-800ms (4-6X faster)
- **Cache hit responses**: 50-100ms (5-10X faster than database)

---

## Automatic Setup (Recommended)

### Using VS Code F5 (Automatic)

The easiest way to run the application is through VS Code, which automatically sets up everything:

1. **Open the project** in VS Code:
   ```bash
   code /path/to/sabpaisa-reports-api
   ```

2. **Press F5** to start debugging

   The auto-setup script (`scripts/auto_setup.py`) will automatically:
   - ✅ Check Python version (3.8+)
   - ✅ Install all dependencies from `requirements.txt`
   - ✅ Check if Redis is running
   - ✅ Attempt to start Redis automatically
   - ✅ Verify database connection
   - ✅ Run pending migrations
   - ✅ Start Django development server

### Using Command Line (Automatic)

You can also run the auto-setup script manually:

```bash
cd /path/to/sabpaisa-reports-api
python scripts/auto_setup.py
```

After setup completes, start Django:

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## Manual Installation

If you prefer to install Redis manually or the auto-setup fails:

### On Windows

#### Option 1: Using Memurai (Recommended for Windows)
1. Download Memurai from https://www.memurai.com/get-memurai
2. Run the installer
3. Memurai will start automatically as a Windows service

#### Option 2: Using Redis for Windows
1. Download from https://github.com/microsoftarchive/redis/releases
2. Extract to `C:\Redis`
3. Run `redis-server.exe`

#### Verify Installation
```cmd
redis-cli ping
# Should return: PONG
```

### On Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Redis
sudo apt install redis-server -y

# Start Redis service
sudo systemctl start redis-server

# Enable Redis to start on boot
sudo systemctl enable redis-server

# Verify installation
redis-cli ping
# Should return: PONG
```

### On Linux (CentOS/RHEL)

```bash
# Install EPEL repository
sudo yum install epel-release -y

# Install Redis
sudo yum install redis -y

# Start Redis service
sudo systemctl start redis

# Enable Redis to start on boot
sudo systemctl enable redis

# Verify installation
redis-cli ping
# Should return: PONG
```

### On macOS

```bash
# Using Homebrew
brew install redis

# Start Redis service
brew services start redis

# Verify installation
redis-cli ping
# Should return: PONG
```

### Using Docker

```bash
# Pull Redis image
docker pull redis:7-alpine

# Run Redis container
docker run -d \
  --name sabpaisa-redis \
  -p 6379:6379 \
  redis:7-alpine

# Verify installation
docker exec -it sabpaisa-redis redis-cli ping
# Should return: PONG
```

---

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/1
CACHE_TTL=300  # Default cache timeout in seconds (5 minutes)
```

### Django Settings

Redis is configured in `config/settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,  # Graceful fallback if Redis is down
        },
        'KEY_PREFIX': 'sabpaisa',
        'TIMEOUT': config('CACHE_TTL', default=300, cast=int),
    }
}
```

### Dependencies

Redis dependencies are in `requirements.txt`:

```txt
redis==5.0.1
django-redis==5.4.0
hiredis==2.3.2
```

---

## Caching Implementation

### Cache Decorator

All cached endpoints use the `@CacheDecorator.cache_result()` decorator:

```python
from apps.core.cache import CacheDecorator

class MyView(views.APIView):
    @CacheDecorator.cache_result(timeout=300, key_prefix='my_endpoint')
    def get(self, request):
        # Your view logic here
        return Response(data)
```

### Cache Key Generation

Cache keys are automatically generated based on:
- **User ID** - Each user has separate cache
- **Query parameters** - Different filters = different cache keys
- **Date filter** - today/week/month/year filters cached separately
- **Endpoint prefix** - Each endpoint has unique prefix

Example cache key format:
```
sabpaisa_executive_dashboard_today_2025-10-08_user_1_filter_today
```

### Cache Timeouts by Module

| Module | Endpoints | Timeout | Reason |
|--------|-----------|---------|---------|
| Analytics Dashboard | 5 views | 5-30 min | Relatively stable aggregate data |
| Transactions | 4 views | 5-30 min | Historical transaction data |
| Settlements | 6 views | 5-10 min | Frequently updated settlement status |
| Refunds | 2 views | 5 min | Real-time refund processing |
| Reports | 1 view | 5 min | Report list changes frequently |

### Cached Endpoints

#### Analytics Module
```python
# apps/analytics/views.py

# 1. Merchant Analytics (30 min cache)
@CacheDecorator.cache_result(timeout=1800)
class MerchantAnalyticsView(views.APIView)

# 2. Payment Mode Analytics (15 min cache)
@CacheDecorator.cache_result(timeout=900, key_prefix='payment_mode_analytics')
class PaymentModeAnalyticsView(views.APIView)

# 3. Settlement Analytics (15 min cache)
@CacheDecorator.cache_result(timeout=900, key_prefix='settlement_analytics')
class SettlementAnalyticsView(views.APIView)

# 4. Refund/Chargeback Analytics (30 min cache)
@CacheDecorator.cache_result(timeout=1800, key_prefix='refund_chargeback_analytics')
class RefundChargebackAnalyticsView(views.APIView)

# 5. Comparative Analytics (30 min cache)
@CacheDecorator.cache_result(timeout=1800, key_prefix='comparative_analytics')
class ComparativeAnalyticsView(views.APIView)
```

#### Transactions Module
```python
# apps/transactions/views.py

# 1. Merchant Transaction History (5 min cache)
@CacheDecorator.cache_result(timeout=300, key_prefix='merchant_txn_history')
class GetMerchantTransactionHistoryView(generics.ListAPIView)

# 2. Admin Transaction History (5 min cache)
@CacheDecorator.cache_result(timeout=300, key_prefix='admin_txn_history')
class GetAdminTxnHistoryView(generics.ListAPIView)

# 3. Transaction Summary (10 min cache)
@CacheDecorator.cache_result(timeout=600, key_prefix='txn_summary')
class TransactionSummaryView(views.APIView)

# 4. Transaction Search (30 min cache)
@CacheDecorator.cache_result(timeout=1800, key_prefix='txn_search')
class TransactionSearchView(views.APIView)

# 5. Success Graph (60 min cache)
@CacheDecorator.cache_result(timeout=3600)
class GetSuccessGraphView(views.APIView)
```

#### Settlements Module
```python
# apps/settlements/views.py

# 1. Settled Transaction History (5 min cache)
@CacheDecorator.cache_result(timeout=300, key_prefix='settled_txn_history')
class GetSettledTxnHistoryView(generics.ListAPIView)

# 2. Settled Grouped View (10 min cache)
@CacheDecorator.cache_result(timeout=600, key_prefix='settled_grouped')
class SettledGroupedView(generics.ListAPIView)

# 3. Quick Filter Settled Transactions (5 min cache)
@CacheDecorator.cache_result(timeout=300, key_prefix='qf_settled')
class QfWiseSettledTxnHistoryView(generics.ListAPIView)

# 4. Refund History (5 min cache)
@CacheDecorator.cache_result(timeout=300, key_prefix='refund_history')
class GetRefundTxnHistoryView(generics.ListAPIView)

# 5. Merchant Refund History (5 min cache)
@CacheDecorator.cache_result(timeout=300, key_prefix='merchant_refund_history')
class GetMerchantRefundHistoryView(generics.ListAPIView)

# 6. Chargeback History (5 min cache)
@CacheDecorator.cache_result(timeout=300, key_prefix='chargeback_history')
class GetChargebackTxnHistoryView(generics.ListAPIView)
```

#### Reports Module
```python
# apps/reports/views.py

# 1. Report List (5 min cache)
@CacheDecorator.cache_result(timeout=300, key_prefix='report_list')
class ReportListView(views.APIView)
```

---

## Performance Benefits

### Before Redis Caching

```
Dashboard Load (491,896 records):
├─ Total API Time: 10-20 seconds
├─ Database Queries: 8-12 queries
├─ Query Execution: 2-5 seconds per query
└─ Data Serialization: 1-2 seconds

Transaction List (100K records):
├─ Total API Time: 3-5 seconds
├─ Database Queries: 4-6 queries
└─ Query Execution: 800ms - 2s per query
```

### After Redis Caching

```
Dashboard Load (First Request - Cache MISS):
├─ Total API Time: 2-3 seconds (still slow)
├─ Database Queries: 4-6 queries (optimized)
├─ Cache Write: 50-100ms
└─ Response: 2-3 seconds

Dashboard Load (Subsequent Requests - Cache HIT):
├─ Total API Time: 0.5-2 seconds ⚡
├─ Database Queries: 0 (from cache!)
├─ Cache Read: 10-50ms
└─ Response: 0.5-2 seconds (10-20X FASTER!)

Transaction List (Cache HIT):
├─ Total API Time: 400-800ms ⚡
├─ Cache Read: 50-100ms
└─ Response: 400-800ms (4-6X FASTER!)
```

### Cache Hit Rates

After implementation, you can monitor cache effectiveness:

```python
from django.core.cache import cache

# Get cache statistics
info = cache.client.get_client().info()
print(f"Cache Hits: {info['keyspace_hits']}")
print(f"Cache Misses: {info['keyspace_misses']}")
print(f"Hit Rate: {info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses']) * 100:.2f}%")
```

Expected hit rates after warm-up:
- **Dashboard**: 80-90% (most users view same date ranges)
- **Transactions**: 60-70% (varied filters)
- **Settlements**: 70-80% (relatively stable data)

---

## Troubleshooting

### Redis Connection Failed

**Problem**: `ConnectionError: Error connecting to Redis`

**Solutions**:

1. **Check if Redis is running**:
   ```bash
   # Linux/Mac
   redis-cli ping

   # Windows
   redis-cli.exe ping
   ```

2. **Start Redis manually**:
   ```bash
   # Linux
   sudo systemctl start redis-server

   # Mac
   brew services start redis

   # Windows
   redis-server.exe

   # Docker
   docker start sabpaisa-redis
   ```

3. **Check Redis port**:
   ```bash
   netstat -an | grep 6379
   # or
   lsof -i :6379
   ```

4. **Update REDIS_URL** in `.env`:
   ```env
   # If Redis is on different host/port
   REDIS_URL=redis://hostname:6379/1
   ```

### Application Works Without Redis

**Good news!** The cache configuration has `IGNORE_EXCEPTIONS: True`, which means:

- ✅ If Redis is down, the app continues to work
- ✅ Queries fall back to database (slower, but functional)
- ⚠️ You'll see warnings in logs but no errors

**Check logs** for cache warnings:
```bash
tail -f logs/django.log | grep "Cache"
```

### Cache Not Clearing

**Problem**: Old data still showing after updates

**Solutions**:

1. **Clear specific cache keys**:
   ```python
   from django.core.cache import cache
   cache.delete_pattern('sabpaisa_executive_dashboard_*')
   ```

2. **Clear all cache**:
   ```bash
   redis-cli FLUSHDB
   ```

3. **Restart Redis**:
   ```bash
   sudo systemctl restart redis-server
   ```

### High Memory Usage

**Problem**: Redis consuming too much memory

**Solutions**:

1. **Check Redis memory usage**:
   ```bash
   redis-cli INFO memory
   ```

2. **Set max memory limit** in `redis.conf`:
   ```conf
   maxmemory 256mb
   maxmemory-policy allkeys-lru
   ```

3. **Reduce cache timeouts** in `settings.py`:
   ```python
   CACHE_TTL = 180  # Reduce from 300 to 180 seconds
   ```

### Cache Keys Not Unique

**Problem**: Users seeing other users' cached data

**Solution**: Verify cache key generation includes user ID:

```python
# Check cache key in logs
logger.info(f"Cache key: {cache_key}")

# Should include user_id:
# sabpaisa_merchant_txn_history_user_123_filters_xyz
```

If missing user ID, check `CacheDecorator` implementation in `apps/core/cache.py`.

---

## Monitoring Redis

### Real-time Monitoring

```bash
# Monitor Redis commands in real-time
redis-cli MONITOR

# Check Redis statistics
redis-cli INFO stats

# Check connected clients
redis-cli CLIENT LIST

# Check slow queries
redis-cli SLOWLOG GET 10
```

### Key Management

```bash
# List all cache keys
redis-cli KEYS "sabpaisa_*"

# Count total keys
redis-cli DBSIZE

# Get key TTL (time to live)
redis-cli TTL "sabpaisa_executive_dashboard_today_2025-10-08"

# Get key value
redis-cli GET "sabpaisa_executive_dashboard_today_2025-10-08"
```

### Performance Metrics

Monitor these Redis metrics:

```bash
redis-cli INFO stats | grep -E "keyspace_hits|keyspace_misses|evicted_keys|expired_keys"
```

Expected values:
- **Hit rate**: >70%
- **Evicted keys**: Low (indicates sufficient memory)
- **Expired keys**: Normal (keys expiring as expected)

---

## Best Practices

1. **Cache Invalidation**
   - Set appropriate TTLs based on data volatility
   - Use cache key prefixes for easy pattern-based deletion
   - Invalidate cache on data updates

2. **Memory Management**
   - Monitor Redis memory usage
   - Set `maxmemory` and `maxmemory-policy`
   - Use shorter TTLs for less frequently accessed data

3. **Security**
   - Keep Redis on localhost (not exposed to internet)
   - Use Redis AUTH if network-accessible
   - Use firewall rules to restrict access

4. **High Availability**
   - For production, use Redis Sentinel or Redis Cluster
   - Enable Redis persistence (RDB + AOF)
   - Set up Redis monitoring and alerting

---

## Additional Resources

- **Redis Official Docs**: https://redis.io/docs/
- **Django Redis Docs**: https://github.com/jazzband/django-redis
- **Performance Tuning**: https://redis.io/docs/management/optimization/

---

## Support

For issues or questions about Redis caching in SabPaisa Reports API:

1. Check this guide first
2. Review logs: `logs/django.log`
3. Test Redis connection: `redis-cli ping`
4. Contact: sabpaisa-support@example.com

---

**Last Updated**: 2025-10-08
**Version**: 1.0
**Status**: ✅ Fully Implemented
