# Mental Wellness Coach - Feature Testing Guide

This document provides comprehensive information about the feature testing script (`test_all_features.py`) for the Mental Wellness Coach application.

## 🎯 Overview

The `test_all_features.py` script is a comprehensive testing tool that validates all implemented features of the Mental Wellness Coach application. It performs end-to-end testing of API endpoints, authentication flows, and integration scenarios to ensure the system works as expected.

## 🚀 Quick Start

### Prerequisites

1. **Backend Server Running**: Ensure the Flask backend is running on `localhost:3000` (or your specified URL)
2. **Database Configured**: PostgreSQL database should be set up and accessible
3. **Environment Variables**: All required environment variables should be set (refer to `env.example`)

### Installation

```bash
# Install testing dependencies
pip install -r test_requirements.txt

# Or install manually
pip install requests colorama
```

### Basic Usage

```bash
# Test against default server (localhost:3000)
python test_all_features.py

# Test against custom server URL
python test_all_features.py http://your-server:3000

# Use environment variable for server URL
export TEST_SERVER_URL=http://your-server:3000
python test_all_features.py
```

## 🧪 Test Coverage

### 1. Authentication System Tests
- **User Registration**: Creates a new test user account
- **User Login**: Authenticates and retrieves access token
- **Protected Route Access**: Validates JWT token authentication

### 2. Mood Tracking System Tests
- **Create Mood Entry**: Tests mood entry creation with full data
- **Get Mood History**: Retrieves user's mood entry history
- **Get Mood Analytics**: Tests analytics endpoint with date ranges
- **Quick Mood Check-in**: Tests simplified mood check-in flow

### 3. AI Conversation System Tests
- **Start New Conversation**: Initiates AI conversation with mental health context
- **Send Message**: Tests message exchange and AI response generation
- **Get Conversation History**: Retrieves conversation message history
- **List User Conversations**: Tests conversation listing functionality

### 4. Crisis Detection System Tests
- **Safe Content Analysis**: Tests crisis detection with normal content
- **Concerning Content Analysis**: Tests crisis detection with concerning language
- **Get Crisis Resources**: Retrieves available crisis support resources
- **Emergency Contact Info**: Tests emergency contact information retrieval

### 5. uAgents System Tests
- **Agent Status Check**: Validates agent system health and status
- **Agent Task Coordination**: Tests inter-agent task coordination
- **Agent Communication**: Tests agent-to-agent messaging
- **Agent Performance Metrics**: Retrieves agent performance data

### 6. Integration Scenario Tests
- **Mood → AI → Agent Flow**: Tests complete mood analysis workflow
- **Crisis → Emergency → Agent Protocol**: Tests crisis escalation workflow

## 📊 Test Output

The script provides colorized output with clear status indicators:

- 🟢 **[PASS]**: Test completed successfully
- 🔴 **[FAIL]**: Test failed with error details
- 🟡 **[SKIP]**: Test skipped (usually due to missing dependencies)
- 🟣 **[ERROR]**: Unexpected error occurred

### Sample Output

```
================================================================================
            Mental Wellness Coach - Comprehensive Feature Test Suite            
================================================================================

Testing server at: http://localhost:3000
Test started at: 2024-12-18 14:30:00

[PASS] Server Health Check
        Server is running

============================================================
                    AUTHENTICATION SYSTEM TESTS                    
============================================================

[PASS] User Registration
        User ID: 123
[PASS] User Login
        Token received, User ID: 123
[PASS] Protected Route Access
        Profile accessed successfully

============================================================
                      MOOD TRACKING SYSTEM TESTS                      
============================================================

[PASS] Create Mood Entry
        Entry ID: 456
[PASS] Get Mood History
        Retrieved 5 entries
[PASS] Get Mood Analytics
        Analytics retrieved successfully
[PASS] Quick Mood Check-in
        Quick check-in successful

... (additional test sections)

============================================================
                        TEST RESULTS SUMMARY                        
============================================================

[PASS] Authentication System Suite
[PASS] Mood Tracking System Suite
[PASS] AI Conversation System Suite
[PASS] Crisis Detection System Suite
[PASS] uAgents System Suite
[PASS] Integration Scenarios Suite

Overall Statistics:
  ✅ Passed: 24
  ❌ Failed: 0
  ⏭️  Skipped: 2
  📊 Success Rate: 100.0%

 🎉 ALL TESTS PASSED! 🎉 

================================================================================
```

## ⚙️ Configuration

### Environment Variables

- **TEST_SERVER_URL**: Override default server URL
- **TEST_USER_EMAIL**: Custom test user email (optional)
- **TEST_USER_PASSWORD**: Custom test user password (optional)

### Custom Configuration

You can modify the test script for custom configurations:

