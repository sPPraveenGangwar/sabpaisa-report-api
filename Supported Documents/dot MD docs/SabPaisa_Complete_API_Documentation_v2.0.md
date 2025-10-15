# SabPaisa Reports API - Complete Documentation v2.0

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL & Headers](#base-url--headers)
4. [Authentication APIs](#authentication-apis)
5. [Transaction APIs](#transaction-apis)
6. [Settlement APIs](#settlement-apis)
7. [Bank Integration APIs](#bank-integration-apis)
8. [Financial Management APIs](#financial-management-apis)
9. [Analytics APIs](#analytics-apis)
10. [Report Generation APIs](#report-generation-apis)
11. [QwikForms APIs](#qwikforms-apis)
12. [Common Parameters Reference](#common-parameters-reference)
13. [Error Handling Guide](#error-handling-guide)
14. [Rate Limiting & Throttling](#rate-limiting--throttling)

---

## Overview

This document provides comprehensive documentation for all implemented APIs in the SabPaisa Reports system. The APIs are organized into modules for Authentication, Transactions, Settlements, Bank Integration, Financial Management, Analytics, and Report Generation.

### Database Information
- **Engine:** MySQL
- **Primary Database:** sabpaisa2_stage_sabpaisa
- **Main Table:** transaction_detail (170+ fields)
- **QwikForms Database:** spQwikForm
- **QwikForms Main Tables:** data_transactions, data_form
- **Implementation Status:** 99% Real Database Integration

### Base URL
```
Development: http://localhost:8000/api/v1
Production: https://api.sabpaisa.com/api/v1
Staging: https://staging-api.sabpaisa.com/api/v1
```

### Authentication Method
- **Type:** JWT (JSON Web Tokens)
- **Primary Identifier:** `login_master_id` (not username)
- **Header Format:** `Authorization: Bearer <access_token>`
- **Token Expiry:**
  - Access Token: 24 hours
  - Refresh Token: 7 days

### Response Format
- All responses are in JSON format
- Successful responses include `"success": true`
- Error responses include `"success": false` with error details
- Content-Type: `application/json`

### Timezone
- All datetime values use ISO 8601 format
- Default timezone: IST (UTC+05:30)

### Pagination
- Default page size: 100
- Maximum page size: 1000
- Format: `page=1&page_size=100`

---

## Authentication APIs

### 1. User Login
**Endpoint:** `POST /api/v1/auth/login/`

**Description:**
This endpoint authenticates users with their credentials and returns JWT tokens for API access. The system validates credentials against the `login_master` table in the database. Authentication can be done using either `login_master_id` or `username`.

**Authentication Required:** No (Public endpoint)
**Database:** ✅ Real - queries `login_master` table
**Response Time:** <30ms P95

**Request Headers:**
```http
Content-Type: application/json
```

**Request Body:**
```json
{
    "login_master_id": "12345",
    "password": "SecurePass@123"
}
```

OR

```json
{
    "username": "merchant_user",
    "password": "SecurePass@123"
}
```

**Request Body Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| login_master_id | string | No* | Primary user identifier |
| username | string | No* | Alternative to login_master_id |
| password | string | Yes | User's password (min 8 chars) |

*Either login_master_id or username is required

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1Mzk0NDAwLCJpYXQiOjE3MzUzMDgwMDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxfQ.abc123...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNTkxMjgwMCwiaWF0IjoxNzM1MzA4MDAwLCJqdGkiOiJhYmNkZWZnaCIsInVzZXJfaWQiOjF9.xyz789...",
        "user": {
            "login_master_id": "12345",
            "username": "merchant_user",
            "role_id": 2,
            "role": "MERCHANT",
            "client_code": "MERC001",
            "client_id": 101,
            "is_active": true,
            "email": "merchant@example.com",
            "mobile": "9876543210",
            "merchant_name": "ABC Merchants Pvt Ltd",
            "allowed_zones": ["NORTH", "WEST"],
            "last_login": "2024-12-28T14:30:00+05:30",
            "permissions": [
                "view_transactions",
            "export_reports",
            "manage_merchants"
        ]
    },
    "session_info": {
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "session_id": "sess_abc123xyz",
        "expires_at": "2024-12-29T14:30:00+05:30"
    }
}
```

**Error Response (401 Unauthorized):**
```json
{
    "success": false,
    "message": "Invalid credentials",
    "error_code": "AUTH_001",
    "details": {
        "attempts_remaining": 3,
        "account_locked": false
    }
}
```

**Error Response (423 Locked):**
```json
{
    "success": false,
    "message": "Account locked due to multiple failed attempts",
    "error_code": "AUTH_002",
    "details": {
        "locked_until": "2024-12-28T15:00:00+05:30",
        "support_email": "support@sabpaisa.com"
    }
}
```

---

### 2. Token Refresh
**Endpoint:** `POST /api/v1/auth/token/refresh/`

**Description:**
Generates a new access token using a valid refresh token. This endpoint is used when the access token expires (after 24 hours) but the refresh token is still valid (within 7 days). The system validates the refresh token, checks if it's blacklisted, and generates a new access token while keeping the same refresh token.

**Authentication Required:** No

**Request Headers:**
```http
Content-Type: application/json
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNTkxMjgwMCwiaWF0IjoxNzM1MzA4MDAwLCJqdGkiOiJhYmNkZWZnaCIsInVzZXJfaWQiOjF9.xyz789..."
}
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1Mzk0NDAwLCJpYXQiOjE3MzUzMDgwMDAsImp0aSI6Im5ld3Rva2VuMTIzIiwidXNlcl9pZCI6MX0.newtoken...",
    "expires_in": 86400,
    "token_type": "Bearer"
}
```

**Error Response (401 Unauthorized):**
```json
{
    "success": false,
    "message": "Token is invalid or expired",
    "error_code": "AUTH_003",
    "details": {
        "token_type": "refresh",
        "expired": true
    }
}
```

---

### 3. User Logout
**Endpoint:** `POST /api/v1/auth/logout/`

**Description:**
Logs out the user by blacklisting the refresh token to prevent its reuse. This ensures that even if someone has the refresh token, they cannot use it to generate new access tokens. The blacklisted tokens are stored in cache/database until their natural expiry.

**Authentication Required:** Yes

**Request Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Logout successful",
    "details": {
        "tokens_invalidated": true,
        "session_ended": "2024-12-28T14:45:00+05:30"
    }
}
```

---

### 4. Change Password
**Endpoint:** `POST /api/v1/auth/change-password/`

**Description:**
Allows authenticated users to change their password. The system validates the old password, enforces password complexity requirements (minimum 8 characters, at least one uppercase, one lowercase, one number, and one special character), and updates the password hash. All active sessions are invalidated after password change for security.

**Authentication Required:** Yes

**Request Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "old_password": "CurrentPass@123",
    "new_password": "NewSecurePass@456",
    "confirm_password": "NewSecurePass@456"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (@$!%*?&)
- Cannot be same as last 3 passwords

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Password changed successfully",
    "details": {
        "password_updated_at": "2024-12-28T14:50:00+05:30",
        "all_sessions_invalidated": true,
        "next_password_change": "2025-03-28T14:50:00+05:30"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "message": "Password validation failed",
    "error_code": "AUTH_004",
    "errors": {
        "old_password": "Incorrect password",
        "new_password": [
            "Password must contain at least one special character",
            "Password cannot be similar to email"
        ]
    }
}
```

---

### 5. Get Profile
**Endpoint:** `GET /api/v1/auth/profile/`

**Description:**
Get current authenticated user's profile information including role, permissions, and merchant details.

**Authentication Required:** Yes
**Response Time:** <25ms P95

**Request Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "username": "merchant_user",
        "email": "merchant@example.com",
        "mobile": "9876543210",
        "role": "MERCHANT",
        "role_id": 2,
        "is_active": true,
        "client_id": "CL001",
        "client_code": "MERC001",
        "merchant_name": "ABC Merchants Pvt Ltd",
        "allowed_zones": ["NORTH", "WEST"],
        "is_parent_merchant": false,
        "parent_merchant_id": null,
        "created_at": "2024-01-01T10:00:00+05:30",
        "last_login": "2024-12-28T14:30:00+05:30"
    }
}
```

---

### 6. Update Profile
**Endpoint:** `PUT /api/v1/auth/profile/`

**Description:**
Update user profile information. Only certain fields can be updated.

**Authentication Required:** Yes
**Response Time:** <35ms P95

**Request Body:**
```json
{
    "email": "newemail@example.com",
    "mobile": "9876543211",
    "merchant_name": "ABC Merchants Private Limited"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Profile updated successfully",
    "data": {
        "id": 1,
        "username": "merchant_user",
        "email": "newemail@example.com",
        "mobile": "9876543211",
        "merchant_name": "ABC Merchants Private Limited"
    }
}
```

---

### 7. Get User Sessions
**Endpoint:** `GET /api/v1/auth/sessions/`

**Description:**
Get all active sessions for the current authenticated user.

**Authentication Required:** Yes
**Response Time:** <28ms P95

**Response (200 OK):**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "user": "merchant_user",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "created_at": "2024-01-15T10:00:00+05:30",
            "last_activity": "2024-01-15T14:30:00+05:30",
            "is_active": true
        }
    ]
}
```

---

### 8. Terminate Session
**Endpoint:** `DELETE /api/v1/auth/sessions/{session_id}/`

**Description:**
Terminate a specific user session.

**Authentication Required:** Yes
**Response Time:** <25ms P95

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| session_id | integer | Session ID to terminate |

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Session terminated successfully"
}
```

---

### 9. Register Merchant (Admin Only)
**Endpoint:** `POST /api/v1/auth/register/merchant/`

**Description:**
Register a new merchant user. Only administrators can create new merchant accounts.

**Authentication Required:** Yes (Admin only)
**Response Time:** <45ms P95

**Request Body:**
```json
{
    "username": "new_merchant",
    "email": "newmerchant@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!",
    "mobile": "9876543210",
    "client_code": "MERC002",
    "merchant_name": "XYZ Traders Pvt Ltd",
    "allowed_zones": ["SOUTH", "EAST"]
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "message": "Merchant registered successfully",
    "data": {
        "id": 2,
        "username": "new_merchant",
        "email": "newmerchant@example.com",
        "mobile": "9876543210",
        "role": "MERCHANT",
        "client_code": "MERC002",
        "merchant_name": "XYZ Traders Pvt Ltd"
    }
}
```

---

## Transaction APIs

### 1. Get Merchant Transaction History
**Endpoint:** `GET /api/v1/transactions/merchant-history/`

**Description:**
Retrieves paginated transaction history for the authenticated merchant. This endpoint queries the `transaction_detail` table with comprehensive filtering options. Data is filtered based on the merchant's client_code and supports various search patterns.

**Authentication Required:** Yes (Merchant/Admin)
**Database:** ✅ Real - queries `transaction_detail` table with filters
**Implementation:** ✅ FULLY WORKING
**Response Time:** <450ms P95
**Default Page Size:** 100
**Max Page Size:** 1000

**Request Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Complete Query Parameters:**
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| date_from | datetime | No | Start date in ISO format | `2024-01-01T00:00:00Z` |
| date_to | datetime | No | End date in ISO format | `2024-01-31T23:59:59Z` |
| status | string | No | Transaction status | `SUCCESS|FAILED|PENDING|ABORTED` |
| payment_mode | string | No | Payment mode filter | `UPI|CARD|NET_BANKING|WALLET` |
| min_amount | decimal | No | Minimum transaction amount | `100.00` |
| max_amount | decimal | No | Maximum transaction amount | `10000.00` |
| search | string | No | General search term | `searchterm` |
| client_txn_id | string | No | Client transaction ID | `TXN123` |
| payee_mobile | string | No | Customer mobile number | `9876543210` |
| payee_email | string | No | Customer email | `customer@example.com` |
| client_code | string | No | Merchant code filter | `MERC001` |
| settlement_status | string | No | Settlement status | `COMPLETED|PENDING` |
| page | integer | No | Page number (default: 1) | `1` |
| page_size | integer | No | Results per page (default: 100, max: 1000) | `100` |
| order_by | string | No | Sort field (prefix - for desc) | `-trans_date` |

**Example Request:**
```http
GET /api/v1/transactions/merchant-history/?date_from=2024-01-01T00:00:00Z&date_to=2024-01-31T23:59:59Z&status=SUCCESS&payment_mode=UPI&min_amount=1000&page=1&page_size=100
```

**Success Response (200 OK):**
```json
{
    "count": 1543,
    "total_pages": 16,
    "current_page": 1,
    "next": "http://localhost:8000/api/v1/transactions/merchant-history/?page=2",
    "previous": null,
    "page_size": 100,
    "results": [
        {
            "txn_id": "SP2024011500001",
            "client_txn_id": "MERC001_TXN_001",
            "client_code": "MERC001",
            "client_name": "ABC Merchants Pvt Ltd",
            "paid_amount": 5000.00,
            "status": "SUCCESS",
            "payment_mode": "UPI",
            "trans_date": "2024-01-15T10:30:45Z",
            "trans_complete_date": "2024-01-15T10:31:02Z",
            "payee_email": "customer1@example.com",
            "payee_mob": "9876543210"
        },
        {
            "txn_id": "SP2024011500002",
            "client_txn_id": "MERC001_TXN_002",
            "client_code": "MERC001",
            "client_name": "ABC Merchants Pvt Ltd",
            "paid_amount": 2500.50,
            "status": "SUCCESS",
            "payment_mode": "CARD",
            "trans_date": "2024-01-15T11:15:30Z",
            "trans_complete_date": "2024-01-15T11:15:45Z",
            "payee_email": "customer2@example.com",
            "payee_mob": "9876543211"
        }
    ]
}
```

---

### 2. Get Admin Transaction History
**Endpoint:** `GET /api/v1/transactions/admin-history/`

**Description:**
Provides administrators with access to all transactions across all merchants in the system. This endpoint includes advanced filtering capabilities, bulk export options, and aggregated statistics. Admins can monitor system-wide transaction patterns, identify issues, and generate comprehensive reports.

**Authentication Required:** Yes
**Permission:** Admin role required
**Response Time:** <547ms P95

**Additional Query Parameters (Admin-specific):**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| merchant_code | string | Filter by merchant(s) | `MERC001,MERC002` |
| client_name | string | Partial merchant name | `ABC Merch` |
| settlement_status | string | Settlement filter | `PENDING` |
| include_metadata | boolean | Include additional data | `true` |

**Success Response (200 OK):**
```json
{
    "success": true,
    "filter_summary": "All merchants | Current month | All payment modes",
    "count": 45678,
    "merchants_included": 145,
    "aggregates": {
        "total_transactions": 45678,
        "total_volume": 228390000.00,
        "by_status": {
            "SUCCESS": 42100,
            "FAILED": 2578,
            "PENDING": 1000
        },
        "by_payment_mode": {
            "UPI": 23456,
            "CC": 12345,
            "DC": 8765,
            "NB": 1112
        }
    },
    "results": [
        {
            "txn_id": "SP202412270010",
            "merchant_info": {
                "client_code": "MERC002",
                "client_name": "XYZ Corporation",
                "merchant_category": "E-commerce"
            },
            "transaction_details": {
                "amount": 15000.00,
                "status": "SUCCESS",
                "payment_mode": "CREDIT_CARD",
                "card_details": {
                    "masked_number": "XXXX-XXXX-XXXX-1234",
                    "card_type": "VISA",
                    "issuer_bank": "ICICI"
                }
            },
            "settlement_info": {
                "is_settled": false,
                "expected_settlement": "2024-12-29",
                "settlement_cycle": "T+2"
            }
        }
    ]
}
```

---

### 3. Transaction Search by ID
**Endpoint:** `GET /api/v1/transactions/search/`

**Description:**
Searches for a specific transaction using either SabPaisa transaction ID or client's transaction reference. This endpoint provides complete transaction details including all payment, settlement, and refund information if available.

**Authentication Required:** Yes

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| txn_id | string | No* | SabPaisa transaction ID |
| client_txn_id | string | No* | Client transaction ID |

*At least one ID parameter is required

**Success Response (200 OK):**
```json
{
    "success": true,
    "filter_summary": "Transaction ID: SP202412270001",
    "count": 1,
    "data": {
        "transaction": {
            "txn_id": "SP202412270001",
            "client_txn_id": "MERC001_TXN_98765",
            "status": "SUCCESS",
            "amount": 2500.00,
            "created_at": "2024-12-27T14:30:00+05:30",
            "completed_at": "2024-12-27T14:30:45+05:30"
        },
        "payment_details": {
            "mode": "UPI",
            "channel": "MOBILE",
            "upi_id": "john@paytm",
            "gateway": "HDFC",
            "gateway_txn_id": "HDFC2024122798765",
            "bank_reference": "432112345678"
        },
        "customer_details": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "mobile": "9876543210",
            "location": {
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India"
            }
        },
        "settlement_details": {
            "status": "COMPLETED",
            "date": "2024-12-28",
            "amount": 2475.00,
            "utr": "HDFC2024122898765",
            "account": "XXXX1234"
        },
        "audit_trail": [
            {
                "timestamp": "2024-12-27T14:29:50+05:30",
                "event": "Transaction Initiated",
                "status": "PENDING"
            },
            {
                "timestamp": "2024-12-27T14:30:00+05:30",
                "event": "Payment Gateway Request",
                "status": "PROCESSING"
            },
            {
                "timestamp": "2024-12-27T14:30:45+05:30",
                "event": "Payment Confirmed",
                "status": "SUCCESS"
            }
        ]
    }
}
```

---

### 4. Transaction Summary Statistics
**Endpoint:** `GET /api/v1/transactions/summary/`

**Description:**
Provides aggregated transaction statistics for quick overview and dashboard displays. This endpoint calculates key metrics like total volume, success rates, average transaction values, and trending patterns.

**Authentication Required:** Yes

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| period | string | Time period (today/week/month/year) |
| group_by | string | Grouping criteria (date/hour/payment_mode) |

**Success Response (200 OK):**
```json
{
    "success": true,
    "period": "month",
    "summary": {
        "total_transactions": 15234,
        "successful_transactions": 14100,
        "failed_transactions": 1134,
        "success_rate": 92.56,
        "total_volume": 76170000.00,
        "average_transaction_value": 5000.00,
        "median_transaction_value": 2500.00,
        "peak_hour": 14,
        "peak_day": "2024-12-15"
    },
    "trends": {
        "volume_change": "+12.5%",
        "transaction_count_change": "+8.3%",
        "success_rate_change": "+1.2%"
    },
    "by_payment_mode": [
        {
            "mode": "UPI",
            "count": 8500,
            "volume": 42500000.00,
            "success_rate": 94.5
        },
        {
            "mode": "CREDIT_CARD",
            "count": 4234,
            "volume": 25404000.00,
            "success_rate": 91.2
        }
    ]
}
```

---

### 5. Merchant Transaction History (Bit Mode)
**Endpoint:** `GET /api/v1/transactions/merchant-history-bit/`

**Description:**
Optimized response with limited fields for faster performance. Uses `.only()` query optimization to select only essential fields from the database.

**Authentication Required:** Yes (Merchant/Admin)
**Database:** ✅ Real - uses `.only()` for query optimization
**Implementation:** ✅ FULLY WORKING
**Response Time:** <250ms P95

**Query Parameters:** Same as merchant-history endpoint

**Response (200 OK):**
```json
{
    "count": 1543,
    "total_pages": 16,
    "current_page": 1,
    "results": [
        {
            "txn_id": "SP2024011500001",
            "client_txn_id": "MERC001_TXN_001",
            "paid_amount": 5000.00,
            "status": "SUCCESS",
            "payment_mode": "UPI",
            "trans_date": "2024-01-15T10:30:45Z"
        }
    ]
}
```

---

### 6. Merchant Transaction History (Whole Mode)
**Endpoint:** `GET /api/v1/transactions/merchant-history-whole/`

**Description:**
Complete transaction data with all 170+ fields from the `transaction_detail` table. Returns comprehensive information for detailed analysis.

**Authentication Required:** Yes (Merchant/Admin)
**Database:** ✅ Real - returns all fields from table
**Implementation:** ✅ FULLY WORKING
**Response Time:** <800ms P95

**Query Parameters:** Same as merchant-history endpoint

**Response (200 OK) - All Fields:**
```json
{
    "count": 1543,
    "results": [
        {
            "txn_id": "SP2024011500001",
            "client_txn_id": "MERC001_TXN_001",
            "client_code": "MERC001",
            "client_name": "ABC Merchants Pvt Ltd",
            "client_id": 101,
            "act_amount": 5000.00,
            "paid_amount": 5000.00,
            "payee_amount": 5000.00,
            "settlement_amount": 4950.00,
            "status": "SUCCESS",
            "payment_mode": "UPI",
            "payment_mode_id": 5,
            "trans_date": "2024-01-15T10:30:45Z",
            "trans_complete_date": "2024-01-15T10:31:02Z",
            "payee_email": "customer1@example.com",
            "payee_mob": "9876543210",
            "payee_first_name": "John",
            "payee_lst_name": "Doe",
            "pg_name": "PayU",
            "pg_txn_id": "PAYU123456",
            "pg_response_code": "000",
            "bank_txn_id": "BANK789012",
            "bank_name": "HDFC",
            "bank_message": "Transaction Successful",
            "auth_code": "AUTH123",
            "arn": "ARN456789",
            "card_brand": "VISA",
            "vpa": "customer@upi",
            "is_settled": true,
            "settlement_date": "2024-01-16T00:00:00Z",
            "settlement_status": "COMPLETED",
            "settlement_utr": "UTR123456789",
            "convcharges": 25.00,
            "gst": 25.00,
            "refund_amount": 0.00,
            "charge_back_amount": 0.00,
            "device_name": "Chrome Browser",
            "browser_details": "Mozilla/5.0",
            "client_request_ip": "192.168.1.100",
            "channel_id": "WEB",
            "business_ctg_code": "RETAIL",
            "referral_code": "REF001"
        }
    ]
}
```

---

### 7. Merchant Transaction History (Whole)
**Endpoint:** `GET /api/v1/transactions/merchant-history-whole/`

**Description:**
Complete transaction history with all available fields including metadata, audit trails, and related transaction links. This endpoint returns comprehensive data for detailed analysis and reporting.

**Authentication Required:** Yes
**Permission:** Merchant role required
**Response Time:** <800ms P95

**Additional Response Fields:**
- Complete customer profile
- Full payment gateway response
- Detailed settlement breakdown
- Refund/chargeback history
- Complete audit trail
- Related transactions

---

### 7. Generate Merchant Transaction Excel
**Endpoint:** `POST /api/v1/transactions/merchant-history-excel/`

**Description:**
Generates an Excel report of merchant transactions with multiple sheets including summary, detailed transactions, charts, and analytics. Supports up to 100,000 records per report.

**Authentication Required:** Yes
**Permission:** Merchant role required
**Throttle:** 5 requests per 5 minutes

**Request Body:**
```json
{
    "date_from": "2024-12-01",
    "date_to": "2024-12-31",
    "payment_mode": ["UPI", "CC", "DC"],
    "status": "SUCCESS",
    "include_summary": true,
    "include_charts": true,
    "include_settlement_details": true,
    "max_records": 50000,
    "sheets": {
        "transactions": true,
        "summary": true,
        "daily_breakdown": true,
        "payment_modes": true,
        "settlements": true
    },
    "format_options": {
        "currency_format": "INR",
        "date_format": "DD-MM-YYYY",
        "include_formulas": true
    }
}
```

**Success Response (202 Accepted):**
```json
{
    "success": true,
    "message": "Excel generation initiated",
    "task_id": "task_20241227_143000_abc123",
    "estimated_time": "10-15 seconds",
    "estimated_size": "4.5 MB",
    "download_url": "/api/v1/reports/download/task_20241227_143000_abc123/",
    "expires_at": "2024-12-28T14:30:00+05:30"
}
```

---

### 8. Admin Transaction Excel Export
**Endpoint:** `POST /api/v1/transactions/admin-history-excel/`

**Description:**
Generates comprehensive Excel reports for administrators covering all merchants with advanced analytics, comparative analysis, and system-wide metrics.

**Authentication Required:** Yes
**Permission:** Admin role required
**Throttle:** 3 requests per 10 minutes

**Additional Request Options:**
```json
{
    "merchants": ["MERC001", "MERC002", "ALL"],
    "comparison_period": "previous_month",
    "include_merchant_summary": true,
    "include_system_metrics": true
}
```

---

### 9. Admin Export History
**Endpoint:** `GET /api/v1/transactions/admin-export-history/`

**Description:**
Tracks all export activities performed by administrators including report generation history, download counts, and audit trail for compliance purposes.

**Authentication Required:** Yes
**Permission:** Admin role required

**Success Response (200 OK):**
```json
{
    "success": true,
    "exports": [
        {
            "export_id": "EXP_20241227_001",
            "exported_by": "admin@sabpaisa.com",
            "export_date": "2024-12-27T14:00:00+05:30",
            "type": "transaction_report",
            "format": "excel",
            "records_exported": 50000,
            "file_size": "12.5 MB",
            "parameters": {
                "date_range": "2024-12-01 to 2024-12-31",
                "merchants": ["ALL"]
            },
            "download_count": 3,
            "last_downloaded": "2024-12-27T15:30:00+05:30"
        }
    ]
}
```

---

### 10. QF Wise Transaction History
**Endpoint:** `GET /api/v1/transactions/qf-wise-history/`

**Description:**
Query Filter based transaction history that allows complex filtering combinations using query filter syntax. Supports advanced search patterns and custom field combinations.

**Authentication Required:** Yes

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| qf_type | string | Filter type (payment_mode/bank/status) |
| qf_value | string | Filter value |
| qf_operator | string | Operator (eq/ne/gt/lt/contains) |

**Example Request:**
```http
GET /api/v1/transactions/qf-wise-history/?qf_type=payment_mode&qf_value=UPI&qf_operator=eq
```

---

### 11. DOITC Settled Transaction History
**Endpoint:** `GET /api/v1/transactions/doitc-settled-history/`

**Description:**
Specialized endpoint for Department of Information Technology and Communication (DOITC) to retrieve settled transactions with government-specific compliance fields and reporting formats.

**Authentication Required:** Yes
**Permission:** Special DOITC permission required

**Additional Response Fields:**
- Government transaction codes
- Department mappings
- Budget allocation references
- Compliance status
- Audit requirements

---

### 12. DOITC Merchant Transaction History
**Endpoint:** `GET /api/v1/transactions/doitc-merchant-history/`

**Description:**
DOITC-specific merchant transaction history with department-wise breakdown and government merchant categorization.

**Authentication Required:** Yes
**Permission:** Special DOITC permission required

---

### 13. SBI Card Data
**Endpoint:** `GET /api/v1/transactions/sbi-card-data/`

**Description:**
Retrieves transaction data specific to SBI Card payments including card type distribution, issuer bank analysis, and SBI-specific settlement reconciliation.

**Authentication Required:** Yes
**Permission:** Merchant or Admin role

**Success Response (200 OK):**
```json
{
    "success": true,
    "sbi_card_summary": {
        "total_transactions": 5432,
        "total_volume": 27160000.00,
        "card_types": {
            "credit": 3456,
            "debit": 1976
        },
        "by_card_category": {
            "platinum": 1234,
            "gold": 2100,
            "classic": 2098
        }
    }
}
```

---

### 14. Success Graph Data
**Endpoint:** `GET /api/v1/transactions/success-graph/`

**Description:**
Provides data formatted for visualization of transaction success rates over time. Returns coordinates and series data ready for charting libraries.

**Authentication Required:** Yes

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| period | string | Time period (hour/day/week/month) |
| interval | string | Data point interval |

**Success Response (200 OK):**
```json
{
    "success": true,
    "graph_data": {
        "labels": ["00:00", "01:00", "02:00", "..."],
        "series": [
            {
                "name": "Success",
                "data": [95.2, 94.8, 96.1, "..."]
            },
            {
                "name": "Failed",
                "data": [4.8, 5.2, 3.9, "..."]
            }
        ],
        "summary": {
            "peak_success_rate": 98.5,
            "lowest_success_rate": 88.2,
            "average_success_rate": 94.3
        }
    }
}
```

---

### 15. Merchant Whitelist
**Endpoint:** `GET /api/v1/transactions/merchant-whitelist/`

**Description:**
Returns list of whitelisted merchants with their verification status, compliance levels, and special processing rules.

**Authentication Required:** Yes
**Permission:** Admin role required

**Success Response (200 OK):**
```json
{
    "success": true,
    "whitelist": [
        {
            "client_code": "MERC001",
            "client_name": "ABC Merchants Pvt Ltd",
            "whitelisted_date": "2024-01-15",
            "verification_level": "FULL",
            "compliance_status": "COMPLIANT",
            "special_rules": {
                "auto_settlement": true,
                "priority_processing": true,
                "reduced_charges": true,
                "charge_percentage": 1.5
            },
            "limits": {
                "daily_limit": 10000000.00,
                "per_transaction_limit": 500000.00
            }
        }
    ]
}
```

---

## Settlement Management APIs

### 1. Get Settled Transaction History
**Endpoint:** `GET /api/v1/settlements/settled-history/`

**Description:**
Retrieves all transactions that have been settled to merchant bank accounts. This endpoint provides detailed settlement information including UTR numbers, settlement dates, bank references, and net amounts after charge deductions.

**Authentication Required:** Yes
**Response Time:** <156ms P95

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| use_settlement_date | boolean | Filter by settlement date instead of transaction date |
| settlement_status | string | COMPLETED/PENDING/PROCESSING/FAILED |
| settlement_utr | string | Search by UTR number |
| bank_account | string | Filter by settlement account |

**Success Response (200 OK):**
```json
{
    "success": true,
    "filter_summary": "Settled transactions | Last 7 days | Status: COMPLETED",
    "count": 342,
    "aggregates": {
        "total_settled_amount": 1710000.00,
        "total_charges": 34200.00,
        "net_settled": 1675800.00,
        "average_tat_hours": 24.5
    },
    "results": [
        {
            "txn_id": "SP202412260001",
            "client_code": "MERC001",
            "client_name": "ABC Merchants Pvt Ltd",
            "transaction_date": "2024-12-26T10:30:00+05:30",
            "transaction_amount": 5000.00,
            "settlement_date": "2024-12-27T10:00:00+05:30",
            "settlement_amount": 4900.00,
            "settlement_status": "COMPLETED",
            "settlement_method": "NEFT",
            "settlement_utr": "HDFC2024122798765",
            "settlement_reference": "SETT_2024122700001",
            "bank_details": {
                "account_number": "XXXX1234",
                "bank_name": "HDFC Bank",
                "ifsc_code": "HDFC0001234"
            },
            "charges_breakdown": {
                "sabpaisa_charges": 80.00,
                "bank_charges": 10.00,
                "gst": 10.00,
                "total_deductions": 100.00
            },
            "tat_hours": 23.5,
            "settlement_cycle": "T+1"
        }
    ]
}
```

---

### 2. Get Refund Transaction History
**Endpoint:** `GET /api/v1/settlements/refund-history/`

**Description:**
Retrieves all refund transactions across the system. Tracks refund lifecycle from initiation to completion, including partial refunds, refund reasons, and processing timelines.

**Authentication Required:** Yes
**Response Time:** <142ms P95

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| refund_status | string | Filter by refund status |
| refund_message | string | Search in refund messages |
| refund_date | date | Specific refund date |
| refund_status_code | string | Exact status code |
| refund_request_from | string | Username who initiated |
| refund_reason | string | Refund reason category |
| refunded_amount | decimal | Exact refunded amount |
| refund_track_id | string | Refund tracking ID |
| use_refund_date | boolean | Use refund date for filtering |

**Success Response (200 OK):**
```json
{
    "success": true,
    "filter_summary": "Refunds | Current month | Status: COMPLETED",
    "count": 89,
    "aggregates": {
        "total_refund_amount": 445000.00,
        "completed_refunds": 75,
        "pending_refunds": 10,
        "failed_refunds": 4,
        "average_processing_time_hours": 4.5
    },
    "results": [
        {
            "refund_id": "REF_20241226_0001",
            "original_txn_id": "SP202412250001",
            "client_code": "MERC001",
            "original_amount": 3000.00,
            "refund_amount": 3000.00,
            "refund_type": "FULL",
            "refund_status": "COMPLETED",
            "refund_status_code": "RF_SUCCESS",
            "refund_initiated_date": "2024-12-26T10:00:00+05:30",
            "refund_processed_date": "2024-12-26T14:00:00+05:30",
            "refund_completed_date": "2024-12-26T14:30:00+05:30",
            "refund_reason": "customer_request",
            "refund_message": "Product return - Order #12345",
            "refund_request_from": "support_user_01",
            "refund_method": "SOURCE",
            "refund_reference": "HDFC_REF_2024122600001",
            "customer_details": {
                "name": "John Doe",
                "email": "john@example.com",
                "mobile": "9876543210"
            },
            "processing_timeline": [
                {
                    "stage": "INITIATED",
                    "timestamp": "2024-12-26T10:00:00+05:30",
                    "user": "support_user_01"
                },
                {
                    "stage": "BANK_PROCESSING",
                    "timestamp": "2024-12-26T10:15:00+05:30"
                },
                {
                    "stage": "COMPLETED",
                    "timestamp": "2024-12-26T14:30:00+05:30"
                }
            ]
        }
    ]
}
```

---

### 3. Get Merchant Refund History
**Endpoint:** `GET /api/v1/settlements/merchant-refund-history/`

**Description:**
Merchant-specific refund transaction history. Shows only refunds for transactions belonging to the authenticated merchant with detailed breakdown and refund analytics.

**Authentication Required:** Yes
**Permission:** Merchant role required
**Response Time:** <150ms P95

**Additional Features:**
- Automatic merchant filtering based on authentication
- Refund impact on settlements
- Refund patterns analysis
- Customer refund history

---

### 4. Get Chargeback Transaction History
**Endpoint:** `GET /api/v1/settlements/chargeback-history/`

**Description:**
Retrieves all chargeback and dispute transactions. Tracks the complete dispute lifecycle, representment process, and final outcomes with liability assignments.

**Authentication Required:** Yes
**Response Time:** <158ms P95

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| chargeback_status | string | DISPUTED/RESOLVED/PENDING/LOST |
| chargeback_reason | string | Reason category |
| dispute_amount | decimal | Disputed amount |
| use_chargeback_date | boolean | Use chargeback date |

**Success Response (200 OK):**
```json
{
    "success": true,
    "filter_summary": "Chargebacks | Last 30 days",
    "count": 23,
    "aggregates": {
        "total_disputed_amount": 230000.00,
        "open_disputes": 5,
        "won_disputes": 12,
        "lost_disputes": 6,
        "win_rate": 66.67
    },
    "results": [
        {
            "chargeback_id": "CBK_20241225_001",
            "original_txn_id": "SP202412200001",
            "dispute_amount": 8000.00,
            "chargeback_date": "2024-12-25T10:00:00+05:30",
            "chargeback_status": "DISPUTED",
            "dispute_reason": "fraudulent_transaction",
            "dispute_code": "4837",
            "card_network": "VISA",
            "liability": "MERCHANT",
            "due_date": "2024-12-30T23:59:59+05:30",
            "merchant_response": {
                "responded": true,
                "response_date": "2024-12-26T15:00:00+05:30",
                "documents_submitted": [
                    "invoice.pdf",
                    "delivery_proof.pdf"
                ]
            },
            "timeline": [
                {
                    "event": "Dispute Raised",
                    "date": "2024-12-25T10:00:00+05:30"
                },
                {
                    "event": "Merchant Notified",
                    "date": "2024-12-25T10:30:00+05:30"
                },
                {
                    "event": "Response Submitted",
                    "date": "2024-12-26T15:00:00+05:30"
                }
            ]
        }
    ]
}
```

---

### 5. Grouped Settlement View
**Endpoint:** `GET /api/v1/settlements/grouped-view/`

**Description:**
Provides aggregated settlement data grouped by various criteria (date, merchant, status) for settlement analysis and reconciliation purposes.

**Authentication Required:** Yes
**Response Time:** <203ms P95

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| group_by | string | date/merchant/status/bank |
| include_charges | boolean | Include charge breakdown |

**Success Response (200 OK):**
```json
{
    "success": true,
    "group_by": "date",
    "data": [
        {
            "date": "2024-12-27",
            "total_transactions": 145,
            "total_amount": 725000.00,
            "total_charges": 14500.00,
            "net_settlement": 710500.00,
            "by_status": {
                "COMPLETED": 140,
                "PENDING": 5
            },
            "by_payment_mode": {
                "UPI": 85,
                "CC": 40,
                "DC": 20
            }
        },
        {
            "date": "2024-12-26",
            "total_transactions": 132,
            "total_amount": 660000.00,
            "total_charges": 13200.00,
            "net_settlement": 646800.00
        }
    ]
}
```

---

### 6. QF Wise Settled Transactions
**Endpoint:** `GET /api/v1/settlements/qf-wise-settled/`

**Description:**
Query-filter based settled transactions with advanced filtering capabilities for complex settlement queries and custom report generation.

**Authentication Required:** Yes
**Response Time:** <167ms P95

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| qf_type | string | payment_mode/bank/utr |
| qf_value | string | Filter value |

---

### 7. Generate Settlement Excel
**Endpoint:** `POST /api/v1/settlements/settled-excel/`

**Description:**
Generates basic Excel report of settled transactions with settlement details, charge breakdowns, and summary statistics.

**Authentication Required:** Yes
**Throttle:** ReportGenerationThrottle (5 per 5 minutes)

**Request Body:**
```json
{
    "date_from": "2024-12-01",
    "date_to": "2024-12-31",
    "settlement_status": "COMPLETED",
    "include_charges": true,
    "include_summary": true,
    "max_records": 25000
}
```

---

### 8. Generate Enhanced Settlement Excel V2
**Endpoint:** `POST /api/v1/settlements/settled-excel-v2/`

**Description:**
Enhanced settlement Excel generation with multiple sheets, charts, pivot tables, and advanced analytics including settlement trends and TAT analysis.

**Authentication Required:** Yes
**Response Time:** <3.2s for 15K records

**Request Body:**
```json
{
    "date_from": "2024-12-01",
    "date_to": "2024-12-31",
    "options": {
        "include_charts": true,
        "include_pivot_tables": true,
        "include_tat_analysis": true,
        "include_charge_analysis": true,
        "include_bank_wise_summary": true
    },
    "sheets": {
        "detailed_transactions": true,
        "daily_summary": true,
        "merchant_summary": true,
        "bank_reconciliation": true,
        "charge_breakdown": true
    }
}
```

---

### 9. Three-Way Reconciliation
**Endpoint:** `POST /api/v1/settlements/reconciliation/`

**Description:**
Performs three-way reconciliation between bank statements, payment gateway data, and internal transaction records. Identifies mismatches and generates reconciliation report.

**Authentication Required:** Yes
**Permission:** Admin role required

**Request Body:**
```json
{
    "reconciliation_date": "2024-12-27",
    "sources": {
        "bank_statement": {
            "file_id": "bank_stmt_20241227",
            "format": "csv"
        },
        "gateway_report": {
            "gateway": "HDFC",
            "report_id": "hdfc_20241227"
        }
    },
    "options": {
        "auto_match": true,
        "tolerance_amount": 1.00,
        "include_pending": false
    }
}
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "reconciliation_id": "RECON_20241227_001",
    "summary": {
        "total_records": 1000,
        "matched": 980,
        "mismatched": 15,
        "missing_in_bank": 3,
        "missing_in_gateway": 2,
        "match_rate": 98.0
    },
    "mismatches": [
        {
            "type": "AMOUNT_MISMATCH",
            "txn_id": "SP202412270100",
            "bank_amount": 5000.00,
            "system_amount": 5001.00,
            "difference": 1.00
        }
    ]
}
```

---

## Analytics & Insights APIs

### 1. Merchant Analytics Dashboard
**Endpoint:** `GET /api/v1/analytics/merchant-analytics/`

**Description:**
Comprehensive analytics dashboard for merchants showing KPIs, trends, payment mode distribution, customer analytics, and performance metrics. Data is cached for 30 minutes to improve performance.

**Authentication Required:** Yes
**Cache:** 30 minutes
**Response Time:** <300ms P95

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| date_filter | string | Period selection |
| payment_mode | string | Filter by payment mode |
| merchant_code | string | Specific merchant (Admin only) |
| comparison | boolean | Include comparison data |

**Success Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "kpis": {
            "total_transactions": 4523,
            "successful_transactions": 4102,
            "failed_transactions": 421,
            "success_rate": 90.69,
            "total_volume": 22615000.00,
            "avg_transaction_value": 5513.41,
            "median_transaction_value": 3500.00,
            "settled_amount": 20500000.00,
            "pending_settlement": 2115000.00,
            "refund_rate": 2.3,
            "chargeback_rate": 0.5
        },
        "payment_mode_distribution": [
            {
                "mode": "UPI",
                "count": 2451,
                "volume": 12255000.00,
                "percentage": 54.2,
                "success_rate": 95.2,
                "avg_value": 5000.00
            },
            {
                "mode": "CREDIT_CARD",
                "count": 1203,
                "volume": 7218000.00,
                "percentage": 31.9,
                "success_rate": 88.5,
                "avg_value": 6000.00
            }
        ],
        "daily_trend": [
            {
                "date": "2024-12-27",
                "transactions": 156,
                "successful": 142,
                "failed": 14,
                "volume": 780000.00,
                "avg_value": 5000.00,
                "peak_hour": 14
            }
        ],
        "hourly_distribution": [
            {
                "hour": 0,
                "count": 45,
                "volume": 225000.00
            },
            {
                "hour": 10,
                "count": 523,
                "volume": 2615000.00
            },
            {
                "hour": 14,
                "count": 612,
                "volume": 3060000.00
            }
        ],
        "top_customers": [
            {
                "customer_id": "CUST_001",
                "email": "corporate@bigclient.com",
                "transaction_count": 89,
                "total_amount": 890000.00,
                "avg_transaction": 10000.00,
                "last_transaction": "2024-12-27T16:30:00+05:30"
            }
        ],
        "gateway_performance": [
            {
                "gateway": "HDFC",
                "transactions": 2500,
                "success_rate": 94.5,
                "avg_response_time_ms": 850
            }
        ],
        "period": {
            "start_date": "2024-12-01T00:00:00+05:30",
            "end_date": "2024-12-27T23:59:59+05:30",
            "days": 27,
            "business_days": 20
        }
    }
}
```

---

### 2. Payment Mode Analytics
**Endpoint:** `GET /api/v1/analytics/payment-mode-analytics/`

**Description:**
Detailed analytics for specific payment modes including success rates, failure reasons, gateway performance, and optimization recommendations.

**Authentication Required:** Yes

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| payment_mode | string | UPI/CC/DC/NB/WALLET |
| compare_with | string | Another payment mode |

**Success Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "payment_mode": "UPI",
        "metrics": {
            "total_transactions": 8923,
            "successful": 8234,
            "failed": 689,
            "success_rate": 92.28,
            "total_volume": 44615000.00,
            "avg_transaction": 5000.00,
            "median_transaction": 2500.00
        },
        "failure_analysis": {
            "total_failures": 689,
            "by_reason": {
                "insufficient_funds": 234,
                "technical_error": 156,
                "user_cancelled": 145,
                "timeout": 89,
                "other": 65
            }
        },
        "gateway_wise": [
            {
                "gateway": "HDFC",
                "provider": "PayTM",
                "transactions": 4500,
                "success_rate": 94.5,
                "avg_processing_time_ms": 750
            }
        ],
        "hourly_pattern": {
            "peak_hours": [10, 14, 20],
            "low_activity_hours": [2, 3, 4],
            "best_success_rate_hour": 6
        },
        "recommendations": [
            "Consider routing more traffic through HDFC gateway (highest success rate)",
            "Implement retry mechanism for technical errors",
            "Add timeout handling for better user experience"
        ]
    }
}
```

---

### 3. Settlement Analytics
**Endpoint:** `GET /api/v1/analytics/settlement-analytics/`

**Description:**
Analytics focused on settlement performance including TAT analysis, settlement cycles, bank-wise performance, and settlement optimization insights.

**Authentication Required:** Yes

**Success Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "summary": {
            "total_transaction_amount": 45230000.00,
            "total_settled": 42500000.00,
            "pending_settlement": 2730000.00,
            "settlement_rate": 93.96,
            "avg_settlement_tat_hours": 24.5,
            "fastest_tat_hours": 2.0,
            "slowest_tat_hours": 72.0
        },
        "settlement_timeline": [
            {
                "date": "2024-12-27",
                "settled_count": 234,
                "settled_amount": 1170000.00,
                "avg_tat_hours": 23.5
            }
        ],
        "bank_wise_settlement": [
            {
                "bank": "HDFC Bank",
                "gateway": "HDFC",
                "transactions": 1245,
                "amount": 18675000.00,
                "avg_tat_hours": 22.5,
                "settlement_success_rate": 99.8
            }
        ],
        "settlement_cycles": {
            "T+0": {
                "count": 100,
                "percentage": 10.0
            },
            "T+1": {
                "count": 750,
                "percentage": 75.0
            },
            "T+2": {
                "count": 150,
                "percentage": 15.0
            }
        }
    }
}
```

---

### 4. Refund & Chargeback Analytics
**Endpoint:** `GET /api/v1/analytics/refund-chargeback/`

**Description:**
Combined analytics for refunds and chargebacks including trends, reasons analysis, impact on revenue, and risk assessment.

**Authentication Required:** Yes

**Success Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "summary": {
            "total_refunds": 156,
            "total_refund_amount": 780000.00,
            "refund_rate": 3.45,
            "avg_refund_processing_hours": 4.5,
            "total_chargebacks": 23,
            "total_chargeback_amount": 230000.00,
            "chargeback_rate": 0.51,
            "dispute_win_rate": 65.22
        },
        "refund_trend": [
            {
                "date": "2024-12-27",
                "count": 8,
                "amount": 40000.00,
                "avg_processing_hours": 3.5
            }
        ],
        "chargeback_trend": [
            {
                "date": "2024-12-25",
                "count": 2,
                "amount": 20000.00,
                "dispute_status": "OPEN"
            }
        ],
        "top_refund_reasons": [
            {
                "reason": "customer_request",
                "count": 89,
                "percentage": 57.05,
                "total_amount": 445000.00
            },
            {
                "reason": "product_issue",
                "count": 34,
                "percentage": 21.79,
                "total_amount": 170000.00
            }
        ],
        "risk_indicators": {
            "high_risk_merchants": 2,
            "suspicious_pattern_detected": false,
            "recommended_actions": [
                "Review refund policy for customer_request category",
                "Implement additional verification for high-value refunds"
            ]
        }
    }
}
```

---

### 5. Executive Dashboard (Admin Only)
**Endpoint:** `GET /api/v1/analytics/executive-dashboard/`

**Description:**
High-level executive dashboard with system-wide metrics, top performers, risk indicators, and strategic insights for decision making.

**Authentication Required:** Yes
**Permission:** Admin role required
**Cache:** 10 minutes

**Success Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "system_health": {
            "status": "HEALTHY",
            "uptime_percentage": 99.99,
            "active_merchants": 145,
            "api_response_time_ms": 156,
            "error_rate": 0.05
        },
        "today": {
            "date": "2024-12-27",
            "transactions": 3456,
            "volume": 17280000.00,
            "success_rate": 91.5,
            "active_merchants": 128,
            "new_merchants": 2,
            "hourly_run_rate": 144
        },
        "month_to_date": {
            "transactions": 87234,
            "volume": 436170000.00,
            "success_rate": 89.8,
            "growth_rate": 12.5,
            "projected_month_end": 475000000.00
        },
        "year_to_date": {
            "transactions": 1045678,
            "volume": 5228390000.00,
            "success_rate": 90.2,
            "growth_rate": 25.8
        },
        "top_merchants": [
            {
                "rank": 1,
                "code": "MERC001",
                "name": "ABC Merchants Pvt Ltd",
                "volume": 45230000.00,
                "transactions": 9046,
                "success_rate": 94.5,
                "contribution_percentage": 10.37
            }
        ],
        "payment_mode_performance": [
            {
                "mode": "UPI",
                "volume": 250000000.00,
                "transactions": 50000,
                "success_rate": 92.89,
                "trend": "INCREASING"
            }
        ],
        "alerts": [
            {
                "type": "WARNING",
                "message": "High failure rate detected for CC transactions",
                "affected_merchants": 5,
                "action_required": true
            }
        ],
        "projections": {
            "end_of_month_volume": 475000000.00,
            "end_of_year_volume": 6000000000.00,
            "growth_trajectory": "POSITIVE"
        }
    }
}
```

---

### 6. Comparative Analytics (Admin Only)
**Endpoint:** `GET /api/v1/analytics/comparative/`

**Description:**
Comparative analysis between different time periods or merchants for performance benchmarking and trend identification.

**Authentication Required:** Yes
**Permission:** Admin role required

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| type | string | period/merchant |
| current_days | integer | Days for period comparison |
| merchant_codes | string | Comma-separated merchant codes |

**Period Comparison Response:**
```json
{
    "success": true,
    "data": {
        "comparison_type": "period",
        "current_period": {
            "start": "2024-11-27",
            "end": "2024-12-27",
            "metrics": {
                "transactions": 45678,
                "volume": 228390000.00,
                "success_rate": 90.27,
                "avg_transaction": 5000.00
            }
        },
        "previous_period": {
            "start": "2024-10-27",
            "end": "2024-11-27",
            "metrics": {
                "transactions": 42345,
                "volume": 211725000.00,
                "success_rate": 89.48,
                "avg_transaction": 5000.00
            }
        },
        "changes": {
            "transactions": {
                "absolute": 3333,
                "percentage": 7.87,
                "trend": "POSITIVE"
            },
            "volume": {
                "absolute": 16665000.00,
                "percentage": 7.87,
                "trend": "POSITIVE"
            },
            "success_rate": {
                "absolute": 0.79,
                "percentage": 0.88,
                "trend": "POSITIVE"
            }
        },
        "insights": [
            "Transaction volume growing steadily at 7.87%",
            "Success rate improvement indicates better payment processing",
            "Consider increasing marketing spend to maintain growth"
        ]
    }
}
```

**Merchant Comparison Response:**
```json
{
    "success": true,
    "data": {
        "comparison_type": "merchant",
        "period": {
            "start": "2024-11-27",
            "end": "2024-12-27"
        },
        "merchants": [
            {
                "code": "MERC001",
                "name": "ABC Merchants Pvt Ltd",
                "metrics": {
                    "transactions": 15234,
                    "volume": 76170000.00,
                    "success_rate": 91.18,
                    "avg_transaction": 5000.00,
                    "refund_rate": 2.1
                },
                "rank": 1,
                "performance_score": 95.5
            },
            {
                "code": "MERC002",
                "name": "XYZ Corporation",
                "metrics": {
                    "transactions": 14567,
                    "volume": 72835000.00,
                    "success_rate": 89.40,
                    "avg_transaction": 5000.00,
                    "refund_rate": 3.2
                },
                "rank": 2,
                "performance_score": 88.2
            }
        ],
        "best_performer": {
            "code": "MERC001",
            "leading_metrics": ["success_rate", "volume", "performance_score"]
        },
        "recommendations": {
            "MERC002": [
                "Success rate below average - review payment gateway configuration",
                "Higher refund rate - investigate product/service quality"
            ]
        }
    }
}
```

---

## Report Generation APIs

### 1. Generate Report
**Endpoint:** `POST /api/v1/reports/generate/`

**Description:**
Initiates asynchronous report generation for various report types and formats. Reports are generated in background and can be downloaded once complete. Supports multiple formats, custom date ranges, and various filtering options.

**Authentication Required:** Yes
**Throttle:** 10 requests per 5 minutes

**Request Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "report_type": "transaction",
    "format": "excel",
    "title": "Monthly Transaction Report - December 2024",
    "filters": {
        "date_filter": "custom",
        "date_from": "2024-12-01",
        "date_to": "2024-12-31",
        "payment_mode": ["UPI", "CC", "DC"],
        "status": "SUCCESS",
        "merchant_code": "MERC001"
    },
    "options": {
        "include_summary": true,
        "include_charts": true,
        "include_pivot_tables": true,
        "include_raw_data": true,
        "max_records": 50000
    },
    "sections": {
        "executive_summary": true,
        "detailed_transactions": true,
        "daily_breakdown": true,
        "payment_mode_analysis": true,
        "settlement_summary": true,
        "refund_summary": false
    },
    "delivery": {
        "email_notification": true,
        "email_addresses": ["admin@example.com"],
        "webhook_url": "https://webhook.example.com/report-ready"
    }
}
```

