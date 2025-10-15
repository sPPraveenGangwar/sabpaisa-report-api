# SabPaisa Reports API - Complete Documentation

## Table of Contents
1. [Authentication APIs](#authentication-apis)
2. [Transaction APIs](#transaction-apis)
3. [Settlement APIs](#settlement-apis)
4. [Analytics APIs](#analytics-apis)
5. [Report Generation APIs](#report-generation-apis)
6. [Common Search Parameters](#common-search-parameters)

---

## Authentication APIs

### 1. User Login
**Endpoint:** `POST /api/v1/auth/login/`
**Description:** Authenticate user and get JWT tokens

**Request:**
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
        "is_active": true
    }
}
```

**Error Response (401):**
```json
{
    "success": false,
    "message": "Invalid credentials"
}
```

### 2. Token Refresh
**Endpoint:** `POST /api/v1/auth/token/refresh/`
**Description:** Refresh access token using refresh token

**Request:**
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
**Description:** Blacklist refresh token
**Headers:** `Authorization: Bearer <access_token>`

**Request:**
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
**Headers:** `Authorization: Bearer <access_token>`

**Request:**
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

**Error Response (400):**
```json
{
    "success": false,
    "message": "Invalid old password"
}
```

---

## Transaction APIs

### 1. Get Merchant Transaction History
**Endpoint:** `GET /api/v1/transactions/merchant-history/`
**Description:** Get transaction history for logged-in merchant
**Headers:** `Authorization: Bearer <access_token>`
**Response Time:** <450ms P95

**Query Parameters:**
```
?date_filter=month
&payment_mode=UPI
&status=SUCCESS
&min_amount=1000
&max_amount=50000
&page=1
&page_size=50
```

**Response (200 OK):**
```json
{
    "success": true,
    "filter_summary": "Current month | Payment mode: UPI | Status: SUCCESS | Amount: ₹1000 - ₹50000",
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
            "status_msg": "Transaction successful",
            "sabpaisa_trans_status": "SUCCESS",
            "payment_mode": "UPI",
            "paid_amount": 2500.00,
            "payee_profile": "Default",
            "payee_name": "John Doe",
            "payee_email": "john.doe@example.com",
            "payee_mob": "9876543210",
            "payee_add": "123 Main St, Mumbai",
            "pg_name": "HDFC",
            "bank_name": "HDFC Bank",
            "bank_txn_id": "HDFC2024122798765",
            "is_settled": true,
            "settlement_date": "2024-12-28",
            "settlement_amount": 2475.00,
            "sabpaisa_charges": 25.00,
            "client_settle_amount": 2475.00
        },
        {
            "txn_id": "SP202412270002",
            "client_txn_id": "MERC001_TXN_98766",
            "client_code": "MERC001",
            "client_name": "ABC Merchants Pvt Ltd",
            "trans_date": "2024-12-27T15:15:00+05:30",
            "trans_complete_date": "2024-12-27T15:15:30+05:30",
            "status": "SUCCESS",
            "status_msg": "Transaction successful",
            "sabpaisa_trans_status": "SUCCESS",
            "payment_mode": "UPI",
            "paid_amount": 5000.00,
            "payee_profile": "Premium",
            "payee_name": "Jane Smith",
            "payee_email": "jane.smith@example.com",
            "payee_mob": "9876543211",
            "payee_add": "456 Park Ave, Delhi",
            "pg_name": "ICICI",
            "bank_name": "ICICI Bank",
            "bank_txn_id": "ICICI2024122798766",
            "is_settled": false,
            "settlement_date": null,
            "settlement_amount": null,
            "sabpaisa_charges": 50.00,
            "client_settle_amount": null
        }
    ]
}
```

### 2. Get Admin Transaction History
**Endpoint:** `GET /api/v1/transactions/admin-history/`
**Description:** Get all transactions (Admin only)
**Headers:** `Authorization: Bearer <admin_token>`
**Response Time:** <547ms P95

**Query Parameters:**
```
?merchant_code=MERC001,MERC002
&date_from=2024-12-01
&date_to=2024-12-31
&payment_mode=UPI,CC,DC
&status=SUCCESS,FAILED
&min_amount=100
&max_amount=100000
&order_by=-paid_amount
```

**Response (200 OK):**
```json
{
    "success": true,
    "filter_summary": "From 2024-12-01 to 2024-12-31 | Merchant: MERC001,MERC002 | Payment mode: UPI,CC,DC | Status: SUCCESS,FAILED | Amount: ₹100 - ₹100000",
    "count": 15234,
    "next": "http://api.sabpaisa.com/api/v1/transactions/admin-history/?page=2",
    "previous": null,
    "results": [
        {
            "txn_id": "SP202412270003",
            "client_txn_id": "MERC002_TXN_12345",
            "client_code": "MERC002",
            "client_name": "XYZ Corporation",
            "trans_date": "2024-12-27T10:00:00+05:30",
            "status": "SUCCESS",
            "payment_mode": "CREDIT_CARD",
            "paid_amount": 75000.00,
            "payee_email": "corporate@xyz.com",
            "payee_mob": "9988776655",
            "bank_name": "AXIS Bank",
            "is_settled": true,
            "settlement_date": "2024-12-28",
            "settlement_amount": 73500.00
        }
    ]
}
```

### 3. Search Transaction by ID
**Endpoint:** `GET /api/v1/transactions/search/`
**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
```
?txn_id=SP202412270001
```
or
```
?client_txn_id=MERC001_TXN_98765
```

**Response (200 OK):**
```json
{
    "success": true,
    "filter_summary": "Transaction ID: SP202412270001",
    "count": 1,
    "data": {
        "txn_id": "SP202412270001",
        "client_txn_id": "MERC001_TXN_98765",
        "client_code": "MERC001",
        "client_name": "ABC Merchants Pvt Ltd",
        "trans_date": "2024-12-27T14:30:00+05:30",
        "status": "SUCCESS",
        "payment_mode": "UPI",
        "paid_amount": 2500.00,
        "full_details": {
            "payee_info": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "mobile": "9876543210",
                "address": "123 Main St, Mumbai"
            },
            "bank_info": {
                "pg_name": "HDFC",
                "bank_name": "HDFC Bank",
                "bank_txn_id": "HDFC2024122798765"
            },
            "settlement_info": {
                "is_settled": true,
                "settlement_date": "2024-12-28",
                "settlement_amount": 2475.00,
                "settlement_utr": "HDFC2024122898765"
            },
            "charges_info": {
                "sabpaisa_charges": 25.00,
                "gst_amount": 4.50,
                "total_charges": 29.50
            }
        }
    }
}
```

### 4. Generate Transaction Excel Report
**Endpoint:** `POST /api/v1/transactions/merchant-history-excel/`
**Headers:** `Authorization: Bearer <access_token>`
**Response Time:** <2.5s for 25K records

**Request:**
```json
{
    "date_filter": "month",
    "payment_mode": "UPI,CC,DC",
    "status": "SUCCESS",
    "min_amount": 1000,
    "max_amount": 50000,
    "max_records": 25000,
    "include_summary": true
}
```

**Response (202 Accepted):**
```json
{
    "success": true,
    "message": "Excel generation initiated",
    "task_id": "task_20241227_143000",
    "estimated_time": "2-3 seconds",
    "download_url": "/api/v1/reports/download/task_20241227_143000/"
}
```

---

## Settlement APIs

### 1. Get Settled Transaction History
**Endpoint:** `GET /api/v1/settlements/settled-history/`
**Headers:** `Authorization: Bearer <access_token>`
**Response Time:** <156ms P95

**Query Parameters:**
```
?date_filter=week
&payment_mode=UPI
&settlement_status=COMPLETED
&use_settlement_date=true
&min_amount=1000
```

**Response (200 OK):**
```json
{
    "success": true,
    "filter_summary": "Last 7 days | Payment mode: UPI | Settlement Status: COMPLETED | Amount: ≥ ₹1000",
    "count": 342,
    "results": [
        {
            "txn_id": "SP202412260001",
            "client_code": "MERC001",
            "client_name": "ABC Merchants Pvt Ltd",
            "trans_date": "2024-12-26T10:30:00+05:30",
            "paid_amount": 5000.00,
            "settlement_date": "2024-12-27",
            "settlement_amount": 4900.00,
            "settlement_status": "COMPLETED",
            "settlement_utr": "HDFC2024122798765",
            "sabpaisa_charges": 100.00,
            "effective_settlement_amount": 4900.00,
            "payment_mode": "UPI",
            "bank_name": "HDFC Bank"
        }
    ]
}
```

### 2. Get Refund Transaction History
**Endpoint:** `GET /api/v1/settlements/refund-history/`
**Headers:** `Authorization: Bearer <access_token>`
**Response Time:** <142ms P95

**Query Parameters:**
```
?date_filter=month
&refund_status=COMPLETED
&use_refund_date=true
&min_refund_amount=100
&refund_reason=customer_request
```

**Response (200 OK):**
```json
{
    "success": true,
    "filter_summary": "Current month | Refund Status: COMPLETED | Refund Reason: customer_request",
    "count": 89,
    "results": [
        {
            "txn_id": "SP202412250001",
            "client_code": "MERC001",
            "trans_date": "2024-12-25T09:00:00+05:30",
            "paid_amount": 3000.00,
            "refund_date": "2024-12-26",
            "refund_amount": 3000.00,
            "refunded_amount": 3000.00,
            "refund_status_code": "COMPLETED",
            "refund_reason": "customer_request",
            "refund_initiated_on": "2024-12-26T10:00:00+05:30",
            "refund_completed_on": "2024-12-26T14:00:00+05:30",
            "refund_reference": "REF2024122600001"
        }
    ]
}
```

### 3. Get Chargeback Transaction History
**Endpoint:** `GET /api/v1/settlements/chargeback-history/`
**Headers:** `Authorization: Bearer <access_token>`
**Response Time:** <158ms P95

**Query Parameters:**
```
?date_from=2024-12-01
&date_to=2024-12-31
&chargeback_status=DISPUTED
&use_chargeback_date=true
&min_chargeback_amount=500
```

**Response (200 OK):**
```json
{
    "success": true,
    "filter_summary": "From 2024-12-01 to 2024-12-31 | Chargeback Status: DISPUTED",
    "count": 23,
    "results": [
        {
            "txn_id": "SP202412200001",
            "client_code": "MERC001",
            "trans_date": "2024-12-20T15:00:00+05:30",
            "paid_amount": 8000.00,
            "charge_back_date": "2024-12-25",
            "charge_back_amount": 8000.00,
            "charge_back_status": "DISPUTED",
            "charge_back_reason": "Fraudulent transaction claim",
            "is_charge_back": true,
            "dispute_raised_on": "2024-12-24T10:00:00+05:30",
            "dispute_reference": "CBK2024122400001"
        }
    ]
}
```

### 4. Grouped Settlement View
**Endpoint:** `GET /api/v1/settlements/grouped-view/`
**Headers:** `Authorization: Bearer <access_token>`
**Response Time:** <203ms P95

**Query Parameters:**
```
?date_filter=month
&group_by=date
&payment_mode=UPI
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": [
        {
            "date": "2024-12-27",
            "total_count": 145,
            "total_amount": 725000.00,
            "total_effective": 710500.00
        },
        {
            "date": "2024-12-26",
            "total_count": 132,
            "total_amount": 660000.00,
            "total_effective": 646800.00
        }
    ]
}
```

### 5. Generate Settlement Excel Reports
**Endpoint:** `POST /api/v1/settlements/settled-excel-v2/`
**Headers:** `Authorization: Bearer <access_token>`
**Response Time:** <3.2s

**Request:**
```json
{
    "date_from": "2024-12-01",
    "date_to": "2024-12-31",
    "payment_mode": "ALL",
    "settlement_status": "COMPLETED",
    "use_settlement_date": true,
    "include_charts": true,
    "max_records": 15000
}
```

**Response (202 Accepted):**
```json
{
    "success": true,
    "message": "Enhanced Settlement Excel generation initiated",
    "task_id": "task_20241227_150000"
}
```

---

## Analytics APIs

### 1. Merchant Analytics Dashboard
**Endpoint:** `GET /api/v1/analytics/merchant-analytics/`
**Headers:** `Authorization: Bearer <access_token>`
**Cache:** 30 minutes

**Query Parameters:**
```
?date_filter=month
&payment_mode=UPI
&merchant_code=MERC001  (Admin only)
```

**Response (200 OK):**
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
            "settled_amount": 20500000.00,
            "pending_settlement": 2115000.00
        },
        "payment_mode_distribution": [
            {
                "mode": "UPI",
                "count": 2451,
                "volume": 12255000.00
            },
            {
                "mode": "CREDIT_CARD",
                "count": 1203,
                "volume": 7218000.00
            },
            {
                "mode": "DEBIT_CARD",
                "count": 869,
                "volume": 3142000.00
            }
        ],
        "daily_trend": [
            {
                "date": "2024-12-27",
                "total": 156,
                "successful": 142,
                "volume": 780000.00
            },
            {
                "date": "2024-12-26",
                "total": 148,
                "successful": 135,
                "volume": 740000.00
            }
        ],
        "hourly_distribution": [
            {
                "hour": 10,
                "count": 523
            },
            {
                "hour": 11,
                "count": 612
            },
            {
                "hour": 14,
                "count": 498
            }
        ],
        "top_customers": [
            {
                "email": "corporate@bigclient.com",
                "transaction_count": 89,
                "total_amount": 890000.00
            }
        ],
        "period": {
            "start_date": "2024-12-01T00:00:00+05:30",
            "end_date": "2024-12-27T23:59:59+05:30",
            "days": 27
        }
    }
}
```