```python
# In test_all_features.py
class MentalWellnessTestSuite:
    def __init__(self, base_url: str = "http://localhost:3000"):
        # Modify test user data
        self.test_user_data = {
            "email": "your_test_user@example.com",
            "password": "YourTestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Server Connection Failed
```
[FAIL] Server Health Check
        Connection error: Connection refused
```

**Solution**: Ensure the backend server is running:
```bash
cd backend
python app.py
```

#### 2. Authentication Failures
```
[FAIL] User Registration
        Status: 400
```

**Solutions**:
- Check database connection
- Verify required environment variables are set
- Ensure user doesn't already exist (test will skip if user exists)

#### 3. Database Connection Issues
```
[ERROR] Create Mood Entry
        Database connection failed
```

**Solutions**:
- Verify PostgreSQL is running
- Check database credentials in environment variables
- Ensure database schema is properly migrated

#### 4. LLM Service Unavailable
```
[FAIL] Start New Conversation
        Status: 503
```

**Solutions**:
- Check ASI LLM service availability
- Verify API keys in environment variables
- Ensure fallback mode is configured properly

### Debug Mode

To enable verbose debugging, modify the script:

```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable request debugging
import http.client as http_client
http_client.HTTPConnection.debuglevel = 1
```

## 🧩 Extending the Tests

### Adding New Test Suites

1. **Create Test Method**:
```python
def test_new_feature_system(self) -> bool:
    """Test the new feature system."""
    self.print_header("NEW FEATURE SYSTEM TESTS")
    
    if not self.auth_token:
        self.print_test("New Feature Tests", "SKIP", "No authentication token")
        return False
    
    headers = {"Authorization": f"Bearer {self.auth_token}"}
    feature_success = True
    
    # Add your tests here
    
    return feature_success
```

2. **Add to Test Suite List**:
```python
test_suites = [
    # ... existing suites
    ("New Feature System", self.test_new_feature_system)
]
```

### Adding Individual Tests

```python
# Test pattern
try:
    response = self.session.post(
        f"{self.base_url}/api/new-endpoint",
        json=test_data,
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        self.print_test("New Test", "PASS", "Test completed successfully")
    else:
        self.print_test("New Test", "FAIL", f"Status: {response.status_code}")
        success = False
        
except Exception as e:
    self.print_test("New Test", "ERROR", str(e))
    success = False
```

## 📋 Integration with CI/CD

### GitHub Actions Integration

```yaml
name: Feature Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r test_requirements.txt
    
    - name: Start backend server
      run: |
        cd backend
        python app.py &
        sleep 10
    
    - name: Run feature tests
      run: python test_all_features.py
```

### Local CI Integration

```bash
#!/bin/bash
# test_runner.sh

# Start services
docker-compose up -d

# Wait for services to be ready
sleep 30

# Run tests
python test_all_features.py

# Capture exit code
TEST_EXIT_CODE=$?

# Cleanup
docker-compose down

# Exit with test result
exit $TEST_EXIT_CODE
```

## 📈 Performance Considerations

### Test Execution Time

- **Full test suite**: ~60-90 seconds
- **Authentication tests**: ~5-10 seconds
- **Mood tracking tests**: ~10-15 seconds
- **Conversation tests**: ~15-25 seconds (depends on AI response time)
- **Crisis detection tests**: ~10-15 seconds
- **Agent system tests**: ~15-20 seconds
- **Integration tests**: ~10-15 seconds

### Optimization Tips

1. **Parallel Testing**: Consider running test suites in parallel for faster execution
2. **Test Data Cleanup**: Implement cleanup routines to prevent data accumulation
3. **Selective Testing**: Add command-line options to run specific test suites
4. **Mocking**: Consider mocking external services for faster unit tests

## 🔒 Security Considerations

### Test Data

- Uses dedicated test user account
- Test data is clearly marked and separate from production data
- Passwords follow security requirements
- No sensitive production data is used

### API Security

- Tests authentication and authorization properly
- Validates JWT token handling
- Tests rate limiting and security headers
- Checks for proper error handling without information disclosure

### Best Practices

- Never commit API keys or secrets in test files
- Use environment variables for sensitive configuration
- Regularly rotate test user credentials
- Monitor test results for security-related failures

## 📞 Support

For issues with the testing script:

1. **Check the troubleshooting section** above
2. **Review the backend logs** for detailed error information
3. **Ensure all prerequisites** are met
4. **Verify environment configuration** matches requirements

## 🔄 Maintenance

### Regular Updates

- **Update test cases** when new features are added
- **Verify test data** remains valid and secure
- **Update dependencies** regularly for security
- **Review test coverage** for new API endpoints

### Test Data Management

```bash
# Clean up test data (if needed)
python -c "
from backend.app import app, db
from backend.models import User
with app.app_context():
    test_user = User.query.filter_by(email='test_user_features@example.com').first()
    if test_user:
        db.session.delete(test_user)
        db.session.commit()
        print('Test user cleaned up')
"
```

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Maintained By**: Mental Wellness Coach QA Team 