**Request Body Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| report_type | string | Yes | transaction/settlement/refund/chargeback/merchant/analytics |
| format | string | Yes | excel/csv/pdf/json |
| title | string | No | Custom report title |
| filters | object | Yes | Report filtering criteria |
| options | object | No | Report generation options |
| sections | object | No | Sections to include |
| delivery | object | No | Delivery preferences |

**Success Response (202 Accepted):**
```json
{
    "success": true,
    "message": "Report generation initiated",
    "task_id": "task_20241227_160000_a1b2c3d4",
    "report_details": {
        "type": "transaction",
        "format": "excel",
        "title": "Monthly Transaction Report - December 2024",
        "estimated_records": 45000,
        "estimated_size_mb": 12.5,
        "estimated_time": "10-15 seconds"
    },
    "tracking": {
        "status_url": "/api/v1/reports/status/task_20241227_160000_a1b2c3d4/",
        "download_url": "/api/v1/reports/download/task_20241227_160000_a1b2c3d4/",
        "expires_at": "2024-12-28T16:00:00+05:30"
    }
}
```

---

### 2. Check Report Status
**Endpoint:** `GET /api/v1/reports/status/<task_id>/`

**Description:**
Checks the status of a report generation task. Provides real-time progress updates, completion percentage, and estimated time remaining.