### 2. Payment Mode Analytics
**Endpoint:** `GET /api/v1/analytics/payment-mode-analytics/`
**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
```
?payment_mode=UPI
&date_filter=week
&merchant_code=MERC001
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "payment_mode": "UPI",
        "metrics": {
            "total_transactions": 892,
            "successful": 823,
            "failed": 69,
            "success_rate": 92.26,
            "total_volume": 4460000.00,
            "avg_transaction": 5420.90
        },
        "gateway_performance": [
            {
                "gateway": "HDFC",
                "total": 456,
                "successful": 425,
                "success_rate": 93.20,
                "volume": 2280000.00
            },
            {
                "gateway": "ICICI",
                "total": 436,
                "successful": 398,
                "success_rate": 91.28,
                "volume": 2180000.00
            }
        ],
        "daily_trend": [
            {
                "date": "2024-12-27",
                "count": 127,
                "successful": 118,
                "volume": 635000.00
            }
        ]
    }
}
```

### 3. Settlement Analytics
**Endpoint:** `GET /api/v1/analytics/settlement-analytics/`
**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
```
?date_filter=month
&merchant_code=ALL
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "summary": {
            "total_transaction_amount": 45230000.00,
            "total_settled": 42500000.00,
            "pending_settlement": 2730000.00,
            "settlement_rate": 93.96,
            "avg_settlement_tat_hours": 24.5
        },
        "settlement_timeline": [
            {
                "date": "2024-12-27",
                "count": 234,
                "amount": 1170000.00
            },
            {
                "date": "2024-12-26",
                "count": 221,
                "amount": 1105000.00
            }
        ],
        "bank_wise_settlement": [
            {
                "bank": "HDFC Bank",
                "count": 1245,
                "amount": 18675000.00
            },
            {
                "bank": "ICICI Bank",
                "count": 1123,
                "amount": 16845000.00
            }
        ]
    }
}
```

