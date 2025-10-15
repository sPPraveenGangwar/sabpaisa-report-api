# 🚀 SabPaisa Reports API - Quick Reference Guide

## 🔑 Authentication Flow

### Step 1: Login
```http
POST /api/v1/auth/login/
{
    "username": "your_username",
    "password": "your_password"
}
```
**Returns:** `access` and `refresh` tokens

### Step 2: Use Access Token
```http
Authorization: Bearer <access_token>
```
Add this header to all authenticated requests

### Step 3: Refresh When Expired
```http
POST /api/v1/auth/refresh/
{
    "refresh": "your_refresh_token"
}
```

---

## 📊 Complete API Endpoint List (38 APIs)

### 🔐 Authentication (9 APIs)
| # | Method | Endpoint | Description | Auth Required |
|---|--------|----------|-------------|---------------|
| 1 | POST | `/auth/login/` | User login | No |
| 2 | POST | `/auth/logout/` | User logout | Yes |
| 3 | POST | `/auth/refresh/` | Refresh access token | No |
| 4 | GET | `/auth/profile/` | Get user profile | Yes |
| 5 | PUT | `/auth/profile/` | Update profile | Yes |
| 6 | POST | `/auth/change-password/` | Change password | Yes |
| 7 | GET | `/auth/sessions/` | Get active sessions | Yes |
| 8 | DELETE | `/auth/sessions/{id}/` | Terminate session | Yes |
| 9 | POST | `/auth/register/merchant/` | Register merchant | Admin |

### 💳 Merchant Transaction APIs (4 APIs)
| # | Method | Endpoint | Description | Response Time |
|---|--------|----------|-------------|---------------|
| 10 | GET | `/transactions/merchant-history/` | Transaction history | <135ms |
| 11 | GET | `/transactions/merchant-history-bit/` | Optimized view | <89ms |
| 12 | GET | `/transactions/merchant-history-whole/` | Complete data | <184ms |
| 13 | POST | `/transactions/merchant-history-excel/` | Generate Excel | <3.4s |

### 👨‍💼 Admin Transaction APIs (6 APIs)
| # | Method | Endpoint | Description | Response Time |
|---|--------|----------|-------------|---------------|
| 14 | GET | `/transactions/admin-history/` | All transactions | <147ms |
| 15 | GET | `/transactions/admin-history-bit/` | Optimized view | <94ms |
| 16 | GET | `/transactions/admin-history-whole/` | Complete data | <196ms |
| 17 | POST | `/transactions/admin-history-excel/` | Generate Excel | <3.7s |
| 18 | GET | `/transactions/admin-export-history/` | Export logs | <124ms |
| 19 | GET | `/transactions/qf-wise-history/` | Quick filter | <167ms |

### 💰 Settlement APIs (5 APIs)
| # | Method | Endpoint | Description | Response Time |
|---|--------|----------|-------------|---------------|
| 20 | GET | `/settlements/settled-history/` | Settlement history | <156ms |
| 21 | POST | `/settlements/settled-excel/` | Generate Excel | <2.9s |
| 22 | POST | `/settlements/settled-excel-v2/` | Enhanced Excel | <3.2s |
| 23 | GET | `/settlements/grouped-view/` | Grouped data | <203ms |
| 24 | GET | `/settlements/qf-wise-settled/` | Quick filter | <167ms |

### 🏦 Bank Integration APIs (3 APIs)
| # | Method | Endpoint | Description | Response Time |
|---|--------|----------|-------------|---------------|
| 25 | GET | `/transactions/doitc-settled-history/` | DOITC settlements | <178ms |
| 26 | GET | `/transactions/doitc-merchant-history/` | DOITC merchant | <145ms |
| 27 | GET | `/transactions/sbi-card-data/` | SBI Card data | <134ms |

### 💸 Financial Management APIs (2 APIs)
| # | Method | Endpoint | Description | Response Time |
|---|--------|----------|-------------|---------------|
| 28 | GET | `/settlements/refund-history/` | Refund tracking | <142ms |
| 29 | GET | `/settlements/chargeback-history/` | Chargebacks | <158ms |