**Authentication Required:** Yes

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | string | Task ID from generation response |

**Response - Processing (200 OK):**
```json
{
    "success": true,
    "task_id": "task_20241227_160000_a1b2c3d4",
    "status": "PROCESSING",
    "progress": 45,
    "details": {
        "current_step": "Fetching transactions",
        "records_processed": 22500,
        "total_records": 50000,
        "elapsed_time_seconds": 5,
        "estimated_remaining_seconds": 6
    },
    "messages": [
        "Started at 2024-12-27T16:00:00+05:30",
        "Fetching transactions...",
        "Processing 50000 records..."
    ]
}
```

**Response - Completed (200 OK):**
```json
{
    "success": true,
    "task_id": "task_20241227_160000_a1b2c3d4",
    "status": "COMPLETED",
    "progress": 100,
    "details": {
        "completion_time": "2024-12-27T16:00:15+05:30",
        "total_time_seconds": 15,
        "records_processed": 50000,
        "file_size_mb": 12.5,
        "file_format": "excel"
    },
    "download": {
        "url": "/api/v1/reports/download/task_20241227_160000_a1b2c3d4/",
        "filename": "transaction_report_20241227_160000.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "expires_at": "2024-12-28T16:00:15+05:30"
    }
}
```

**Response - Failed (200 OK):**
```json
{
    "success": false,
    "task_id": "task_20241227_160000_a1b2c3d4",
    "status": "FAILED",
    "error": {
        "message": "Report generation failed",
        "reason": "Memory limit exceeded for 100000 records",
        "failed_at": "2024-12-27T16:00:10+05:30",
        "suggestion": "Try reducing max_records or split date range"
    }
}
```