### 4. Refund & Chargeback Analytics
**Endpoint:** `GET /api/v1/analytics/refund-chargeback/`
**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
```
?date_filter=month
&merchant_code=MERC001
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "summary": {
            "total_refunds": 156,
            "total_refund_amount": 780000.00,
            "refunded_amount": 750000.00,
            "total_chargebacks": 23,
            "total_chargeback_amount": 230000.00
        },
        "refund_trend": [
            {
                "date": "2024-12-27",
                "count": 8,
                "amount": 40000.00
            }
        ],
        "chargeback_trend": [
            {
                "date": "2024-12-25",
                "count": 2,
                "amount": 20000.00
            }
        ],
        "top_refund_reasons": [
            {
                "reason": "Customer request",
                "count": 89
            },
            {
                "reason": "Product issue",
                "count": 34
            },
            {
                "reason": "Duplicate payment",
                "count": 23
            }
        ]
    }
}
```

### 5. Executive Dashboard (Admin Only)
**Endpoint:** `GET /api/v1/analytics/executive-dashboard/`
**Headers:** `Authorization: Bearer <admin_token>`
**Cache:** 10 minutes

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "today": {
            "date": "2024-12-27",
            "transactions": 3456,
            "volume": 17280000.00,
            "success_rate": 91.5
        },
        "month_to_date": {
            "start_date": "2024-12-01",
            "end_date": "2024-12-27",
            "transactions": 87234,
            "volume": 436170000.00,
            "success_rate": 89.8
        },
        "merchants": {
            "total": 145,
            "active": 128,
            "activation_rate": 88.28
        },
        "top_merchants": [
            {
                "code": "MERC001",
                "name": "ABC Merchants Pvt Ltd",
                "volume": 45230000.00,
                "transactions": 9046
            },
            {
                "code": "MERC002",
                "name": "XYZ Corporation",
                "volume": 38450000.00,
                "transactions": 7690
            }
        ],
        "payment_mode_performance": [
            {
                "mode": "UPI",
                "total": 45623,
                "successful": 42378,
                "success_rate": 92.89
            },
            {
                "mode": "CREDIT_CARD",
                "total": 23456,
                "successful": 20987,
                "success_rate": 89.47
            }
        ]
    }
}
```

### 6. Comparative Analytics (Admin Only)
**Endpoint:** `GET /api/v1/analytics/comparative/`
**Headers:** `Authorization: Bearer <admin_token>`

**Query Parameters for Period Comparison:**
```
?type=period
&current_days=30
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "current_period": {
            "start": "2024-11-27T00:00:00+05:30",
            "end": "2024-12-27T23:59:59+05:30",
            "metrics": {
                "total_transactions": 45678,
                "successful_transactions": 41234,
                "success_rate": 90.27,
                "total_volume": 228390000.00
            }
        },
        "previous_period": {
            "start": "2024-10-28T00:00:00+05:30",
            "end": "2024-11-27T23:59:59+05:30",
            "metrics": {
                "total_transactions": 42345,
                "successful_transactions": 37890,
                "success_rate": 89.48,
                "total_volume": 211725000.00
            }
        },
        "changes": {
            "total_transactions_change": 7.87,
            "successful_transactions_change": 8.82,
            "success_rate_change": 0.88,
            "total_volume_change": 7.88
        }
    }
}
```

**Query Parameters for Merchant Comparison:**
```
?type=merchant
&merchant_codes=MERC001,MERC002,MERC003
&days=30
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "period": {
            "start": "2024-11-27T00:00:00+05:30",
            "end": "2024-12-27T23:59:59+05:30"
        },
        "merchants": [
            {
                "merchant_code": "MERC001",
                "total_transactions": 15234,
                "successful_transactions": 13890,
                "success_rate": 91.18,
                "total_volume": 76170000.00,
                "avg_transaction": 5483.15
            },
            {
                "merchant_code": "MERC002",
                "total_transactions": 14567,
                "successful_transactions": 13023,
                "success_rate": 89.40,
                "total_volume": 72835000.00,
                "avg_transaction": 5593.84
            },
            {
                "merchant_code": "MERC003",
                "total_transactions": 12345,
                "successful_transactions": 11234,
                "success_rate": 91.00,
                "total_volume": 61725000.00,
                "avg_transaction": 5493.98
            }
        ]
    }
}
```

---

## Report Generation APIs

### 1. Generate Report
**Endpoint:** `POST /api/v1/reports/generate/`
**Headers:** `Authorization: Bearer <access_token>`

**Request:**
```json
{
    "report_type": "transaction",
    "format": "excel",
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
    "task_id": "task_20241227_160000",
    "report_type": "transaction",
    "format": "excel",
    "estimated_time": "5-10 seconds for 50K records"
}
```

### 2. Check Report Status
**Endpoint:** `GET /api/v1/reports/status/{task_id}/`
**Headers:** `Authorization: Bearer <access_token>`

**Response (200 OK - In Progress):**
```json
{
    "success": true,
    "task_id": "task_20241227_160000",
    "status": "processing",
    "progress": 45,
    "message": "Processing records... 22500 of 50000 completed"
}
```

**Response (200 OK - Completed):**
```json
{
    "success": true,
    "task_id": "task_20241227_160000",
    "status": "completed",
    "progress": 100,
    "download_url": "/api/v1/reports/download/task_20241227_160000/",
    "file_size": "4.5 MB",
    "expiry": "2024-12-28T16:00:00+05:30"
}
```

### 3. Download Report
**Endpoint:** `GET /api/v1/reports/download/{task_id}/`
**Headers:** `Authorization: Bearer <access_token>`

**Response:** Binary file download (Excel/CSV)

**Headers:**
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="transaction_report_20241227_160000.xlsx"
Content-Length: 4718592
```

