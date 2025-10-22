# SabPaisa Reports API - Complete Final Documentation v1.0

## Overview
This document provides comprehensive documentation for all implemented APIs in the SabPaisa Reports system. The APIs are organized into modules for Authentication, Transactions, Settlements, Analytics, and Report Generation.

---

## Table of Contents
1. [Authentication APIs](#authentication-apis)
2. [Transaction APIs](#transaction-apis)
3. [Settlement APIs](#settlement-apis)
4. [Analytics APIs](#analytics-apis)
5. [Report Generation APIs](#report-generation-apis)
6. [Additional Endpoints](#additional-endpoints)
7. [Common Parameters & Error Responses](#common-parameters--error-responses)

---

## Authentication APIs

### 1. User Login
**Endpoint:** `POST /api/v1/auth/login/`
**Description:** Authenticate user and receive JWT access and refresh tokens
**Authentication:** None (Public endpoint)

**Request Body:**
```json
{
    "username": "admin@sabpaisa.com",
    "password": "SecurePass@123"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    },
    "user": {
        "id": 1,
        "username": "admin@sabpaisa.com",
        "email": "admin@sabpaisa.com",
        "role": "ADMIN",
        "client_code": null,
        "is_active": true,
        "last_login": "2024-12-27T14:30:00+05:30"
    }
}
```

### 2. Token Refresh
**Endpoint:** `POST /api/v1/auth/token/refresh/`
**Description:** Generate new access token using refresh token
**Authentication:** None

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. User Logout
**Endpoint:** `POST /api/v1/auth/logout/`
**Description:** Blacklist refresh token to prevent reuse
**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Logout successful"
}
```

### 4. Change Password
**Endpoint:** `POST /api/v1/auth/change-password/`
**Description:** Update user password
**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "old_password": "CurrentPass@123",
    "new_password": "NewSecurePass@456"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Password changed successfully"
}
```

---

## Transaction APIs

### 1. Get Merchant Transaction History
**Endpoint:** `GET /api/v1/transactions/merchant-history/`
**Description:** Retrieve paginated transaction history for authenticated merchant
**Headers:** `Authorization: Bearer <access_token>`
**Permission:** Merchant role required
**Response Time:** <450ms P95

**Query Parameters:**
- `date_filter`: `today`, `3days`, `week`, `month`, `year`, `custom`
- `date_from`, `date_to`: For custom date range (YYYY-MM-DD)
- `payment_mode`: `UPI`, `CC`, `DC`, `NB`, `ALL` (comma-separated)
- `status`: `SUCCESS`, `FAILED`, `PENDING` (comma-separated)
- `min_amount`, `max_amount`: Amount range filter
- `page`, `page_size`: Pagination (default: page=1, page_size=50)

**Example Request:**
```
GET /api/v1/transactions/merchant-history/?date_filter=month&payment_mode=UPI,CC&status=SUCCESS&page=1
```

**Response (200 OK):**
```json
{
    "success": true,
    "filter_summary": "Current month | Payment mode: UPI,CC | Status: SUCCESS",
    "count": 2847,
    "next": "http://api.sabpaisa.com/api/v1/transactions/merchant-history/?page=2",
    "previous": null,
    "results": [
        {
            "txn_id": "SP202412270001",
            "client_txn_id": "MERC001_TXN_98765",
            "client_code": "MERC001",
            "client_name": "ABC Merchants Pvt Ltd",
            "trans_date": "2024-12-27T14:30:00+05:30",
            "trans_complete_date": "2024-12-27T14:30:45+05:30",
            "status": "SUCCESS",
            "payment_mode": "UPI",
            "paid_amount": 2500.00,
            "payee_email": "john.doe@example.com",
            "payee_mob": "9876543210",
            "bank_txn_id": "HDFC2024122798765",
            "is_settled": true,
            "settlement_date": "2024-12-28",
            "settlement_amount": 2475.00
        }
    ]
}
```

### 2. Get Admin Transaction History
**Endpoint:** `GET /api/v1/transactions/admin-history/`
**Description:** Retrieve all transactions across all merchants
**Headers:** `Authorization: Bearer <admin_token>`
**Permission:** Admin role required
**Response Time:** <547ms P95

**Additional Query Parameters:**
- `merchant_code`: Filter by specific merchant(s) (comma-separated)
- `client_name`: Partial merchant name search
- `order_by`: Sort field (`trans_date`, `-paid_amount`, etc.)

### 3. Transaction Search by ID
**Endpoint:** `GET /api/v1/transactions/search/`
**Description:** Search for specific transaction by ID
**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `txn_id`: SabPaisa transaction ID (e.g., SP202412270001)
- `client_txn_id`: Client's transaction reference

### 4. Transaction Summary
**Endpoint:** `GET /api/v1/transactions/summary/`
**Description:** Get aggregated transaction statistics
**Headers:** `Authorization: Bearer <access_token>`

### 5. Merchant Transaction History (Bit)
**Endpoint:** `GET /api/v1/transactions/merchant-history-bit/`
**Description:** Lightweight version with limited fields
**Headers:** `Authorization: Bearer <access_token>`

### 6. Merchant Transaction History (Whole)
**Endpoint:** `GET /api/v1/transactions/merchant-history-whole/`
**Description:** Complete transaction details with all fields
**Headers:** `Authorization: Bearer <access_token>`

### 7. Generate Transaction Excel
**Endpoint:** `POST /api/v1/transactions/merchant-history-excel/`
**Description:** Generate Excel report of transactions
**Headers:** `Authorization: Bearer <access_token>`
**Throttle:** 5 requests per 5 minutes

### 8. Admin Transaction Excel
**Endpoint:** `POST /api/v1/transactions/admin-history-excel/`
**Description:** Generate Excel report for all merchants
**Headers:** `Authorization: Bearer <admin_token>`
**Permission:** Admin role required

### 9. Admin Transaction Export History
**Endpoint:** `GET /api/v1/transactions/admin-export-history/`
**Description:** Track admin export activities
**Permission:** Admin role required

### 10. QF Wise Transaction History
**Endpoint:** `GET /api/v1/transactions/qf-wise-history/`
**Description:** Query-filter based transaction history
**Headers:** `Authorization: Bearer <access_token>`

### 11. DOITC Settled Transaction History
**Endpoint:** `GET /api/v1/transactions/doitc-settled-history/`
**Description:** Department of IT specific settled transactions
**Headers:** `Authorization: Bearer <access_token>`

### 12. DOITC Merchant Transaction History
**Endpoint:** `GET /api/v1/transactions/doitc-merchant-history/`
**Description:** Department of IT merchant-specific transactions
**Headers:** `Authorization: Bearer <access_token>`

### 13. SBI Card Data
**Endpoint:** `GET /api/v1/transactions/sbi-card-data/`
**Description:** SBI card transaction data
**Headers:** `Authorization: Bearer <access_token>`

### 14. Success Graph Data
**Endpoint:** `GET /api/v1/transactions/success-graph/`
**Description:** Transaction success rate visualization data
**Headers:** `Authorization: Bearer <access_token>`

### 15. Merchant Whitelist
**Endpoint:** `GET /api/v1/transactions/merchant-whitelist/`
**Description:** Get whitelisted merchants
**Headers:** `Authorization: Bearer <access_token>`

---

## Settlement APIs

### 1. Get Settled Transaction History
**Endpoint:** `GET /api/v1/settlements/settled-history/`
**Description:** Retrieve settled transactions
**Headers:** `Authorization: Bearer <access_token>`
**Response Time:** <156ms P95

**Query Parameters:**
- `use_settlement_date`: Use settlement date instead of transaction date
- `settlement_status`: `COMPLETED`, `PENDING`, `PROCESSING`
- All common transaction filters apply

### 2. Get Refund Transaction History
**Endpoint:** `GET /api/v1/settlements/refund-history/`
**Description:** Retrieve all refund transactions
**Headers:** `Authorization: Bearer <access_token>`
**Response Time:** <142ms P95

**Query Parameters:**
- `refund_status`: Refund status filter
- `refund_message`: Search in refund messages
- `refund_date`: Specific refund date
- `refund_status_code`: Exact status code
- `refund_request_from`: Username who initiated refund
- `refund_reason`: Reason for refund
- `refunded_amount`: Exact refunded amount
- `refund_track_id`: Refund tracking ID
- `use_refund_date`: Use refund date for filtering

### 3. Get Merchant Refund History
**Endpoint:** `GET /api/v1/settlements/merchant-refund-history/`
**Description:** Merchant-specific refund transactions
**Headers:** `Authorization: Bearer <access_token>`
**Permission:** Merchant role required
**Response Time:** <150ms P95

### 4. Get Chargeback Transaction History
**Endpoint:** `GET /api/v1/settlements/chargeback-history/`
**Description:** Retrieve chargeback transactions
**Headers:** `Authorization: Bearer <access_token>`
**Response Time:** <158ms P95

**Query Parameters:**
- `chargeback_status`: `DISPUTED`, `RESOLVED`, `PENDING`
- `chargeback_reason`: Reason for chargeback
- `use_chargeback_date`: Use chargeback date for filtering
- `min_chargeback_amount`, `max_chargeback_amount`: Amount range

### 5. Grouped Settlement View
**Endpoint:** `GET /api/v1/settlements/grouped-view/`
**Description:** Aggregated settlement data
**Headers:** `Authorization: Bearer <access_token>`
**Response Time:** <203ms P95

**Query Parameters:**
- `group_by`: `date`, `merchant`, `status`

### 6. QF Wise Settled Transactions
**Endpoint:** `GET /api/v1/settlements/qf-wise-settled/`
**Description:** Query-filter based settled transactions
**Headers:** `Authorization: Bearer <access_token>`
**Response Time:** <167ms P95

### 7. Generate Settlement Excel
**Endpoint:** `POST /api/v1/settlements/settled-excel/`
**Description:** Generate basic settlement Excel report
**Headers:** `Authorization: Bearer <access_token>`
**Throttle:** ReportGenerationThrottle

### 8. Generate Settlement Excel V2
**Endpoint:** `POST /api/v1/settlements/settled-excel-v2/`
**Description:** Enhanced settlement Excel with charts
**Headers:** `Authorization: Bearer <access_token>`
**Response Time:** <3.2s

### 9. Three-Way Reconciliation
**Endpoint:** `POST /api/v1/settlements/reconciliation/`
**Description:** Perform three-way reconciliation
**Headers:** `Authorization: Bearer <admin_token>`
**Permission:** Admin role required

---

## Analytics APIs

### 1. Merchant Analytics Dashboard
**Endpoint:** `GET /api/v1/analytics/merchant-analytics/`
**Description:** Comprehensive merchant performance analytics
**Headers:** `Authorization: Bearer <access_token>`
**Cache:** 30 minutes

**Response includes:**
- KPIs: Total transactions, success rate, volume, settlement metrics
- Payment mode distribution
- Daily/hourly trends
- Top customers

### 2. Payment Mode Analytics
**Endpoint:** `GET /api/v1/analytics/payment-mode-analytics/`
**Description:** Analytics specific to payment methods
**Headers:** `Authorization: Bearer <access_token>`

### 3. Settlement Analytics
**Endpoint:** `GET /api/v1/analytics/settlement-analytics/`
**Description:** Settlement performance and TAT analysis
**Headers:** `Authorization: Bearer <access_token>`

### 4. Refund & Chargeback Analytics
**Endpoint:** `GET /api/v1/analytics/refund-chargeback/`
**Description:** Refund and chargeback trend analysis
**Headers:** `Authorization: Bearer <access_token>`

### 5. Executive Dashboard (Admin Only)
**Endpoint:** `GET /api/v1/analytics/executive-dashboard/`
**Description:** High-level executive metrics
**Headers:** `Authorization: Bearer <admin_token>`
**Permission:** Admin role required
**Cache:** 10 minutes

### 6. Comparative Analytics (Admin Only)
**Endpoint:** `GET /api/v1/analytics/comparative/`
**Description:** Compare periods or merchants
**Headers:** `Authorization: Bearer <admin_token>`
**Permission:** Admin role required

**Query Parameters:**
- `type`: `period` or `merchant`
- For period: `current_days` (e.g., 30)
- For merchant: `merchant_codes` (comma-separated), `days`

---

## Report Generation APIs

### 1. Generate Report
**Endpoint:** `POST /api/v1/reports/generate/`
**Description:** Initiate asynchronous report generation
**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "report_type": "transaction|settlement|refund|chargeback|merchant|analytics",
    "format": "excel|csv|pdf|json",
    "date_filter": "month",
    "payment_mode": "ALL",
    "status": "SUCCESS",
    "merchant_code": "MERC001",
    "include_summary": true,
    "include_charts": true,
    "max_records": 50000
}
```

**Response (202 Accepted):**
```json
{
    "success": true,
    "message": "Report generation initiated",
    "task_id": "task_20241227_160000_a1b2c3d4",
    "report_type": "transaction",
    "format": "excel",
    "estimated_time": "5-10 seconds for 50K records"
}
```

### 2. Check Report Status
**Endpoint:** `GET /api/v1/reports/status/<task_id>/`
**Description:** Check report generation progress
**Headers:** `Authorization: Bearer <access_token>`

### 3. Download Report
**Endpoint:** `GET /api/v1/reports/download/<task_id>/`
**Description:** Download generated report file
**Headers:** `Authorization: Bearer <access_token>`

### 4. List Generated Reports
**Endpoint:** `GET /api/v1/reports/list/`
**Description:** List user's generated reports
**Headers:** `Authorization: Bearer <access_token>`

---

## Common Parameters & Error Responses

### Date Filter Options
- `today`: Current day only
- `3days`: Last 3 days
- `week`: Last 7 days
- `month`: Current month
- `quarter`: Current quarter
- `year`: Current year
- `custom`: Use with `date_from` and `date_to`

### Pagination
- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 50, max: 200)

### Sorting
- `order_by`: Field name, prefix with `-` for descending

### Standard Error Responses

**400 Bad Request:**
```json
{
    "success": false,
    "message": "Invalid filter parameters",
    "errors": {
        "field_name": "Error description"
    }
}
```

**401 Unauthorized:**
```json
{
    "success": false,
    "message": "Authentication credentials were not provided",
    "code": "not_authenticated"
}
```

**403 Forbidden:**
```json
{
    "success": false,
    "message": "You do not have permission to perform this action",
    "code": "permission_denied"
}
```

**404 Not Found:**
```json
{
    "success": false,
    "message": "Resource not found",
    "code": "not_found"
}
```

**429 Too Many Requests:**
```json
{
    "success": false,
    "message": "Request limit exceeded",
    "retry_after": 60
}
```

**500 Internal Server Error:**
```json
{
    "success": false,
    "message": "An unexpected error occurred",
    "error_id": "ERR_20241227_143000"
}
```

---

## Rate Limiting

| Endpoint Type | Rate Limit | Window |
|--------------|------------|--------|
| Authentication | 5 requests | 1 minute |
| Transaction Search | 100 requests | 1 minute |
| Analytics | 30 requests | 1 minute |
| Report Generation | 10 requests | 5 minutes |
| Excel/CSV Export | 5 requests | 5 minutes |

---

## Important Notes

1. **Authentication:** All endpoints except login/refresh require Bearer token
2. **Timezone:** All datetime values in ISO 8601 with timezone (IST +05:30)
3. **Currency:** All amounts in INR (Indian Rupees)
4. **Performance:** Response times are P95 (95th percentile)
5. **File Storage:** Generated reports available for 24 hours
6. **Token Expiry:** Access token: 24 hours, Refresh token: 7 days
7. **HTTPS:** Required for all production endpoints
8. **API Version:** Current version is v1
9. **Database:** Uses multiple MySQL databases
10. **Field Availability:** Some fields may return null due to database schema variations

---

## Contact & Support

For API support and issues:
- Email: api-support@sabpaisa.com
- Documentation: https://api.sabpaisa.com/docs
- Status Page: https://status.sabpaisa.com

---

**Document Version:** 1.0
**Last Updated:** December 2024
**API Version:** v1