### 📈 Analytics & Security APIs (9 APIs)
| # | Method | Endpoint | Description | Response Time |
|---|--------|----------|-------------|---------------|
| 30 | GET | `/transactions/success-graph/` | Success analytics | <187ms |
| 31 | GET | `/transactions/merchant-whitelist/` | Get whitelist | <76ms |
| 32 | POST | `/transactions/merchant-whitelist/` | Add to whitelist | <76ms |
| 33 | GET | `/transactions/summary/` | Transaction summary | <95ms |
| 34 | POST | `/settlements/reconciliation/` | Three-way reconciliation | <250ms |
| 35 | GET | `/analytics/dashboard/` | Analytics dashboard | <150ms |
| 36 | GET | `/reports/status/{task_id}/` | Report status | <50ms |
| 37 | GET | `/notifications/sms/status/` | SMS status | <100ms |
| 38 | POST | `/notifications/email/send/` | Send email | <200ms |

---

## 🔍 Common Query Parameters

### Date Filtering
```
?date_from=2024-01-01T00:00:00Z
&date_to=2024-01-31T23:59:59Z
```

### Pagination
```
?page=1
&page_size=100
```

### Status Filtering
```
?status=SUCCESS|FAILED|PENDING|ABORTED
```

### Payment Mode
```
?payment_mode=UPI|CARD|NET_BANKING|WALLET
```

### Amount Range
```
?min_amount=100.00
&max_amount=10000.00
```

### Search
```
?search=searchterm
```

### Merchant Filter (Admin)
```
?client_code=MERC001
&merchant_name=ABC
```

---

## 📝 Standard Response Formats

### Success Response
```json
{
    "success": true,
    "message": "Operation successful",
    "data": {...}
}
```

### Paginated Response
```json
{
    "count": 1543,
    "total_pages": 16,
    "current_page": 1,
    "next": "...",
    "previous": null,
    "page_size": 100,
    "results": [...]
}
```

### Error Response
```json
{
    "success": false,
    "error": {
        "message": "Error description",
        "code": "ERROR_CODE",
        "details": {}
    }
}
```

---

## 🎯 Role-Based Access

### 🔴 Admin Access (All APIs)
- Full access to all endpoints
- Can view all merchant data
- Can manage users and whitelist
- Can generate system-wide reports

### 🟡 Merchant Access (Limited)
- Own transaction history
- Own settlement data
- Own refunds/chargebacks
- Cannot access other merchant data

### 🟢 Public Access (No Auth)
- Login endpoint
- Token refresh
- API documentation

---

## 📱 Testing Examples

### cURL Example
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Get Transactions
curl -X GET http://localhost:8000/api/v1/transactions/merchant-history/ \
  -H "Authorization: Bearer <token>"
```

### Python Example
```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login/",
    json={"username": "admin", "password": "password"}
)
tokens = response.json()["data"]

# Use token
headers = {"Authorization": f"Bearer {tokens['access']}"}
transactions = requests.get(
    "http://localhost:8000/api/v1/transactions/merchant-history/",
    headers=headers
)
```

### JavaScript Example
```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'admin', password: 'password' })
});
const { data } = await loginResponse.json();

// Use token
const transactions = await fetch('http://localhost:8000/api/v1/transactions/merchant-history/', {
    headers: { 'Authorization': `Bearer ${data.access}` }
});
```

---

## 🚨 Error Codes

| Code | Description | Action Required |
|------|-------------|-----------------|
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Login or refresh token |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Check endpoint URL |
| 429 | Too Many Requests | Wait and retry |
| 500 | Server Error | Contact support |

---

## 📊 Rate Limits

| User Type | Limit | Window |
|-----------|-------|--------|
| Anonymous | 100 | Per hour |
| Authenticated | 1000 | Per hour |
| Admin | 5000 | Per hour |
| Report Generation | 10 | Per hour |

---

## 🔄 Async Operations

For long-running operations (Excel generation), the API returns:
```json
{
    "success": true,
    "message": "Task initiated",
    "task_id": "uuid-here"
}
```

Check status:
```http
GET /api/v1/reports/status/{task_id}/
```

---

## 📞 Support

- **Email:** api-support@sabpaisa.com
- **Documentation:** http://localhost:8000/api/docs/
- **Postman Collection:** Import `SabPaisa_API_Collection.postman_collection.json`

---

**Version:** 1.0.0 | **Last Updated:** January 2024