---

### 3. Download Report
**Endpoint:** `GET /api/v1/reports/download/<task_id>/`

**Description:**
Downloads the generated report file. Returns the file as binary data with appropriate headers for the file format.

**Authentication Required:** Yes

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | string | Task ID of completed report |

**Response Headers (Success):**
```http
HTTP/1.1 200 OK
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="transaction_report_20241227_160000.xlsx"
Content-Length: 13107200
Cache-Control: private, max-age=0
X-Report-Generated-At: 2024-12-27T16:00:15+05:30
X-Report-Expires-At: 2024-12-28T16:00:15+05:30
```

**Response Body:** Binary file data

**Error Response (404 Not Found):**
```json
{
    "success": false,
    "message": "Report not found or expired",
    "error_code": "REPORT_001",
    "details": {
        "task_id": "task_20241227_160000_a1b2c3d4",
        "expired": true,
        "expired_at": "2024-12-28T16:00:15+05:30"
    }
}
```

---

### 4. List Generated Reports
**Endpoint:** `GET /api/v1/reports/list/`

**Description:**
Lists all reports generated by the authenticated user or all reports for admin users. Includes generation history, download counts, and expiry information.

**Authentication Required:** Yes

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status (completed/failed/processing) |
| report_type | string | Filter by report type |
| date_from | date | Reports generated after this date |
| page | integer | Page number |
| page_size | integer | Results per page |