---

## Common Search Parameters

All transaction and settlement APIs support these common search parameters:

### Date Filters
| Parameter | Description | Example |
|-----------|-------------|---------|
| `date_filter` | Predefined ranges | `today`, `3days`, `week`, `month`, `year`, `custom` |
| `date_from` | Custom start date | `2024-12-01` |
| `date_to` | Custom end date | `2024-12-31` |
| `use_settlement_date` | Use settlement date for filtering | `true` |
| `use_refund_date` | Use refund date for filtering | `true` |
| `use_chargeback_date` | Use chargeback date for filtering | `true` |

### Merchant Filters (Admin Only)
| Parameter | Description | Example |
|-----------|-------------|---------|
| `merchant_code` or `client_code` | Single or multiple merchants | `MERC001` or `MERC001,MERC002` |
| `client_name` | Partial merchant name search | `ABC Merch` |

### Transaction Filters
| Parameter | Description | Example |
|-----------|-------------|---------|
| `payment_mode` | Payment method(s) | `UPI`, `CC,DC`, `ALL` |
| `status` | Transaction status(es) | `SUCCESS`, `FAILED,PENDING` |
| `min_amount` | Minimum amount | `1000` |
| `max_amount` | Maximum amount | `50000` |
| `txn_id` | SabPaisa transaction ID | `SP202412270001` |
| `client_txn_id` | Client transaction ID | `MERC001_TXN_12345` |
| `search` or `q` | General search | Searches multiple fields |

