# Quick Testing Guide
## Feature Enhancements Verification

**Purpose**: Quick reference for testing the 7 new feature enhancements

---

## 🚀 Quick Start

### 1. Start the Server
```bash
cd /path/to/sabpaisa-reports-api
python manage.py runserver
```

### 2. Get Admin Token
```bash
curl -X POST http://13.127.244.103:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@sabpaisa.in",
    "password": "your_password"
  }'
```

Save the token for subsequent requests.

---

## ✅ Test Existing APIs (Verify Nothing Broke)

### Critical Test: Verify Response Bodies Unchanged

**Test 1: Login API**
```bash
curl -X POST http://13.127.244.103:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "test123"}'
```
✅ **Expected**: Response body structure **identical** to before
✅ **New**: Headers `X-Request-ID`, `X-Response-Time`, `X-Performance` added

---

**Test 2: Transactions List**
```bash
curl -X GET http://13.127.244.103:8000/api/v1/transactions/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```
✅ **Expected**: Response body structure **identical** to before
✅ **New**: Headers added (see Test 1)

---

**Test 3: Settlements List**
```bash
curl -X GET http://13.127.244.103:8000/api/v1/settlements/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```
✅ **Expected**: Response body structure **identical** to before
✅ **New**: Headers added

---

**Test 4: Analytics Dashboard**
```bash
curl -X GET http://13.127.244.103:8000/api/v1/analytics/dashboard/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```
✅ **Expected**: Response body structure **identical** to before
✅ **New**: Headers added

---

**Test 5: Reports List**
```bash
curl -X GET http://13.127.244.103:8000/api/v1/reports/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```
✅ **Expected**: Response body structure **identical** to before
✅ **New**: Headers added

---

## 🆕 Test New System Endpoints

### New Endpoint 1: Health Check (Public)
```bash
curl -X GET http://13.127.244.103:8000/api/v1/system/health/
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T...",
  "version": "1.0.0",
  "services": {
    "database_default": {"status": "healthy", "response_time_ms": 12.45},
    "database_legacy": {"status": "healthy", "response_time_ms": 15.23},
    "database_user_management": {"status": "healthy", "response_time_ms": 11.87},
    "database_qwikforms_db": {"status": "healthy", "response_time_ms": 13.56},
    "redis_cache": {"status": "healthy", "response_time_ms": 2.34, "memory_used": "45.2M"}
  },
  "system": {
    "cpu_percent": 23.5,
    "memory_percent": 45.2,
    "disk_percent": 67.8
  }
}
```

---

### New Endpoint 2: System Metrics (Admin Only)
```bash
curl -X GET http://13.127.244.103:8000/api/v1/system/metrics/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Expected Response**:
```json
{
  "success": true,
  "timestamp": "2025-10-14T...",
  "data": {
    "api_stats": {...},
    "transaction_stats": {...},
    "cache_stats": {...},
    "database_stats": {...}
  }
}
```

---

### New Endpoint 3: Database Status (Admin Only)
```bash
curl -X GET http://13.127.244.103:8000/api/v1/system/database/status/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Expected Response**:
```json
{
  "success": true,
  "timestamp": "2025-10-14T...",
  "databases": {
    "default": {"status": "healthy", "response_time_ms": 12.45, "version": "8.0.35", "active_connections": 12},
    "legacy": {...},
    "user_management": {...},
    "qwikforms_db": {...}
  }
}
```

---

