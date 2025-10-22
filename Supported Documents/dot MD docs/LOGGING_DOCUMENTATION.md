# Logging Documentation - SabPaisa Reports API

## Overview
Comprehensive logging has been implemented across all modules for better tracking, debugging, and security monitoring.

## Log Files Structure

```
logs/
├── sabpaisa_api.log          # General application logs
├── errors.log                 # Error logs only
├── transactions.log           # Transaction-specific logs
├── security.log              # Security events and authentication logs
└── performance.log           # Performance metrics and slow queries
```

## Logger Configuration

### Available Loggers

1. **Application Loggers**
   - `apps.authentication` - Authentication and login events
   - `apps.transactions` - Transaction processing logs
   - `apps.settlements` - Settlement operations
   - `apps.analytics` - Analytics and reporting
   - `apps.reports` - Report generation
   - `apps.core.middleware` - Request/response middleware

2. **Specialized Loggers**
   - `security` - Security events (login attempts, password changes)
   - `performance` - Performance metrics and slow operations
   - `django.db.backends` - Database queries

## Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages (slow queries, failed attempts)
- **ERROR**: Error messages with stack traces
- **CRITICAL**: Critical system failures

## Log Format

### Standard Format
```
[LEVEL] YYYY-MM-DD HH:MM:SS | module.name | function() | Line: XXX | Message
```

### Example Logs

#### Successful Login
```
[INFO] 2024-12-27 14:30:00 | apps.authentication | post() | Line: 123 | Login successful | User: admin@sabpaisa.com | IP: 192.168.1.100
[INFO] 2024-12-27 14:30:00 | security | post() | Line: 124 | LOGIN_SUCCESS | User: admin@sabpaisa.com | IP: 192.168.1.100 | Role: ADMIN
```

#### Failed Login
```
[WARNING] 2024-12-27 14:31:00 | apps.authentication | post() | Line: 150 | Login failed - invalid credentials | User: unknown@test.com | IP: 192.168.1.100
[WARNING] 2024-12-27 14:31:00 | security | post() | Line: 151 | LOGIN_FAILED | User: unknown@test.com | IP: 192.168.1.100 | Reason: Invalid credentials
```

#### Transaction Search
```
[INFO] 2024-12-27 14:32:00 | apps.transactions | list() | Line: 200 | Transaction history request | User: merchant01 | IP: 192.168.1.101 | Filters: {'date_filter': 'month', 'status': 'SUCCESS'}
[INFO] 2024-12-27 14:32:01 | apps.transactions | apply_filters() | Line: 250 | Filter applied | Initial: 50000 | Final: 1234 | Filters: Date: month | Status: SUCCESS
[INFO] 2024-12-27 14:32:01 | performance | list() | Line: 280 | Transaction history API | User: merchant01 | Records: 1234 | Response time: 0.456s
```

#### Slow Query Warning
```
[WARNING] 2024-12-27 14:33:00 | performance | process_response() | Line: 89 | SLOW_REQUEST | Method: GET | Path: /api/v1/transactions/admin-history/ | Duration: 2.345s | Threshold: 0.150s | User: admin | IP: 192.168.1.100
```

#### Error with Stack Trace
```
[ERROR] 2024-12-27 14:34:00 | apps.transactions | list() | Line: 300 | Database Error | User: merchant01 | IP: 192.168.1.101 | Error: OperationalError: (1054, "Unknown column 'bank_message1' in 'field list'")
[DEBUG] 2024-12-27 14:34:00 | apps.transactions | list() | Line: 301 | Traceback:
  File "/app/views.py", line 300, in list
    queryset = self.get_queryset()
  ...
```

## Security Events Logging

### Events Tracked
- Login attempts (success/failure)
- Logout events
- Password changes
- Rate limit violations
- Suspicious activity
- Invalid token attempts
- Permission violations

### Security Log Format
```
SECURITY_EVENT | Type: <EVENT_TYPE> | User: <username> | IP: <ip_address> | Details
```

### Examples
```
LOGIN_SUCCESS | User: admin@sabpaisa.com | IP: 192.168.1.100 | Role: ADMIN
LOGIN_FAILED | User: unknown | IP: 192.168.1.100 | Reason: Invalid credentials
PASSWORD_CHANGED | User: merchant01 | IP: 192.168.1.101
RATE_LIMIT_EXCEEDED | IP: 192.168.1.102 | User: Anonymous | Path: /api/v1/auth/login/ | Count: 10001
```

## Performance Monitoring

### Metrics Tracked
- API response times
- Database query times
- Slow request detection (>150ms)
- Report generation times
- Cache hit/miss rates

### Performance Log Examples
```
[INFO] API Performance | Action: Get Transaction History | User: merchant01 | Time: 0.234s | Status: 200
[WARNING] Slow query | Type: transaction_filter | Time: 0.567s
[INFO] Report generation | Type: Excel | Records: 25000 | Time: 3.456s
```

## Using the Logging System

