# 📘 SabPaisa Reports API - Complete Documentation

**Version**: 1.1.0
**Last Updated**: October 14, 2025
**Base URL**: `http://localhost:8000/api/v1/`

> **🆕 What's New in v1.1.0**: Added System Monitoring APIs and Enhanced Response Headers (see Section 6.7 and 9)

---

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Prerequisites](#-prerequisites)
3. [Installation & Setup](#-installation--setup)
4. [Running the Application](#%EF%B8%8F-running-the-application)
5. [Authentication](#-authentication)
6. [API Endpoints](#-api-endpoints)
   - 6.1 [Authentication APIs](#1️⃣-authentication-apis)
   - 6.2 [Transaction APIs](#2️⃣-transaction-apis)
   - 6.3 [Settlement APIs](#3️⃣-settlement-apis)
   - 6.4 [Analytics APIs](#4️⃣-analytics-apis)
   - 6.5 [Reports APIs](#5️⃣-reports-apis)
   - 6.6 [QwikForms APIs](#6️⃣-qwikforms-apis-admin-only)
   - 6.7 [🆕 System Monitoring APIs](#7️⃣--system-monitoring-apis-new)
7. [Error Handling](#-error-handling)
8. [Performance Features](#-performance-features)
9. [🆕 Response Headers](#-response-headers-new)
10. [Troubleshooting](#-troubleshooting)

---

## 🎯 Project Overview

**SabPaisa Reports API** is a high-performance Django REST API for managing 240M+ payment transactions, settlements, analytics, and reporting.

### Key Features:
- ✅ JWT Authentication (Access + Refresh tokens)
- ✅ Redis Caching (10-20X faster responses)
- ✅ Database Partitioning (optimized for 240M records)
- ✅ Real-time Analytics Dashboards
- ✅ Excel/CSV Export capabilities
- ✅ Role-based Access Control (Admin/Merchant)
- 🆕 System Monitoring APIs (Health checks, Metrics, Audit logs)
- 🆕 Enhanced Response Headers (Request tracking, Performance classification, Rate limits)

### Technology Stack:
```
Backend: Django 4.2.15 + Django REST Framework
Database: MySQL 8.0+ (3 databases)
Cache: Redis 6.x
Authentication: JWT (djangorestframework-simplejwt)
Python: 3.12+
```

---

## 🆕 What's New in Version 1.1.0 (For UI Team)

### Summary of Changes

**Important**: All changes are **100% backward compatible**. Your existing frontend code will continue to work without any modifications.

### 1. New System Monitoring APIs (4 Endpoints)

Four new endpoints added under `/api/v1/system/` for system monitoring:

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/system/health/` | GET | Public | Health check for all services |
| `/system/metrics/` | GET | Admin | System performance metrics |
| `/system/database/status/` | GET | Admin | Database connection status |
| `/system/audit-logs/` | GET | Admin | Security audit logs |

**UI Usage**: Build admin monitoring dashboard showing system health, performance metrics, and audit trails.

**Example:**
```javascript
// Check system health (no auth required)
const response = await fetch('http://localhost:8000/api/v1/system/health/');
const health = await response.json();

if (health.status === 'unhealthy') {
  showSystemAlert('System experiencing issues');
}
```

### 2. Enhanced Response Headers (All APIs)

Every API response now includes additional headers for monitoring and debugging:

| Header | Purpose | Example Value |
|--------|---------|---------------|
| `X-Request-ID` | Request tracking | `550e8400-e29b-41d4-a716-446655440000` |
| `X-Response-Time` | Performance monitoring | `0.087s` |
| `X-Performance` | Performance classification | `excellent` / `good` / `acceptable` / `slow` |
| `X-RateLimit-Limit` | Max requests per hour | `5000` |
| `X-RateLimit-Remaining` | Requests remaining | `4987` |
| `X-RateLimit-Reset` | Limit reset timestamp | `1728912600` |

**UI Usage**:
- Include `X-Request-ID` in error reports for faster debugging
- Monitor API performance using `X-Performance` and `X-Response-Time`
- Warn users when approaching rate limits using `X-RateLimit-Remaining`

**Example:**
```javascript
const response = await fetch(apiUrl, options);

// Extract headers
const requestId = response.headers.get('X-Request-ID');
const performance = response.headers.get('X-Performance');
const remaining = response.headers.get('X-RateLimit-Remaining');

// Log for debugging
console.log('Request ID:', requestId);

// Show warning if approaching rate limit
if (remaining < 100) {
  showWarning(`Only ${remaining} API calls remaining this hour`);
}

// Show loading indicator for slow APIs
if (performance === 'slow') {
  showLoadingIndicator();
}
```

### 3. Response Body Changes

**None!** All existing API response bodies remain exactly the same. Only HTTP headers are added.

### 4. Breaking Changes

**None!** This update is 100% backward compatible:
- ✅ All existing endpoints work unchanged
- ✅ All response structures remain the same
- ✅ No changes required to existing frontend code
- ✅ New headers can be ignored if not needed

### 5. Quick Integration Checklist for UI Team

**Optional Enhancements** (recommended but not required):

- [ ] Add `X-Request-ID` to error logging/reporting
- [ ] Display API performance indicators using `X-Performance`
- [ ] Show rate limit warnings using `X-RateLimit-Remaining`
- [ ] Create admin dashboard for system monitoring (using new `/system/*` endpoints)
- [ ] Log response times for analytics

**No Changes Needed**:
- [ ] Existing API calls continue working
- [ ] Response parsing code remains unchanged
- [ ] Authentication flow unchanged
- [ ] Error handling remains the same

### 6. Documentation Sections for UI Team

- **Section 6.7**: System Monitoring APIs - New endpoints
- **Section 9**: Response Headers - Header details and usage examples
- **React/Angular Examples**: Section 9 includes integration examples

---

## 📋 Prerequisites

### Required Software:
```bash
✓ Python 3.12 or higher
✓ MySQL 8.0 or higher
✓ Redis 6.0 or higher
✓ Git
```

### System Requirements:
```
RAM: 8GB minimum (16GB recommended)
Storage: 50GB+ for 240M transaction database
OS: Windows 10/11, Linux, or macOS
```

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
# Navigate to your project directory
cd D:\Hackathon-Project-new\Cleaned_SabPaisa_Report_Solution

# If using git
git clone <your-repo-url>
cd sabpaisa-reports-api
```

### Step 2: Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

**Windows:**
```bash
pip install -r requirements_windows.txt
```

**Linux/Mac:**
```bash
pip install -r requirements.txt
```

**If `mysqlclient` installation fails on Windows:**
```
Don't worry! The application is configured to use PyMySQL as a fallback.
PyMySQL is already included in requirements.txt
```

### Step 4: Install Redis

**Windows:**
```powershell
# Run the automated installer script
powershell -ExecutionPolicy Bypass -File install_redis.ps1
```

**Manual Windows Installation:**
```powershell
# Download Redis for Windows
# Extract to C:\Redis
# Start Redis server
C:\Redis\redis-server.exe
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### Step 5: Configure Environment Variables

**Copy example environment file:**
```bash
cp .env.example .env
```

**Edit `.env` file with your configuration:**

```ini
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production-use-random-string
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration - Primary (Transaction Database)
DB_PRIMARY_NAME=sabpaisa2
DB_PRIMARY_USER=root
DB_PRIMARY_PASSWORD=your_mysql_root_password
DB_PRIMARY_HOST=localhost
DB_PRIMARY_PORT=3306

# Database Configuration - Legacy
DB_LEGACY_NAME=sabpaisa2_legacy
DB_LEGACY_USER=root
DB_LEGACY_PASSWORD=your_mysql_root_password
DB_LEGACY_HOST=localhost
DB_LEGACY_PORT=3306

# Database Configuration - User Management
DB_USER_NAME=spclientonboard
DB_USER_USER=root
DB_USER_PASSWORD=your_mysql_root_password
DB_USER_HOST=localhost
DB_USER_PORT=3306

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=1

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# CORS Settings (Frontend URL)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Application Settings
PAGINATION_PAGE_SIZE=100
CACHE_TTL=300
```

### Step 6: Create MySQL Databases

**Open MySQL Workbench or command line and run:**

```sql
-- Create primary transaction database
CREATE DATABASE sabpaisa2 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

-- Create legacy database
CREATE DATABASE sabpaisa2_legacy 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

-- Create user management database
CREATE DATABASE spclientonboard 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

-- Verify databases created
SHOW DATABASES;
```

### Step 7: Run Database Migrations

```bash
python manage.py migrate
```

**Expected output:**
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

### Step 8: Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

**Follow the prompts:**
```
Username: srssuperadmin@sp
Email: admin@sabpaisa.in
Password: (enter your password)
Password (again): (re-enter password)
Superuser created successfully.
```

### Step 9: (Optional) Create Performance Indexes

**For production with 240M records, run these SQL scripts:**

```bash
# In MySQL Workbench or command line
mysql -u root -p sabpaisa2 < fix_payment_performance_index.sql
```

**Or manually execute:**
```sql
USE sabpaisa2;

-- Create optimized composite indexes
CREATE INDEX idx_trans_date_payment_status
    ON transaction_detail (trans_date, payment_mode, status);

CREATE INDEX idx_status_date_client_amount
    ON transaction_detail (status, trans_date, client_code, client_name, paid_amount);

CREATE INDEX idx_date_status_amount
    ON transaction_detail (trans_date, status, paid_amount);

-- Update table statistics
ANALYZE TABLE transaction_detail;
```

---

## ▶️ Running the Application

### Method 1: Command Line

```bash
# Make sure virtual environment is activated
python manage.py runserver 0.0.0.0:8000
```

**Expected output:**
```
Performing system checks...

System check identified no issues (0 silenced).
October 08, 2025 - 18:30:00
Django version 4.2.15, using settings 'config.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CTRL-BREAK.
```

### Method 2: VS Code (Press F5)

Already configured in `.vscode/launch.json` - just press **F5** in VS Code.

### Method 3: Custom Port

```bash
python manage.py runserver 0.0.0.0:9000
```

### Verify Installation

**Test 1: Health Check**
```bash
curl http://localhost:8000/api/v1/auth/health/
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-08T18:30:00Z",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

**Test 2: API Documentation**

Open in browser:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

---

## 🔐 Authentication

All APIs use **JWT (JSON Web Tokens)** for authentication.

### Authentication Flow:

```
1. Login with username/password → Get access & refresh tokens
2. Use access token in Authorization header for all API requests
3. When access token expires (24 hours) → Use refresh token to get new access token
4. When refresh token expires (7 days) → User must login again
5. Logout → Invalidate tokens
```

### Token Expiration:
- **Access Token**: Valid for **24 hours**
- **Refresh Token**: Valid for **7 days**

### Step 1: Login

**Endpoint:** `POST /api/v1/auth/login/`

**Request (cURL):**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "srssuperadmin@sp",
    "password": "Admin@123"
  }'
```

**Request (PowerShell):**
```powershell
$body = @{
    username = "srssuperadmin@sp"
    password = "Admin@123"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/auth/login/" `
    -ContentType "application/json" `
    -Body $body
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI4NDEyMjAwLCJpYXQiOjE3Mjg0MDg2MDAsImp0aSI6ImFiYzEyMyIsInVzZXJfaWQiOjF9.xyz789",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyODQ5NTAwMCwiaWF0IjoxNzI4NDA4NjAwLCJqdGkiOiJkZWY0NTYiLCJ1c2VyX2lkIjoxfQ.abc123",
    "user": {
      "username": "srssuperadmin@sp",
      "email": "admin@sabpaisa.in",
      "role": "ADMIN",
      "client_code": null
    }
  }
}
```

**⚠️ SAVE THE ACCESS TOKEN - You'll need it for all API calls!**

### Step 2: Using the Access Token

**Add to Authorization header in ALL subsequent requests:**

```bash
curl -X GET http://localhost:8000/api/v1/transactions/admin-history/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json"
```

### Step 3: Refresh Access Token (When Expired)

**Endpoint:** `POST /api/v1/auth/refresh/`

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...(NEW_TOKEN)",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...(NEW_REFRESH_TOKEN)"
}
```

### Step 4: Logout

**Endpoint:** `POST /api/v1/auth/logout/`

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

---

## 📚 API Endpoints

**Base URL:** `http://localhost:8000/api/v1/`

**All endpoints require authentication unless specified**

---

### 1️⃣ AUTHENTICATION APIS

#### 1.1 Login
**POST** `/auth/login/`

**No authentication required**

**Request:**
```json
{
  "username": "srssuperadmin@sp",
  "password": "Admin@123"
}
```

**Copy-Paste cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"srssuperadmin@sp","password":"Admin@123"}'
```

---

#### 1.2 Get User Profile
**GET** `/auth/profile/`

**Copy-Paste cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "username": "srssuperadmin@sp",
    "email": "admin@sabpaisa.in",
    "role": "ADMIN",
    "client_code": null,
    "is_active": true
  }
}
```

---

#### 1.3 Change Password
**POST** `/auth/change-password/`

**Request:**
```json
{
  "old_password": "OldPassword123",
  "new_password": "NewPassword456"
}
```

**Copy-Paste cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"old_password":"OldPassword123","new_password":"NewPassword456"}'
```

---

### 2️⃣ TRANSACTION APIS

#### 2.1 Get Admin Transaction History
**GET** `/transactions/admin-history/`

**Description:** Get paginated transaction history. **Defaults to today's data** to ensure fast loading with 240M+ records.

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| date_from | string | No | Today | Start date (YYYY-MM-DD) |
| date_to | string | No | Today | End date (YYYY-MM-DD) |
| page | integer | No | 1 | Page number |
| page_size | integer | No | 100 | Records per page (max 10000) |
| status | string | No | ALL | SUCCESS/FAILED/PENDING |
| payment_mode | string | No | ALL | UPI/CC/DC/NB/WALLET |
| client_code | string | No | ALL | Merchant code |
| search | string | No | - | Search term |

**Example 1: Get Today's Transactions (Default - Fast!)**
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/admin-history/?page=1&page_size=100" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Example 2: Get Specific Date Range**
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/admin-history/?date_from=2025-10-01&date_to=2025-10-08&page=1&page_size=100" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Example 3: Filter by Status and Payment Mode**
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/admin-history/?date_from=2025-10-01&date_to=2025-10-08&status=SUCCESS&payment_mode=UPI&page=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Example 4: Search by Transaction ID or Mobile Number**
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/admin-history/?search=9876543210&page=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200 OK):**
```json
{
  "success": true,
  "count": 239006,
  "filter_summary": "From 2025-10-01 to 2025-10-08",
  "next": "http://localhost:8000/api/v1/transactions/admin-history/?page=2",
  "previous": null,
  "results": [
    {
      "txn_id": "SABP2025100812345678",
      "client_txn_id": "MERCHANT_TXN_001",
      "client_code": "MERC001",
      "client_name": "ABC Merchant Ltd",
      "paid_amount": 1500.00,
      "status": "SUCCESS",
      "payment_mode": "UPI",
      "trans_date": "2025-10-08T14:30:25+05:30",
      "payee_email": "customer@example.com",
      "payee_mob": "9876543210",
      "is_settled": true,
      "settlement_date": "2025-10-09"
    }
  ]
}
```

**Performance:**
- First load (today): ~300ms (fast!)
- Week filter: 1-2 seconds
- Month filter: 3-5 seconds
- Year filter: 6-11 seconds
- Second request (cached): 50-100ms ⚡

---

#### 2.2 Get Merchant Transaction History
**GET** `/transactions/merchant-history/`

**Description:** Get transactions for logged-in merchant (auto-filtered by merchant's client_code)

**Query Parameters:** Same as Admin Transaction History

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/merchant-history/?date_from=2025-10-01&date_to=2025-10-08&page=1" \
  -H "Authorization: Bearer MERCHANT_ACCESS_TOKEN"
```

---

#### 2.3 Transaction Summary
**GET** `/transactions/summary/`

**Description:** Get aggregated transaction statistics

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/summary/?date_from=2025-10-01&date_to=2025-10-08" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_transactions": 239006,
    "successful_transactions": 215406,
    "failed_transactions": 21000,
    "pending_transactions": 2600,
    "success_rate": 90.12,
    "total_volume": 358500000.00,
    "success_volume": 345000000.00,
    "average_ticket_size": 1500.00
  }
}
```

---

#### 2.4 Export Transactions to Excel
**GET** `/transactions/admin-history-excel/`

**Description:** Download transaction history as Excel file

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/admin-history-excel/?date_from=2025-10-01&date_to=2025-10-08" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --output transactions.xlsx
```

**Response:** Excel file download starts

---

#### 2.5 Success Graph Data
**GET** `/transactions/success-graph/`

**Description:** Get success rate trends over time

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/success-graph/?date_from=2025-10-01&date_to=2025-10-08" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "daily_trend": [
      {
        "date": "2025-10-01",
        "total": 32000,
        "successful": 28800,
        "success_rate": 90.0
      },
      {
        "date": "2025-10-02",
        "total": 31500,
        "successful": 28350,
        "success_rate": 90.0
      }
    ]
  }
}
```

---

### 3️⃣ SETTLEMENT APIS

#### 3.1 Get Settled Transactions
**GET** `/settlements/settled-history/`

**Description:** Get settled transactions with settlement details

**Query Parameters:**
- date_from, date_to - Transaction date range (defaults to today)
- settlement_date_from, settlement_date_to - Settlement date range
- client_code - Filter by merchant
- page, page_size - Pagination

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/settlements/settled-history/?date_from=2025-10-01&date_to=2025-10-08&page=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "count": 180000,
  "results": [
    {
      "txn_id": "SABP2025100812345678",
      "client_code": "MERC001",
      "client_name": "ABC Merchant Ltd",
      "paid_amount": 1500.00,
      "settlement_amount": 1470.00,
      "settlement_date": "2025-10-09",
      "settlement_status": "SETTLED",
      "settlement_utr": "UTR123456789",
      "charges": 30.00,
      "gst": 5.40
    }
  ]
}
```

---

#### 3.2 Settlement Grouped View
**GET** `/settlements/grouped-view/`

**Description:** Get settlements grouped by merchant and settlement date

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/settlements/grouped-view/?settlement_date_from=2025-10-01&settlement_date_to=2025-10-08" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "client_code": "MERC001",
      "client_name": "ABC Merchant Ltd",
      "settlement_date": "2025-10-09",
      "transaction_count": 1200,
      "total_amount": 1800000.00,
      "settlement_amount": 1764000.00,
      "charges": 36000.00
    }
  ]
}
```

---

#### 3.3 Refund Transaction History
**GET** `/settlements/refund-history/`

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/settlements/refund-history/?date_from=2025-10-01&date_to=2025-10-08" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "count": 450,
  "results": [
    {
      "txn_id": "SABP2025100812345678",
      "refund_id": "RFD2025100800001",
      "original_amount": 1500.00,
      "refund_amount": 1500.00,
      "refund_status": "SUCCESS",
      "refund_date": "2025-10-08T16:20:00+05:30"
    }
  ]
}
```

---

#### 3.4 Chargeback History
**GET** `/settlements/chargeback-history/`

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/settlements/chargeback-history/?date_from=2025-10-01&date_to=2025-10-08" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

#### 3.5 Export Settlements to Excel
**GET** `/settlements/settled-excel/`

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/settlements/settled-excel/?date_from=2025-10-01&date_to=2025-10-08" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --output settlements.xlsx
```

---

### 4️⃣ ANALYTICS APIS

#### 4.1 Merchant Analytics Dashboard
**GET** `/analytics/merchant-analytics/`

**Description:** Comprehensive merchant performance dashboard (optimized for 240M+ records)

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/merchant-analytics/?date_from=2025-10-01&date_to=2025-10-08" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_transactions": 239006,
      "total_volume": 358500000.00,
      "successful_transactions": 215406,
      "success_rate": 90.12,
      "active_merchants": 1250
    },
    "top_merchants": [
      {
        "client_code": "MERC001",
        "client_name": "ABC Merchant Ltd",
        "volume": 45000000.00,
        "count": 30000
      }
    ],
    "payment_performance": [
      {
        "payment_mode": "UPI",
        "total": 120000,
        "successful": 114000,
        "success_rate": 95.0
      }
    ],
    "daily_trend": [
      {
        "date": "2025-10-01",
        "transactions": 32000,
        "volume": 48000000.00
      }
    ]
  }
}
```

**Performance:**
- First load (year filter): ~3 seconds
- Cached request: ~50-100ms ⚡

---

#### 4.2 Payment Mode Analytics
**GET** `/analytics/payment-mode-analytics/`

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/payment-mode-analytics/?date_from=2025-10-01&date_to=2025-10-08" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

#### 4.3 Settlement Analytics
**GET** `/analytics/settlement-analytics/`

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/settlement-analytics/?date_from=2025-10-01&date_to=2025-10-08" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

#### 4.4 Refund & Chargeback Analytics
**GET** `/analytics/refund-chargeback/`

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/refund-chargeback/?date_from=2025-10-01&date_to=2025-10-08" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

#### 4.5 Comparative Analytics
**GET** `/analytics/comparative/`

**Description:** Compare performance across two time periods

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/comparative/?current_date_from=2025-10-01&current_date_to=2025-10-08&previous_date_from=2025-09-24&previous_date_to=2025-09-30" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

#### 4.6 Executive Dashboard
**GET** `/analytics/executive-dashboard/`

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/executive-dashboard/?date_from=2025-10-01&date_to=2025-10-08" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 5️⃣ REPORTS APIS

#### 5.1 Generate Report (Async)
**POST** `/reports/generate/`

**Description:** Generate custom report asynchronously

**Request:**
```json
{
  "report_type": "TRANSACTION_REPORT",
  "date_from": "2025-10-01",
  "date_to": "2025-10-08",
  "format": "EXCEL",
  "filters": {
    "status": "SUCCESS",
    "payment_mode": "UPI"
  }
}
```

**Copy-Paste cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/reports/generate/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "TRANSACTION_REPORT",
    "date_from": "2025-10-01",
    "date_to": "2025-10-08",
    "format": "EXCEL"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Report generation started",
  "task_id": "abc123-def456-ghi789",
  "status_url": "/api/v1/reports/status/abc123-def456-ghi789/"
}
```

**Available Report Types:**
- TRANSACTION_REPORT
- SETTLEMENT_REPORT
- REFUND_REPORT
- MERCHANT_REPORT
- PAYMENT_MODE_REPORT

**Formats:** EXCEL, CSV, PDF

---

#### 5.2 Check Report Status
**GET** `/reports/status/{task_id}/`

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/reports/status/abc123-def456-ghi789/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (Completed):**
```json
{
  "success": true,
  "status": "COMPLETED",
  "progress": 100,
  "download_url": "/api/v1/reports/download/abc123-def456-ghi789/"
}
```

---

#### 5.3 Download Report
**GET** `/reports/download/{task_id}/`

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/reports/download/abc123-def456-ghi789/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --output report.xlsx
```

---

#### 5.4 List Generated Reports
**GET** `/reports/list/`

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/reports/list/?page=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 6️⃣ QWIKFORMS APIS (Admin Only)

#### 6.1 QwikForms Transactions
**GET** `/qwikforms/transactions/`

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/qwikforms/transactions/?qf_id=QF12345&date_from=2025-10-01" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

---

#### 6.2 QwikForms Settlements
**GET** `/qwikforms/settlements/`

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/qwikforms/settlements/?qf_id=QF12345" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

---

#### 6.3 QwikForms Analytics
**GET** `/qwikforms/analytics/`

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/qwikforms/analytics/?qf_id=QF12345&date_from=2025-10-01&date_to=2025-10-08" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

---

### 7️⃣ 🆕 SYSTEM MONITORING APIS (NEW)

> **New Feature**: System health monitoring and metrics endpoints for DevOps and monitoring tools.

#### 7.1 System Health Check
**GET** `/system/health/`

**Description:** Comprehensive health check for all system dependencies (databases, Redis, system resources)

**Authentication:** ⚠️ **Public** - No authentication required (for load balancers/monitoring tools)

**Copy-Paste cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/system/health/
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T15:30:00.123456+05:30",
  "version": "1.0.0",
  "services": {
    "database_default": {
      "status": "healthy",
      "response_time_ms": 12.45
    },
    "database_legacy": {
      "status": "healthy",
      "response_time_ms": 15.23
    },
    "database_user_management": {
      "status": "healthy",
      "response_time_ms": 11.87
    },
    "database_qwikforms_db": {
      "status": "healthy",
      "response_time_ms": 13.56
    },
    "redis_cache": {
      "status": "healthy",
      "response_time_ms": 2.34,
      "memory_used": "45.2M"
    }
  },
  "system": {
    "cpu_percent": 23.5,
    "memory_percent": 45.2,
    "disk_percent": 67.8
  }
}
```

**Use Cases:**
- Load balancer health checks
- Monitoring tool integration (Prometheus, Datadog, etc.)
- Automated health monitoring
- Kubernetes liveness/readiness probes

**Response Codes:**
- `200 OK` - System is healthy
- `503 Service Unavailable` - One or more services unhealthy

---

#### 7.2 System Metrics
**GET** `/system/metrics/`

**Description:** System-wide performance metrics and statistics

**Authentication:** ✅ **Required** - Admin only

**Copy-Paste cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/system/metrics/ \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2025-10-14T15:30:00.123456+05:30",
  "data": {
    "api_stats": {
      "total_requests_today": 45632,
      "avg_response_time_ms": 87.45,
      "error_rate_percent": 0.23,
      "slow_requests": 45
    },
    "transaction_stats": {
      "total_today": 8934,
      "successful": 8912,
      "failed": 22,
      "success_rate": 99.75
    },
    "cache_stats": {
      "hit_rate": 94.5,
      "miss_rate": 5.5,
      "memory_used": "45.2M"
    },
    "database_stats": {
      "default": {
        "active_connections": 12,
        "status": "connected"
      },
      "legacy": {
        "active_connections": 8,
        "status": "connected"
      }
    }
  }
}
```

**UI Integration:**
- Display metrics in admin dashboard
- Create performance monitoring charts
- Show system health indicators
- Alert on anomalies

---

#### 7.3 Database Status
**GET** `/system/database/status/`

**Description:** Detailed status of all database connections

**Authentication:** ✅ **Required** - Admin only

**Copy-Paste cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/system/database/status/ \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2025-10-14T15:30:00.123456+05:30",
  "databases": {
    "default": {
      "status": "healthy",
      "response_time_ms": 12.45,
      "version": "8.0.35-0ubuntu0.22.04.1",
      "active_connections": 12
    },
    "legacy": {
      "status": "healthy",
      "response_time_ms": 15.23,
      "version": "8.0.35-0ubuntu0.22.04.1",
      "active_connections": 8
    },
    "user_management": {
      "status": "healthy",
      "response_time_ms": 11.87,
      "version": "8.0.35-0ubuntu0.22.04.1",
      "active_connections": 5
    },
    "qwikforms_db": {
      "status": "healthy",
      "response_time_ms": 13.56,
      "version": "8.0.35-0ubuntu0.22.04.1",
      "active_connections": 3
    }
  }
}
```

**UI Integration:**
- Show database health indicators
- Display connection pool status
- Alert on slow response times
- Monitor connection counts

---

#### 7.4 Audit Logs
**GET** `/system/audit-logs/`

**Description:** View audit logs for sensitive operations

**Authentication:** ✅ **Required** - Admin only

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| action | string | No | ALL | Filter by action type |
| user | string | No | ALL | Filter by user |
| date_from | string | No | - | Start date (YYYY-MM-DD) |
| date_to | string | No | - | End date (YYYY-MM-DD) |
| limit | integer | No | 100 | Number of results |

**Copy-Paste cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/system/audit-logs/?limit=50" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "count": 25,
  "data": [
    {
      "timestamp": "2025-10-14T15:30:00.123456+05:30",
      "action": "user_login",
      "user": "admin@sabpaisa.in",
      "ip_address": "192.168.1.100",
      "details": "Successful login"
    },
    {
      "timestamp": "2025-10-14T15:25:00.123456+05:30",
      "action": "report_generated",
      "user": "merchant1@example.com",
      "ip_address": "192.168.1.101",
      "details": "Transaction report exported"
    }
  ]
}
```

**UI Integration:**
- Display audit trail in admin panel
- Filter by action, user, date range
- Show security events
- Export audit logs

---

## 🚨 Error Handling

### Standard Error Response Format:

```json
{
  "success": false,
  "message": "Error description",
  "errors": {
    "field_name": ["Error detail"]
  }
}
```

### HTTP Status Codes:

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal error |

### Common Errors:

**1. Authentication Error (401):**
```json
{
  "success": false,
  "message": "Authentication credentials were not provided"
}
```

**Solution:** Add `Authorization: Bearer YOUR_ACCESS_TOKEN` header

**2. Validation Error (400):**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "date_from": ["Invalid date format. Use YYYY-MM-DD"]
  }
}
```

**3. Permission Denied (403):**
```json
{
  "success": false,
  "message": "You do not have permission to perform this action"
}
```

---

## ⚡ Performance Features

### 1. Redis Caching
- **Cache Hit**: 50-100ms response time ⚡
- **Cache TTL**: 5-30 minutes (varies by endpoint)
- **Filter-aware**: Different cache for different date ranges

### 2. Database Optimizations
- **Table Partitioning**: Production DB uses monthly partitions
- **Covering Indexes**: Reduce table access by 10-20X
- **Index Hints**: Force MySQL to use optimal indexes
- **Raw SQL**: Critical queries optimized with raw SQL

### 3. Default Date Filtering
- **Transaction APIs**: Default to TODAY to avoid scanning 240M records
- **First Load**: ~300ms (today's ~80K records)
- **Performance Table:**

| Date Range | Records | Load Time |
|------------|---------|-----------|
| Today | 80K | 300ms ⚡ |
| Week | 560K | 1-2s ✅ |
| Month | 2.4M | 3-5s ✅ |
| Year | 20M | 6-11s ✅ |

---

## 🆕 Response Headers (NEW)

> **New Feature**: All API responses now include additional metadata headers for better monitoring and debugging.

### Overview

**Important**: All existing API response **bodies remain unchanged**. Only HTTP headers are added. Your existing code continues to work without any modifications.

### Headers Added to ALL Responses

#### 1. Request Tracking Headers

**X-Request-ID**
- **Type**: UUID string
- **Purpose**: Unique identifier for request tracing across distributed systems
- **Example**: `X-Request-ID: 550e8400-e29b-41d4-a716-446655440000`
- **UI Usage**:
  - Include in error reports for easier debugging
  - Track API calls across different services
  - Correlate logs between frontend and backend

**X-Response-Time**
- **Type**: String (time in seconds)
- **Purpose**: Time taken to process the request
- **Example**: `X-Response-Time: 0.087s`
- **UI Usage**:
  - Monitor API performance from client side
  - Display response time in developer console
  - Alert users on slow responses

#### 2. Performance Classification Header

**X-Performance**
- **Type**: String enum
- **Values**: `excellent` | `good` | `acceptable` | `slow`
- **Purpose**: Quick classification of API response performance
- **Example**: `X-Performance: excellent`
- **Classification**:
  - `excellent`: < 100ms ⚡
  - `good`: 100-200ms ✅
  - `acceptable`: 200-500ms ⚠️
  - `slow`: > 500ms 🐌

**UI Usage**:
```javascript
// Example: Show performance indicator
const response = await fetch(apiUrl, options);
const performance = response.headers.get('X-Performance');

if (performance === 'slow') {
  console.warn('API response is slow. Consider showing loading indicator.');
}
```

#### 3. Rate Limit Information Headers

**X-RateLimit-Limit**
- **Type**: Integer
- **Purpose**: Maximum requests allowed per hour
- **Example**: `X-RateLimit-Limit: 5000`
- **Limits by Role**:
  - Admin: 10,000 requests/hour
  - Merchant: 5,000 requests/hour
  - Anonymous: 100 requests/hour

**X-RateLimit-Remaining**
- **Type**: Integer
- **Purpose**: Remaining requests in current window
- **Example**: `X-RateLimit-Remaining: 4987`

**X-RateLimit-Reset**
- **Type**: Unix timestamp
- **Purpose**: When the rate limit resets
- **Example**: `X-RateLimit-Reset: 1728912600`

**UI Usage**:
```javascript
// Example: Check rate limit and warn user
const response = await fetch(apiUrl, options);
const remaining = parseInt(response.headers.get('X-RateLimit-Remaining'));
const limit = parseInt(response.headers.get('X-RateLimit-Limit'));

if (remaining < limit * 0.1) {
  // Less than 10% remaining
  showNotification('Warning: Approaching API rate limit. Please slow down requests.');
}
```

### Complete Example

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/transactions/admin-history/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -I
```

**Response Headers:**
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 15234
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Response-Time: 0.087s
X-Performance: excellent
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4987
X-RateLimit-Reset: 1728912600
```

**Response Body** (unchanged):
```json
{
  "success": true,
  "count": 239006,
  "filter_summary": "From 2025-10-01 to 2025-10-08",
  "results": [...]
}
```

### UI Integration Guide

#### React/JavaScript Example

```javascript
// Create API utility function
async function callAPI(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });

  // Extract useful headers
  const headers = {
    requestId: response.headers.get('X-Request-ID'),
    responseTime: response.headers.get('X-Response-Time'),
    performance: response.headers.get('X-Performance'),
    rateLimitRemaining: parseInt(response.headers.get('X-RateLimit-Remaining')),
    rateLimitLimit: parseInt(response.headers.get('X-RateLimit-Limit')),
    rateLimitReset: parseInt(response.headers.get('X-RateLimit-Reset'))
  };

  // Log performance
  console.log(`API Call: ${url}`);
  console.log(`Request ID: ${headers.requestId}`);
  console.log(`Response Time: ${headers.responseTime}`);
  console.log(`Performance: ${headers.performance}`);

  // Warn about rate limits
  if (headers.rateLimitRemaining < 100) {
    console.warn(`⚠️ Rate limit warning: ${headers.rateLimitRemaining} requests remaining`);
  }

  const data = await response.json();

  return {
    data,
    headers,
    status: response.status
  };
}

// Usage
const result = await callAPI('http://localhost:8000/api/v1/transactions/admin-history/');
console.log('Data:', result.data);
console.log('Request ID for debugging:', result.headers.requestId);
```

#### Angular Example

```typescript
// API Interceptor
@Injectable()
export class ApiHeadersInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      tap((event: HttpEvent<any>) => {
        if (event instanceof HttpResponse) {
          const requestId = event.headers.get('X-Request-ID');
          const responseTime = event.headers.get('X-Response-Time');
          const performance = event.headers.get('X-Performance');

          console.log('API Response:', {
            url: event.url,
            requestId,
            responseTime,
            performance
          });

          // Handle slow responses
          if (performance === 'slow') {
            this.notificationService.warn('API response is slow');
          }
        }
      })
    );
  }
}
```

### Benefits for UI Team

1. **Better Error Reporting**: Include `X-Request-ID` in bug reports for faster debugging
2. **Performance Monitoring**: Track slow APIs and optimize user experience
3. **Rate Limit Awareness**: Warn users before hitting rate limits
4. **Request Tracing**: Correlate frontend and backend logs using request ID
5. **User Experience**: Show loading indicators for slow responses

### Backward Compatibility

✅ **100% Backward Compatible**
- All existing API response bodies remain unchanged
- New headers are optional - your code works without reading them
- No changes needed to existing frontend code
- Headers can be ignored if not needed

### Testing Headers

```bash
# View all response headers
curl -I http://localhost:8000/api/v1/transactions/admin-history/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# View specific header
curl -X GET http://localhost:8000/api/v1/transactions/admin-history/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -D - -o /dev/null | grep "X-Request-ID"
```

---

## 🐛 Troubleshooting

### Issue 1: Redis Connection Failed

**Check if Redis is running:**
```bash
# Windows
tasklist | findstr redis-server

# Linux
ps aux | grep redis

# Test connection
redis-cli ping
```

**Start Redis:**
```bash
# Windows
C:\Redis\redis-server.exe

# Linux
sudo systemctl start redis
```

---

### Issue 2: MySQL Connection Error

**Verify MySQL is running:**
```bash
# Windows
tasklist | findstr mysqld

# Test connection
mysql -u root -p
```

**Check .env file:**
```ini
DB_PRIMARY_HOST=localhost
DB_PRIMARY_PORT=3306
DB_PRIMARY_USER=root
DB_PRIMARY_PASSWORD=your_password
DB_PRIMARY_NAME=sabpaisa2
```

---

### Issue 3: Token Expired

**Use refresh token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

---

### Issue 4: Slow Query Performance (240M records)

**Run these commands:**

```sql
-- Check indexes exist
SHOW INDEX FROM transaction_detail;

-- Update statistics
ANALYZE TABLE transaction_detail;
```

**If still slow, create indexes:**
```sql
CREATE INDEX idx_trans_date_payment_status
    ON transaction_detail (trans_date, payment_mode, status);

ANALYZE TABLE transaction_detail;
```

---

### Issue 5: Unicode Encoding Errors (Windows Console)

**Error:** `'charmap' codec can't encode character '\u2717'`

**Solution:** This is cosmetic - API works fine. To fix console:
```bash
chcp 65001
python manage.py runserver
```

---

## 📚 Additional Resources

### Interactive API Documentation:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

### Performance Documentation:
- `REDIS_VERIFICATION_REPORT.md` - Redis cache verification
- `PERFORMANCE_OPTIMIZATION_SUMMARY.md` - Query optimization details
- `TRANSACTION_LIST_OPTIMIZATION.md` - Transaction list optimization
- `scale_240m_optimization_plan.md` - Scaling strategy for 240M records

### Database Scripts:
- `fix_payment_performance_index.sql` - Create performance indexes
- `create_summary_tables.sql` - Summary tables for 240M scale

---

## ✅ Quick Start Checklist

- [ ] Python 3.12+ installed
- [ ] MySQL 8.0+ installed and running
- [ ] Redis installed and running
- [ ] Virtual environment created (`python -m venv venv`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured
- [ ] Databases created (sabpaisa2, sabpaisa2_legacy, spclientonboard)
- [ ] Migrations run (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)
- [ ] Server running (`python manage.py runserver`)
- [ ] Health check passed (http://localhost:8000/api/v1/auth/health/)
- [ ] Successfully logged in and got JWT token
- [ ] Tested first API call

---

## 📞 Support

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Review API docs: http://localhost:8000/api/docs/
3. Check application logs
4. Contact technical team

---

## 📝 Changelog

### Version 1.1.0 (October 14, 2025)

**New Features:**
- ✅ Added 4 new System Monitoring API endpoints
  - System Health Check (Public endpoint)
  - System Metrics (Admin only)
  - Database Status (Admin only)
  - Audit Logs (Admin only)
- ✅ Added Response Headers to all API responses
  - X-Request-ID: Request tracking
  - X-Response-Time: Performance monitoring
  - X-Performance: Performance classification
  - X-RateLimit-*: Rate limit information
- ✅ 100% Backward compatible - All existing APIs work unchanged

**Backward Compatibility:**
- ✅ All existing API response bodies unchanged
- ✅ No changes to business logic
- ✅ Existing frontend code continues to work without modifications
- ✅ New features are purely additive

### Version 1.0.0 (October 8, 2025)
- Initial production release
- Transaction, Settlement, Analytics APIs
- QwikForms integration
- Redis caching and performance optimizations

---

## 📞 Support & Contact

**For UI Team:**
- Questions about new endpoints: Check Section 6.7 (System Monitoring APIs)
- Questions about new headers: Check Section 9 (Response Headers)
- Integration examples: See React/Angular examples in Section 9
- Testing: Use provided cURL examples

**For Issues:**
1. Check [Troubleshooting](#-troubleshooting) section
2. Review API docs: http://localhost:8000/api/docs/
3. Check application logs
4. Contact backend team with X-Request-ID from error

---

**Generated**: October 14, 2025
**Version**: 1.1.0
**Status**: Production Ready
**Breaking Changes**: None - 100% Backward Compatible

---

**End of Documentation**