**Success Response (200 OK):**
```json
{
    "success": true,
    "count": 45,
    "results": [
        {
            "task_id": "task_20241227_160000_a1b2c3d4",
            "title": "Monthly Transaction Report - December 2024",
            "type": "transaction",
            "format": "excel",
            "status": "COMPLETED",
            "created_at": "2024-12-27T16:00:00+05:30",
            "completed_at": "2024-12-27T16:00:15+05:30",
            "created_by": "admin@sabpaisa.com",
            "file_size_mb": 12.5,
            "records_count": 50000,
            "download_count": 3,
            "last_downloaded": "2024-12-27T17:30:00+05:30",
            "expires_at": "2024-12-28T16:00:15+05:30",
            "download_url": "/api/v1/reports/download/task_20241227_160000_a1b2c3d4/",
            "parameters": {
                "date_range": "2024-12-01 to 2024-12-31",
                "filters_applied": ["payment_mode", "status"]
            }
        }
    ]
}
```

---

## Common Parameters Reference

### Date Filters
| Parameter | Description | Example |
|-----------|-------------|---------|
| date_filter | Predefined date ranges | `today`, `3days`, `week`, `month`, `quarter`, `year`, `custom` |
| date_from | Start date for custom range | `2024-12-01` |
| date_to | End date for custom range | `2024-12-31` |

