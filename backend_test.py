#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Laude Agent Enterprise
Tests all endpoints including authentication, reports, automation requests, and admin functions
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class LaudeAgentAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.session_token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test data
        self.test_email = "test.user@hssmedicine.com"
        self.test_user_data = {
            "email": self.test_email,
            "full_name": "Test User",
            "department": "IT Testing"
        }
        
    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED")
        else:
            print(f"❌ {name}: FAILED - {details}")
            
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    expected_status: int = 200, use_auth: bool = False) -> tuple[bool, Dict]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if use_auth and self.session_token:
            headers['Authorization'] = f'Bearer {self.session_token}'
            
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            else:
                return False, {"error": f"Unsupported method: {method}"}
                
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text, "status_code": response.status_code}
                
            return success, response_data
            
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        success, response = self.make_request('GET', '/')
        
        if success and response.get('service') == 'Laude Agent Enterprise API':
            self.log_test("Health Check", True, "API is operational")
            return True
        else:
            self.log_test("Health Check", False, f"Unexpected response: {response}")
            return False
    
    def test_user_registration(self):
        """Test user registration with domain validation"""
        print("\n🔐 Testing User Registration...")
        
        # Test valid domain registration
        success, response = self.make_request('POST', '/api/auth/register', self.test_user_data, 200)
        
        if success and response.get('success'):
            self.log_test("User Registration (Valid Domain)", True, "User registered successfully")
        else:
            # User might already exist, which is fine for testing
            if "already registered" in str(response.get('detail', '')):
                self.log_test("User Registration (Valid Domain)", True, "User already exists (expected)")
            else:
                self.log_test("User Registration (Valid Domain)", False, f"Registration failed: {response}")
        
        # Test invalid domain registration
        invalid_user = {
            "email": "test@invalid-domain.com",
            "full_name": "Invalid User",
            "department": "Testing"
        }
        
        success, response = self.make_request('POST', '/api/auth/register', invalid_user, 400)
        
        if success and "restricted to hssmedicine.com" in str(response.get('detail', '')):
            self.log_test("User Registration (Invalid Domain)", True, "Domain validation working")
        else:
            self.log_test("User Registration (Invalid Domain)", False, f"Domain validation failed: {response}")
    
    def test_otp_generation(self):
        """Test OTP generation"""
        print("\n📧 Testing OTP Generation...")
        
        # Test valid email OTP generation
        success, response = self.make_request('POST', '/api/auth/generate-otp', 
                                            {"email": self.test_email}, 200)
        
        if success and response.get('success'):
            self.log_test("OTP Generation (Valid Email)", True, "OTP generated successfully")
            return True
        else:
            self.log_test("OTP Generation (Valid Email)", False, f"OTP generation failed: {response}")
            return False
    
    def test_otp_verification(self):
        """Test OTP verification - requires manual OTP from file"""
        print("\n🔑 Testing OTP Verification...")
        
        # First generate OTP
        if not self.test_otp_generation():
            return False
            
        # Try to find OTP from saved file
        import os
        from pathlib import Path
        
        otp_dir = Path("backend/otp_emails")
        if otp_dir.exists():
            # Find the most recent OTP file
            otp_files = list(otp_dir.glob(f"otp_{self.test_email.replace('@', '_at_')}_*.html"))
            if otp_files:
                latest_file = max(otp_files, key=os.path.getctime)
                
                try:
                    with open(latest_file, 'r') as f:
                        content = f.read()
                        # Extract OTP from comment
                        for line in content.split('\n'):
                            if line.startswith('<!-- OTP:'):
                                otp_code = line.split('OTP:')[1].split('-->')[0].strip()
                                
                                # Test OTP verification
                                success, response = self.make_request('POST', '/api/auth/verify-otp',
                                                                    {"email": self.test_email, "otp_code": otp_code}, 200)
                                
                                if success and response.get('success') and response.get('session_token'):
                                    self.session_token = response['session_token']
                                    self.user_data = response.get('user_data', {})
                                    self.log_test("OTP Verification", True, "Login successful with session token")
                                    return True
                                else:
                                    self.log_test("OTP Verification", False, f"OTP verification failed: {response}")
                                    return False
                                    
                except Exception as e:
                    self.log_test("OTP Verification", False, f"Error reading OTP file: {str(e)}")
                    return False
        
        # If we can't find OTP file, try a mock verification (will fail but test the endpoint)
        success, response = self.make_request('POST', '/api/auth/verify-otp',
                                            {"email": self.test_email, "otp_code": "123456"}, 400)
        
        if success and "Invalid or expired OTP" in str(response.get('detail', '')):
            self.log_test("OTP Verification (Invalid Code)", True, "OTP validation working correctly")
        else:
            self.log_test("OTP Verification (Invalid Code)", False, f"Unexpected response: {response}")
        
        return False
    
    def test_protected_endpoints(self):
        """Test endpoints that require authentication"""
        if not self.session_token:
            print("\n⚠️  Skipping protected endpoint tests - no valid session token")
            return
            
        print("\n🔒 Testing Protected Endpoints...")
        
        # Test report generation
        report_data = {
            "transcript": "This week I worked on testing the Laude Agent application. I completed comprehensive API testing and frontend validation. The system is working well with proper authentication and data flow.",
            "user_id": self.user_data.get('user_id', '')
        }
        
        success, response = self.make_request('POST', '/api/reports/generate', report_data, 200, use_auth=True)
        
        if success and response.get('success'):
            self.log_test("Report Generation", True, "Report generated successfully")
            report_id = response.get('report_id')
        else:
            self.log_test("Report Generation", False, f"Report generation failed: {response}")
            report_id = None
        
        # Test report history
        success, response = self.make_request('GET', '/api/reports/history', use_auth=True)
        
        if success and response.get('success'):
            self.log_test("Report History", True, f"Retrieved {len(response.get('reports', []))} reports")
        else:
            self.log_test("Report History", False, f"Report history failed: {response}")
        
        # Test automation request creation
        automation_data = {
            "title": "Test Automation Request",
            "description": "This is a test automation request for API testing purposes",
            "priority": "medium",
            "user_id": self.user_data.get('user_id', '')
        }
        
        success, response = self.make_request('POST', '/api/automation/requests', automation_data, 200, use_auth=True)
        
        if success and response.get('success'):
            self.log_test("Automation Request Creation", True, "Request created successfully")
            request_id = response.get('request_id')
        else:
            self.log_test("Automation Request Creation", False, f"Request creation failed: {response}")
            request_id = None
        
        # Test getting user's automation requests
        success, response = self.make_request('GET', '/api/automation/requests', use_auth=True)
        
        if success and response.get('success'):
            self.log_test("Get User Automation Requests", True, f"Retrieved {len(response.get('requests', []))} requests")
        else:
            self.log_test("Get User Automation Requests", False, f"Get requests failed: {response}")
        
        # Test adding message to request
        if request_id:
            message_data = {
                "request_id": request_id,
                "message": "This is a test message for the automation request",
                "sender_type": "user",
                "user_id": self.user_data.get('user_id', '')
            }
            
            success, response = self.make_request('POST', f'/api/automation/requests/{request_id}/messages', 
                                                message_data, 200, use_auth=True)
            
            if success and response.get('success'):
                self.log_test("Add Message to Request", True, "Message added successfully")
            else:
                self.log_test("Add Message to Request", False, f"Add message failed: {response}")
            
            # Test getting messages
            success, response = self.make_request('GET', f'/api/automation/requests/{request_id}/messages', use_auth=True)
            
            if success and response.get('success'):
                self.log_test("Get Request Messages", True, f"Retrieved {len(response.get('messages', []))} messages")
            else:
                self.log_test("Get Request Messages", False, f"Get messages failed: {response}")
    
    def test_admin_endpoints(self):
        """Test admin-only endpoints"""
        if not self.session_token:
            print("\n⚠️  Skipping admin endpoint tests - no valid session token")
            return
            
        print("\n👑 Testing Admin Endpoints...")
        
        # Test admin stats (will fail if user is not admin)
        success, response = self.make_request('GET', '/api/admin/stats', use_auth=True)
        
        if success and response.get('success'):
            self.log_test("Admin Stats", True, "Admin stats retrieved successfully")
            
            # Test getting all requests
            success, response = self.make_request('GET', '/api/admin/requests', use_auth=True)
            
            if success and response.get('success'):
                self.log_test("Admin Get All Requests", True, f"Retrieved {len(response.get('requests', []))} requests")
            else:
                self.log_test("Admin Get All Requests", False, f"Get all requests failed: {response}")
                
        else:
            if response.get('detail') == 'Admin access required':
                self.log_test("Admin Stats (Non-Admin User)", True, "Admin access properly restricted")
            else:
                self.log_test("Admin Stats", False, f"Admin stats failed: {response}")
    
    def test_logout(self):
        """Test logout functionality"""
        if not self.session_token:
            return
            
        print("\n🚪 Testing Logout...")
        
        success, response = self.make_request('POST', '/api/auth/logout', use_auth=True)
        
        if success and response.get('success'):
            self.log_test("Logout", True, "Logout successful")
            self.session_token = None
            self.user_data = None
        else:
            self.log_test("Logout", False, f"Logout failed: {response}")
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Laude Agent Enterprise API Tests")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return False
        
        # Authentication flow
        self.test_user_registration()
        
        # Try to authenticate
        if self.test_otp_verification():
            # Run protected endpoint tests
            self.test_protected_endpoints()
            self.test_admin_endpoints()
            self.test_logout()
        else:
            print("⚠️  Authentication failed - skipping protected endpoint tests")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/max(self.tests_run, 1)*100):.1f}%")
        
        # Show failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['name']}: {test['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = LaudeAgentAPITester("http://localhost:8001")
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())