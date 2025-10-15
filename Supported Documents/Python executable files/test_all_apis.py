#!/usr/bin/env python
"""
Comprehensive test script for all implemented APIs

This script tests:
1. Authentication APIs
2. Transaction APIs
3. Settlement APIs
4. Analytics APIs
"""
import requests
import json
import sys
from datetime import datetime, timedelta
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

BASE_URL = "http://localhost:8000/api/v1"
access_token = None
user_info = None


def print_success(message):
    """Print success message in green"""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")


def print_error(message):
    """Print error message in red"""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")


def print_info(message):
    """Print info message in blue"""
    print(f"{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")


def print_warning(message):
    """Print warning message in yellow"""
    print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")


def print_section(title):
    """Print section header"""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{title}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")


def test_endpoint(method, endpoint, headers=None, data=None, params=None, description=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"

    print(f"{Fore.YELLOW}Testing: {method} {endpoint}{Style.RESET_ALL}")
    if description:
        print(f"  {description}")

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print_error(f"Unknown method: {method}")
            return None

        if response.status_code in [200, 201, 202]:
            print_success(f"Status: {response.status_code}")
            return response.json()
        else:
            print_error(f"Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}..." if len(response.text) > 200 else f"  Response: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Is it running?")
        return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None


def test_authentication_apis():
    """Test all authentication endpoints"""
    global access_token, user_info

    print_section("AUTHENTICATION APIS")

    # 1. Login
    print("\n1. Testing Login")
    username = input("Enter username or login_master_id: ")
    password = input("Enter password: ")

    payload = {"password": password}
    if username.isdigit():
        payload["login_master_id"] = username
    else:
        payload["username"] = username

    response_data = test_endpoint("POST", "/auth/login/", data=payload, description="User login")

    if response_data and response_data.get('success'):
        access_token = response_data['data']['access']
        user_info = response_data['data']['user']
        print_info(f"Logged in as: {user_info.get('username')} (Role: {user_info.get('role_id')})")
    else:
        print_error("Login failed. Cannot continue testing.")
        return False

    # Set auth headers for remaining tests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # 2. Profile
    test_endpoint("GET", "/auth/profile/", headers=headers, description="Get user profile")

    # 3. Sessions
    test_endpoint("GET", "/auth/sessions/", headers=headers, description="Get active sessions")

    # 4. Roles
    test_endpoint("GET", "/auth/roles/", headers=headers, description="Get available roles")

    # 5. Health Check
    test_endpoint("GET", "/auth/health/", description="Health check (no auth required)")

    return True


def test_transaction_apis():
    """Test all transaction endpoints"""
    print_section("TRANSACTION APIS")

    if not access_token:
        print_error("Not authenticated. Skipping transaction tests.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Date filters for testing
    date_to = datetime.now()
    date_from = date_to - timedelta(days=30)
    params = {
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "page": 1,
        "page_size": 10
    }

    # Merchant APIs
    test_endpoint("GET", "/transactions/merchant-history/", headers=headers, params=params,
                 description="Merchant transaction history")

    test_endpoint("GET", "/transactions/merchant-history-bit/", headers=headers, params=params,
                 description="Merchant history (optimized/bit mode)")

    test_endpoint("GET", "/transactions/merchant-history-whole/", headers=headers, params=params,
                 description="Merchant history (complete data)")

    # Admin APIs (will fail if not admin)
    test_endpoint("GET", "/transactions/admin-history/", headers=headers, params=params,
                 description="Admin transaction history")

    test_endpoint("GET", "/transactions/admin-history-bit/", headers=headers, params=params,
                 description="Admin history (optimized)")

    test_endpoint("GET", "/transactions/admin-history-whole/", headers=headers, params=params,
                 description="Admin history (complete)")

    # Analytics
    test_endpoint("GET", "/transactions/success-graph/", headers=headers, params={"days": 7},
                 description="Success rate graph data")

    test_endpoint("GET", "/transactions/summary/", headers=headers, params=params,
                 description="Transaction summary statistics")

    # Quick filter
    test_endpoint("GET", "/transactions/qf-wise-history/", headers=headers,
                 params={"qf_type": "payment_mode", "qf_value": "UPI"},
                 description="Quick filter wise history")

    # Bank specific
    test_endpoint("GET", "/transactions/doitc-settled-history/", headers=headers, params=params,
                 description="DOITC settled transactions")

    test_endpoint("GET", "/transactions/sbi-card-data/", headers=headers, params=params,
                 description="SBI card transactions")

    # Excel generation (POST)
    excel_data = {
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "format": "excel"
    }
    test_endpoint("POST", "/transactions/merchant-history-excel/", headers=headers, data=excel_data,
                 description="Generate merchant Excel report")


def test_settlement_apis():
    """Test all settlement endpoints"""
    print_section("SETTLEMENT APIS")

    if not access_token:
        print_error("Not authenticated. Skipping settlement tests.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Date filters
    date_to = datetime.now()
    date_from = date_to - timedelta(days=30)
    params = {
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "page": 1,
        "page_size": 10
    }

    # Settlement history
    test_endpoint("GET", "/settlements/settled-history/", headers=headers, params=params,
                 description="Settled transaction history")

    test_endpoint("GET", "/settlements/grouped-view/", headers=headers,
                 params={**params, "group_by": "date"},
                 description="Grouped settlement view")

    test_endpoint("GET", "/settlements/qf-wise-settled/", headers=headers,
                 params={"qf_type": "payment_mode", "qf_value": "UPI"},
                 description="Quick filter wise settlements")

    # Refunds and chargebacks
    test_endpoint("GET", "/settlements/refund-history/", headers=headers, params=params,
                 description="Refund history")

    test_endpoint("GET", "/settlements/chargeback-history/", headers=headers, params=params,
                 description="Chargeback history")

    # Excel generation
    excel_data = {
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat()
    }
    test_endpoint("POST", "/settlements/settled-excel/", headers=headers, data=excel_data,
                 description="Generate settlement Excel")

    test_endpoint("POST", "/settlements/settled-excel-v2/", headers=headers, data=excel_data,
                 description="Generate enhanced settlement Excel")

    # Reconciliation (Admin only)
    recon_data = {
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "type": "three_way"
    }
    test_endpoint("POST", "/settlements/reconciliation/", headers=headers, data=recon_data,
                 description="Three-way reconciliation")


def test_admin_specific_apis():
    """Test admin-only endpoints"""
    print_section("ADMIN-SPECIFIC APIS")

    if not access_token:
        print_error("Not authenticated. Skipping admin tests.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Merchant whitelist
    test_endpoint("GET", "/transactions/merchant-whitelist/", headers=headers,
                 description="Get merchant whitelist")

    # Export history
    test_endpoint("GET", "/transactions/admin-export-history/", headers=headers,
                 description="Get export history")

    # Merchant registration
    merchant_data = {
        "username": "test_merchant_" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "password": "TestPass123!",
        "email": "merchant@test.com",
        "client_name": "Test Merchant",
        "client_code": "TM" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "business_category": "RETAIL"
    }
    test_endpoint("POST", "/auth/register/merchant/", headers=headers, data=merchant_data,
                 description="Register new merchant (Admin only)")


def generate_summary():
    """Generate test summary"""
    print_section("TEST SUMMARY")

    print_info("All API endpoints have been tested.")
    print_info("Check the output above for any failures.")

    if user_info:
        print(f"\nTested as user: {user_info.get('username')}")
        print(f"Role: {user_info.get('role_id')}")

    print("\n" + "="*60)
    print("Test Categories:")
    print("  1. ✅ Authentication APIs")
    print("  2. ✅ Transaction APIs")
    print("  3. ✅ Settlement APIs")
    print("  4. ✅ Admin-specific APIs")
    print("="*60)


def main():
    """Main test execution"""
    print(f"{Fore.MAGENTA}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     SABPAISA REPORTS API - COMPREHENSIVE TEST SUITE      ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")

    print_info(f"Testing against: {BASE_URL}")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run tests
    if test_authentication_apis():
        test_transaction_apis()
        test_settlement_apis()
        test_admin_specific_apis()

    # Generate summary
    generate_summary()

    print_info(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        sys.exit(1)