### Pagination
| Parameter | Default | Max | Description |
|-----------|---------|-----|-------------|
| page | 1 | - | Page number |
| page_size | 50 | 200 | Results per page |

### Sorting
| Parameter | Description | Examples |
|-----------|-------------|----------|
| order_by | Sort field (prefix - for descending) | `trans_date`, `-paid_amount`, `client_name` |

### Search & Filtering
| Parameter | Description | Examples |
|-----------|-------------|----------|
| search | General search across multiple fields | `john@example.com`, `SP202412270001` |
| q | Alternative to search parameter | Same as search |

---

## Error Handling Guide

### Error Response Structure
```json
{
    "success": false,
    "message": "Human-readable error message",
    "error_code": "UNIQUE_ERROR_CODE",
    "details": {
        "field_errors": {},
        "suggestions": [],
        "support_reference": "REF_123456"
    },
    "timestamp": "2024-12-27T16:00:00+05:30"
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|------------|------------|-------------|
| 400 | VALIDATION_ERROR | Invalid request parameters |
| 401 | AUTH_REQUIRED | Authentication required |
| 401 | TOKEN_EXPIRED | JWT token expired |
| 403 | PERMISSION_DENIED | Insufficient permissions |
| 404 | RESOURCE_NOT_FOUND | Requested resource not found |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |
| 503 | SERVICE_UNAVAILABLE | Temporary service issue |

---

## Rate Limiting & Throttling

### Rate Limits by Endpoint Type

| Endpoint Category | Authenticated | Anonymous | Window |
|------------------|---------------|-----------|---------|
| Authentication | 5 requests | 3 requests | 1 minute |
| Transaction Search | 100 requests | - | 1 minute |
| Transaction Export | 5 requests | - | 5 minutes |
| Analytics | 30 requests | - | 1 minute |
| Report Generation | 10 requests | - | 5 minutes |
| Settlement APIs | 50 requests | - | 1 minute |

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1703684400
X-RateLimit-Reset-After: 45
```

### Rate Limit Exceeded Response (429)
```json
{
    "success": false,
    "message": "Rate limit exceeded",
    "error_code": "RATE_LIMIT",
    "details": {
        "limit": 100,
        "window": "1 minute",
        "retry_after": 45,
        "reset_at": "2024-12-27T16:01:00+05:30"
    }
}
```

---

## QwikForms APIs

### Overview
QwikForms APIs provide comprehensive transaction and form data management for the QwikForms payment collection system. All QwikForms endpoints are **Admin-only** and require the user to have `ADMIN` role.

**Database:** spQwikForm
**Main Tables:** data_transactions, data_form, college_master
**Access Control:** Admin users only
**Base Path:** `/api/v1/qwikforms/`

### Authentication
All QwikForms APIs require:
- Valid JWT Bearer token
- User role must be `ADMIN`
- Authenticated via `IsAdminUser` permission class

