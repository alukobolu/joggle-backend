"""
Comprehensive Endpoint Testing Script for Joggle Backend
This script tests all API endpoints with proper flow and error handling.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional

# Configuration
BASE_URL = "http://127.0.0.1:8000"
COLORS = {
    'GREEN': '\033[92m',
    'RED': '\033[91m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'MAGENTA': '\033[95m',
    'CYAN': '\033[96m',
    'RESET': '\033[0m',
    'BOLD': '\033[1m'
}

# Test data
test_user = {
    'email': f'testuser_{datetime.now().timestamp()}@example.com',
    'password': 'TestPass123!@#',
    'password_confirm': 'TestPass123!@#',
    'firstname': 'Test',
    'lastname': 'User'
}

# Session storage
session = requests.Session()
test_data = {
    'user_id': None,
    'email': None,
    'otp_code': None,
    'csrf_token': None
}


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{COLORS['BOLD']}{COLORS['CYAN']}{'=' * 80}{COLORS['RESET']}")
    print(f"{COLORS['BOLD']}{COLORS['CYAN']}{text.center(80)}{COLORS['RESET']}")
    print(f"{COLORS['BOLD']}{COLORS['CYAN']}{'=' * 80}{COLORS['RESET']}\n")


def print_test(test_name: str):
    """Print test name"""
    print(f"{COLORS['BOLD']}{COLORS['BLUE']}Testing: {test_name}{COLORS['RESET']}")


def print_success(message: str):
    """Print success message"""
    print(f"{COLORS['GREEN']}✓ {message}{COLORS['RESET']}")


def print_error(message: str):
    """Print error message"""
    print(f"{COLORS['RED']}✗ {message}{COLORS['RESET']}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{COLORS['YELLOW']}⚠ {message}{COLORS['RESET']}")


def print_info(message: str):
    """Print info message"""
    print(f"{COLORS['MAGENTA']}ℹ {message}{COLORS['RESET']}")


def make_request(method: str, endpoint: str, data: Optional[Dict] = None, 
                 expected_status: int = 200, use_session: bool = True) -> Optional[requests.Response]:
    """Make HTTP request and handle response"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if use_session:
            if method.upper() == 'GET':
                response = session.get(url)
            elif method.upper() == 'POST':
                response = session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = session.put(url, json=data)
            elif method.upper() == 'PATCH':
                response = session.patch(url, json=data)
        else:
            if method.upper() == 'GET':
                response = requests.get(url)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, json=data)
        
        print_info(f"Request: {method.upper()} {endpoint}")
        if data:
            print_info(f"Payload: {json.dumps(data, indent=2)}")
        print_info(f"Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print_info(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            print_info(f"Response: {response.text}")
        
        if response.status_code == expected_status:
            print_success(f"Expected status {expected_status} received")
            return response
        else:
            print_error(f"Expected status {expected_status}, got {response.status_code}")
            return response
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return None


def test_signup():
    """Test user registration endpoint"""
    print_test("User Signup - POST /account/signup/")
    
    response = make_request('POST', '/account/signup/', test_user, expected_status=201)
    
    if response and response.status_code == 201:
        data = response.json()
        test_data['user_id'] = data.get('user_id')
        test_data['email'] = data.get('email')
        print_success(f"User created with ID: {test_data['user_id']}")
        print_warning("Check console for OTP code (using console email backend)")
        return True
    return False


def test_signup_duplicate():
    """Test duplicate email registration (should fail)"""
    print_test("Duplicate Signup - POST /account/signup/ (should fail)")
    
    response = make_request('POST', '/account/signup/', test_user, expected_status=400)
    
    if response and response.status_code == 400:
        print_success("Correctly rejected duplicate email")
        return True
    return False


def test_verify_otp():
    """Test OTP verification"""
    print_test("OTP Verification - POST /account/verify-otp/")
    
    print_warning("OTP is displayed in the console where Django server is running")
    otp = input(f"{COLORS['YELLOW']}Enter the OTP code from server console: {COLORS['RESET']}")
    
    data = {
        'email': test_data['email'],
        'otp_code': otp
    }
    
    response = make_request('POST', '/account/verify-otp/', data, expected_status=200)
    
    if response and response.status_code == 200:
        print_success("OTP verified successfully")
        return True
    return False


def test_resend_otp():
    """Test resend OTP"""
    print_test("Resend OTP - POST /account/resend-otp/")
    
    data = {
        'email': test_data['email']
    }
    
    response = make_request('POST', '/account/resend-otp/', data, expected_status=200)
    
    if response and response.status_code == 200:
        print_success("OTP resent successfully")
        return True
    return False


def test_login():
    """Test user login"""
    print_test("User Login - POST /account/login/")
    
    data = {
        'email': test_user['email'],
        'password': test_user['password']
    }
    
    response = make_request('POST', '/account/login/', data, expected_status=200)
    
    if response and response.status_code == 200:
        print_success("Login successful")
        # Store session cookies
        return True
    return False


def test_login_unverified():
    """Test login with unverified account (before OTP verification)"""
    print_test("Login Before Verification - POST /account/login/ (should fail)")
    
    # Create a new unverified user
    new_user = {
        'email': f'unverified_{datetime.now().timestamp()}@example.com',
        'password': 'TestPass123!@#',
        'password_confirm': 'TestPass123!@#',
        'firstname': 'Unverified',
        'lastname': 'User'
    }
    
    # Register user
    make_request('POST', '/account/signup/', new_user, expected_status=201)
    
    # Try to login without verification
    login_data = {
        'email': new_user['email'],
        'password': new_user['password']
    }
    
    response = make_request('POST', '/account/login/', login_data, expected_status=400, use_session=False)
    
    if response and response.status_code == 400:
        print_success("Correctly blocked unverified user from logging in")
        return True
    return False


def test_user_status():
    """Test getting user status"""
    print_test("User Status - GET /account/status/")
    
    response = make_request('GET', '/account/status/', expected_status=200)
    
    if response and response.status_code == 200:
        print_success("User status retrieved successfully")
        return True
    return False


def test_user_profile():
    """Test getting user profile"""
    print_test("Get User Profile - GET /account/profile/")
    
    response = make_request('GET', '/account/profile/', expected_status=200)
    
    if response and response.status_code == 200:
        print_success("User profile retrieved successfully")
        return True
    return False


def test_update_profile():
    """Test updating user profile"""
    print_test("Update User Profile - PUT /account/profile/update/")
    
    data = {
        'firstname': 'Updated',
        'lastname': 'Name',
        'country': 'USA',
        'phone': '+1234567890'
    }
    
    response = make_request('PUT', '/account/profile/update/', data, expected_status=200)
    
    if response and response.status_code == 200:
        print_success("User profile updated successfully")
        return True
    return False


def test_change_password():
    """Test changing password"""
    print_test("Change Password - POST /account/change-password/")
    
    data = {
        'old_password': test_user['password'],
        'new_password': 'NewTestPass123!@#',
        'new_password_confirm': 'NewTestPass123!@#'
    }
    
    response = make_request('POST', '/account/change-password/', data, expected_status=200)
    
    if response and response.status_code == 200:
        print_success("Password changed successfully")
        # Update password for future tests
        test_user['password'] = 'NewTestPass123!@#'
        return True
    return False


def test_change_password_wrong_old():
    """Test changing password with wrong old password"""
    print_test("Change Password with Wrong Old Password - POST /account/change-password/ (should fail)")
    
    data = {
        'old_password': 'WrongPassword123!@#',
        'new_password': 'AnotherPass123!@#',
        'new_password_confirm': 'AnotherPass123!@#'
    }
    
    response = make_request('POST', '/account/change-password/', data, expected_status=400)
    
    if response and response.status_code == 400:
        print_success("Correctly rejected wrong old password")
        return True
    return False


def test_request_password_reset():
    """Test requesting password reset"""
    print_test("Request Password Reset - POST /account/request-password-reset/")
    
    data = {
        'email': test_data['email']
    }
    
    response = make_request('POST', '/account/request-password-reset/', data, expected_status=200)
    
    if response and response.status_code == 200:
        print_success("Password reset OTP sent successfully")
        return True
    return False


def test_confirm_password_reset():
    """Test confirming password reset with OTP"""
    print_test("Confirm Password Reset - POST /account/confirm-password-reset/")
    
    print_warning("Check console for password reset OTP")
    otp = input(f"{COLORS['YELLOW']}Enter the OTP code from server console: {COLORS['RESET']}")
    
    new_password = 'ResetPass123!@#'
    data = {
        'email': test_data['email'],
        'otp_code': otp,
        'new_password': new_password,
        'new_password_confirm': new_password
    }
    
    response = make_request('POST', '/account/confirm-password-reset/', data, expected_status=200)
    
    if response and response.status_code == 200:
        print_success("Password reset successfully")
        # Update password for logout test
        test_user['password'] = new_password
        return True
    return False


def test_logout():
    """Test user logout"""
    print_test("User Logout - POST /account/logout/")
    
    response = make_request('POST', '/account/logout/', expected_status=200)
    
    if response and response.status_code == 200:
        print_success("Logout successful")
        return True
    return False


def test_unauthorized_access():
    """Test accessing protected endpoints without authentication"""
    print_test("Unauthorized Access - GET /account/profile/ (should fail)")
    
    # Create new session without authentication
    response = requests.get(f"{BASE_URL}/account/profile/")
    
    print_info(f"Status Code: {response.status_code}")
    
    if response.status_code in [401, 403]:
        print_success("Correctly blocked unauthorized access")
        return True
    else:
        print_error(f"Expected 401/403, got {response.status_code}")
        return False


def run_all_tests():
    """Run all endpoint tests"""
    print_header("JOGGLE BACKEND API ENDPOINT TESTING")
    
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Authentication Flow Tests
    print_header("AUTHENTICATION TESTS")
    results.append(("Signup", test_signup()))
    results.append(("Duplicate Signup", test_signup_duplicate()))
    results.append(("Resend OTP", test_resend_otp()))
    results.append(("Verify OTP", test_verify_otp()))
    results.append(("Login Unverified User", test_login_unverified()))
    results.append(("Login", test_login()))
    
    # Protected Endpoints Tests
    print_header("PROFILE MANAGEMENT TESTS")
    results.append(("Get User Status", test_user_status()))
    results.append(("Get User Profile", test_user_profile()))
    results.append(("Update User Profile", test_update_profile()))
    
    # Password Management Tests
    print_header("PASSWORD MANAGEMENT TESTS")
    results.append(("Change Password (Wrong Old)", test_change_password_wrong_old()))
    results.append(("Change Password", test_change_password()))
    results.append(("Request Password Reset", test_request_password_reset()))
    results.append(("Confirm Password Reset", test_confirm_password_reset()))
    
    # Re-login with new password
    print_header("RE-LOGIN AFTER PASSWORD RESET")
    results.append(("Login with New Password", test_login()))
    
    # Logout Test
    print_header("LOGOUT TEST")
    results.append(("Logout", test_logout()))
    
    # Unauthorized Access Test
    print_header("SECURITY TESTS")
    results.append(("Unauthorized Access", test_unauthorized_access()))
    
    # Print Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    print(f"\n{COLORS['BOLD']}Total Tests: {len(results)}{COLORS['RESET']}")
    print(f"{COLORS['GREEN']}Passed: {passed}{COLORS['RESET']}")
    print(f"{COLORS['RED']}Failed: {failed}{COLORS['RESET']}")
    
    if failed > 0:
        print(f"\n{COLORS['BOLD']}{COLORS['RED']}Failed Tests:{COLORS['RESET']}")
        for test_name, result in results:
            if not result:
                print(f"{COLORS['RED']}  ✗ {test_name}{COLORS['RESET']}")
    
    print(f"\n{COLORS['BOLD']}{'=' * 80}{COLORS['RESET']}\n")
    
    return passed, failed


if __name__ == "__main__":
    try:
        print(f"{COLORS['YELLOW']}")
        print("=" * 80)
        print("IMPORTANT: Make sure the Django development server is running on port 8000")
        print("Run: python manage.py runserver")
        print("=" * 80)
        print(f"{COLORS['RESET']}\n")
        
        input(f"{COLORS['YELLOW']}Press Enter to start testing...{COLORS['RESET']}")
        
        passed, failed = run_all_tests()
        
        if failed == 0:
            print(f"{COLORS['GREEN']}{COLORS['BOLD']}🎉 All tests passed!{COLORS['RESET']}")
        else:
            print(f"{COLORS['RED']}{COLORS['BOLD']}⚠️  Some tests failed. Please review the output above.{COLORS['RESET']}")
            
    except KeyboardInterrupt:
        print(f"\n\n{COLORS['YELLOW']}Testing interrupted by user{COLORS['RESET']}")
    except Exception as e:
        print(f"\n\n{COLORS['RED']}Fatal error: {str(e)}{COLORS['RESET']}")