### New Endpoint 4: Audit Logs (Admin Only)
```bash
curl -X GET "http://13.127.244.103:8000/api/v1/system/audit-logs/?limit=10" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Expected Response**:
```json
{
  "success": true,
  "count": 10,
  "data": [
    {
      "timestamp": "2025-10-14T...",
      "action": "user_login",
      "user": "admin@sabpaisa.in",
      "ip_address": "192.168.1.100",
      "details": "Successful login"
    }
  ]
}
```

---

## 🔍 Verify New Response Headers

### Check Headers in Any Response
```bash
curl -X GET http://13.127.244.103:8000/api/v1/transactions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -I
```

**Expected Headers**:
```
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Response-Time: 0.087s
X-Performance: excellent
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4987
X-RateLimit-Reset: 1728912600
```

### Header Meanings:
- **X-Request-ID**: Unique identifier for request tracing
- **X-Response-Time**: Time taken to process request
- **X-Performance**: Classification (excellent/good/acceptable/slow)
- **X-RateLimit-Limit**: Max requests allowed per hour
- **X-RateLimit-Remaining**: Requests remaining in current window
- **X-RateLimit-Reset**: Unix timestamp when limit resets

---

## ✅ Verification Checklist

### Pre-Testing
- [ ] Server is running
- [ ] Can access login endpoint
- [ ] Have admin credentials

### Test Existing APIs
- [ ] Login API works (response body unchanged)
- [ ] Transactions API works (response body unchanged)
- [ ] Settlements API works (response body unchanged)
- [ ] Analytics API works (response body unchanged)
- [ ] Reports API works (response body unchanged)

### Test New Headers
- [ ] X-Request-ID present in responses
- [ ] X-Response-Time present in responses
- [ ] X-Performance present in responses
- [ ] X-RateLimit-* headers present in responses

### Test New Endpoints
- [ ] Health check endpoint accessible (no auth)
- [ ] System metrics endpoint works (admin auth)
- [ ] Database status endpoint works (admin auth)
- [ ] Audit logs endpoint works (admin auth)

### Verify Security
- [ ] Metrics endpoint requires admin auth
- [ ] Database status requires admin auth
- [ ] Audit logs requires admin auth
- [ ] Health check is public (no auth required)

---

## 🐛 Troubleshooting

### Issue: "Module not found" error
**Solution**: Install dependencies
```bash
pip install psutil django-redis
```

### Issue: Headers not appearing
**Solution**: Check middleware is enabled in `config/settings.py`
```python
MIDDLEWARE = [
    # ... other middleware ...
    'apps.core.middleware.RequestCorrelationMiddleware',
    'apps.core.middleware.PerformanceHeaderMiddleware',
    'apps.core.middleware.RateLimitHeaderMiddleware',
]
```

### Issue: New endpoints return 404
**Solution**: Check URL configuration in `config/urls.py`
```python
urlpatterns = [
    # ... other patterns ...
    path('api/v1/system/', include('apps.core.urls')),
]
```

### Issue: Database connection error
**Solution**: Check `.env` file has correct database credentials

---

## 📊 Performance Benchmarking

### Test Response Times
```bash
# Run 100 requests and measure average response time
for i in {1..100}; do
  curl -X GET http://13.127.244.103:8000/api/v1/system/health/ -s -o /dev/null -w "%{time_total}\n"
done | awk '{sum+=$1; count++} END {print "Average:", sum/count, "seconds"}'
```

### Expected Performance:
- Health endpoint: 50-100ms
- Metrics endpoint: 100-200ms
- Database status: 50-100ms
- Audit logs: 50-150ms

---

## 🎯 Success Criteria

All tests pass if:
1. ✅ All existing API endpoints return **identical response bodies**
2. ✅ New headers are present in all responses
3. ✅ All 4 new system endpoints are accessible
4. ✅ Admin-only endpoints require authentication
5. ✅ Health endpoint is publicly accessible
6. ✅ No errors in server logs
7. ✅ Performance is acceptable (<200ms for most endpoints)

---

## 📞 Need Help?

If any tests fail:
1. Check server logs: `tail -f logs/sabpaisa_api.log`
2. Check error logs: `tail -f logs/errors.log`
3. Run Django system check: `python manage.py check`
4. Review documentation: `FEATURE_ENHANCEMENTS_DOCUMENTATION.md`

---

**Document Version**: 1.0.0
**Last Updated**: October 14, 2025