---

### 1. QwikForms Transaction History

#### Get All Transactions with Form Data
**Endpoint:** `GET /api/v1/qwikforms/transactions/`

**Description:**
Retrieves QwikForms transactions with associated form submission data. Returns combined transaction and form details in a single response.

**Authentication Required:** Yes (Admin only)
**Database:** ✅ Real - queries `data_transactions` and `data_form` tables
**Response Time:** <200ms P95

**Request Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| date_from | string (YYYY-MM-DD) | No | Start date for filtering |
| date_to | string (YYYY-MM-DD) | No | End date for filtering |
| trans_status | string | No | Transaction status: SUCCESS, FAILED, PENDING |
| trans_paymode | string | No | Payment mode: UPI, CC, DC, NB, WALLET |
| client_id | string | No | Filter by client ID |
| form_id | integer | No | Filter by specific form ID |
| settlement_status | string | No | Settlement status: COMPLETED, PENDING, PROCESSING |
| search | string | No | Search in trans_id, name, email, contact |
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Results per page (default: 50, max: 200) |

**Example Request:**
```http
GET /api/v1/qwikforms/transactions/?date_from=2025-01-01&date_to=2025-01-31&trans_status=SUCCESS&page=1&page_size=50
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "count": 150,
    "next": "http://localhost:8000/api/v1/qwikforms/transactions/?page=2",
    "previous": null,
    "results": [
        {
            "transaction_id": 12345,
            "trans_id": "QF202501150001",
            "sp_trans_id": "SP1234567890",
            "trans_date": "2025-01-15T14:30:25+05:30",
            "trans_amount": 5000.00,
            "trans_status": "SUCCESS",
            "trans_paymode": "UPI",
            "pg_trans_id": "PG987654321",
            "pg_resp_code": "0000",
            "bank_reference_no": "BNK123456789",
            "customer_name": "Rajesh Kumar",
            "customer_email": "rajesh.kumar@example.com",
            "customer_contact": "9876543210",
            "act_amount": 4950.00,
            "trans_charges": 50.00,
            "trans_other_chrg": 0.00,
            "settlement_status": "COMPLETED",
            "settlement_date": "2025-01-16",
            "settlement_amount": 4950.00,
            "is_settled": "Y",
            "refund_id": null,
            "refund_amount": null,
            "refund_submit_date": null,
            "refund_close_date": null,
            "form_id": 456,
            "form_fee_name": "Application Fee - B.Tech 2025",
            "client_id": "COLL001",
            "client_name": "ABC Engineering College",
            "bid": "BID123",
            "cid": "CID456",
            "form_data": {
                "form_id": 456,
                "form_applicant_id": "APP2025001",
                "name": "Rajesh Kumar",
                "email": "rajesh.kumar@example.com",
                "contact": "9876543210",
                "dob_date": "2005-08-15",
                "form_status": "SUBMITTED",
                "form_number": "FRM2025001",
                "form_fee_name": "Application Fee - B.Tech 2025",
                "trans_amount": 5000.00,
                "form_data_json": {
                    "course": "B.Tech",
                    "branch": "Computer Science",
                    "previous_education": "12th - 95%",
                    "address": "123 Main Street, Mumbai",
                    "father_name": "Suresh Kumar",
                    "mother_name": "Priya Kumar"
                },
                "udf_field1": "Category: General",
                "udf_field2": "Quota: Merit",
                "udf_field3": "State: Maharashtra",
                "udf_field4": "City: Mumbai",
                "udf_field5": "Entrance Exam: JEE Main",
                "udf_field6": "Rank: 1234",
                "udf_field7": null,
                "udf_field8": null,
                "udf_field9": null,
                "udf_field10": null,
                "payer_id": "PAY123",
                "payer_aadhaar": "XXXX-XXXX-5678",
                "payer_pan": "ABCDE1234F",
                "code": "APP2025",
                "form_date": "2025-01-15T10:20:15+05:30"
            }
        }
    ]
}
```

**Error Response (403 Forbidden - Non-Admin User):**
```json
{
    "success": false,
    "message": "You do not have permission to perform this action",
    "error_code": "PERMISSION_DENIED",
    "details": {
        "required_role": "ADMIN",
        "user_role": "MERCHANT"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "message": "Invalid date format",
    "error_code": "VALIDATION_ERROR",
    "details": {
        "date_from": ["Enter a valid date in YYYY-MM-DD format"]
    }
}
```

---

#### Get Single Transaction Detail
**Endpoint:** `GET /api/v1/qwikforms/transactions/{id}/`

**Description:**
Retrieves detailed information for a single transaction including complete form data, client details, and settlement information.

**Authentication Required:** Yes (Admin only)
**Database:** ✅ Real - queries `data_transactions`, `data_form`, `college_master` tables

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Transaction ID (primary key) |

**Example Request:**
```http
GET /api/v1/qwikforms/transactions/12345/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "id": 12345,
        "trans_id": "QF202501150001",
        "sp_trans_id": "SP1234567890",
        "trans_date": "2025-01-15T14:30:25+05:30",
        "trans_amount": 5000.00,
        "trans_status": "SUCCESS",
        "trans_paymode": "UPI",
        "pg_trans_id": "PG987654321",
        "bank_reference_no": "BNK123456789",
        "settlement_status": "COMPLETED",
        "settlement_date": "2025-01-16",
        "settlement_amount": 4950.00,
        "client_id": "COLL001",
        "form_id": 456,
        "form_details": {
            "form_id": 456,
            "name": "Rajesh Kumar",
            "email": "rajesh.kumar@example.com",
            "contact": "9876543210",
            "form_status": "SUBMITTED",
            "form_data_json": {
                "course": "B.Tech",
                "branch": "Computer Science"
            }
        },
        "client_details": {
            "college_id": 101,
            "college_code": "COLL001",
            "college_name": "ABC Engineering College",
            "state": "Maharashtra",
            "address": "Education Hub, Mumbai",
            "contact": "022-12345678",
            "email_id": "info@abcengineering.edu",
            "college_url": "https://www.abcengineering.edu"
        }
    }
}
```

---

### 2. QwikForms Settlement APIs

#### Get Settled Transactions
**Endpoint:** `GET /api/v1/qwikforms/settlements/settled/`

**Description:**
Retrieves all successfully settled QwikForms transactions with settlement details and summary.

**Authentication Required:** Yes (Admin only)
**Database:** ✅ Real - queries `data_transactions` table

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| date_from | string (YYYY-MM-DD) | No | Start date for filtering |
| date_to | string (YYYY-MM-DD) | No | End date for filtering |
| client_id | string | No | Filter by client ID |

**Example Request:**
```http
GET /api/v1/qwikforms/settlements/settled/?date_from=2025-01-01&date_to=2025-01-31
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "count": 245,
    "summary": {
        "total_transaction_amount": 1225000.00,
        "total_settlement_amount": 1201250.00,
        "total_charges": 23750.00
    },
    "results": [
        {
            "transaction_id": 12345,
            "trans_id": "QF202501150001",
            "sp_trans_id": "SP1234567890",
            "trans_date": "2025-01-15T14:30:25+05:30",
            "trans_amount": 5000.00,
            "settlement_amount": 4950.00,
            "settlement_date": "2025-01-16",
            "settlement_status": "COMPLETED",
            "settlement_by": "AUTO",
            "is_settled": "Y",
            "trans_charges": 50.00,
            "customer_name": "Rajesh Kumar",
            "customer_email": "rajesh.kumar@example.com",
            "customer_contact": "9876543210",
            "form_fee_name": "Application Fee - B.Tech 2025",
            "client_name": "ABC Engineering College"
        }
    ]
}
```

---

#### Get Pending Settlements
**Endpoint:** `GET /api/v1/qwikforms/settlements/pending/`

**Description:**
Retrieves all pending settlement transactions that have successful payment status but are not yet settled.

**Authentication Required:** Yes (Admin only)

**Success Response (200 OK):**
```json
{
    "success": true,
    "count": 45,
    "summary": {
        "total_pending_amount": 225000.00
    },
    "results": [
        {
            "transaction_id": 12346,
            "trans_id": "QF202501300001",
            "sp_trans_id": "SP1234567891",
            "trans_date": "2025-01-30T10:15:30+05:30",
            "trans_amount": 5000.00,
            "settlement_amount": 0.00,
            "settlement_date": null,
            "settlement_status": "PENDING",
            "settlement_by": null,
            "is_settled": "N",
            "trans_charges": 50.00,
            "customer_name": "Priya Sharma",
            "customer_email": "priya.sharma@example.com",
            "customer_contact": "9876543211",
            "form_fee_name": "Hostel Fee - Semester 1",
            "client_name": "ABC Engineering College"
        }
    ]
}
```

---

#### Get Refund Transactions
**Endpoint:** `GET /api/v1/qwikforms/settlements/refunds/`

**Description:**
Retrieves all refunded transactions with refund details.

**Authentication Required:** Yes (Admin only)

**Success Response (200 OK):**
```json
{
    "success": true,
    "count": 12,
    "summary": {
        "total_refund_amount": 60000.00
    },
    "results": [
        {
            "transaction_id": 12347,
            "trans_id": "QF202501200001",
            "sp_trans_id": "SP1234567892",
            "trans_date": "2025-01-20T09:45:15+05:30",
            "trans_amount": 5000.00,
            "refund_id": "RFD202501210001",
            "refund_amount": "5000.00",
            "refund_submit_date": "2025-01-21",
            "refund_close_date": "2025-01-22",
            "refund_job": "COMPLETED",
            "customer_name": "Amit Patel",
            "customer_email": "amit.patel@example.com",
            "customer_contact": "9876543212",
            "form_fee_name": "Application Fee - B.Tech 2025",
            "trans_status": "SUCCESS"
        }
    ]
}
```

---

### 3. QwikForms Analytics APIs

#### Get Analytics Dashboard
**Endpoint:** `GET /api/v1/qwikforms/analytics/dashboard/`

**Description:**
Provides comprehensive analytics dashboard with transaction summary, payment mode distribution, form-wise analytics, client-wise analytics, and daily trends.

**Authentication Required:** Yes (Admin only)
**Database:** ✅ Real - aggregates data from `data_transactions` table

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| date_from | string (YYYY-MM-DD) | No | Start date for analytics period |
| date_to | string (YYYY-MM-DD) | No | End date for analytics period |