### Settlement Specific
| Parameter | Description | Example |
|-----------|-------------|---------|
| `settlement_status` | Settlement status | `COMPLETED`, `PENDING` |
| `settlement_utr` | Settlement UTR | `HDFC2024122798765` |
| `refund_status` | Refund status | `COMPLETED`, `INITIATED` |
| `refund_reason` | Refund reason | `customer_request` |
| `chargeback_status` | Chargeback status | `DISPUTED`, `RESOLVED` |

### Pagination & Sorting
| Parameter | Description | Example |
|-----------|-------------|---------|
| `page` | Page number | `1`, `2`, `3` |
| `page_size` | Results per page | `50`, `100`, `200` |
| `order_by` | Sort field | `trans_date`, `-paid_amount` |

### Response Control
| Parameter | Description | Example |
|-----------|-------------|---------|
| `fields` | Limit returned fields | `basic`, `full`, `custom` |
| `include_summary` | Include summary stats | `true`, `false` |
| `format` | Response format | `json`, `xml` |

---

## Error Responses

### 400 Bad Request
```json
{
    "success": false,
    "message": "Invalid filter parameters",
    "errors": {
        "date_from": "Invalid date format. Use YYYY-MM-DD",
        "amount_range": "Minimum amount cannot be greater than maximum amount"
    }
}
```