### In Views
```python
from apps.core.logging_utils import LoggingMixin, log_api_call

class MyView(LoggingMixin, APIView):
    @log_api_call(action="Get Transaction Data")
    def get(self, request):
        # Log request
        self.log_request(request, action="Get Transactions")

        try:
            # Your logic here
            data = process_transactions()

            # Log success
            self.logger.info(f"Successfully processed {len(data)} transactions")

            return Response(data)
        except Exception as e:
            # Log error
            self.log_error(e, action="Get Transactions", request=request)
            raise
```

### Direct Logging
```python
import logging

logger = logging.getLogger('apps.transactions')
security_logger = logging.getLogger('security')
performance_logger = logging.getLogger('performance')

# Info log
logger.info(f"Processing transaction: {txn_id}")

# Warning log
logger.warning(f"Transaction retry attempt {retry_count} for {txn_id}")

# Error log with exception
try:
    process_payment()
except Exception as e:
    logger.exception(f"Payment processing failed for {txn_id}")

# Security event
security_logger.warning(f"SUSPICIOUS_ACTIVITY | User: {user} | IP: {ip} | Multiple failed attempts")

# Performance metric
performance_logger.info(f"Batch processing | Records: 1000 | Time: 2.5s")
```

## Log Rotation

Logs are automatically rotated based on size:
- `sabpaisa_api.log`: 15MB, 10 backups
- `errors.log`: 15MB, 10 backups
- `transactions.log`: 50MB, 20 backups
- `security.log`: 10MB, 10 backups
- `performance.log`: 20MB, 5 backups

## Monitoring and Alerts

### Critical Events to Monitor
1. Multiple failed login attempts (potential brute force)
2. Rate limit violations
3. Database connection errors
4. Slow API responses (>1 second)
5. Report generation failures
6. Settlement processing errors

### Log Analysis Commands

#### View recent errors
```bash
tail -f logs/errors.log
```

#### Monitor security events
```bash
tail -f logs/security.log | grep "LOGIN_FAILED"
```

#### Track slow APIs
```bash
grep "SLOW_REQUEST" logs/performance.log | tail -20
```

#### Count failed logins by IP
```bash
grep "LOGIN_FAILED" logs/security.log | awk -F'IP: ' '{print $2}' | awk '{print $1}' | sort | uniq -c | sort -rn
```

#### Find errors for specific user
```bash
grep "User: merchant01" logs/errors.log
```

## Best Practices

1. **Always log user context**: Include username and IP in logs
2. **Sanitize sensitive data**: Never log passwords, tokens, or keys
3. **Use appropriate log levels**: INFO for normal flow, WARNING for issues, ERROR for failures
4. **Include timing metrics**: Log response times for performance tracking
5. **Log both success and failure**: Track both scenarios for complete audit trail
6. **Use structured logging**: Include consistent fields for easier parsing
7. **Add request IDs**: Use unique IDs to track requests across logs

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Logs not appearing
- Check log level in settings.py
- Verify log directory exists and has write permissions
- Check if logger name matches configuration

#### 2. Log files growing too large
- Adjust rotation settings in LOGGING configuration
- Reduce log level from DEBUG to INFO in production
- Archive old logs regularly

#### 3. Performance impact
- Use async logging for high-volume applications
- Adjust log levels per environment
- Use sampling for very high-frequency events

#### 4. Missing context in logs
- Ensure request.user is available
- Add middleware for request ID tracking
- Use LoggingMixin for consistent context

## Security Considerations

1. **Log Storage**: Store logs securely with appropriate permissions
2. **Sensitive Data**: Never log passwords, tokens, or payment details
3. **Log Access**: Restrict log file access to authorized personnel
4. **Log Retention**: Define retention policies based on compliance requirements
5. **Log Shipping**: Use secure methods for centralized logging
6. **Audit Trail**: Maintain immutable audit logs for critical operations

## Integration with Monitoring Tools

The logging system can be integrated with:
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Splunk**: Enterprise log management
- **CloudWatch**: AWS logging service
- **Datadog**: Application monitoring
- **Grafana Loki**: Log aggregation system

## Environment-Specific Configuration

### Development
```python
'level': 'DEBUG',
'handlers': ['console', 'file'],
```

### Staging
```python
'level': 'INFO',
'handlers': ['file', 'error_file'],
```

### Production
```python
'level': 'WARNING',
'handlers': ['file', 'error_file', 'remote'],
```

## Compliance and Audit

The logging system helps meet compliance requirements:
- **PCI DSS**: Transaction and access logging
- **GDPR**: User activity tracking with privacy considerations
- **SOC 2**: Security event monitoring
- **ISO 27001**: Information security management

## Maintenance

### Daily Tasks
- Review error logs for critical issues
- Check security logs for suspicious activity
- Monitor performance logs for degradation

### Weekly Tasks
- Analyze log patterns for optimization opportunities
- Review and archive old logs
- Update monitoring alerts based on trends

### Monthly Tasks
- Generate log analysis reports
- Review and update logging configuration
- Conduct security audit of log access