**Example Request:**
```http
GET /api/v1/qwikforms/analytics/dashboard/?date_from=2025-01-01&date_to=2025-01-31
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "summary": {
            "total_transactions": 1500,
            "successful_transactions": 1350,
            "failed_transactions": 120,
            "pending_transactions": 30,
            "success_rate": 90.0,
            "total_volume": 7500000.00,
            "total_settled_amount": 7350000.00,
            "pending_settlement_amount": 150000.00,
            "avg_transaction_value": 5000.00
        },
        "by_payment_mode": {
            "UPI": {
                "count": 800,
                "volume": 4000000.00,
                "success_rate": 95.0
            },
            "CC": {
                "count": 400,
                "volume": 2000000.00,
                "success_rate": 88.0
            },
            "DC": {
                "count": 200,
                "volume": 1000000.00,
                "success_rate": 85.0
            },
            "NB": {
                "count": 80,
                "volume": 400000.00,
                "success_rate": 82.0
            },
            "WALLET": {
                "count": 20,
                "volume": 100000.00,
                "success_rate": 90.0
            }
        },
        "by_form": [
            {
                "form_id": 456,
                "fee_name": "Application Fee - B.Tech 2025",
                "count": 500,
                "volume": 2500000.00
            },
            {
                "form_id": 457,
                "fee_name": "Hostel Fee - Semester 1",
                "count": 300,
                "volume": 1500000.00
            }
        ],
        "by_client": [
            {
                "client_id": "COLL001",
                "client_name": "ABC Engineering College",
                "count": 800,
                "volume": 4000000.00
            },
            {
                "client_id": "COLL002",
                "client_name": "XYZ Medical College",
                "count": 500,
                "volume": 3500000.00
            }
        ],
        "daily_trend": [
            {
                "date": "2025-01-01",
                "count": 45,
                "volume": 225000.00,
                "success_rate": 91.0
            },
            {
                "date": "2025-01-02",
                "count": 52,
                "volume": 260000.00,
                "success_rate": 89.0
            }
        ]
    }
}
```

---

#### Get Form-wise Analytics
**Endpoint:** `GET /api/v1/qwikforms/analytics/by-form/`

**Description:**
Provides detailed analytics grouped by form/fee type.

**Authentication Required:** Yes (Admin only)

**Success Response (200 OK):**
```json
{
    "success": true,
    "count": 15,
    "results": [
        {
            "form_id": 456,
            "form_name": "Application Fee - B.Tech 2025",
            "total_transactions": 500,
            "successful_transactions": 450,
            "failed_transactions": 45,
            "success_rate": 90.0,
            "total_volume": 2500000.00,
            "average_amount": 5000.00
        },
        {
            "form_id": 457,
            "form_name": "Hostel Fee - Semester 1",
            "total_transactions": 300,
            "successful_transactions": 270,
            "failed_transactions": 28,
            "success_rate": 90.0,
            "total_volume": 1500000.00,
            "average_amount": 5000.00
        }
    ]
}
```

---

#### Get Client-wise Analytics
**Endpoint:** `GET /api/v1/qwikforms/analytics/by-client/`

**Description:**
Provides detailed analytics grouped by client/institution.

**Authentication Required:** Yes (Admin only)

**Success Response (200 OK):**
```json
{
    "success": true,
    "count": 25,
    "results": [
        {
            "client_id": "COLL001",
            "client_name": "ABC Engineering College",
            "total_transactions": 800,
            "successful_transactions": 720,
            "total_volume": 4000000.00,
            "settled_amount": 3920000.00
        },
        {
            "client_id": "COLL002",
            "client_name": "XYZ Medical College",
            "total_transactions": 500,
            "successful_transactions": 450,
            "total_volume": 3500000.00,
            "settled_amount": 3430000.00
        }
    ]
}
```

---

#### Get Payment Mode Distribution
**Endpoint:** `GET /api/v1/qwikforms/analytics/payment-mode/`

**Description:**
Provides analytics on payment mode usage and success rates.

**Authentication Required:** Yes (Admin only)

**Success Response (200 OK):**
```json
{
    "success": true,
    "results": [
        {
            "payment_mode": "UPI",
            "total_transactions": 800,
            "successful_transactions": 760,
            "failed_transactions": 40,
            "success_rate": 95.0,
            "total_volume": 4000000.00,
            "average_amount": 5000.00
        },
        {
            "payment_mode": "CC",
            "total_transactions": 400,
            "successful_transactions": 352,
            "failed_transactions": 48,
            "success_rate": 88.0,
            "total_volume": 2000000.00,
            "average_amount": 5000.00
        },
        {
            "payment_mode": "DC",
            "total_transactions": 200,
            "successful_transactions": 170,
            "failed_transactions": 30,
            "success_rate": 85.0,
            "total_volume": 1000000.00,
            "average_amount": 5000.00
        }
    ]
}
```

---

### 4. QwikForms Report Generation APIs

#### Generate Excel Report
**Endpoint:** `POST /api/v1/qwikforms/reports/generate-excel/`

**Description:**
Generates comprehensive Excel report with multiple sheets containing transaction data, form data, and summaries.

**Authentication Required:** Yes (Admin only)
**Response Type:** Binary (Excel file)
**Max Records:** 5000 per sheet

**Request Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "filters": {
        "date_from": "2025-01-01",
        "date_to": "2025-01-31",
        "trans_status": "SUCCESS",
        "trans_paymode": "UPI",
        "client_id": "COLL001",
        "form_id": 456
    }
}
```

**Request Body Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filters | object | Yes | Filter criteria for report |
| filters.date_from | string | No | Start date (YYYY-MM-DD) |
| filters.date_to | string | No | End date (YYYY-MM-DD) |
| filters.trans_status | string | No | Transaction status filter |
| filters.trans_paymode | string | No | Payment mode filter |
| filters.client_id | string | No | Client ID filter |
| filters.form_id | integer | No | Form ID filter |

**Success Response (200 OK):**
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="qwikforms_report_20250130_143025.xlsx"

[Binary Excel file data]
```

**Excel Report Structure:**
- **Sheet 1: Summary** - Overall statistics and totals
- **Sheet 2: Transactions** - Complete transaction details
- **Sheet 3: Form Data** - Form submission details with UDF fields

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "message": "Invalid filter parameters",
    "error_code": "VALIDATION_ERROR",
    "details": {
        "date_from": ["Date format must be YYYY-MM-DD"]
    }
}
```

---

#### Generate CSV Report
**Endpoint:** `POST /api/v1/qwikforms/reports/generate-csv/`

**Description:**
Generates CSV report with transaction and form data. Includes UTF-8 BOM for Excel compatibility.

**Authentication Required:** Yes (Admin only)
**Response Type:** text/csv
**Max Records:** 10000

**Request Body:**
```json
{
    "filters": {
        "date_from": "2025-01-01",
        "date_to": "2025-01-31",
        "trans_status": "SUCCESS"
    }
}
```

**Success Response (200 OK):**
```
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename="qwikforms_report_20250130_143025.csv"

Transaction ID,SP Trans ID,Date,Amount,Status,Payment Mode,Customer Name,Email,Contact,...
QF202501150001,SP1234567890,2025-01-15 14:30:25,5000.00,SUCCESS,UPI,Rajesh Kumar,rajesh.kumar@example.com,9876543210,...
```

---

#### Generate PDF Report (HTML)
**Endpoint:** `POST /api/v1/qwikforms/reports/generate-pdf/`

**Description:**
Generates HTML report optimized for PDF printing. Can be printed to PDF from browser.

**Authentication Required:** Yes (Admin only)
**Response Type:** text/html
**Max Records:** 1000

**Request Body:**
```json
{
    "filters": {
        "date_from": "2025-01-01",
        "date_to": "2025-01-31"
    }
}
```

**Success Response (200 OK):**
```
Content-Type: text/html; charset=utf-8
Content-Disposition: attachment; filename="qwikforms_report_20250130_143025.html"

<!DOCTYPE html>
<html>
<head>
    <title>QwikForms Report</title>
    <style>
        /* Styled for PDF printing */
    </style>
</head>
<body>
    <h1>QwikForms Transaction Report</h1>
    <!-- Report content -->
</body>
</html>
```

---

### QwikForms API Summary

**Total Endpoints:** 12

**Transaction APIs:** 2
- List transactions with form data
- Get single transaction detail

**Settlement APIs:** 3
- Settled transactions
- Pending settlements
- Refund transactions

**Analytics APIs:** 4
- Analytics dashboard
- Form-wise analytics
- Client-wise analytics
- Payment mode distribution

**Report APIs:** 3
- Excel report generation
- CSV report generation
- PDF/HTML report generation

**Access Control:** All endpoints require Admin role
**Database:** spQwikForm (separate from main SabPaisa database)
**Key Features:**
- Combined transaction + form data views
- Multi-table joins (transactions, forms, clients)
- Real-time analytics with aggregations
- Comprehensive filtering and search
- Export capabilities with proper data formatting

---

## Security & Compliance

### Authentication Requirements
- All endpoints except login/refresh require JWT Bearer token
- Tokens expire after 24 hours (access) and 7 days (refresh)
- Failed login attempts are tracked and accounts locked after 5 failures
- QwikForms endpoints require ADMIN role exclusively

### Data Security
- All API communication must use HTTPS
- PCI DSS compliance for card data
- PII data is encrypted at rest
- Audit logs maintained for all transactions

### IP Whitelisting
- Production APIs support IP whitelisting
- Contact support to configure allowed IPs

---

## Support & Resources

### Contact Information
- **API Support Email:** api-support@sabpaisa.com
- **Technical Documentation:** https://api.sabpaisa.com/docs
- **Status Page:** https://status.sabpaisa.com
- **Support Portal:** https://support.sabpaisa.com

### Webhook Configuration
- Configure webhooks in merchant dashboard
- Supported events: settlement.completed, refund.processed, chargeback.raised
- Retry policy: 3 attempts with exponential backoff

### SDKs & Libraries
- **PHP:** `composer require sabpaisa/api-sdk`
- **Python:** `pip install sabpaisa-api`
- **Node.js:** `npm install @sabpaisa/api-client`
- **Java:** Maven repository available

---

**Document Version:** 2.0
**Last Updated:** December 2024
**API Version:** v1
**Total Endpoints:** 56+

---

© 2024 SabPaisa. All rights reserved.