### 401 Unauthorized
```json
{
    "success": false,
    "message": "Authentication credentials were not provided",
    "code": "not_authenticated"
}
```

### 403 Forbidden
```json
{
    "success": false,
    "message": "You do not have permission to perform this action",
    "code": "permission_denied"
}
```

### 404 Not Found
```json
{
    "success": false,
    "message": "Transaction not found",
    "code": "not_found"
}
```

### 429 Too Many Requests
```json
{
    "success": false,
    "message": "Request limit exceeded. Please try again after 60 seconds",
    "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
    "success": false,
    "message": "An unexpected error occurred",
    "error_id": "ERR_20241227_143000",
    "support_message": "Please contact support with error ID"
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

## Webhook Events (Future Implementation)

### Settlement Completed
```json
{
    "event": "settlement.completed",
    "timestamp": "2024-12-27T14:30:00+05:30",
    "data": {
        "settlement_id": "SETT_20241227_001",
        "merchant_code": "MERC001",
        "amount": 245000.00,
        "transaction_count": 49,
        "utr": "HDFC2024122798765"
    }
}
```

### Refund Processed
```json
{
    "event": "refund.processed",
    "timestamp": "2024-12-27T15:00:00+05:30",
    "data": {
        "refund_id": "REF_20241227_001",
        "txn_id": "SP202412270001",
        "amount": 2500.00,
        "status": "COMPLETED"
    }
}
```

---

## Notes

1. All datetime values are in ISO 8601 format with timezone
2. All amount values are in INR (Indian Rupees)
3. Response times mentioned are P95 (95th percentile)
4. Excel reports support up to 1 million rows
5. API versioning follows semantic versioning (v1, v2, etc.)
6. All endpoints require HTTPS in production
7. JWT tokens expire after 24 hours (access) and 7 days (refresh)
8. File downloads are available for 24 hours after generation