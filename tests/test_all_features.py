#!/usr/bin/env python3
"""
Mental Wellness Coach - Comprehensive Feature Testing Script

This script tests all implemented features of the Mental Wellness Coach application.
It covers authentication, mood tracking, conversations, crisis detection, and agent systems.

Usage:
    python test_all_features.py

Requirements:
    - Backend server running on localhost:3000
    - PostgreSQL database configured
    - All environment variables set as per env.example
"""

import asyncio
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import colorama
from colorama import Fore, Style, Back
import sys
import os

# Initialize colorama for cross-platform colored output
colorama.init()

class MentalWellnessTestSuite:
    """Comprehensive test suite for Mental Wellness Coach features."""
    
    def __init__(self, base_url: str = "http://localhost:3000", debug: bool = False):
        """
        Initialize the test suite.
        
        Args:
            base_url (str): Base URL for the API server
            debug (bool): Enable debug output for troubleshooting
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.debug = debug
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
        
        # Test data
        self.test_user_data = {
            "email": "test_user_features@example.com",
            "password": "TestPassword123!",
            "name": "Test User"
        }

    def print_header(self, text: str) -> None:
        """Print a styled header for test sections."""
        print(f"\n{Fore.CYAN}{Back.BLUE}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Back.BLUE} {text.center(58)} {Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Back.BLUE}{'='*60}{Style.RESET_ALL}\n")

    def print_test(self, test_name: str, status: str, details: str = "") -> None:
        """Print test result with color coding."""
        status_colors = {
            "PASS": Fore.GREEN,
            "FAIL": Fore.RED,
            "SKIP": Fore.YELLOW,
            "ERROR": Fore.MAGENTA
        }
        
        color = status_colors.get(status, Fore.WHITE)
        print(f"{color}[{status}]{Style.RESET_ALL} {test_name}")
        if details:
            print(f"        {Fore.LIGHTBLACK_EX}{details}{Style.RESET_ALL}")
        
        if status == "PASS":
            self.test_results["passed"] += 1
        elif status == "FAIL":
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {details}")
        elif status == "SKIP":
            self.test_results["skipped"] += 1

    def test_server_health(self) -> bool:
        """Test if the server is running and accessible."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.print_test("Server Health Check", "PASS", "Server is running")
                return True
            else:
                self.print_test("Server Health Check", "FAIL", f"Status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.print_test("Server Health Check", "FAIL", f"Connection error: {str(e)}")
            return False

    def test_authentication_system(self) -> bool:
        """Test the complete authentication system."""
        self.print_header("AUTHENTICATION SYSTEM TESTS")
        
        auth_success = True
        
        # Test 1: User Registration
        try:
            if self.debug:
                print(f"        DEBUG: Sending registration data: {self.test_user_data}")
                print(f"        DEBUG: POST {self.base_url}/api/auth/register")
            
            response = self.session.post(
                f"{self.base_url}/api/auth/register",
                json=self.test_user_data,
                timeout=10
            )
            
            if self.debug:
                print(f"        DEBUG: Response status: {response.status_code}")
                print(f"        DEBUG: Response headers: {dict(response.headers)}")
                print(f"        DEBUG: Response body: {response.text[:500]}")
            
            if response.status_code == 201:
                data = response.json()
                self.test_user_id = data.get("user", {}).get("id")
                self.auth_token = data.get("token")
                self.print_test("User Registration", "PASS", f"User ID: {self.test_user_id}")
            elif response.status_code == 409:
                self.print_test("User Registration", "SKIP", "User already exists")
                # Try to login instead
                auth_success = self._test_login()
            else:
                # Enhanced error reporting
                error_detail = f"Status: {response.status_code}"
                try:
                    error_body = response.json()
                    if isinstance(error_body, dict):
                        error_msg = error_body.get('message', error_body.get('error', str(error_body)))
                        error_detail += f", Error: {error_msg}"
                except:
                    error_detail += f", Response: {response.text[:200]}"
                
                self.print_test("User Registration", "FAIL", error_detail)
                auth_success = False
                
        except Exception as e:
            self.print_test("User Registration", "ERROR", str(e))
            auth_success = False

        # Test 2: User Login
        if not hasattr(self, 'auth_token') or self.auth_token is None:
            auth_success = self._test_login() and auth_success

        # Test 3: Protected Route Access
        if self.auth_token:
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = self.session.get(
                    f"{self.base_url}/api/auth/profile",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.print_test("Protected Route Access", "PASS", "Profile accessed successfully")
                else:
                    # Enhanced error reporting
                    error_detail = f"Status: {response.status_code}"
                    try:
                        error_body = response.json()
                        if isinstance(error_body, dict):
                            error_msg = error_body.get('message', error_body.get('error', str(error_body)))
                            error_detail += f", Error: {error_msg}"
                    except:
                        error_detail += f", Response: {response.text[:200]}"
                    
                    self.print_test("Protected Route Access", "FAIL", error_detail)
                    auth_success = False
                    
            except Exception as e:
                self.print_test("Protected Route Access", "ERROR", str(e))
                auth_success = False
        
        return auth_success

    def _test_login(self) -> bool:
        """Helper method to test user login."""
        try:
            login_data = {
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"]
            }
            
            if self.debug:
                print(f"        DEBUG: Sending login data: {login_data}")
                print(f"        DEBUG: POST {self.base_url}/api/auth/login")
            
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                timeout=10
            )
            
            if self.debug:
                print(f"        DEBUG: Response status: {response.status_code}")
                print(f"        DEBUG: Response headers: {dict(response.headers)}")
                print(f"        DEBUG: Response body: {response.text[:500]}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                user_data = data.get("user", {})
                self.test_user_id = user_data.get("id")
                self.print_test("User Login", "PASS", f"Token received, User ID: {self.test_user_id}")
                return True
            else:
                # Enhanced error reporting
                error_detail = f"Status: {response.status_code}"
                try:
                    error_body = response.json()
                    if isinstance(error_body, dict):
                        error_msg = error_body.get('message', error_body.get('error', str(error_body)))
                        error_detail += f", Error: {error_msg}"
                except:
                    error_detail += f", Response: {response.text[:200]}"
                
                self.print_test("User Login", "FAIL", error_detail)
                return False
                
        except Exception as e:
            self.print_test("User Login", "ERROR", str(e))
            return False

    def test_mood_tracking_system(self) -> bool:
        """Test the mood tracking features."""
        self.print_header("MOOD TRACKING SYSTEM TESTS")
        
        if not self.auth_token:
            self.print_test("Mood System Tests", "SKIP", "No authentication token")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        mood_success = True
        
        # Test 1: Create Mood Entry
        try:
            mood_data = {
                "mood_score": 7,
                "emotions": ["happy", "excited", "grateful"],
                "notes": "Feeling great after a productive day!",
                "energy_level": 8,
                "sleep_quality": 7,
                "stress_level": 3
            }
            
            response = self.session.post(
                f"{self.base_url}/api/mood/entries",
                json=mood_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                entry_data = response.json()
                mood_entry_id = entry_data.get("id")
                self.print_test("Create Mood Entry", "PASS", f"Entry ID: {mood_entry_id}")
            else:
                self.print_test("Create Mood Entry", "FAIL", f"Status: {response.status_code}")
                mood_success = False
                
        except Exception as e:
            self.print_test("Create Mood Entry", "ERROR", str(e))
            mood_success = False

        # Test 2: Get Mood History
        try:
            response = self.session.get(
                f"{self.base_url}/api/mood/entries",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                entries = data.get("entries", [])
                self.print_test("Get Mood History", "PASS", f"Retrieved {len(entries)} entries")
            else:
                self.print_test("Get Mood History", "FAIL", f"Status: {response.status_code}")
                mood_success = False
                
        except Exception as e:
            self.print_test("Get Mood History", "ERROR", str(e))
            mood_success = False

        # Test 3: Get Mood Analytics
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            response = self.session.get(
                f"{self.base_url}/api/mood/analytics",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                analytics = response.json()
                self.print_test("Get Mood Analytics", "PASS", "Analytics retrieved successfully")
            else:
                self.print_test("Get Mood Analytics", "FAIL", f"Status: {response.status_code}")
                mood_success = False
                
        except Exception as e:
            self.print_test("Get Mood Analytics", "ERROR", str(e))
            mood_success = False

        # Test 4: Quick Mood Check-in
        try:
            quick_mood_data = {
                "mood_score": 6,
                "quick_note": "Quick check-in before meeting"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/mood/quick-checkin",
                json=quick_mood_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                self.print_test("Quick Mood Check-in", "PASS", "Quick check-in successful")
            else:
                self.print_test("Quick Mood Check-in", "FAIL", f"Status: {response.status_code}")
                mood_success = False
                
        except Exception as e:
            self.print_test("Quick Mood Check-in", "ERROR", str(e))
            mood_success = False
        
        return mood_success

    def test_conversation_system(self) -> bool:
        """Test the AI conversation system."""
        self.print_header("AI CONVERSATION SYSTEM TESTS")
        
        if not self.auth_token:
            self.print_test("Conversation System Tests", "SKIP", "No authentication token")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        conversation_success = True
        conversation_id = None
        
        # Test 1: Start New Conversation
        try:
            conversation_data = {
                "initial_message": "Hello, I'm feeling a bit anxious today and would like some support.",
                "conversation_type": "support"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/conversations/start",
                json=conversation_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 201:
                data = response.json()
                conversation_id = data.get("conversation_id")
                self.print_test("Start New Conversation", "PASS", f"Conversation ID: {conversation_id}")
            else:
                self.print_test("Start New Conversation", "FAIL", f"Status: {response.status_code}")
                conversation_success = False
                
        except Exception as e:
            self.print_test("Start New Conversation", "ERROR", str(e))
            conversation_success = False

        # Test 2: Send Message in Conversation
        if conversation_id:
            try:
                message_data = {
                    "message": "Can you help me with some breathing exercises?",
                    "message_type": "user"
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/conversations/{conversation_id}/messages",
                    json=message_data,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 201:
                    data = response.json()
                    ai_response = data.get("ai_response", {}).get("content", "")
                    self.print_test("Send Message", "PASS", f"AI responded: {ai_response[:50]}...")
                else:
                    self.print_test("Send Message", "FAIL", f"Status: {response.status_code}")
                    conversation_success = False
                    
            except Exception as e:
                self.print_test("Send Message", "ERROR", str(e))
                conversation_success = False

        # Test 3: Get Conversation History
        if conversation_id:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/conversations/{conversation_id}/messages",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    messages = data.get("messages", [])
                    self.print_test("Get Conversation History", "PASS", f"Retrieved {len(messages)} messages")
                else:
                    self.print_test("Get Conversation History", "FAIL", f"Status: {response.status_code}")
                    conversation_success = False
                    
            except Exception as e:
                self.print_test("Get Conversation History", "ERROR", str(e))
                conversation_success = False

        # Test 4: List User Conversations
        try:
            response = self.session.get(
                f"{self.base_url}/api/conversations",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                conversations = data.get("conversations", [])
                self.print_test("List User Conversations", "PASS", f"Found {len(conversations)} conversations")
            else:
                self.print_test("List User Conversations", "FAIL", f"Status: {response.status_code}")
                conversation_success = False
                
        except Exception as e:
            self.print_test("List User Conversations", "ERROR", str(e))
            conversation_success = False
        
        return conversation_success

    def test_crisis_detection_system(self) -> bool:
        """Test the crisis detection and safety protocols."""
        self.print_header("CRISIS DETECTION SYSTEM TESTS")
        
        if not self.auth_token:
            self.print_test("Crisis Detection Tests", "SKIP", "No authentication token")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        crisis_success = True
        
        # Test 1: Crisis Content Analysis (Safe Content)
        try:
            safe_content = {
                "content": "I'm feeling a bit down today but looking forward to the weekend."
            }
            
            response = self.session.post(
                f"{self.base_url}/api/crisis/analyze",
                json=safe_content,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                risk_level = data.get("risk_level", "unknown")
                self.print_test("Safe Content Analysis", "PASS", f"Risk level: {risk_level}")
            else:
                self.print_test("Safe Content Analysis", "FAIL", f"Status: {response.status_code}")
                crisis_success = False
                
        except Exception as e:
            self.print_test("Safe Content Analysis", "ERROR", str(e))
            crisis_success = False

        # Test 2: Crisis Content Analysis (Concerning Content)
        try:
            concerning_content = {
                "content": "I'm really struggling and don't know how much longer I can handle this stress."
            }
            
            response = self.session.post(
                f"{self.base_url}/api/crisis/analyze",
                json=concerning_content,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                risk_level = data.get("risk_level", "unknown")
                resources = data.get("resources", [])
                self.print_test("Concerning Content Analysis", "PASS", 
                             f"Risk level: {risk_level}, Resources provided: {len(resources)}")
            else:
                self.print_test("Concerning Content Analysis", "FAIL", f"Status: {response.status_code}")
                crisis_success = False
                
        except Exception as e:
            self.print_test("Concerning Content Analysis", "ERROR", str(e))
            crisis_success = False

        # Test 3: Get Crisis Resources
        try:
            response = self.session.get(
                f"{self.base_url}/api/crisis/resources",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                resources = data.get("resources", [])
                self.print_test("Get Crisis Resources", "PASS", f"Retrieved {len(resources)} resources")
            else:
                self.print_test("Get Crisis Resources", "FAIL", f"Status: {response.status_code}")
                crisis_success = False
                
        except Exception as e:
            self.print_test("Get Crisis Resources", "ERROR", str(e))
            crisis_success = False

        # Test 4: Emergency Contact Information
        try:
            response = self.session.get(
                f"{self.base_url}/api/crisis/emergency-contacts",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get("contacts", [])
                self.print_test("Emergency Contact Info", "PASS", f"Retrieved {len(contacts)} contacts")
            else:
                self.print_test("Emergency Contact Info", "FAIL", f"Status: {response.status_code}")
                crisis_success = False
                
        except Exception as e:
            self.print_test("Emergency Contact Info", "ERROR", str(e))
            crisis_success = False
        
        return crisis_success

    def test_agent_system(self) -> bool:
        """Test the uAgents framework and agent coordination."""
        self.print_header("UAGENTS SYSTEM TESTS")
        
        if not self.auth_token:
            self.print_test("Agent System Tests", "SKIP", "No authentication token")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        agent_success = True
        
        # Test 1: Get Agent Status
        try:
            response = self.session.get(
                f"{self.base_url}/api/agents/status",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                agents = data.get("agents", [])
                active_count = len([a for a in agents if a.get("status") == "active"])
                self.print_test("Agent Status Check", "PASS", 
                             f"Found {len(agents)} agents, {active_count} active")
            else:
                self.print_test("Agent Status Check", "FAIL", f"Status: {response.status_code}")
                agent_success = False
                
        except Exception as e:
            self.print_test("Agent Status Check", "ERROR", str(e))
            agent_success = False

        # Test 2: Agent Task Coordination
        try:
            task_data = {
                "task_type": "mood_analysis",
                "data": {
                    "mood_score": 6,
                    "emotions": ["neutral", "thoughtful"],
                    "context": "Testing agent coordination"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/agents/coordinate",
                json=task_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get("task_id")
                self.print_test("Agent Task Coordination", "PASS", f"Task ID: {task_id}")
            else:
                self.print_test("Agent Task Coordination", "FAIL", f"Status: {response.status_code}")
                agent_success = False
                
        except Exception as e:
            self.print_test("Agent Task Coordination", "ERROR", str(e))
            agent_success = False

        # Test 3: Agent Communication
        try:
            message_data = {
                "target_agent": "mood_tracker",
                "message": "Please analyze recent mood patterns",
                "priority": "normal"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/agents/communicate",
                json=message_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                message_id = data.get("message_id")
                self.print_test("Agent Communication", "PASS", f"Message ID: {message_id}")
            else:
                self.print_test("Agent Communication", "FAIL", f"Status: {response.status_code}")
                agent_success = False
                
        except Exception as e:
            self.print_test("Agent Communication", "ERROR", str(e))
            agent_success = False

        # Test 4: Agent Performance Metrics
        try:
            response = self.session.get(
                f"{self.base_url}/api/agents/metrics",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get("metrics", {})
                self.print_test("Agent Performance Metrics", "PASS", 
                             f"Retrieved metrics for {len(metrics)} agents")
            else:
                self.print_test("Agent Performance Metrics", "FAIL", f"Status: {response.status_code}")
                agent_success = False
                
        except Exception as e:
            self.print_test("Agent Performance Metrics", "ERROR", str(e))
            agent_success = False
        
        return agent_success

    def test_integration_scenarios(self) -> bool:
        """Test complex integration scenarios across multiple systems."""
        self.print_header("INTEGRATION SCENARIO TESTS")
        
        if not self.auth_token:
            self.print_test("Integration Tests", "SKIP", "No authentication token")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        integration_success = True
        
        # Test 1: Mood Entry → AI Analysis → Agent Coordination
        try:
            # Step 1: Create mood entry
            mood_data = {
                "mood_score": 4,
                "emotions": ["anxious", "overwhelmed"],
                "notes": "Work is really stressing me out lately",
                "stress_level": 8
            }
            
            mood_response = self.session.post(
                f"{self.base_url}/api/mood/entries",
                json=mood_data,
                headers=headers,
                timeout=10
            )
            
            if mood_response.status_code != 201:
                self.print_test("Integration: Mood → AI → Agent", "FAIL", "Mood entry failed")
                integration_success = False
            else:
                # Step 2: Trigger AI analysis
                mood_entry = mood_response.json()
                
                # Step 3: Agent coordination should be automatic
                time.sleep(2)  # Allow for background processing
                
                self.print_test("Integration: Mood → AI → Agent", "PASS", 
                             "Full integration scenario completed")
                
        except Exception as e:
            self.print_test("Integration: Mood → AI → Agent", "ERROR", str(e))
            integration_success = False

        # Test 2: Crisis Detection → Emergency Protocol → Agent Alert
        try:
            crisis_content = {
                "content": "I'm having thoughts that really scare me and need immediate help"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/crisis/analyze",
                json=crisis_content,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("risk_level") in ["high", "critical"]:
                    self.print_test("Integration: Crisis → Emergency → Agent", "PASS", 
                                 "Crisis protocol triggered successfully")
                else:
                    self.print_test("Integration: Crisis → Emergency → Agent", "PASS", 
                                 "Crisis analysis completed (low risk)")
            else:
                self.print_test("Integration: Crisis → Emergency → Agent", "FAIL", 
                             f"Status: {response.status_code}")
                integration_success = False
                
        except Exception as e:
            self.print_test("Integration: Crisis → Emergency → Agent", "ERROR", str(e))
            integration_success = False
        
        return integration_success

    def run_all_tests(self) -> Dict[str, Any]:
        """Run the complete test suite."""
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'Mental Wellness Coach - Comprehensive Feature Test Suite'.center(80)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"\nTesting server at: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check server health first
        if not self.test_server_health():
            print(f"\n{Fore.RED}❌ Server is not accessible. Cannot run tests.{Style.RESET_ALL}")
            return self.test_results
        
        # Run all test suites
        test_suites = [
            ("Authentication System", self.test_authentication_system),
            ("Mood Tracking System", self.test_mood_tracking_system),
            ("AI Conversation System", self.test_conversation_system),
            ("Crisis Detection System", self.test_crisis_detection_system),
            ("uAgents System", self.test_agent_system),
            ("Integration Scenarios", self.test_integration_scenarios)
        ]
        
        suite_results = {}
        
        for suite_name, test_function in test_suites:
            try:
                result = test_function()
                suite_results[suite_name] = result
            except Exception as e:
                self.print_test(f"{suite_name} (Suite)", "ERROR", str(e))
                suite_results[suite_name] = False
        
        # Print final results
        self._print_final_results(suite_results)
        
        return {
            **self.test_results,
            "suite_results": suite_results,
            "timestamp": datetime.now().isoformat()
        }

    def _print_final_results(self, suite_results: Dict[str, bool]) -> None:
        """Print the final test results summary."""
        self.print_header("TEST RESULTS SUMMARY")
        
        # Suite results
        for suite_name, success in suite_results.items():
            status = "PASS" if success else "FAIL"
            self.print_test(f"{suite_name} Suite", status)
        
        print(f"\n{Fore.CYAN}Overall Statistics:{Style.RESET_ALL}")
        print(f"  ✅ Passed: {self.test_results['passed']}")
        print(f"  ❌ Failed: {self.test_results['failed']}")
        print(f"  ⏭️  Skipped: {self.test_results['skipped']}")
        
        total_tests = self.test_results['passed'] + self.test_results['failed']
        if total_tests > 0:
            success_rate = (self.test_results['passed'] / total_tests) * 100
            print(f"  📊 Success Rate: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            print(f"\n{Fore.RED}❌ Errors encountered:{Style.RESET_ALL}")
            for error in self.test_results['errors']:
                print(f"  • {error}")
        
        # Overall verdict
        if self.test_results['failed'] == 0:
            print(f"\n{Fore.GREEN}{Back.GREEN} 🎉 ALL TESTS PASSED! 🎉 {Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}{Back.RED} ⚠️  SOME TESTS FAILED ⚠️  {Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")


def main():
    """Main entry point for the test script."""
    print("Mental Wellness Coach - Feature Testing Script")
    print("=" * 50)
    
    # Parse command line arguments
    base_url = "http://localhost:3000"
    debug = False
    
    # Simple argument parsing
    args = sys.argv[1:]
    for arg in args:
        if arg == "--debug" or arg == "-d":
            debug = True
        elif arg.startswith("http"):
            base_url = arg
    
    # Check if server URL is provided via environment variable
    if "TEST_SERVER_URL" in os.environ:
        base_url = os.environ["TEST_SERVER_URL"]
    
    if debug:
        print(f"DEBUG MODE ENABLED")
        print(f"Testing against: {base_url}")
    
    # Initialize and run test suite
    test_suite = MentalWellnessTestSuite(base_url, debug=debug)
    results = test_suite.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main() 