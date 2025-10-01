# Joggle Backend API Testing Guide

## Overview
This testing script (`test.py`) provides comprehensive endpoint testing for the Joggle backend API. It tests all authentication, profile management, and password management endpoints with proper flow simulation.

## Features

### Tested Endpoints

#### Authentication Endpoints
- ✅ **POST /account/signup/** - User registration
- ✅ **POST /account/login/** - User login
- ✅ **POST /account/logout/** - User logout
- ✅ **POST /account/verify-otp/** - Email verification with OTP
- ✅ **POST /account/resend-otp/** - Resend OTP code

#### Password Management Endpoints
- ✅ **POST /account/change-password/** - Change user password
- ✅ **POST /account/request-password-reset/** - Request password reset
- ✅ **POST /account/confirm-password-reset/** - Confirm password reset with OTP

#### Profile Management Endpoints
- ✅ **GET /account/profile/** - Get user profile
- ✅ **PUT /account/profile/update/** - Update user profile
- ✅ **GET /account/status/** - Get user status

### Test Coverage

The script tests:
1. **Happy Path Scenarios** - Normal user flow from registration to logout
2. **Error Scenarios** - Invalid credentials, duplicate emails, wrong passwords
3. **Security Scenarios** - Unauthorized access, unverified user login
4. **Session Management** - Proper cookie/session handling across requests
5. **OTP Flow** - Complete OTP generation, sending, and verification

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Django development server** running
3. **Required packages** installed (see Installation)

## Installation

1. Install required Python packages:
```bash
pip install -r requirements.txt
```

2. Ensure Django migrations are applied:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Start the Django development server:
```bash
python manage.py runserver
```

## Usage

### Running the Test Script

1. **Start Django Server** (in one terminal):
```bash
python manage.py runserver
```

2. **Run the Test Script** (in another terminal):
```bash
python test.py
```

### Interactive Testing

The script will:
1. Display a welcome message and wait for you to press Enter
2. Begin testing endpoints sequentially
3. Prompt you to enter OTP codes when needed (check Django console output)
4. Display colored output for each test:
   - 🟢 Green ✓ = Test passed
   - 🔴 Red ✗ = Test failed
   - 🟡 Yellow ⚠ = Warning/Info
   - 🔵 Blue = Test name
   - 🟣 Magenta ℹ = Information

### Sample Output

```
================================================================================
                    JOGGLE BACKEND API ENDPOINT TESTING                    
================================================================================

ℹ Base URL: http://127.0.0.1:8000
ℹ Test started at: 2025-10-01 14:30:00

================================================================================
                          AUTHENTICATION TESTS                          
================================================================================

Testing: User Signup - POST /account/signup/
ℹ Request: POST /account/signup/
ℹ Payload: {
  "email": "testuser_1234567890@example.com",
  "password": "TestPass123!@#",
  ...
}
ℹ Status Code: 201
✓ Expected status 201 received
✓ User created with ID: 123
⚠ Check console for OTP code (using console email backend)

...
```

## OTP Handling

Since the development environment uses Django's console email backend, OTP codes are displayed in the Django server console output. When prompted:

1. Check the terminal where `python manage.py runserver` is running
2. Look for output like:
   ```
   Your verification code is: 123456
   
   This code will expire in 10 minutes.
   ```
3. Copy the 6-digit code
4. Paste it into the test script when prompted

## Configuration

You can modify the following in `test.py`:

```python
# Change the base URL
BASE_URL = "http://127.0.0.1:8000"

# Modify test user data
test_user = {
    'email': f'testuser_{datetime.now().timestamp()}@example.com',
    'password': 'TestPass123!@#',
    'firstname': 'Test',
    'lastname': 'User'
}
```

## Test Flow

The script follows this flow:

1. **User Registration**
   - Register new user
   - Attempt duplicate registration (should fail)
   
2. **OTP Verification**
   - Resend OTP
   - Verify OTP
   - Test login before verification (should fail)
   
3. **Login**
   - Login with verified account
   
4. **Profile Management**
   - Get user status
   - Get user profile
   - Update user profile
   
5. **Password Management**
   - Attempt password change with wrong old password (should fail)
   - Change password successfully
   - Request password reset
   - Confirm password reset with OTP
   
6. **Re-login**
   - Login with new password after reset
   
7. **Logout**
   - Logout user
   
8. **Security**
   - Test unauthorized access (should fail)

## Troubleshooting

### Connection Refused Error
**Problem:** `ConnectionRefusedError` or `Connection refused`

**Solution:** 
- Ensure Django server is running on port 8000
- Check if another process is using port 8000
- Try: `python manage.py runserver 0.0.0.0:8000`

### CSRF Token Error
**Problem:** `403 Forbidden - CSRF verification failed`

**Solution:**
- The script uses session-based requests which handle CSRF automatically
- Ensure `CSRF_TRUSTED_ORIGINS` in settings.py includes your URL

### OTP Not Received
**Problem:** Can't find OTP in console

**Solution:**
- Check the terminal where Django server is running
- Ensure `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` in settings.py
- Look for recent output after signup/reset password requests

### Authentication Errors
**Problem:** `401 Unauthorized` or `403 Forbidden` on protected endpoints

**Solution:**
- Ensure login test passed before testing protected endpoints
- The script uses `requests.Session()` to maintain authentication
- Check if session middleware is enabled in Django

### Test Failures
**Problem:** Multiple tests failing

**Solution:**
1. Run tests one at a time to isolate issues
2. Check Django server logs for errors
3. Verify database is accessible and migrations are applied
4. Ensure all required packages are installed

## Extending the Tests

To add custom tests:

```python
def test_custom_endpoint():
    """Test your custom endpoint"""
    print_test("Custom Test - GET /custom/endpoint/")
    
    response = make_request('GET', '/custom/endpoint/', expected_status=200)
    
    if response and response.status_code == 200:
        print_success("Custom test passed")
        return True
    return False

# Add to run_all_tests() function:
results.append(("Custom Test", test_custom_endpoint()))
```

## Notes

- Tests create real database entries - consider using a test database
- Unique emails are generated using timestamps to avoid conflicts
- The script maintains session state between requests
- All passwords follow Django's validation rules (min 8 chars, not common, etc.)
- Color codes work on most terminals (Windows 10+, Linux, macOS)

## Support

For issues or questions:
1. Check the Django server logs for backend errors
2. Review the test script output for specific error messages
3. Ensure all prerequisites are met
4. Verify settings.py configuration matches the project requirements

